import requests
from requests.auth import HTTPBasicAuth
import json
import random
from string import ascii_lowercase
import os
import time
import datetime
import sys
import getpass
import unittest
import multiprocessing
from multiprocessing import current_process
# Add the ptdraft folder path to the sys.path list

from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


sys.path.append('..')

from config import shared_dict, logger

from test_ci_executions import ExecutionsTest
from utils import random_string
from ingenium_client import StepTypes

def random_text(num_rows, num_columns):
    chars = ascii_lowercase + '   '

    rows = []
    for i in range(num_rows):
        char_list = map(lambda x: random.choice(chars), range(num_columns))
        rows.append(''.join(char_list))

    return '\n'.join(rows)

class ProcedureTest(ExecutionsTest):
    def __init__(self, login_url, server, username, password):
        self.login_url = login_url
        self.server = server
        self.username = username
        self.password = password
        
        unittest.TestCase.__init__(self)
        
    def create_test_procedure(self, num_sections, num_steps_per_section, num_entries):
        self.set_headers()
        
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')
        
        # print(procedure_dict)

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id    

        # Add sections and steps
        insert_after_id = '-1'
        level = 'CHILD'
        for i in range(num_sections):
            if i % 10 == 0:
                self.set_headers()
            
            res = self.add_section(base_url=procedure_url,
                insert_after_id=insert_after_id,
                level=level,
                title='Section {}'.format(i + 1),
                description=random_text(20, 80)
                )

            section = res['elem']
            section_id = section['elem_id']

            insert_after_id = section_id
            level = 'CHILD'
            for j in range(num_steps_per_section):
                print(f'i: {i} j: {j}')
                res = self.add_step(base_url=procedure_url,
                    step_type=StepTypes.MANUAL_EIP,
                    insert_after_id=insert_after_id,
                    level=level
                    )
                step = res['elem']
                step_id = step['elem_id']          

                insert_after_id = step_id
                level = 'SIBLING'
                

                self.update_step(procedure_url, StepTypes.MANUAL_EIP, step_id, 
                {'title': 'Step {}-{}'.format(i+1, j+1), 'description': random_text(5, 80)}) 
                 
                entries = []
                for k in range(1, num_entries+1):
                    entries.append({
                        'signal_name': f'signal {k}',
                        'icds': f'ICDS {k}',
                        'from': f'from {k}',
                        'to': f'to {k}',
                        'unit': 'Volt',
                        'min_value': '8',
                        'max_value': '12'
                    })
                user_input = {'entries': entries}
                self.set_step_input(procedure_url, StepTypes.MANUAL_EIP, step_id, user_input)
            
            insert_after_id = section_id
            level = 'SIBLING'    
 

        return procedure_id

    def set_headers(self):
        res = requests.get(self.login_url, auth=HTTPBasicAuth(self.username, self.password))    
        
        if res.status_code != 200:
            print('authentication failed. status_code:', res.status_code)
            sys.exit(-1)
            
        res_dict = json.loads(res.text)
        access_token = res_dict['access_token']
        
        jwt_token = 'Bearer {0}'.format(access_token)
        
        headers = {'Authorization': jwt_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        
        api_path = '{0}/core_server/api/v5'.format(self.server)     

        logger.debug('use api_path: %s', api_path)    
        
        shared_dict['host'] = api_path
        shared_dict['headers'] = headers    

def print_usage():
    print('USAGE: python create_eip_procedures.py server num_sections num_steps_per_section num_entries num_procs')
    print('Example: python create_eip_procedures.py https://ingenium-ci.cld.jpl.nasa.gov 100 10 50 100')

if __name__ == "__main__":    
    logger.setLevel('DEBUG')

    if len(sys.argv) < 6:
        print_usage()
        sys.exit(-1)

    server = sys.argv[1]
    num_sections = int(sys.argv[2])
    num_steps_per_section = int(sys.argv[3]) 
    num_entries = int(sys.argv[4])
    num_procs = int(sys.argv[5])

    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    print(login_url)
    
    username = input("username:")
    password = getpass.getpass("password:")
    
    pt = ProcedureTest(login_url, server, username, password)
    for i in range(num_procs):
        procedure_id = pt.create_test_procedure(num_sections, num_steps_per_section, num_entries)
        print('procedure_id:', procedure_id)

