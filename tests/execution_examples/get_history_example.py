import sys
import requests
import json
import random
import os

import sys
# Add the ptdraft folder path to the sys.path list

sys.path.append('..')

from test_ci_executions import ExecutionsTest
from config import shared_dict, logger


class GetExecutionHistory(ExecutionsTest):
    def get_data(self, execution_id):        

        execution_url = shared_dict['host'] + '/executions/' + execution_id
        elements = self.get_elements(execution_url)
        print("elements:", json.dumps(elements, indent=4)) 

        history_dict = self.get_history(execution_id)
        print("history_dict:", json.dumps(history_dict, indent=4))        
                     

if __name__ == "__main__":

    geh = GetExecutionHistory()
    geh.get_data('clipper-ingenium-10113')

 


    
    
    