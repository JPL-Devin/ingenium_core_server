import xmlrunner
import os
import sys
import unittest
import requests
import json
import random
import time
import string
from dateutil import parser
from datetime import datetime
import math
import dateutil.tz
from config import shared_dict, logger
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes

class VIStepsTest(CoreTestBase):
    def test_vi_step_refresh(self):
        self.check_vi_step(True)

    def test_vi_step_run(self):
        self.check_vi_step(False) 

    def test_missing_step_refresh(self):
        self.check_missing_step(True)      

    def test_missing_step_run(self):
        self.check_missing_step(False)    

    def test_missing_vi_step_refresh(self):
        self.check_missing_vi_step(True)      

    def test_missing_vi_step_run(self):
        self.check_missing_vi_step(False)    

    def check_vi_step(self, validate=True):
        execution_id, execution_url, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vi_name_1, vi_name_2, vi_id_1, vi_id_2, first_env_step_title, second_env_step_title = self.setup_elements()

        # should not be able to override VI step
        res_dict = self.override_step_status(execution_id, elem_id_1, {'override_justification': 'test override'}, 400)
        self.assertTrue(res_dict['details'][0].startswith('Cannot override status that is not PASS or FAIL'))  

        # should not be able to override step that has not been executed
        self.override_step_status(execution_id, elem_id_2, {'override_justification': 'test override'}, 400)
        self.assertTrue(res_dict['details'][0].startswith('Cannot override status that is not PASS or FAIL'))  

        # run env steps
        res_dict = self.run_step(execution_id, elem_id_2)
        res_dict = self.run_step(execution_id, elem_id_3)

        if validate:
            updated_elems = self.refresh_execution(execution_id)
            logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
            self.assertEqual(len(updated_elems), 1)

            vi_status_step = updated_elems[0]
            logger.debug('validate vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
            self.assertEqual(vi_status_step['executed'], True)               
        else:
            vi_status_step = self.run_step(execution_id, elem_id_4)         
            logger.debug('run vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')         
            self.assertEqual(vi_status_step['executed'], True)                  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)            

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=4))

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))
        self.assertEqual(len(vis), 2)

        pass_count = 0
        for vi in vis:
            if vi['vi_name'] == vi_name_1:
                self.assertDictEqual(vi, {'vi_name': vi_name_1, 'vi_id': vi_id_1, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_2:
                self.assertDictEqual(vi, {'vi_name': vi_name_2, 'vi_id': vi_id_2, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1

        self.assertEqual(pass_count, 2)


        ### add more VI and VIStatus steps
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=elem_id_4,
            level='SIBLING')

        elem_id_5 = res_dict['elem']['elem_id']

        vi_name_3 = 'third vi'
        vi_id_3 = 'vi_3'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name_3,                
                    'vi_id': vi_id_3,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 3',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }              
                    ]
                }         
            ]
        }
        # update
        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_5, user_input)

        # add another VI status step
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=elem_id_5,
            level='SIBLING')

        elem_id_6 = res_dict['elem']['elem_id']

        execution_user_input = {
            'vis': [
                {
                    'vi_name': vi_name_3,                
                    'vi_id': vi_id_3,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 3',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }               
                    ]
                }                   
            ],
            'steps': [
                {
                    'elem_id': elem_id_2,
                    'title': first_env_step_title,
                    'number': '2'
                }            
            ]
        }

        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6, execution_user_input)

        ### check vis status again
        # check the steps
        res_dict = self.get_execution_steps(execution_id)
        self.assertEqual(len(res_dict), 6)

        if validate:
            updated_elems = self.refresh_execution(execution_id)
            logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
            self.assertEqual(len(updated_elems), 2)

            vi_status_step = updated_elems[0]
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
            self.assertEqual(vi_status_step['executed'], True) 


            vi_status_step = updated_elems[1]
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')  
            self.assertEqual(vi_status_step['executed'], True)                

        else:
            vi_status_step = self.run_step(execution_id, elem_id_4)         
            logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
            self.assertEqual(vi_status_step['executed'], True) 

            vi_status_step = self.run_step(execution_id, elem_id_6)         
            logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL') 
            # VI status is a computed step. But executed flag should be true.
            self.assertEqual(vi_status_step['executed'], True)                   

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')   
        self.assertEqual(vi_status_step['executed'], True)      

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=4))

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))

        pass_count = 0
        for vi in vis:
            if vi['vi_name'] == vi_name_1:
                self.assertDictEqual(vi, {'vi_name': vi_name_1, 'vi_id': vi_id_1, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_2:
                self.assertDictEqual(vi, {'vi_name': vi_name_2, 'vi_id': vi_id_2, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_3:
                self.assertDictEqual(vi, {'vi_name': vi_name_3, 'vi_id': vi_id_3, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_6]})
                pass_count = pass_count + 1                

        self.assertEqual(pass_count, 3)

        ### override to PASS
        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4))        
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 1)
        self.assertEqual(execution_dict['num_steps_failed'], 3)
        self.assertEqual(execution_dict['num_steps_errored'], 0)  

        res_dict = self.override_step_status(execution_id, elem_id_2, {'override_justification': 'override to pass'})
        self.assertEqual(res_dict['execution']['meta_data']['status'], 'OVERRIDE_PASS')
        self.assertEqual(res_dict['execution']['meta_data']['override_justification'], 'override to pass')
        self.assertTrue(len(res_dict['execution']['meta_data']['overridden_by']) > 0)
        self.assertTrue(len(res_dict['execution']['meta_data']['time_overridden']) > 0)
        
        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4))        
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 2)
        self.assertEqual(execution_dict['num_steps_failed'], 2)
        self.assertEqual(execution_dict['num_steps_errored'], 0)       

        res_dict = self.discard_override_step_status(execution_id, elem_id_2)
        self.assertEqual(res_dict['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(res_dict['execution']['meta_data']['override_justification'], '')
        self.assertEqual(res_dict['execution']['meta_data']['overridden_by'], '')
        self.assertEqual(res_dict['execution']['meta_data']['time_overridden'], '')    

        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4))        
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 1)
        self.assertEqual(execution_dict['num_steps_failed'], 3)
        self.assertEqual(execution_dict['num_steps_errored'], 0)                

        # Fix the first env step
        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'GREATER_THAN',
                'verification_values': [20.0],
                'actual_value': 21.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 41.0
            }
        }        
        self.create_new_run(execution_id, elem_id_2)
        self.set_step_input(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_2, user_input)
        res_dict = self.run_step(execution_id, elem_id_2)

        if validate:
            updated_elems = self.refresh_execution(execution_id)
            logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
            self.assertEqual(len(updated_elems), 2)

            vi_status_step = updated_elems[0]
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
            self.assertEqual(vi_status_step['executed'], True) 


            vi_status_step = updated_elems[1]
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')  
            self.assertEqual(vi_status_step['executed'], True)                

        else:
            vi_status_step = self.run_step(execution_id, elem_id_4)         
            logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
            self.assertEqual(vi_status_step['executed'], True) 

            vi_status_step = self.run_step(execution_id, elem_id_6)         
            logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS') 
            # VI status is a computed step. But executed flag should be true.
            self.assertEqual(vi_status_step['executed'], True)                   

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(vi_status_step['executed'], True)  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')   
        self.assertEqual(vi_status_step['executed'], True)      

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))
        pass_count = 0
        for vi in vis:
            if vi['vi_name'] == vi_name_1:
                self.assertDictEqual(vi, {'vi_name': vi_name_1, 'vi_id': vi_id_1, 'status': 'PASS', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_2:
                self.assertDictEqual(vi, {'vi_name': vi_name_2, 'vi_id': vi_id_2, 'status': 'PASS', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_3:
                self.assertDictEqual(vi, {'vi_name': vi_name_3, 'vi_id': vi_id_3, 'status': 'PASS', 'vi_status_step_ids': [elem_id_6]})
                pass_count = pass_count + 1                

        self.assertEqual(pass_count, 3)        

        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4)) 
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 4)
        self.assertEqual(execution_dict['num_steps_failed'], 0)
        self.assertEqual(execution_dict['num_steps_errored'], 0)        

        ### Override
        res_dict = self.get_step(execution_url, StepTypes.WAIT, elem_id_2)
        self.assertEqual(res_dict['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(res_dict['execution']['meta_data']['override_justification'], '')
        self.assertEqual(res_dict['execution']['meta_data']['overridden_by'], '')
        self.assertEqual(res_dict['execution']['meta_data']['time_overridden'], '')        
        
        # should not be able to override vi status step
        res_dict = self.override_step_status(execution_id, elem_id_1, {'override_justification': 'test override'}, 400)
        self.assertTrue(res_dict['details'][0].startswith('Cannot override status that is not PASS or FAIL'))         

        # should not be able to discard override step that has not been overriden
        res_dict = self.discard_override_step_status(execution_id, elem_id_2, 400)
        self.assertTrue(res_dict['details'][0].startswith('Cannot discard override status that was not overriden'))  

        # override to fail
        res_dict = self.override_step_status(execution_id, elem_id_2, {'override_justification': 'override to fail'})
        self.assertEqual(res_dict['execution']['meta_data']['status'], 'OVERRIDE_FAIL')
        self.assertEqual(res_dict['execution']['meta_data']['override_justification'], 'override to fail')
        self.assertTrue(len(res_dict['execution']['meta_data']['overridden_by']) > 0)
        self.assertTrue(len(res_dict['execution']['meta_data']['time_overridden']) > 0)

        res_dict2 = self.update_override_step_status(execution_id, elem_id_2, {'override_justification': 'override to fail 2'})
        self.assertEqual(res_dict2['execution']['meta_data']['status'], 'OVERRIDE_FAIL')
        self.assertEqual(res_dict2['execution']['meta_data']['override_justification'], 'override to fail 2')
        self.assertEqual(res_dict2['execution']['meta_data']['overridden_by'], res_dict['execution']['meta_data']['overridden_by'])
        self.assertEqual(res_dict2['execution']['meta_data']['time_overridden'], res_dict['execution']['meta_data']['time_overridden'])

        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4))        
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 3)
        self.assertEqual(execution_dict['num_steps_failed'], 1)
        self.assertEqual(execution_dict['num_steps_errored'], 0)

        updated_elems = self.refresh_execution(execution_id)
        logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
        self.assertEqual(len(updated_elems), 2)

        vi_status_step = updated_elems[0]
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'OVERRIDE_FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True) 

        vi_status_step = updated_elems[1]
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'OVERRIDE_FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')  
        self.assertEqual(vi_status_step['executed'], True)      

        # discard override
        res_dict = self.discard_override_step_status(execution_id, elem_id_2)
        self.assertEqual(res_dict['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(res_dict['execution']['meta_data']['override_justification'], '')
        self.assertEqual(res_dict['execution']['meta_data']['overridden_by'], '')
        self.assertEqual(res_dict['execution']['meta_data']['time_overridden'], '')
    
        updated_elems = self.refresh_execution(execution_id)
        logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
        self.assertEqual(len(updated_elems), 2)

        vi_status_step = updated_elems[0]
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(vi_status_step['executed'], True) 

        vi_status_step = updated_elems[1]
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 1)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')  
        self.assertEqual(vi_status_step['executed'], True)   

        execution_dict = self.get_execution(execution_id)
        logger.debug('execution_dict: %s', json.dumps(execution_dict, indent=4))        
        self.assertEqual(execution_dict['num_steps_executed'], 4)       
        self.assertEqual(execution_dict['num_steps_passed'], 4)
        self.assertEqual(execution_dict['num_steps_failed'], 0)
        self.assertEqual(execution_dict['num_steps_errored'], 0)        

        ### add an element to change numbers
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id='-1',
            level='CHILD')        

        # close execution
        self.close_execution(execution_id)

        # check vi status steps
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '4')        
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')  

    def check_missing_step(self, validate = True):
        execution_id, execution_url, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vi_name_1, vi_name_2, vi_id_1, vi_id_2, first_env_step_title, second_env_step_title = self.setup_elements()

        # delete the first env step
        self.delete_element(execution_url, elem_id_2)

        # run env steps
        res_dict = self.run_step(execution_id, elem_id_3)        

        if validate:
            updated_elems = self.refresh_execution(execution_id)
            logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
            self.assertEqual(len(updated_elems), 1)

            vi_status_step = updated_elems[0]
            logger.debug('validate vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'NOT_FOUND')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
            self.assertEqual(vi_status_step['executed'], True)               
        else:
            vi_status_step = self.run_step(execution_id, elem_id_4)         
            logger.debug('run vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'NOT_FOUND')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')         
            self.assertEqual(vi_status_step['executed'], True)                  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'NOT_FOUND')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)            

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=3))

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))
        self.assertEqual(len(vis), 2)

        pass_count = 0
        for vi in vis:
            if vi['vi_name'] == vi_name_1:
                self.assertDictEqual(vi, {'vi_name': vi_name_1, 'vi_id': vi_id_1, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_2:
                self.assertDictEqual(vi, {'vi_name': vi_name_2, 'vi_id': vi_id_2, 'status': 'FAIL', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1

        self.assertEqual(pass_count, 2)        

    def check_missing_vi_step(self, validate = True):
        execution_id, execution_url, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vi_name_1, vi_name_2, vi_id_1, vi_id_2, first_env_step_title, second_env_step_title = self.setup_elements()

        # delete the vi step
        self.delete_element(execution_url, elem_id_1)

        # run env steps
        res_dict = self.run_step(execution_id, elem_id_2)
        res_dict = self.run_step(execution_id, elem_id_3)        

        if validate:
            updated_elems = self.refresh_execution(execution_id)
            logger.debug('updated_elems: %s', json.dumps(updated_elems, indent=4))
            self.assertEqual(len(updated_elems), 1)

            vi_status_step = updated_elems[0]
            logger.debug('validate vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
            self.assertEqual(vi_status_step['executed'], True)               
        else:
            vi_status_step = self.run_step(execution_id, elem_id_4)         
            logger.debug('run vi_status_step: %s', json.dumps(vi_status_step, indent=4))
            self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
            self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
            self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
            self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
            self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')         
            self.assertEqual(vi_status_step['executed'], True)                  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['vis']), 2)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'FAIL')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)            

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=3))

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))
        self.assertEqual(len(vis), 0)
            


    def test_vi_step_auto(self):
        random_name = random_string(8)
        description = 'My execution for test_vi_step ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        res_dict = self.create_execution(venue_id, description)

        execution_id = res_dict['execution_id']

        execution_url = shared_dict['host'] + '/executions/' + execution_id

        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=-1,
            level='CHILD')

        elem_id_1 = res_dict['elem']['elem_id']

        vi_name_1 = 'first vi'
        vi_name_2 = 'second vi'        
        vi_id_1 = 'vi_1'
        vi_id_2 = 'vi_2'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name_1,                
                    'vi_id': vi_id_1,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        },
                        {
                            'va_name': 'second va',
                            'va_id': 'va_2',
                            'va_poc': 'hongmank',
                            'vac_name': 'second vac',
                            'vac_id': 'vac_2'
                        }                    
                    ]
                },
                {
                    'vi_name': vi_name_2,                
                    'vi_id': vi_id_2,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 2',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }            
                    ]
                }            
            ]
        }
        
        # update
        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1, user_input)


        ### Add env step 
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_1,
            level='SIBLING')
        elem_id_2 = res_dict['elem']['elem_id']
        first_env_step_title = 'First env step'
        self.update_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_2, {'title': first_env_step_title})        

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 11.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 41.0
            }
        }        

        self.set_step_input(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_2, user_input)

        
        ### Add another env step 
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_2,
            level='SIBLING')

        elem_id_3 = res_dict['elem']['elem_id']
        second_env_step_title = 'Second env step'
        self.update_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_3, {'title': second_env_step_title})        

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 22.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 44.0
            }
        }        

        self.set_step_input(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_3, user_input)

        # add VI status step
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=elem_id_3,
            level='SIBLING')

        elem_id_4 = res_dict['elem']['elem_id']

        execution_user_input = {
            'vis': [
                {
                    'vi_name': 'first vi',                
                    'vi_id': 'vi_1',
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        },
                        {
                            'va_name': 'second va',
                            'va_id': 'va_2',
                            'va_poc': 'hongmank',
                            'vac_name': 'second vac',
                            'vac_id': 'vac_2'
                        }                    
                    ]
                },
                {
                    'vi_name': 'second vi',                
                    'vi_id': 'vi_2',
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 2',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }            
                    ]
                }                      
            ],
            'steps': [
                {
                    'elem_id': elem_id_2,
                    'title': first_env_step_title,
                    'number': '2'
                },
                {
                    'elem_id': elem_id_3,
                    'title': second_env_step_title,
                    'number': '3'
                }                
            ]
        }

        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4, execution_user_input)


        ### add more VI and VIStatus steps
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=elem_id_4,
            level='SIBLING')

        elem_id_5 = res_dict['elem']['elem_id']

        vi_name_3 = 'third vi'
        vi_id_3 = 'vi_3'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name_3,                
                    'vi_id': vi_id_3,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 3',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }              
                    ]
                }         
            ]
        }
        # update
        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_5, user_input)

        # add another VI status step
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=elem_id_5,
            level='SIBLING')

        elem_id_6 = res_dict['elem']['elem_id']

        execution_user_input = {
            'vis': [
                {
                    'vi_name': 'third vi',                
                    'vi_id': 'vi_3',
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 3',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }               
                    ]
                }                   
            ],
            'steps': [
                {
                    'elem_id': elem_id_2,
                    'title': first_env_step_title,
                    'number': '2'
                }            
            ]
        }

        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6, execution_user_input)

        ### Before running the env steps, run the first vi status step
        self.run_step_async(execution_id, elem_id_4, 202)     
        
        time.sleep(1)
        
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'NONE')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'NONE')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)       

        # Run the first env step  
        env_step = self.run_step_async(execution_id, elem_id_2, 202)
        time.sleep(1)

        ### Run the first vi status step again
        self.run_step_async(execution_id, elem_id_4, 202)  
        
        time.sleep(1)
        
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'NONE')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'FAIL')
        self.assertEqual(vi_status_step['executed'], True)    

        # Run the second env step  
        env_step = self.run_step_async(execution_id, elem_id_3, 202)
        time.sleep(1)

        ### Run the first vi status step again
        self.run_step_async(execution_id, elem_id_4, 202)
        
        time.sleep(1)      
        
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(vi_status_step['executed'], True)                  

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=4))  

        self.assertEqual(len(elements[0]['run_records']), 0)
        self.assertEqual(len(elements[1]['run_records']), 0)
        self.assertEqual(len(elements[2]['run_records']), 0)
        self.assertEqual(len(elements[3]['run_records']), 0)
        self.assertEqual(len(elements[4]['run_records']), 0)
        self.assertEqual(len(elements[5]['run_records']), 0)

        ##### AUTOMATIC execution
        execution_info = {
            'mode': 'AUTO', 
            'pause_conditions': {
                'on_manual_input': False
            }
        }
        self.update_execution(execution_id, execution_info, code_expected=200)

        # Note that elem_id_1 is the VI step, which is not executable.
        # elem_id_2 is the first executable step and it has been executed. A new run will be created automatically
        self.run_step_async(execution_id, elem_id_1, 202)

        time.sleep(3)

        elements = self.get_elements(execution_url)
        logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements[0]['run_records']), 0)
        self.assertEqual(len(elements[1]['run_records']), 1)
        self.assertEqual(len(elements[2]['run_records']), 1)
        self.assertEqual(len(elements[3]['run_records']), 0)
        self.assertEqual(len(elements[4]['run_records']), 0)
        self.assertEqual(len(elements[5]['run_records']), 0)        

        env_step = self.get_step(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_2)
        logger.debug('env_step: %s', json.dumps(env_step, indent=4))
        self.assertEqual(env_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(env_step['executed'], True) 

        env_step = self.get_step(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_3)
        logger.debug('env_step: %s', json.dumps(env_step, indent=4))
        self.assertEqual(env_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(env_step['executed'], True)           

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')        
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')
        self.assertEqual(vi_status_step['executed'], True)  

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')   
        self.assertEqual(vi_status_step['executed'], True)      

        # check vis
        vis = self.getVIs(execution_id)
        logger.debug('vis: %s', json.dumps(vis, indent=4))

        pass_count = 0
        for vi in vis:
            if vi['vi_name'] == vi_name_1:
                self.assertDictEqual(vi, {'vi_name': vi_name_1, 'vi_id': vi_id_1, 'status': 'PASS', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_2:
                self.assertDictEqual(vi, {'vi_name': vi_name_2, 'vi_id': vi_id_2, 'status': 'PASS', 'vi_status_step_ids': [elem_id_4]})
                pass_count = pass_count + 1
            if vi['vi_name'] == vi_name_3:
                self.assertDictEqual(vi, {'vi_name': vi_name_3, 'vi_id': vi_id_3, 'status': 'PASS', 'vi_status_step_ids': [elem_id_6]})
                pass_count = pass_count + 1                

        self.assertEqual(pass_count, 3)

        ### add an element to change numbers
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id='-1',
            level='CHILD')        

        # close execution
        self.close_execution(execution_id)

        # check vi status steps
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 2)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][1]['number'], '4')        
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')

        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_6)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['execution']['results']['steps']), 1)
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['status'], 'PASS')
        self.assertEqual(vi_status_step['execution']['results']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['execution']['meta_data']['status'], 'PASS')   

        

        logger.debug('The end')  

    def setup_procedure_elements(self):
        procedure_title = 'My procedure'
        procedure_description = 'My procedure description'
        institutional_id = 'ins_1'
        institutional_release_id = 'rel_1'

        procedure = self.create_procedure(procedure_title, procedure_description,
            institutional_id)

        procedure_id = procedure['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # 
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=-1,
            level='CHILD')

        elem_id_1 = res_dict['elem']['elem_id']

        vi_name_1 = 'first vi'
        vi_name_2 = 'second vi'        
        vi_id_1 = 'vi_1'
        vi_id_2 = 'vi_2'  
        vis = [
            {
                'vi_name': vi_name_1,
                'vi_id': vi_id_1,
                'vi_owner': 'hongmank',
                'vi_type': 'REQUIREMENT',
                'vi_text': 'some requirement 1',
                'vi_additional_procs': '',
                'vas': []
            },
            {
                'vi_name': vi_name_2,
                'vi_id': vi_id_2,
                'vi_owner': 'hongmank',
                'vi_type': 'REQUIREMENT',
                'vi_text': 'some requirement 2',
                'vi_additional_procs': '',
                'vas': []
            }
        ]

        user_input = {
            'vis': vis
        }

        # update
        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM, elem_id_1, user_input)

        # check the steps
        res_dict = self.get_steps(procedure_url, StepTypes.VERIFICATION_ITEM)
        self.assertEqual(len(res_dict), 1)

        ### Add env step 
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_1,
            level='SIBLING')
        elem_id_2 = res_dict['elem']['elem_id']
        first_env_step_title = 'First env step'
        self.update_step(procedure_url, StepTypes.VERIFICATION_ITEM, elem_id_2, {'title': first_env_step_title})           

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            }
        }        

        self.set_step_input(procedure_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_2, user_input)
        
        ### Add another env step 
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_2,
            level='SIBLING')

        elem_id_3 = res_dict['elem']['elem_id']
        second_env_step_title = 'Second env step'
        self.update_step(procedure_url, StepTypes.VERIFICATION_ITEM, elem_id_3, {'title': second_env_step_title})                

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            }
        }        

        self.set_step_input(procedure_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_3, user_input)

        # add VI status step
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=elem_id_3,
            level='SIBLING')

        elem_id_4 = res_dict['elem']['elem_id']

        procedure_user_input = {
            'vis': vis,
            'steps': [
                {
                    'elem_id': elem_id_2,
                    'title': first_env_step_title,
                    'number': '2'
                },
                {
                    'elem_id': elem_id_3,
                    'title': second_env_step_title,
                    'number': '3'
                }                
            ]
        }

        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4, procedure_user_input)
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': True
        }
        res = self.validate_procedure_element(procedure_id, elem_id_4, validation_input)
        self.assertEqual(len(res['elements']), 0)
        self.assertEqual(len(res['validation_items']), 0)    

        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 2)
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][0]['number'], '2')
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][1]['number'], '3')

        return (procedure_id, procedure_url, procedure_title, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vis, first_env_step_title, second_env_step_title)

    def test_vi_step_procedure(self):

        procedure_id, procedure_url, procedure_title, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vis, first_env_step_title, second_env_step_title = self.setup_procedure_elements()

        ### add an element to change numbers
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id='-1',
            level='CHILD')        

        # dry run
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': False
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 0)
        self.assertEqual(len(validation_items), 1)

        self.assertEqual(res_dict['validation_items'][0]['elem_id'], elem_id_4)
        self.assertEqual(res_dict['validation_items'][0]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(res_dict['validation_items'][0]['number'], '5')
        self.assertEqual(res_dict['validation_items'][0]['title'], '')
        self.assertEqual(res_dict['validation_items'][0]['user_action_msg'], '')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items']), 2)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['item_type'], 'STEP')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['item_name'], '2: First env step')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['change_type'], 'MODIFIED')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items'][0]['changed_fields']), 1)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['field_name'], 'number')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['previous_value'], '2')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['new_value'], '3')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['item_type'], 'STEP')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['item_name'], '3: Second env step')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['change_type'], 'MODIFIED')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items'][1]['changed_fields']), 1)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['field_name'], 'number')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['previous_value'], '3')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['new_value'], '4')

        #        
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']
        self.assertEqual(len(updated_elems), 1)
        self.assertEqual(len(validation_items), 1)

        self.assertEqual(res_dict['validation_items'][0]['elem_id'], elem_id_4)
        self.assertEqual(res_dict['validation_items'][0]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(res_dict['validation_items'][0]['number'], '5')
        self.assertEqual(res_dict['validation_items'][0]['title'], '')
        self.assertEqual(res_dict['validation_items'][0]['user_action_msg'], '')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items']), 2)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['item_type'], 'STEP')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['item_name'], '2: First env step')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['change_type'], 'MODIFIED')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items'][0]['changed_fields']), 1)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['field_name'], 'number')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['previous_value'], '2')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][0]['changed_fields'][0]['new_value'], '3')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['item_type'], 'STEP')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['item_name'], '3: Second env step')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['change_type'], 'MODIFIED')
        self.assertEqual(len(res_dict['validation_items'][0]['changed_items'][1]['changed_fields']), 1)
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['field_name'], 'number')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['previous_value'], '3')
        self.assertEqual(res_dict['validation_items'][0]['changed_items'][1]['changed_fields'][0]['new_value'], '4')


        # check vi status steps
        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 2)
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][1]['number'], '4')    

        ### add another element to change numbers
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id='-1',
            level='CHILD') 

        # check vi status steps
        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 2)
        # numbers should not change
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][0]['number'], '3')
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][1]['number'], '4')             
        
        rand_1 = random_string()
        description_1 = 'description_' + rand_1
        institutional_release_id_1 = 'institutional_release_id_1_' + rand_1
        self.create_procedure_version(procedure_id, description_1, institutional_release_id_1)    

        # check vi status steps
        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 2)
        # numbers should have been updated when a version was created
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][0]['number'], '4')
        self.assertEqual(vi_status_step['authoring_user_input']['steps'][1]['number'], '5')      

        elems = self.get_version_elements(procedure_id=procedure_id, version=1)
        count = 0
        for elem in elems:
            if elem.get('step_type') == 'VERIFICATION_ITEM_STATUS':
                self.assertEqual(len(elem['authoring_user_input']['steps']), 2)
                # numbers should have been updated when a version was created
                self.assertEqual(elem['authoring_user_input']['steps'][0]['number'], '4')
                self.assertEqual(elem['authoring_user_input']['steps'][1]['number'], '5')      
                count = count  + 1
        self.assertEqual(1, count)    

        ### import a procedure version to an execution
        random_name = random_string(8)
        description = 'My execution for test_vi_step ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        res_dict = self.create_execution(venue_id, description)

        execution_id = res_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        procedure_section_data = {'title': 'Procedure Section 1'}
        res = self.add_procedure_section(base_url=execution_url,
            insert_after_id="-1",
            level='CHILD',
            procedure_section=procedure_section_data)

        procedure_section_id = res['elem']['elem_id']
        procedure_section = self.get_procedure_section(execution_url, procedure_section_id)

        version = 1
        outline_elems = self.get_outline(procedure_url, version)

        procedure_section_input = {
            'callable': False,
            'reference_procedure_id': procedure_id,
            'reference_procedure_version': version,
            'elements': outline_elems,
            'reference_procedure_version_description': description_1,
            'reference_procedure_institutional_id': '',
            'reference_procedure_institutional_release_id': '',            
            'reference_procedure_title': procedure_title,
            'run_for_score': True,
            'tag_selections': []
        }

        self.update_procedure_section_input(execution_url, procedure_section_id, procedure_section_input)
        user_input = self.get_procedure_section_input(execution_url, procedure_section_id)
        self.assertDictEqual(procedure_section_input, user_input)

        proc_section_elems = self.import_procedure_section(execution_id, procedure_section_id)
        logger.debug('proc_section_elems= %s', json.dumps(proc_section_elems, indent=4))    
        vi_status_step = None
        imported_elem_map = {}
        for elem in proc_section_elems:
            imported_elem_map[elem['elem_id']] = elem
            if elem.get('step_type') == 'VERIFICATION_ITEM_STATUS':
                self.assertTrue(vi_status_step is None)
                vi_status_step = elem
        
        self.assertTrue(vi_status_step is not None)

        logger.debug('vi_status_step= %s', json.dumps(vi_status_step, indent=4))  

        self.assertEqual(len(vi_status_step['execution_user_input']['steps']), 2)
        # elem_id's should be pointing to imported execution elements

        ref_elem_id_1 = vi_status_step['execution_user_input']['steps'][0]['elem_id']
        logger.debug('ref_elem_id_1= %s', ref_elem_id_1)  
        self.assertTrue(imported_elem_map.get(ref_elem_id_1) is not None)
        self.assertEqual(vi_status_step['execution_user_input']['steps'][0]['number'], '4')
        self.assertEqual(vi_status_step['execution_user_input']['steps'][0]['number'], imported_elem_map[ref_elem_id_1]['number'])
        self.assertEqual(imported_elem_map[ref_elem_id_1]['step_type'], 'ENVIRONMENT_MANUAL')

        ref_elem_id_2 = vi_status_step['execution_user_input']['steps'][1]['elem_id']
        logger.debug('ref_elem_id_2= %s', ref_elem_id_2)  
        self.assertTrue(imported_elem_map.get(ref_elem_id_2) is not None)
        self.assertEqual(vi_status_step['execution_user_input']['steps'][1]['number'], '5')
        self.assertEqual(vi_status_step['execution_user_input']['steps'][1]['number'], imported_elem_map[ref_elem_id_2]['number'])        
        self.assertEqual(imported_elem_map[ref_elem_id_2]['step_type'], 'ENVIRONMENT_MANUAL')

        self.assertNotEqual(ref_elem_id_1, ref_elem_id_2)
        
    def test_missing_procedure_step(self):
        procedure_id, procedure_url, procedure_title, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vis, first_env_step_title, second_env_step_title = self.setup_procedure_elements()

        # delete the first env step
        self.delete_element(procedure_url, elem_id_2)

        ### validate working version 
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': True
        }
        res_dict = self.validate_procedure_version(procedure_id, 0, validation_input)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']

        self.assertEqual(len(updated_elems), 1)
        self.assertEqual(len(validation_items), 1)
        self.assertEqual(validation_items[0]['elem_id'], elem_id_4)
        self.assertEqual(validation_items[0]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(validation_items[0]['number'], '3')
        self.assertEqual(len(validation_items[0]['changed_items']), 2)
        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'STEP')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], '%s: %s' % ('2', first_env_step_title))
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'DELETED')
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 0)
        self.assertEqual(validation_items[0]['changed_items'][1]['item_type'], 'STEP')
        self.assertEqual(validation_items[0]['changed_items'][1]['item_name'], '%s: %s' % ('3', second_env_step_title))
        self.assertEqual(validation_items[0]['changed_items'][1]['change_type'], 'MODIFIED')
        self.assertEqual(validation_items[0]['changed_items'][1]['changed_fields'][0]['field_name'], 'number')
        self.assertEqual(validation_items[0]['changed_items'][1]['changed_fields'][0]['previous_value'], '3')
        self.assertEqual(validation_items[0]['changed_items'][1]['changed_fields'][0]['new_value'], '2')

        vi_status_step = updated_elems[0]
        logger.debug('validate vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['vis']), 2)
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 1)
           
        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['vis']), 2)
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 1)

        elements = self.get_elements(procedure_url)
        logger.debug('elements: %s', json.dumps(elements, indent=3))

        # delete the second env step
        self.delete_element(procedure_url, elem_id_3)

        # run env steps
        vi_2_id = vis[1]['vi_id']
        vi_2_name = vis[1]['vi_name']
        vis.pop(1)

        # dry run
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': False
        }
        res_dict = self.validate_procedure_element(procedure_id, elem_id_4, validation_input)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']

        self.assertEqual(len(updated_elems), 0)
        self.assertEqual(len(validation_items), 1)
        self.assertEqual(validation_items[0]['elem_id'], elem_id_4)
        self.assertEqual(validation_items[0]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(validation_items[0]['number'], '2')

        self.assertEqual(len(validation_items[0]['changed_items']), 2)
        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'VI')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], '%s: %s' % (vi_2_id, vi_2_name))
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'DELETED')
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 0)
        self.assertEqual(validation_items[0]['changed_items'][1]['item_type'], 'STEP')
        self.assertEqual(validation_items[0]['changed_items'][1]['item_name'], '%s: %s' % ('2', second_env_step_title))
        self.assertEqual(validation_items[0]['changed_items'][1]['change_type'], 'DELETED')
        self.assertEqual(len(validation_items[0]['changed_items'][1]['changed_fields']), 0)

        #
        validation_input = {
            'vis': vis,
            'scripts': [],
            'update': True
        }
        res_dict = self.validate_procedure_element(procedure_id, elem_id_4, validation_input)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        updated_elems = res_dict['elements']
        validation_items = res_dict['validation_items']

        self.assertEqual(len(updated_elems), 1)
        self.assertEqual(len(validation_items), 1)
        self.assertEqual(validation_items[0]['elem_id'], elem_id_4)
        self.assertEqual(validation_items[0]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(validation_items[0]['number'], '2')

        self.assertEqual(len(validation_items[0]['changed_items']), 2)
        self.assertEqual(validation_items[0]['changed_items'][0]['item_type'], 'VI')
        self.assertEqual(validation_items[0]['changed_items'][0]['item_name'], '%s: %s' % (vi_2_id, vi_2_name))
        self.assertEqual(validation_items[0]['changed_items'][0]['change_type'], 'DELETED')
        self.assertEqual(len(validation_items[0]['changed_items'][0]['changed_fields']), 0)
        self.assertEqual(validation_items[0]['changed_items'][1]['item_type'], 'STEP')
        self.assertEqual(validation_items[0]['changed_items'][1]['item_name'], '%s: %s' % ('2', second_env_step_title))
        self.assertEqual(validation_items[0]['changed_items'][1]['change_type'], 'DELETED')
        self.assertEqual(len(validation_items[0]['changed_items'][1]['changed_fields']), 0)

        vi_status_step = updated_elems[0]

        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))

        logger.debug('validate vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['vis']), 1)
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 0)     

        vi_status_step = self.get_step(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        logger.debug('vi_status_step: %s', json.dumps(vi_status_step, indent=4))
        self.assertEqual(len(vi_status_step['authoring_user_input']['vis']), 1)
        self.assertEqual(len(vi_status_step['authoring_user_input']['steps']), 0)      
         
        elements = self.get_elements(procedure_url)
        logger.debug('elements: %s', json.dumps(elements, indent=3))        

    def getVIs(self, execution_id):
        url = '{0}/executions/{1}/vis'.format(shared_dict['host'], execution_id)

        result = requests.get(url,
            headers=shared_dict['headers'])

        self.assertEqual(result.status_code, 200)

        return json.loads(result.text)

    def refresh_execution(self, execution_id):
        url = '{0}/executions/{1}/refresh'.format(shared_dict['host'], execution_id)

        result = requests.post(url,
            headers=shared_dict['headers'])

        self.assertEqual(result.status_code, 200)

        return json.loads(result.text)      

    def validate_procedure_version(self, procedure_id, version, validation_input=None, code_expected=200):
        url = '{0}/procedures/{1}/versions/{2}/validate'.format(shared_dict['host'], procedure_id, version)

        if validation_input:
            result = requests.post(url, json=validation_input,
                headers=shared_dict['headers'])
        else:
            result = requests.post(url,
                headers=shared_dict['headers'])


        return self.check_response(result, code_expected) 

    def validate_procedure_element(self, procedure_id, elem_id, validation_input=None):
        url = '{0}/procedures/{1}/elements/{2}/validate'.format(shared_dict['host'], procedure_id, elem_id)

        if validation_input:
            result = requests.post(url, json=validation_input,
                headers=shared_dict['headers'])
        else:
            result = requests.post(url,
                headers=shared_dict['headers'])

        self.assertEqual(result.status_code, 200)

        return json.loads(result.text)         

    def run_step_async(self, execution_id, current_step_id, code_expected=200):

        url = '{0}/executions/{1}/run'.format(shared_dict['host'],
                                              execution_id)

        if current_step_id:
            params = {'current_step_id': current_step_id, 'run_mode': 'ASYNC'}
        else:
            params = {'run_mode': 'ASYNC'}  
        result = requests.post(url,
                               headers=shared_dict['headers'],
                               params=params)
        logger.debug(result.status_code)
        logger.debug(result.text)
            
        return self.check_response(result, code_expected) 

    def override_step_status(self, execution_id, elem_id, override_input, code_expected=200):
        url = '{0}/executions/{1}/steps/{2}/override'.format(shared_dict['host'],
                                              execution_id, elem_id)
        result = requests.post(url,
                                json=override_input,
                                headers=shared_dict['headers'])
        logger.debug(result.status_code)
        logger.debug(result.text)
            
        return self.check_response(result, code_expected)   

    def update_override_step_status(self, execution_id, elem_id, override_input, code_expected=200):
        url = '{0}/executions/{1}/steps/{2}/override'.format(shared_dict['host'],
                                              execution_id, elem_id)
        result = requests.patch(url,
                                json=override_input,
                                headers=shared_dict['headers'])
        logger.debug(result.status_code)
        logger.debug(result.text)
            
        return self.check_response(result, code_expected)           

    def discard_override_step_status(self, execution_id, elem_id, code_expected=200):
        url = '{0}/executions/{1}/steps/{2}/discard_override'.format(shared_dict['host'],
                                              execution_id, elem_id)
        result = requests.post(url, headers=shared_dict['headers'])
        logger.debug(result.status_code)
        logger.debug(result.text)
            
        return self.check_response(result, code_expected)             

    def setup_elements(self):        
        random_name = random_string(8)
        description = 'My execution for test_vi_step ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        res_dict = self.create_execution(venue_id, description)

        execution_id = res_dict['execution_id']

        execution_url = shared_dict['host'] + '/executions/' + execution_id


        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=-1,
            level='CHILD')

        elem_id_1 = res_dict['elem']['elem_id']

        # update
        self.update_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1, {'description': 'Test step'})

        # check the step
        res_dict = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1)

        self.assertEqual(res_dict['elem_id'], elem_id_1)
        self.assertEqual(res_dict['step_type'], 'VERIFICATION_ITEM')
        self.assertEqual(res_dict['description'], 'Test step')

        vi_name_1 = 'first vi'
        vi_name_2 = 'second vi'        
        vi_id_1 = 'vi_1'
        vi_id_2 = 'vi_2'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name_1,                
                    'vi_id': vi_id_1,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        },
                        {
                            'va_name': 'second va',
                            'va_id': 'va_2',
                            'va_poc': 'hongmank',
                            'vac_name': 'second vac',
                            'vac_id': 'vac_2'
                        }                    
                    ]
                },
                {
                    'vi_name': vi_name_2,                
                    'vi_id': vi_id_2,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 2',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }            
                    ]
                }            
            ]
        }
        
        # update
        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1, user_input)

        # check the step
        vi_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1)

        # check the step input
        step_input = self.get_step_input(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_1)

        self.assertSequenceEqual(step_input, user_input)

        # check the steps
        res_dict = self.get_steps(execution_url, StepTypes.VERIFICATION_ITEM)
        self.assertEqual(len(res_dict), 1)

        ### Add env step 
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_1,
            level='SIBLING')
        elem_id_2 = res_dict['elem']['elem_id']
        first_env_step_title = 'First env step'
        self.update_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_2, {'title': first_env_step_title})

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'GREATER_THAN',
                'verification_values': [20.0],
                'actual_value': 11.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 41.0
            }
        }        

        self.set_step_input(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_2, user_input)
        
        ### Add another env step 
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=elem_id_2,
            level='SIBLING')

        elem_id_3 = res_dict['elem']['elem_id']
        second_env_step_title = 'Second env step'
        self.update_step(execution_url, StepTypes.VERIFICATION_ITEM, elem_id_3, {'title': second_env_step_title})        

        user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 22.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 44.0
            }
        }        

        self.set_step_input(execution_url, StepTypes.ENVIRONMENT_MANUAL, elem_id_3, user_input)

        # add VI status step
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=elem_id_3,
            level='SIBLING')

        elem_id_4 = res_dict['elem']['elem_id']

        execution_user_input = {
            'vis': [
                {
                    'vi_name': 'first vi',                
                    'vi_id': 'vi_1',
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        },
                        {
                            'va_name': 'second va',
                            'va_id': 'va_2',
                            'va_poc': 'hongmank',
                            'vac_name': 'second vac',
                            'vac_id': 'vac_2'
                        }                    
                    ]
                },
                {
                    'vi_name': 'second vi',                
                    'vi_id': 'vi_2',
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 2',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'third va',
                            'va_id': 'va_3',
                            'va_poc': 'hongmank',
                            'vac_name': 'third vac',
                            'vac_id': 'vac_3'
                        }            
                    ]
                }                      
            ],
            'steps': [
                {
                    'elem_id': elem_id_2,
                    'title': first_env_step_title,
                    'number': '2'
                },
                {
                    'elem_id': elem_id_3,
                    'title': second_env_step_title,
                    'number': '3'
                }                
            ]
        }

        self.set_step_input(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4, execution_user_input)

        # check the step
        vi_status_step = self.get_step(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)

        # check the step input
        step_input = self.get_step_input(execution_url, StepTypes.VERIFICATION_ITEM_STATUS, elem_id_4)
        self.assertDictEqual(step_input, execution_user_input)

        # check the steps
        res_dict = self.get_execution_steps(execution_id)
        self.assertEqual(len(res_dict), 4)        

        return (execution_id, execution_url, elem_id_1, elem_id_2, elem_id_3, elem_id_4, vi_name_1, vi_name_2, vi_id_1, vi_id_2, first_env_step_title, second_env_step_title)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
