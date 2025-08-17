import requests
import json
import random
import os

import sys
# Add the ptdraft folder path to the sys.path list

sys.path.append('..')

from config import shared_dict, logger

from test_ci_executions import ExecutionsTest
from utils import random_string
from ingenium_client import StepTypes


class Execution(ExecutionsTest):
    def run_get_elements(self, execution_id):        
        elements = self.get_elements(execution_id)

        return elements
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('USAGE: python get_execution_elements.py execution_id')
    
    execution_id = sys.argv[1]

    execution_url = shared_dict['host'] + '/executions/' + execution_id

    c = Execution()
    
    print('execution_url:', execution_url)
        
    elements = c.run_get_elements(execution_url)
    
    logger.info('elements: %s', json.dumps(elements, indent=4)) 
    
    