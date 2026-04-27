'use strict';

jest.mock('aws-sdk', () => {
  return {
    S3: jest.fn().mockImplementation(() => ({
      headBucket: jest.fn(),
      createBucket: jest.fn(),
      putBucketPolicy: jest.fn(),
      putObject: jest.fn(),
      getObject: jest.fn(),
      deleteObject: jest.fn(),
      listObjectsV2: jest.fn(),
    })),
  };
});

jest.mock('async-redis', () => ({
  createClient: jest.fn().mockReturnValue({
    on: jest.fn(),
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
  }),
}));

jest.mock('jsonwebtoken', () => ({
  verify: jest.fn().mockReturnValue({ username: 'testuser', scopes: [{ scope: 'admin' }] }),
}));

jest.mock('socket.io-client', () => {
  const socket = {
    on: jest.fn(),
    open: jest.fn(),
    emit: jest.fn(),
    io: { on: jest.fn() },
  };
  return jest.fn(() => socket);
});

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  patch: jest.fn(),
  delete: jest.fn(),
}));

const axios = require('axios');

describe('node_funcs execution functions', () => {
  let node_funcs;

  beforeAll(() => {
    node_funcs = require('../../api/node_funcs');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createExecution', () => {
    test('should call archive service to create execution', async () => {
      const mockVenue = { _id: 'venue-1', name: 'WSTS' };
      const mockExecution = { _id: 'exec-1', title: 'Test Execution', status: 'IDLE' };

      axios.get.mockResolvedValue({ data: mockVenue });
      axios.post.mockResolvedValue({ data: mockExecution });

      const result = await node_funcs.createExecution(
        { title: 'Test Execution', procedure_id: 'proc-1', venue_id: 'venue-1' },
        'Bearer token123'
      );

      expect(axios.get).toHaveBeenCalled();
      expect(axios.post).toHaveBeenCalled();
      expect(result).toEqual(mockExecution);
    });

    test('should reject on archive service error', async () => {
      axios.get.mockRejectedValue({
        response: { status: 500, data: { message: 'Server Error' } },
        message: 'Request failed',
      });

      await expect(
        node_funcs.createExecution({ title: 'Test', venue_id: 'v1' }, 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('updateExecutionStatus', () => {
    test('should call archive service to update execution status', async () => {
      // updateExecutionStatus calls getExecution (get), then _updateExecutionStatus (post)
      const mockExecution = { _id: 'exec-1', status: 'IDLE', venue_id: 'v1' };
      const mockResponse = { _id: 'exec-1', status: 'RUNNING' };
      axios.get.mockResolvedValue({ data: mockExecution });
      axios.post.mockResolvedValue({ data: mockResponse });

      const result = await node_funcs.updateExecutionStatus(
        'exec-1',
        { status: 'RUNNING' },
        'Bearer token'
      );

      expect(axios.get).toHaveBeenCalled();
      expect(axios.post).toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });

    test('should reject when transitioning from closed to open status', async () => {
      const mockExecution = { _id: 'exec-1', status: 'CLOSED', venue_id: 'v1' };
      axios.get.mockResolvedValue({ data: mockExecution });

      await expect(
        node_funcs.updateExecutionStatus('exec-1', { status: 'RUNNING' }, 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('getAllExecutions', () => {
    test('should fetch executions from archive service', async () => {
      const mockData = [{ _id: 'exec-1' }, { _id: 'exec-2' }];
      axios.get.mockResolvedValue({
        data: mockData,
        headers: { 'x-total-count': 2 },
      });

      const result = await node_funcs.getAllExecutions({}, 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result.executions).toEqual(mockData);
      expect(result.total_count).toBe(2);
    });

    test('should default total_count to 0 when header missing', async () => {
      axios.get.mockResolvedValue({ data: [], headers: {} });
      const result = await node_funcs.getAllExecutions({}, 'Bearer token');
      expect(result.total_count).toBe(0);
    });

    test('should reject on archive error', async () => {
      axios.get.mockRejectedValue({
        response: { status: 500, data: { message: 'Error' } },
        message: 'fail',
      });

      await expect(
        node_funcs.getAllExecutions({}, 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('removeExecution', () => {
    test('should call archive service to delete execution', async () => {
      axios.delete.mockResolvedValue({ data: { message: 'deleted' } });

      const result = await node_funcs.removeExecution('exec-1', 'Bearer token');

      expect(axios.delete).toHaveBeenCalled();
      // removeExecution does not return a value
      expect(result).toBeUndefined();
    });

    test('should reject on error', async () => {
      axios.delete.mockRejectedValue({
        response: { status: 404, data: { message: 'Not Found' } },
        message: 'Not found',
      });

      await expect(
        node_funcs.removeExecution('exec-1', 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('getExecution', () => {
    test('should fetch a single execution', async () => {
      const mockExec = { _id: 'exec-1', title: 'Test', status: 'IDLE' };
      axios.get.mockResolvedValue({ data: mockExec });

      const result = await node_funcs.getExecution('exec-1', 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toEqual(mockExec);
    });
  });

  describe('getExecutionStatus', () => {
    test('should fetch execution status', async () => {
      const mockStatus = { status: 'RUNNING' };
      axios.get.mockResolvedValue({ data: mockStatus });

      const result = await node_funcs.getExecutionStatus('exec-1', 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toEqual(mockStatus);
    });
  });

  describe('updateExecution', () => {
    test('should call archive service to update execution', async () => {
      const mockResponse = { _id: 'exec-1', title: 'Updated' };
      axios.patch.mockResolvedValue({ data: mockResponse });

      const result = await node_funcs.updateExecution(
        'exec-1',
        { title: 'Updated' },
        'Bearer token'
      );

      expect(axios.patch).toHaveBeenCalled();
      expect(result).toEqual(mockResponse);
    });
  });
});
