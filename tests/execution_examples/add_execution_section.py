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
    def add_section_to_front(self, execution_url):        
        res_dict = self.add_section(base_url=execution_url,
            insert_after_id='-1',
            level='',
            title='Section New',
            description='Section New')

        return res_dict
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('USAGE: python get_execution_elements.py execution_id')
    
    execution_id = sys.argv[1]

    execution_url = shared_dict['host'] + '/executions/' + execution_id

    c = Execution()
    
    print('execution_url:', execution_url)
        
    res_dict = c.add_section_to_front(execution_url)
    
    logger.info('res_dict: %s', json.dumps(res_dict, indent=4)) 
    
    