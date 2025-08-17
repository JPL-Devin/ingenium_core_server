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


class ChangeTestConductor(ExecutionsTest):
    def change_it(self, execution_id, user_name):        
        
        execution_dict = self.get_execution(execution_id)
        venue_id = execution_dict['venue_id']

        test_conductors = execution_dict['test_conductors']

        if user_name not in test_conductors:
            test_conductors.append(user_name)
        print("test_conductors:", test_conductors) 

        execution_update_dict = {'test_conductors': test_conductors}

        self.update_execution(execution_id, execution_update_dict, code_expected=200)

        venue_update_dict = {'venue_status': {'test_conductor': user_name}}

        url = shared_dict['host'] + '/venues/' + venue_id

        result = requests.patch(url,
            headers=shared_dict['headers'],
            data=json.dumps(venue_update_dict))  

        if result.status_code == 204:
            print('Test conductor was changed.')
        else:
            print('Failed to change the test conductor. status_code:', result.status_code)        
            print('Message:', result.text)                       

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python change_test_conductor.py <execution_id> <user_name>")
        print("Example: python change_test_conductor.py m2020-ingenium-10001 hongmank")
        sys.exit(1)
    
    execution_id = sys.argv[1]
    user_name = sys.argv[2]

    print("execution_id:", execution_id)
    print("user_name:", user_name)

    ctc = ChangeTestConductor()
    ctc.change_it(execution_id, user_name)

 


    
    
    