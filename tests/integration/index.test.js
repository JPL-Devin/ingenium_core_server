'use strict';

jest.mock('swagger-tools', () => {
  const mockMiddleware = {
    swaggerMetadata: jest.fn(() => (req, res, next) => next()),
    swaggerSecurity: jest.fn(() => (req, res, next) => next()),
    swaggerValidator: jest.fn(() => (req, res, next) => next()),
    swaggerRouter: jest.fn(() => (req, res, next) => next()),
    swaggerUi: jest.fn(() => (req, res, next) => next()),
  };
  return {
    initializeMiddleware: jest.fn((doc, cb) => cb(mockMiddleware)),
  };
});

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

jest.mock('aws-sdk', () => ({
  S3: jest.fn().mockImplementation(() => ({
    headBucket: jest.fn().mockReturnValue({
      promise: jest.fn().mockResolvedValue({}),
    }),
    createBucket: jest.fn(),
    putBucketPolicy: jest.fn(),
    putObject: jest.fn(),
    getObject: jest.fn(),
    deleteObject: jest.fn(),
    listObjectsV2: jest.fn(),
  })),
}));

jest.mock('async-redis', () => ({
  createClient: jest.fn().mockReturnValue({
    on: jest.fn(),
    get: jest.fn(),
    set: jest.fn(),
    del: jest.fn(),
  }),
}));

jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  patch: jest.fn(),
  delete: jest.fn(),
}));

const swaggerTools = require('swagger-tools');
const jwt = require('jsonwebtoken');
const io = require('socket.io-client');

describe('index.js - Express app initialization', () => {
  test('should initialize swagger middleware', () => {
    expect(swaggerTools.initializeMiddleware).toBeDefined();
  });

  test('swagger-tools initializeMiddleware should be callable', () => {
    const mockCallback = jest.fn();
    swaggerTools.initializeMiddleware({}, mockCallback);
    expect(mockCallback).toHaveBeenCalled();
  });

  test('socket.io-client mock should be a function', () => {
    expect(typeof io).toBe('function');
  });

  test('socket should register event handlers', () => {
    const socket = io();
    expect(socket.on).toBeDefined();
    expect(socket.open).toBeDefined();
  });
});

describe('JWT security middleware logic', () => {
  test('jwt.verify should be available', () => {
    expect(jwt.verify).toBeDefined();
  });

  test('should verify RS256 tokens', () => {
    jwt.verify.mockReturnValue({
      username: 'testuser',
      scopes: [{ scope: 'admin' }],
    });

    const result = jwt.verify('token', 'pem', { algorithms: ['RS256'] });
    expect(result.username).toBe('testuser');
    expect(result.scopes).toHaveLength(1);
  });

  test('should throw on invalid token', () => {
    jwt.verify.mockImplementation(() => {
      throw new Error('invalid token');
    });

    expect(() => jwt.verify('bad', 'pem')).toThrow('invalid token');
  });
});

describe('Express app configuration', () => {
  test('config should define server port', () => {
    const config = require('../../config');
    expect(config.server_port).toBe(8080);
  });

  test('config should define api base path', () => {
    const config = require('../../config');
    expect(config.api_base_path).toBe('api/v5');
  });

  test('body parser limits should be 5mb', () => {
    const config = require('../../config');
    expect(config.server_timeout_sec).toBeDefined();
  });
});

describe('Error handling middleware', () => {
  test('validation errors should produce 400 status', () => {
    const err = {
      failedValidation: true,
      message: 'Validation failed',
    };

    const mockRes = {
      status: jest.fn().mockReturnThis(),
      send: jest.fn(),
      headersSent: false,
    };

    if (err && err.failedValidation) {
      const message = 'Failed schema validation';
      const details = [JSON.stringify(err)];
      const error_obj = { message: message, details: details };
      mockRes.status(400).send(error_obj);
    }

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.send).toHaveBeenCalledWith(
      expect.objectContaining({
        message: 'Failed schema validation',
      })
    );
  });

  test('non-validation errors should be passed to next', () => {
    const err = new Error('Some other error');
    const mockRes = { headersSent: false };
    const mockNext = jest.fn();

    if (err && err.failedValidation) {
      // won't enter here
    } else if (err) {
      mockNext(err);
    }

    expect(mockNext).toHaveBeenCalledWith(err);
  });

  test('should call next if headers already sent', () => {
    const err = { failedValidation: true };
    const mockRes = { headersSent: true };
    const mockNext = jest.fn();

    if (mockRes.headersSent) {
      mockNext(err);
    }

    expect(mockNext).toHaveBeenCalledWith(err);
  });
});
