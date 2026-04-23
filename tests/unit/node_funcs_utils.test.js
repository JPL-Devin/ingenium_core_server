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
  verify: jest.fn(),
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

const jwt = require('jsonwebtoken');

describe('node_funcs utility functions', () => {
  let node_funcs;

  beforeAll(() => {
    node_funcs = require('../../api/node_funcs');
  });

  describe('findLevel', () => {
    test('should return the array containing the matching elem_id at top level', () => {
      const as_run = [
        { elem_id: 'a1', children: [] },
        { elem_id: 'a2', children: [] },
      ];
      const result = node_funcs.findLevel(as_run, 'a1');
      expect(result).toBe(as_run);
    });

    test('should find elem_id in nested children', () => {
      const children = [
        { elem_id: 'b1', children: [] },
        { elem_id: 'b2', children: [] },
      ];
      const as_run = [
        { elem_id: 'a1', children: children },
      ];
      const result = node_funcs.findLevel(as_run, 'b2');
      expect(result).toBe(children);
    });

    test('should find elem_id deeply nested', () => {
      const deepChildren = [{ elem_id: 'c1' }];
      const as_run = [
        {
          elem_id: 'a1',
          children: [
            {
              elem_id: 'b1',
              children: deepChildren,
            },
          ],
        },
      ];
      const result = node_funcs.findLevel(as_run, 'c1');
      expect(result).toBe(deepChildren);
    });

    test('should return null if elem_id not found', () => {
      const as_run = [
        { elem_id: 'a1', children: [] },
        { elem_id: 'a2' },
      ];
      const result = node_funcs.findLevel(as_run, 'missing');
      expect(result).toBeNull();
    });

    test('should handle empty array', () => {
      const result = node_funcs.findLevel([], 'any');
      expect(result).toBeNull();
    });

    test('should search all siblings, not just the first one', () => {
      const targetChildren = [{ elem_id: 'target' }];
      const as_run = [
        { elem_id: 'a1', children: [] },
        { elem_id: 'a2', children: targetChildren },
      ];
      const result = node_funcs.findLevel(as_run, 'target');
      expect(result).toBe(targetChildren);
    });
  });

  describe('NumerTOC', () => {
    test('should generate TOC from flat section items', () => {
      const section = [
        { elem_type: 'SECTION', number: '1', title: 'Section 1' },
        { elem_type: 'SECTION', number: '2', title: 'Section 2' },
      ];
      const result = node_funcs.NumerTOC(section, []);
      expect(result).toEqual([
        { number: '1', title: 'Section 1' },
        { number: '2', title: 'Section 2' },
      ]);
    });

    test('should skip PARAGRAPH items', () => {
      const section = [
        { elem_type: 'SECTION', number: '1', title: 'Section 1' },
        { elem_type: 'PARAGRAPH', number: '2', title: 'Paragraph 1' },
        { elem_type: 'STEP', number: '3', title: 'Step 1' },
      ];
      const result = node_funcs.NumerTOC(section, []);
      expect(result).toEqual([
        { number: '1', title: 'Section 1' },
        { number: '3', title: 'Step 1' },
      ]);
    });

    test('should recurse into children', () => {
      const section = [
        {
          elem_type: 'SECTION',
          number: '1',
          title: 'Parent',
          children: [
            { elem_type: 'SECTION', number: '1.1', title: 'Child' },
          ],
        },
      ];
      const result = node_funcs.NumerTOC(section, []);
      expect(result).toEqual([
        { number: '1', title: 'Parent' },
        { number: '1.1', title: 'Child' },
      ]);
    });

    test('should process ALL items (not just first non-paragraph)', () => {
      const section = [
        { elem_type: 'SECTION', number: '1', title: 'First' },
        { elem_type: 'STEP', number: '2', title: 'Second' },
        { elem_type: 'SECTION', number: '3', title: 'Third' },
      ];
      const result = node_funcs.NumerTOC(section, []);
      expect(result).toHaveLength(3);
      expect(result[2]).toEqual({ number: '3', title: 'Third' });
    });

    test('should handle empty section', () => {
      const result = node_funcs.NumerTOC([], []);
      expect(result).toEqual([]);
    });

    test('should handle deeply nested structures', () => {
      const section = [
        {
          elem_type: 'SECTION', number: '1', title: 'L1',
          children: [
            {
              elem_type: 'SECTION', number: '1.1', title: 'L2',
              children: [
                { elem_type: 'STEP', number: '1.1.1', title: 'L3' },
              ],
            },
          ],
        },
      ];
      const result = node_funcs.NumerTOC(section, []);
      expect(result).toEqual([
        { number: '1', title: 'L1' },
        { number: '1.1', title: 'L2' },
        { number: '1.1.1', title: 'L3' },
      ]);
    });
  });

  describe('parse_token', () => {
    test('should extract token from Bearer authorization header', () => {
      const result = node_funcs.parse_token('Bearer abc123xyz');
      expect(result).toBe('abc123xyz');
    });

    test('should return empty string for single word header', () => {
      const result = node_funcs.parse_token('nobearer');
      expect(result).toBe('');
    });

    test('should handle header with multiple spaces', () => {
      const result = node_funcs.parse_token('Bearer token extra');
      expect(result).toBe('token');
    });
  });

  describe('parse_username', () => {
    test('should decode JWT and return username', () => {
      jwt.verify.mockReturnValue({ username: 'testuser' });
      const result = node_funcs.parse_username('Bearer faketoken');
      expect(result).toBe('testuser');
      expect(jwt.verify).toHaveBeenCalled();
    });

    test('should return empty string for empty header', () => {
      const result = node_funcs.parse_username('');
      expect(result).toBe('');
    });
  });

  describe('is_string', () => {
    test('should return true for string literals', () => {
      expect(node_funcs.is_string('hello')).toBe(true);
    });

    test('should return true for String objects', () => {
      expect(node_funcs.is_string(String('test'))).toBe(true);
    });

    test('should return false for numbers', () => {
      expect(node_funcs.is_string(123)).toBe(false);
    });

    test('should return false for objects', () => {
      expect(node_funcs.is_string({})).toBe(false);
    });

    test('should return false for null', () => {
      expect(node_funcs.is_string(null)).toBe(false);
    });
  });

  describe('to_obj_string', () => {
    test('should return string as-is', () => {
      expect(node_funcs.to_obj_string('hello')).toBe('hello');
    });

    test('should convert objects to inspect string', () => {
      const result = node_funcs.to_obj_string({ a: 1 });
      expect(typeof result).toBe('string');
      expect(result).toContain('a');
    });
  });

  describe('transform_axios_error', () => {
    test('should transform error with response data', () => {
      const err = {
        response: {
          status: 404,
          data: {
            message: 'Not Found',
            details: ['resource missing'],
            error_type: 'NotFoundError',
            error_source: 'archive',
          },
        },
        message: 'Request failed',
      };
      const result = node_funcs.transform_axios_error(err);
      expect(result.message).toBe('Not Found');
      expect(result.http_code_at_source).toBe(404);
      expect(result.details).toEqual(['resource missing']);
      expect(result.error_type).toBe('NotFoundError');
      expect(result.error_source).toBe('archive');
    });

    test('should handle string response data', () => {
      const err = {
        response: {
          status: 500,
          data: 'Internal Server Error',
        },
        message: 'fail',
      };
      const result = node_funcs.transform_axios_error(err);
      expect(result.message).toBe('Internal Server Error');
      expect(result.http_code_at_source).toBe(500);
    });

    test('should handle error without response', () => {
      const err = {
        message: 'Network Error',
        stack: 'Error: Network Error\n    at ...',
      };
      const result = node_funcs.transform_axios_error(err);
      expect(result.message).toBe('Network Error');
      expect(result.details).toHaveLength(1);
    });
  });

  describe('push_error', () => {
    test('should wrap error with message', () => {
      const err = { message: 'original error' };
      const result = node_funcs.push_error('wrapper message', err);
      expect(result.message).toBe('wrapper message');
      expect(result.details).toContain('original error');
    });

    test('should handle string error', () => {
      const result = node_funcs.push_error('wrapper', 'simple error');
      expect(result.message).toBe('wrapper');
    });
  });

  describe('get_auth_key', () => {
    test('should return authorization header value', () => {
      const result = node_funcs.get_auth_key({ authorization: 'Bearer xyz' });
      expect(result).toBe('Bearer xyz');
    });

    test('should return empty string when no authorization header', () => {
      const result = node_funcs.get_auth_key({});
      expect(result).toBe('');
    });
  });

  describe('is_break_point_on', () => {
    test('should return true when auto mode with break points enabled', () => {
      const execution = {
        mode: 'AUTO',
        pause_conditions: { on_break_point: true },
      };
      expect(node_funcs.is_break_point_on(execution)).toBe(true);
    });

    test('should return false when not auto mode', () => {
      const execution = {
        mode: 'MANUAL',
        pause_conditions: { on_break_point: true },
      };
      expect(node_funcs.is_break_point_on(execution)).toBe(false);
    });
  });

  describe('is_closed', () => {
    test('should return true for CLOSED status', () => {
      expect(node_funcs.is_closed({ status: 'CLOSED' })).toBe(true);
    });

    test('should return false for other statuses', () => {
      expect(node_funcs.is_closed({ status: 'RUNNING' })).toBe(false);
    });
  });

  describe('get_step_completion_status', () => {
    test('should return status for PASS', () => {
      const step = { execution: { meta_data: { status: 'PASS' } } };
      expect(node_funcs.get_step_completion_status(step)).toBe('PASS');
    });

    test('should return status for FAIL', () => {
      const step = { execution: { meta_data: { status: 'FAIL' } } };
      expect(node_funcs.get_step_completion_status(step)).toBe('FAIL');
    });

    test('should return status for ERROR', () => {
      const step = { execution: { meta_data: { status: 'ERROR' } } };
      expect(node_funcs.get_step_completion_status(step)).toBe('ERROR');
    });

    test('should return status for OVERRIDE_PASS', () => {
      const step = { execution: { meta_data: { status: 'OVERRIDE_PASS' } } };
      expect(node_funcs.get_step_completion_status(step)).toBe('OVERRIDE_PASS');
    });

    test('should return status for OVERRIDE_FAIL', () => {
      const step = { execution: { meta_data: { status: 'OVERRIDE_FAIL' } } };
      expect(node_funcs.get_step_completion_status(step)).toBe('OVERRIDE_FAIL');
    });

    test('should return null for RUNNING status', () => {
      const step = { execution: { meta_data: { status: 'RUNNING' } } };
      expect(node_funcs.get_step_completion_status(step)).toBeNull();
    });

    test('should return null for NONE status', () => {
      const step = { execution: { meta_data: { status: 'NONE' } } };
      expect(node_funcs.get_step_completion_status(step)).toBeNull();
    });

    test('should return null for null step', () => {
      expect(node_funcs.get_step_completion_status(null)).toBeNull();
    });

    test('should return null for step without execution', () => {
      expect(node_funcs.get_step_completion_status({})).toBeNull();
    });
  });

  describe('time_references', () => {
    test('should be an array of valid time reference strings', () => {
      expect(Array.isArray(node_funcs.time_references)).toBe(true);
      expect(node_funcs.time_references).toContain('CURRENT_TIME');
      expect(node_funcs.time_references).toContain('LAST_STEP_START');
      expect(node_funcs.time_references).toContain('LAST_STEP_END');
      expect(node_funcs.time_references.length).toBeGreaterThan(5);
    });
  });
});
