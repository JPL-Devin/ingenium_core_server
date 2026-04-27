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

describe('node_funcs venue functions', () => {
  let node_funcs;

  beforeAll(() => {
    node_funcs = require('../../api/node_funcs');
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('createVenue', () => {
    test('should call archive service to create a venue', async () => {
      const mockVenue = { _id: 'venue-1', name: 'WSTS-Lab', type: 'WSTS' };
      axios.post.mockResolvedValue({ data: mockVenue });

      const result = await node_funcs.createVenue(
        { name: 'WSTS-Lab', type: 'WSTS' },
        'Bearer token'
      );

      expect(axios.post).toHaveBeenCalled();
      expect(result).toEqual(mockVenue);
    });

    test('should reject on archive service error', async () => {
      axios.post.mockRejectedValue({
        response: { status: 400, data: { message: 'Invalid venue' } },
        message: 'Bad request',
      });

      await expect(
        node_funcs.createVenue({ name: '' }, 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('createVenueGroup', () => {
    test('should call archive service to create venue group', async () => {
      const mockGroup = { _id: 'group-1', name: 'Test Group' };
      axios.post.mockResolvedValue({ data: mockGroup });

      const result = await node_funcs.createVenueGroup(
        { name: 'Test Group' },
        'Bearer token'
      );

      expect(axios.post).toHaveBeenCalled();
      expect(result).toEqual(mockGroup);
    });

    test('should reject on error', async () => {
      axios.post.mockRejectedValue({
        response: { status: 500, data: { message: 'Error' } },
        message: 'fail',
      });

      await expect(
        node_funcs.createVenueGroup({}, 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('getVenues', () => {
    test('should fetch venues from archive service', async () => {
      const mockData = [{ _id: 'v1' }, { _id: 'v2' }];
      axios.get.mockResolvedValue({
        data: mockData,
        headers: { 'x-total-count': 2 },
      });

      const result = await node_funcs.getVenues({}, 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result.venues).toEqual(mockData);
      expect(result.total_count).toBe(2);
    });

    test('should default total_count to 0 when header missing', async () => {
      axios.get.mockResolvedValue({ data: [], headers: {} });
      const result = await node_funcs.getVenues({}, 'Bearer token');
      expect(result.total_count).toBe(0);
    });
  });

  describe('getVenueGroups', () => {
    test('should fetch venue groups from archive service', async () => {
      const mockData = [{ _id: 'g1', name: 'Group1' }];
      axios.get.mockResolvedValue({
        data: mockData,
        headers: { 'x-total-count': 1 },
      });

      const result = await node_funcs.getVenueGroups({}, 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result.venue_groups).toEqual(mockData);
      expect(result.total_count).toBe(1);
    });
  });

  describe('getVenue', () => {
    test('should fetch a single venue', async () => {
      const mockVenue = { _id: 'v1', name: 'WSTS' };
      axios.get.mockResolvedValue({ data: mockVenue });

      const result = await node_funcs.getVenue('v1', 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toEqual(mockVenue);
    });
  });

  describe('updateVenue', () => {
    test('should update a venue (returns undefined)', async () => {
      axios.patch.mockResolvedValue({ data: {} });

      const result = await node_funcs.updateVenue('v1', { name: 'Updated' }, 'Bearer token');

      expect(axios.patch).toHaveBeenCalled();
      expect(result).toBeUndefined();
    });
  });

  describe('deleteVenue', () => {
    test('should delete a venue after checking status', async () => {
      axios.get.mockResolvedValueOnce({ data: { status: 'AVAILABLE' } })
               .mockResolvedValueOnce({ data: { _id: 'v1' }, status: 200 });
      axios.delete.mockResolvedValue({ data: { message: 'deleted' } });

      await node_funcs.deleteVenue('v1', 'Bearer token');

      expect(axios.delete).toHaveBeenCalled();
    });

    test('should reject when venue is in use', async () => {
      axios.get.mockResolvedValueOnce({ data: { status: 'IN_USE' } });

      await expect(
        node_funcs.deleteVenue('v1', 'Bearer token')
      ).rejects.toEqual({ message: 'Cannot delete venue that is in use' });
    });

    test('should reject on error', async () => {
      axios.get.mockRejectedValue({
        response: { status: 404, data: { message: 'Not Found' } },
        message: 'fail',
      });

      await expect(
        node_funcs.deleteVenue('nonexistent', 'Bearer token')
      ).rejects.toBeDefined();
    });
  });

  describe('getVenueGroup', () => {
    test('should fetch a venue group by id', async () => {
      const mockGroup = { _id: 'g1', name: 'Group1' };
      axios.get.mockResolvedValue({ data: mockGroup });

      const result = await node_funcs.getVenueGroup('g1', 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toEqual(mockGroup);
    });
  });

  describe('updateVenueGroup', () => {
    test('should update a venue group (returns undefined)', async () => {
      axios.patch.mockResolvedValue({ data: {} });

      const result = await node_funcs.updateVenueGroup('g1', { name: 'Updated Group' }, 'Bearer token');

      expect(axios.patch).toHaveBeenCalled();
      expect(result).toBeUndefined();
    });
  });

  describe('getVenueStatus', () => {
    test('should fetch venue status', async () => {
      const mockStatus = { status: 'ONLINE' };
      axios.get.mockResolvedValue({ data: mockStatus });

      const result = await node_funcs.getVenueStatus('v1', 'Bearer token');

      expect(axios.get).toHaveBeenCalled();
      expect(result).toEqual(mockStatus);
    });
  });

  describe('updateVenueStatus', () => {
    test('should update venue status (returns undefined)', async () => {
      axios.patch.mockResolvedValue({ data: {} });

      const result = await node_funcs.updateVenueStatus('v1', { status: 'OFFLINE' }, 'Bearer token');

      expect(axios.patch).toHaveBeenCalled();
      expect(result).toBeUndefined();
    });
  });
});
