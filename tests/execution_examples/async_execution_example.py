"""
Usage:
 - Run all tests
   $ python executions_test.py

 - Run a class
   $ python executions_test.py ExecutionsTest

 - Run a method
   $ python executions_test.py ExecutionDeleteTest.test_delete_executions

"""

import os
import sys
import unittest
import requests
import json

import random
import time

import string

sys.path.append('..')

from config import shared_dict, logger
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes



class AsyncExecutionExample(CoreTestBase):

    def run_step_async(self, execution_id, current_step_id, code_expected=200):

        url = '{0}/executions/{1}/run'.format(shared_dict['host'],
                                              execution_id)

        params = {'current_step_id': current_step_id, 'run_mode': 'ASYNC'}
        result = requests.post(url,
                               headers=shared_dict['headers'],
                               params=params)
            
        return self.check_response(result, code_expected)  

    def run_example(self):
        ## Add a venue
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']

        ## Add an execution
        description = 'My new execution'
        execution_dict = self.create_execution(venue_id, description)

        execution_id = execution_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id        

        ## Add step 1

        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.WAIT,
            insert_after_id='-1',
            level='CHILD')
        step_id_1 = res_dict['elem']['elem_id']

        logger.debug('step_1_id: %s', step_id_1)

        user_input_1 = {
            'wait_type': 'DURATION',
            'time_value': '22'
        }

        self.set_step_input(execution_url, StepTypes.WAIT, step_id_1, user_input_1)

        #res_dict = self.run_step(execution_id, step_id_1)
        #logger.debug('run_step res_dict: %s', json.dumps(res_dict, indent=4))

        res_dict = self.run_step_async(execution_id, step_id_1, 202)
        logger.debug('run_step res_dict: %s', json.dumps(res_dict, indent=4))

if __name__ == "__main__":

    aee = AsyncExecutionExample()
    aee.run_example()