'use strict';

const { step_dict } = require('../../api/step_definitions');

describe('step_definitions', () => {
  test('should export step_dict', () => {
    expect(step_dict).toBeDefined();
    expect(typeof step_dict).toBe('object');
  });

  test('should contain MANUAL_INPUT step type', () => {
    expect(step_dict).toHaveProperty('MANUAL_INPUT');
    expect(step_dict.MANUAL_INPUT.elem_type).toBe('STEP');
    expect(step_dict.MANUAL_INPUT.step_type).toBe('MANUAL_INPUT');
  });

  test('should contain MANUAL_EIP step type', () => {
    expect(step_dict).toHaveProperty('MANUAL_EIP');
    expect(step_dict.MANUAL_EIP.elem_type).toBe('STEP');
    expect(step_dict.MANUAL_EIP.step_type).toBe('MANUAL_EIP');
  });

  test('should contain VENUE_CONFIG_MANUAL step type', () => {
    expect(step_dict).toHaveProperty('VENUE_CONFIG_MANUAL');
    expect(step_dict.VENUE_CONFIG_MANUAL.step_type).toBe('VENUE_CONFIG_MANUAL');
  });

  test('should contain ENVIRONMENT_MANUAL step type', () => {
    expect(step_dict).toHaveProperty('ENVIRONMENT_MANUAL');
    expect(step_dict.ENVIRONMENT_MANUAL.step_type).toBe('ENVIRONMENT_MANUAL');
  });

  test('should contain GDS_MANUAL step type', () => {
    expect(step_dict).toHaveProperty('GDS_MANUAL');
    expect(step_dict.GDS_MANUAL.step_type).toBe('GDS_MANUAL');
  });

  test('should contain VERIFICATION_ITEM step type', () => {
    expect(step_dict).toHaveProperty('VERIFICATION_ITEM');
    expect(step_dict.VERIFICATION_ITEM.step_type).toBe('VERIFICATION_ITEM');
    expect(step_dict.VERIFICATION_ITEM.executable).toBe('NONE');
    expect(step_dict.VERIFICATION_ITEM.verifiable).toBe(false);
  });

  test('should contain VERIFICATION_ITEM_STATUS step type', () => {
    expect(step_dict).toHaveProperty('VERIFICATION_ITEM_STATUS');
    expect(step_dict.VERIFICATION_ITEM_STATUS.step_type).toBe('VERIFICATION_ITEM_STATUS');
    expect(step_dict.VERIFICATION_ITEM_STATUS.executable).toBe('COMPUTED');
  });

  test('should contain BUS_1553 step type', () => {
    expect(step_dict).toHaveProperty('BUS_1553');
    expect(step_dict.BUS_1553.step_type).toBe('BUS_1553');
  });

  test('should contain GRAPH_EHA step type', () => {
    expect(step_dict).toHaveProperty('GRAPH_EHA');
    expect(step_dict.GRAPH_EHA.step_type).toBe('GRAPH_EHA');
  });

  test('should contain QUERY_EVR step type', () => {
    expect(step_dict).toHaveProperty('QUERY_EVR');
    expect(step_dict.QUERY_EVR.step_type).toBe('QUERY_EVR');
  });

  test('should contain VERIFY_EHA step type', () => {
    expect(step_dict).toHaveProperty('VERIFY_EHA');
    expect(step_dict.VERIFY_EHA.step_type).toBe('VERIFY_EHA');
  });

  test('should contain WAIT_EHA step type', () => {
    expect(step_dict).toHaveProperty('WAIT_EHA');
    expect(step_dict.WAIT_EHA.step_type).toBe('WAIT_EHA');
  });

  test('each step should have execution meta_data template', () => {
    const keys = Object.keys(step_dict);
    for (const key of keys) {
      const step = step_dict[key];
      if (step.execution) {
        expect(step.execution.meta_data).toBeDefined();
        expect(step.execution.meta_data).toHaveProperty('status');
        expect(step.execution.meta_data).toHaveProperty('test_conductor');
        expect(step.execution.meta_data).toHaveProperty('time_started');
        expect(step.execution.meta_data).toHaveProperty('time_completed');
      }
    }
  });

  test('step entries with elem_type STEP should have step_type', () => {
    const keys = Object.keys(step_dict);
    for (const key of keys) {
      if (step_dict[key].elem_type === 'STEP') {
        expect(step_dict[key]).toHaveProperty('step_type');
      }
    }
  });

  test('all entries should have an elem_type property', () => {
    const keys = Object.keys(step_dict);
    for (const key of keys) {
      expect(step_dict[key]).toHaveProperty('elem_type');
    }
  });

  test('step types with specification should have authoring_user_input', () => {
    const keys = Object.keys(step_dict);
    for (const key of keys) {
      const step = step_dict[key];
      if (step.specification) {
        expect(step.specification).toHaveProperty('authoring_user_input');
      }
    }
  });

  test('executable steps should have code property', () => {
    const executableSteps = Object.keys(step_dict).filter(
      (k) => step_dict[k].executable === 'EXECUTED'
    );
    expect(executableSteps.length).toBeGreaterThan(0);
    for (const key of executableSteps) {
      expect(step_dict[key]).toHaveProperty('code');
      expect(step_dict[key].code).toHaveProperty('name');
    }
  });
});
