
import json

import os

import sys
import time
# Add the parent folder path to the sys.path list so that we can load library

sys.path.append('..')

from config import shared_dict, logger

from test_ci_executions import ExecutionsTest
from utils import random_string
from ingenium_client import StepTypes

meta_data_template = {
    "test_conductor": "",    
    "time_started": "",
    "time_completed": "",    
    "status": "NONE",    
    "error": {}
}

class CreateExecution(ExecutionsTest):
    def run_steps(self):        
        ### Create an execution
        
        random_name = random_string(8)
        description = 'My execution ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        execution_dict = self.create_execution(venue_id, description)            
    
        execution_id = execution_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        num_steps = 100
        step_ids = []

        t0 = time.time()
        for i in range(num_steps):
            res = self.add_step(execution_url, StepTypes.MANUAL_INPUT, '-1', 'CHILD')
            step_ids.append(res['elem']['elem_id'])
        t1 = time.time()
        user_input = {
            'entries': [
                {
                    'name': 'param1',
                    'type': 'STRING',
                    'verify_on': 'VALUE',
                    'verification_condition': 'RECORD',
                    'verification_values': [],
                    'actual_value': 'abc'
                },
                {
                    'name': 'param2',
                    'type': 'FLOAT',
                    'verify_on': 'VALUE',
                    'verification_condition': 'RECORD',
                    'verification_values': [],
                    'actual_value': '11.0'
                }
            ]
        }

        for step_id in step_ids:
            self.set_step_input(execution_url, StepTypes.MANUAL_INPUT, step_id, user_input)
        t2 = time.time()

        for step_id in step_ids:
            step_result = self.run_step(execution_id, step_id)         
            self.assertEqual(step_result['execution']['meta_data']['status'], 'PASS')
        t3 = time.time()   

        print('num of steps: ', num_steps)
        print('adding steps total: ', t1-t0, ' average:', (t1-t0)/num_steps)
        print('setting inputs total: ', t2-t1, ' average:', (t2-t1)/num_steps)
        print('running steps total: ', t3-t2, ' average:', (t3-t2)/num_steps)


    
if __name__ == "__main__":
    
        
    c = CreateExecution()
    
    c.run_steps()
    
    print('done')
    
    