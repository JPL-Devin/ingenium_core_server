import xmlrunner
import os
import sys
from utils import random_string
import unittest
from config import shared_dict, logger
import json
import copy
import requests
from ingenium_client import CoreTestBase, StepTypes


class CustomScriptStepTest(CoreTestBase):
    def test_custom_script_step(self):

        authoring_user_input = {
            'script_name': 'my script one',
            'script_path': 'path1/path2/py_script.py',
            'script_id': '',
            'description': 'test script',
            'hash': 'abcdefg',
            'status': 'ACTIVE',                                
            'timeout': 240,
            'inputs': [
                {
                    'name': 'var1',
                    'description': 'first input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'value': '2'                                                                                                                     
                },
                {
                    'name': 'var2',
                    'description': 'second input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'value': '3'                                                                                                                     
                }            
            ],
            'entries': [
                {
                    'display_field': '',
                    'entry_inputs': [
                        {
                            'name': '',
                            'description': '',
                            'phase': 'AUTHORING',
                            'required': 'YES',
                            'type': 'INT',
                            'enumerations': [],
                            'value': '',
                            'default_value': ''
                        }
                    ],
                    'entry_outputs': [
                        {
                            'name': '',
                            'description': '',
                            'type': 'INT'
                        }
                    ],
                    'entry_output_array': {
                        'name': '',
                        'description': '',
                        'max_entries': 10,
                        'outputs': [
                            {
                                'name': '',
                                'description': '',
                                'visible': 'YES',
                                'type': 'INT'
                            }
                        ]
                    }
                }
            ],
            'outputs': [
                {
                    'name': 'out1',
                    'description': 'first output',
                    'type': 'INT'                                                                                                             
                },
                {
                    'name': 'out2',
                    'description': 'second output',
                    'type': 'INT'                                                                                                             
                }                
            ],
            'output_array': {
                'name': '',
                'description': '',
                'max_entries': 10,
                'outputs': [
                    {
                        'name': '',
                        'description': '',
                        'visible': 'YES',
                        'type': 'INT'
                    }
                ]
            }
        }

        step = self.perform_step_operations(StepTypes.CUSTOM_SCRIPT, authoring_user_input, False, False, procedure=True)

        execution_user_input = {
            'script_name': 'my script one',
            'script_path': 'path1/path2/py_script.py',
            'script_id': '',
            'description': 'test script',
            'hash': 'abcdefg',
            'status': 'ACTIVE',                                
            'timeout': 240,
            'inputs': [
                {
                    'name': 'var1',
                    'description': 'first input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'value': '2'                                                                                                                     
                },
                {
                    'name': 'var2',
                    'description': 'second input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'value': '3'                                                                                                                     
                }            
            ],
            'entries': [
                {
                    'display_field': '',
                    'entry_inputs': [
                        {
                            'name': '',
                            'description': '',
                            'phase': 'AUTHORING',
                            'required': 'YES',
                            'type': 'INT',
                            'enumerations': [],
                            'value': '',
                            'default_value': ''
                        }
                    ],
                    'entry_outputs': [
                        {
                            'name': '',
                            'description': '',
                            'type': 'INT'
                        }
                    ],
                    'entry_output_array': {
                        'name': '',
                        'description': '',
                        'max_entries': 10,
                        'outputs': [
                            {
                                'name': '',
                                'description': '',
                                'visible': 'YES',
                                'type': 'INT'
                            }
                        ]
                    }
                }
            ],
            'outputs': [
                {
                    'name': 'out1',
                    'description': 'first output',
                    'type': 'INT'                                                                                                             
                },
                {
                    'name': 'out2',
                    'description': 'second output',
                    'type': 'INT'                                                                                                             
                }                
            ],
            'output_array': {
                'name': '',
                'description': '',
                'max_entries': 10,
                'outputs': [
                    {
                        'name': '',
                        'description': '',
                        'visible': 'YES',
                        'type': 'INT'
                    }
                ]
            }
        }

        step = self.perform_step_operations(StepTypes.CUSTOM_SCRIPT, execution_user_input, True, False, procedure=False)

    def test_validate_procedure(self):
        procedure = self.create_procedure('proc with custom script', 'test procedure',
            'ins_id_1')

        procedure_id = procedure['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # 
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.CUSTOM_SCRIPT,
            insert_after_id=-1,
            level='CHILD')

        elem_id = res_dict['elem']['elem_id']

        script = {
            'script_name': 'my script one',
            'script_path': 'path1/path2/py_script.py',
            'script_id': 'id_1',
            'description': 'test script',
            'hash': 'abcdefg',
            'status': 'ACTIVE',
            'inputs': [
                {
                    'name': 'var1',
                    'description': 'first input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'default_value': '0'                                                                                                                
                },
                {
                    'name': 'var2',
                    'description': 'second input var',
                    'phase': 'AUTHORING',
                    'required': 'YES',
                    'type': 'INT',
                    'enumerations': [],
                    'default_value': '0'                                                                                                                
                }            
            ],
            'entries': [
                {
                    'display_field': '',
                    'entry_inputs': [
                        {
                            'name': 'entry_inputs1',
                            'description': '',
                            'phase': 'AUTHORING',
                            'required': 'YES',
                            'type': 'INT',
                            'enumerations': [],
                            'default_value': ''
                        }
                    ],
                    'entry_outputs': [
                        {
                            'name': 'entry_outputs1',
                            'description': '',
                            'type': 'INT'
                        }
                    ],
                    'entry_output_array': {
                        'name': 'entry_output_array1',
                        'description': '',
                        'max_entries': 10,
                        'outputs': [
                            {
                                'name': 'entry_output_array1_1',
                                'description': '',
                                'visible': 'YES',
                                'type': 'INT'
                            }
                        ]
                    }
                }
            ],
            'outputs': [
                {
                    'name': 'out1',
                    'description': 'first output',
                    'type': 'INT'                                                                                                             
                },
                {
                    'name': 'out2',
                    'description': 'second output',
                    'type': 'INT'                                                                                                             
                }                
            ],
            'output_array': {
                'name': 'output_array1',
                'description': '',
                'max_entries': 10,
                'outputs': [
                    {
                        'name': 'output_array11',
                        'description': '',
                        'visible': 'YES',
                        'type': 'INT'
                    }
                ]
            }
        }

        authoring_user_input = copy.deepcopy(script)

        authoring_user_input['timeout'] = 240
        authoring_user_input['inputs'][0]['value'] = '2'
        authoring_user_input['inputs'][1]['value'] = '3'
        authoring_user_input['entries'][0]['entry_inputs'][0]['value'] = ''

        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ### Create a version
        rand_1 = random_string()
        description_1 = 'description_' + rand_1
        institutional_release_id_1 = 'institutional_release_id_1_' + rand_1
        self.create_procedure_version(procedure_id, description_1, institutional_release_id_1)    

        version1_elements = self.get_version_elements(procedure_id, 1)
        version1_elem_id = version1_elements[0]['elem_id']

        ## validate with no change
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=None)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        self.assertEqual(len(validation_items), 0)

        validation_input = {
            'vis': [],
            'scripts': [script],
            'update': True
        }

        ## validate with no change
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        self.assertEqual(len(validation_items), 0)

        ## validate with hash change
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        script_1['description'] = 'description_new'
        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }

        # cannot update a version
        res_dict = self.validate_procedure_version(procedure_id, 1, validation_input, 400)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        validation_input0 = {
            'vis': [],
            'scripts': [script_1],
            'update': False
        }

        # validate a version (no update)
        res_dict = self.validate_procedure_version(procedure_id, 1, validation_input0, 200)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)

        self.assertEqual(len(validation_items), 1)
        self.assertEqual(validation_items[0]['user_action_msg'], '')
        self.assertEqual(validation_items[0]['elem_id'], version1_elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 2)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'description')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], script['description'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], script_1['description'])

        # validate working version
        
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 1)
        self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])

        updated_elems[0]['authoring_user_input']['description'] = script['description']
        updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertEqual(validation_items[0]['user_action_msg'], '')
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 2)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'description')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], script['description'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], script_1['description'])


        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## change input type
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        script_1['inputs'][0]['type'] = 'STRING'
        script_1['inputs'][0]['default_value'] = 'abc'

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        # Do not update CS step with spec changes

        # self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        # self.assertEqual(updated_elems[0]['authoring_user_input']['inputs'][0]['type'], script_1['inputs'][0]['type'])
        # self.assertEqual(updated_elems[0]['authoring_user_input']['inputs'][0]['value'], script_1['inputs'][0]['default_value'] )

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #updated_elems[0]['authoring_user_input']['inputs'][0] = authoring_user_input['inputs'][0]
        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## added input
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        script_1['inputs'].append(
            {
                'name': 'var3',
                'description': 'third input var',
                'phase': 'AUTHORING',
                'required': 'YES',
                'type': 'INT',
                'enumerations': [],
                'default_value': '0'                                                                                                                
            }  
        )

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        #self.assertEqual(len(updated_elems[0]['authoring_user_input']['inputs']), 3)

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #del updated_elems[0]['authoring_user_input']['inputs'][2]
        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## remove input
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        del script_1['inputs'][1]

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        #self.assertEqual(len(updated_elems[0]['authoring_user_input']['inputs']), 1)

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #updated_elems[0]['authoring_user_input']['inputs'].append(authoring_user_input['inputs'][1])
        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## change entry type
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        script_1['entries'][0]['entry_inputs'][0]['type'] = 'STRING'
        script_1['entries'][0]['entry_inputs'][0]['default_value'] = 'abc'

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        #self.assertEqual(updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'][0]['type'], script_1['entries'][0]['entry_inputs'][0]['type'])
        #self.assertEqual(updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'][0]['value'], script_1['entries'][0]['entry_inputs'][0]['default_value'])

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'][0] = authoring_user_input['entries'][0]['entry_inputs'][0]

        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## add entry input
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        script_1['entries'][0]['entry_inputs'].append(
            {
                'name': 'entry_inputs2',
                'description': '',
                'phase': 'AUTHORING',
                'required': 'YES',
                'type': 'INT',
                'enumerations': [],
                'default_value': ''
            }
        )

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        #self.assertEqual(len(updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs']), 2)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'][1]['name'], script_1['entries'][0]['entry_inputs'][1]['name'])

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #del updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'][1]
        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)

        ## remove entry 
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        del script_1['entries'][0]['entry_inputs'][0]

        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        #self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        #self.assertEqual(len(updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs']), 0)

        #updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        #updated_elems[0]['authoring_user_input']['entries'][0]['entry_inputs'].append(authoring_user_input['entries'][0]['entry_inputs'][0])
        #self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 1)
        self.assertTrue(len(validation_items[0]['user_action_msg']) > 0)
        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['field_name'], 'specification')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['previous_value'], '')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][1]['new_value'], '')

        ## reset
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id, authoring_user_input)
        
        ## add another step
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.CUSTOM_SCRIPT,
            insert_after_id=elem_id,
            level='SIBLING')

        elem_id_2 = res_dict['elem']['elem_id']
        self.set_step_input(procedure_url, StepTypes.CUSTOM_SCRIPT, elem_id_2, authoring_user_input)

        ## validate with hash change
        script_1 = copy.deepcopy(script)
        script_1['hash'] = 'hash_new'
        validation_input = {
            'vis': [],
            'scripts': [script_1],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input=validation_input)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 2)
        self.assertEqual(updated_elems[0]['elem_id'], elem_id)
        self.assertEqual(updated_elems[1]['elem_id'], elem_id_2)
        self.assertEqual(updated_elems[0]['authoring_user_input']['hash'], script_1['hash'])
        self.assertEqual(updated_elems[1]['authoring_user_input']['hash'], script_1['hash'])

        updated_elems[0]['authoring_user_input']['hash'] = script['hash']
        self.assertDictEqual(updated_elems[0]['authoring_user_input'], authoring_user_input)

        updated_elems[1]['authoring_user_input']['hash'] = script['hash']
        self.assertDictEqual(updated_elems[1]['authoring_user_input'], authoring_user_input)

        self.assertEqual(len(validation_items), 2)

        self.assertEqual(validation_items[0]['elem_id'], elem_id)
        self.assertEqual(validation_items[0]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[0]['number'], '1')
        self.assertEqual(len(validation_items[0]['changed_items']), 1)
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 1)

        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[0]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

        self.assertEqual(validation_items[1]['elem_id'], elem_id_2)
        self.assertEqual(validation_items[1]['step_type'], 'CUSTOM_SCRIPT')
        self.assertEqual(validation_items[1]['number'], '2')
        self.assertEqual(len(validation_items[1]['changed_items']), 1)
        self.assertEqual(len(validation_items[1]['changed_items'][0]['changed_fields']), 1)

        self.assertEqual(validation_items[1]['changed_items'][0]['item_type'], 'SCRIPT')
        self.assertEqual(validation_items[1]['changed_items'][0]['item_name'], script_1['script_path'])
        self.assertEqual(validation_items[1]['changed_items'][0]['change_type'], 'MODIFIED')

        self.assertEqual(validation_items[1]['changed_items'][0]['changed_fields'][0]['field_name'], 'hash')
        self.assertEqual(validation_items[1]['changed_items'][0]['changed_fields'][0]['previous_value'], script['hash'])
        self.assertEqual(validation_items[1]['changed_items'][0]['changed_fields'][0]['new_value'], script_1['hash'])

    def validate_procedure_version(self, procedure_id, version, validation_input=None, code_expected=200):
        url = '{0}/procedures/{1}/versions/{2}/validate'.format(shared_dict['host'], procedure_id, version)

        if validation_input:
            result = requests.post(url, json=validation_input,
                headers=shared_dict['headers'])
        else:
            result = requests.post(url,
                headers=shared_dict['headers'])

        return self.check_response(result, code_expected)      

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='./test-reports/'))
