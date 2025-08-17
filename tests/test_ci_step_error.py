import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes
from utils import random_string


class StepErrorTest(CoreTestBase):

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
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=-1,
            level='CHILD')

        step_id = res_dict['elem']['elem_id']
        user_input = {
            'entries': [
                {
                    'name': '_TEST_MODE_',
                    'type': 'STRING',
                    'verify_on': 'VALUE',
                    'verification_condition': 'RECORD',
                    'verification_values': [],
                    'actual_value': 'RUN_ERROR'
                }
            ]
        }

        res_dict = self.set_step_input(execution_url, StepTypes.MANUAL_INPUT, step_id, user_input)

        # run the step
        res_dict = self.run_step(execution_id, step_id, 200)

        error_dict = res_dict['execution']['meta_data']['error']
        self.assertTrue(len(error_dict['message']) > 0)
        self.assertTrue(len(error_dict['details']) > 0)
        self.assertEqual(error_dict['error_type'], 'INGENIUM_SERVICE_ERROR')
        self.assertEqual(error_dict['error_source'], 'EXECUTION_SERVICE')
        self.assertEqual(error_dict['http_code_at_source'], 0)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
