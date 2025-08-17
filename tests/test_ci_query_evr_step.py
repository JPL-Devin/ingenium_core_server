import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
import requests
from ingenium_client import CoreTestBase, StepTypes
from utils import random_string


class QueryEVRStepTest(CoreTestBase):
    def test_query_evr_step_dummy(self):


        user_input = {
            "evr_name": "EVR_PROCESS_CMD",
            "evr_id": "1879113732",
            "evr_type": "SSE",
            "evr_level": "ACTIVITY_LO",
            "start_time": "0555401349",
            "end_time": "0555401369",
            "duration": "20",
            "time_type": "SCLK",
            "message_filter": "",
            "timeout": 240,
            "verification_condition": "RECORD",
            "verification_value": -1,
            "data_path": "SIDE B"
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.QUERY_EVR, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.QUERY_EVR, user_input, False, False, procedure=True)

    def test_run_error(self):
        random_name = random_string(8)
        description = 'My execution for test_run_error ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']         
        res_dict = self.create_execution(venue_id, description)

        execution_id = res_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.QUERY_EVR,
            insert_after_id=-1,
            level='CHILD')

        step_id = res_dict['elem']['elem_id']

        ### input with no data_path
        user_input = {
            "evr_name": "EVR_PROCESS_CMD",
            "evr_id": "1879113732",
            "evr_type": "SSE",
            "evr_level": "ACTIVITY_LO",
            "start_time": "0555401349",
            "end_time": "0555401369",
            "duration": "",
            "time_type": "SCLK",
            "message_filter": "",
            "timeout": 240,
            "verification_condition": "RECORD",
            "verification_value": -1,
            "data_path": ""
        }

        self.set_step_input(execution_url, StepTypes.QUERY_EVR, step_id, user_input)

        # run the step
        res_dict = self.run_step(execution_id, step_id)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertTrue(len(res_dict['execution']['meta_data']['error']['message']) > 0)
        self.assertTrue(len(res_dict['execution']['meta_data']['error']['details']) == 0)
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_type'], 'USER_INPUT_ERROR')
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_source'], 'EMBEDDED_CODE')
        self.assertEqual(res_dict['execution']['meta_data']['error']['http_code_at_source'], 0)

        ### input with invalid time type
        user_input = {
            "evr_name": "EVR_PROCESS_CMD",
            "evr_id": "1879113732",
            "evr_type": "SSE",
            "evr_level": "ACTIVITY_LO",
            "start_time": "0555401349",
            "end_time": "0555401369",
            "duration": "",
            "time_type": "ERT",
            "message_filter": "",
            "timeout": 240,
            "verification_condition": "RECORD",
            "verification_value": -1,
            "data_path": "side a"
        }

        # to run it again
        res_dict = self.create_new_run(execution_id, step_id)
        self.assertEqual(res_dict['elem_id'], step_id)
        self.assertEqual(len(res_dict['run_records']), 1)
        self.assertNotEqual(res_dict['run_records'][0]['elem_id'], step_id)

        self.set_step_input(execution_url, StepTypes.QUERY_EVR, step_id, user_input)

        # run the step
        res_dict = self.run_step(execution_id, step_id)

        self.assertTrue(len(res_dict['execution']['meta_data']['error']['message']) > 0)
        # self.assertTrue(len(res_dict['details']) > 0)
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_type'], 'USER_INPUT_ERROR')
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_source'], 'EMBEDDED_CODE')
        self.assertEqual(res_dict['execution']['meta_data']['error']['http_code_at_source'], 0)

        ### Valid input and the step execution will fail since session_id was not set
        user_input = {
            "evr_name": "EVR_PROCESS_CMD",
            "evr_id": "1879113732",
            "evr_type": "SSE",
            "evr_level": "ACTIVITY_LO",
            "start_time": "0555401349",
            "end_time": "0555401369",
            "duration": "",
            "time_type": "SCLK",
            "message_filter": "",
            "timeout": 240,
            "verification_condition": "RECORD",
            "verification_value": -1,
            "data_path": "side a"
        }

        # to run it again
        res_dict = self.create_new_run(execution_id, step_id)
        self.assertEqual(res_dict['elem_id'], step_id)
        self.assertEqual(len(res_dict['run_records']), 2)
        self.assertNotEqual(res_dict['run_records'][0]['elem_id'], step_id)
        self.assertNotEqual(res_dict['run_records'][1]['elem_id'], step_id)

        self.set_step_input(execution_url, StepTypes.QUERY_EVR, step_id, user_input)


        # run the step
        res_dict = self.run_step(execution_id, step_id)  

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertTrue(len(res_dict['execution']['meta_data']['error']['message']) > 0)
        self.assertTrue(len(res_dict['execution']['meta_data']['error']['details']) > 0)
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_type'], 'USER_INPUT_ERROR')
        self.assertEqual(res_dict['execution']['meta_data']['error']['error_source'], 'EMBEDDED_CODE')
        self.assertEqual(res_dict['execution']['meta_data']['error']['http_code_at_source'], 0)

        url = shared_dict['host'] + '/executions/' + execution_id + '/as_run'
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        as_run_dict = json.loads(result.text)    
        
        logger.debug('as_run_dict: %s', json.dumps(as_run_dict, indent=4))  
        
        self.assertEqual(len(as_run_dict['children'][0]['run_records']), 2)
        
                

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
