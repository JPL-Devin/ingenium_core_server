'use strict';

describe('config', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  test('should have default values when no env vars set', () => {
    delete process.env.EXECUTION_MONITOR_URL;
    delete process.env.FILE_SERVER_API_HOST;
    delete process.env.FILE_SERVER_ACCESS_KEY;
    delete process.env.FILE_SERVER_SECRET_KEY;
    delete process.env.MEDIA_BUCKET;
    delete process.env.REDIS_HOST;
    delete process.env.REDIS_PORT;
    delete process.env.SERVER_TIMEOUT_SEC;
    delete process.env.PUBLIC_PEM;
    delete process.env.EMS_SECRET;

    const config = require('../../config');

    expect(config.EXECUTION_MONITOR_URL).toBe('http://localhost:3000/api/v2/execution_event_publish');
    expect(config.api_base_path).toBe('api/v5');
    expect(config.server_port).toBe(8080);
    expect(config.FILE_SERVER_API_HOST).toBe('http://localhost:9000');
    expect(config.FILE_SERVER_ACCESS_KEY).toBe('');
    expect(config.FILE_SERVER_SECRET_KEY).toBe('');
    expect(config.MEDIA_BUCKET).toBe('ingenium-media-test');
    expect(config.REDIS_HOST).toBe('exec_redis');
    expect(config.REDIS_PORT).toBe(6379);
    expect(config.server_timeout_sec).toBe('290');
    expect(config.public_pem).toBe('');
    expect(config.ems_secret).toBe('');
    expect(config.EXECUTION_SWITCH_WAIT_SEC).toBe(10);
  });

  test('should use env var values when set', () => {
    process.env.EXECUTION_MONITOR_URL = 'http://monitor:4000/api/v2/publish';
    process.env.FILE_SERVER_API_HOST = 'http://fileserver:8000';
    process.env.FILE_SERVER_ACCESS_KEY = 'access123';
    process.env.FILE_SERVER_SECRET_KEY = 'secret456';
    process.env.MEDIA_BUCKET = 'custom-bucket';
    process.env.REDIS_HOST = 'redis-host';
    process.env.REDIS_PORT = '6380';
    process.env.SERVER_TIMEOUT_SEC = '120';
    process.env.PUBLIC_PEM = 'test-pem';
    process.env.EMS_SECRET = 'test-secret';

    const config = require('../../config');

    expect(config.EXECUTION_MONITOR_URL).toBe('http://monitor:4000/api/v2/publish');
    expect(config.FILE_SERVER_API_HOST).toBe('http://fileserver:8000');
    expect(config.FILE_SERVER_ACCESS_KEY).toBe('access123');
    expect(config.FILE_SERVER_SECRET_KEY).toBe('secret456');
    expect(config.MEDIA_BUCKET).toBe('custom-bucket');
    expect(config.REDIS_HOST).toBe('redis-host');
    expect(config.REDIS_PORT).toBe(6380);
    expect(config.server_timeout_sec).toBe('120');
    expect(config.public_pem).toBe('test-pem');
    expect(config.ems_secret).toBe('test-secret');
  });
});
