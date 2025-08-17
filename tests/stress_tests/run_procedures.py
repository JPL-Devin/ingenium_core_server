import requests
import json
import random
from string import ascii_lowercase
import os
import time
import datetime
import sys
from requests.auth import HTTPBasicAuth
import getpass
import multiprocessing
from multiprocessing import current_process

# Add the parent folder to the sys.path list

sys.path.append('..')

from config import shared_dict, logger

from test_ci_executions import ExecutionsTest
from utils import random_string
from ingenium_client import StepTypes
from ingenium_client.config import generate_token

def random_text(num_rows, num_columns):
    chars = ascii_lowercase + '   '

    rows = []
    for i in range(num_rows):
        char_list = map(lambda x: random.choice(chars), range(num_columns))
        rows.append(''.join(char_list))

    return '\n'.join(rows)

class RunProcedures(ExecutionsTest):

    def create_venues(self, num_venues):
        venue_ids = []
        for i in range(num_venues):
            venue = self.create_venue(venue_type='WSTS', description_prefix='TEST_', status='AVAILABLE', code_expected=200)
            venue_ids.append(venue['venue_id'])
        
        return venue_ids

    def create_test_procedure(self, num_sections, num_steps_per_section):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        user_input_0 = {
            'wait_type': 'DURATION',
            'time_value': '0'
        }        

        # Add sections and steps
        insert_after_id = '-1'
        level = 'CHILD'
        for i in range(num_sections):
            res = self.add_section(base_url=procedure_url,
                insert_after_id=insert_after_id,
                level=level,
                title='Section {}'.format(i + 1),
                description=random_text(100,80)
                )

            section = res['elem']
            section_id = section['elem_id']

            insert_after_id = section_id
            level = 'CHILD'
            for j in range(num_steps_per_section):
                res = self.add_step(base_url=procedure_url,
                    step_type=StepTypes.WAIT,
                    insert_after_id=insert_after_id,
                    level=level
                    )
                step = res['elem']
                step_id = step['elem_id']          

                insert_after_id = step_id
                level = 'SIBLING'

                self.update_step(procedure_url, StepTypes.WAIT, step_id, 
                {'title': 'Step {}-{}'.format(i+1, j+1), 'description': random_text(100, 80)})
                self.set_step_input(procedure_url, StepTypes.WAIT, step_id, user_input_0)                      
            
            insert_after_id = section_id
            level = 'SIBLING'    

        version_dict = self.create_procedure_version(procedure_id, 'First version', '')
        version = version_dict['version']           

        return (procedure_id, version)

    def run_procedure(self, venue_id, procedure_id, version, timeout):

        timed_out = False

        t0 = time.time()

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id
        execution_description = 'Test Execution ' + random_string()
        execution_dict = self.create_execution(venue_id, execution_description)

        try:
            execution_id = execution_dict['execution_id']
            execution_url = shared_dict['host'] + '/executions/' + execution_id

            procedure_section_data = {'elem_type': 'PROCEDURE_SECTION',
                                        'title': 'Procedure Section 1'}
            res = self.add_procedure_section(base_url=execution_url,
                insert_after_id="-1",
                level='CHILD',
                procedure_section=procedure_section_data)

            procedure_section_id = res['elem']['elem_id']
            procedure_section = self.get_procedure_section(execution_url, procedure_section_id)

            outline_elems = self.get_outline(procedure_url, version)

            procedure_section_input = {
                'reference_procedure_id': procedure_id,
                'reference_procedure_version': version,
                'elements': outline_elems,
                'reference_procedure_version_description': '',
                'reference_procedure_institutional_id': '',
                'reference_procedure_institutional_release_id': '',                
                'reference_procedure_title': '',
                'run_for_score': False            
            }

            self.update_procedure_section_input(execution_url, procedure_section_id, procedure_section_input)

            user_input = self.get_procedure_section_input(execution_url, procedure_section_id)

            proc_section_elems = self.import_procedure_section(execution_id, procedure_section_id)

            execution_info = {
                'mode': 'AUTO',
                'delay': 0, 
                'pause_conditions': {
                    'on_error': True, 
                    'on_fail': True, 
                    'on_section_end': False, 
                    'on_procedure_end': False,
                    'on_manual_input': True,
                    'on_break_point': True                
                }
            }            
            self.update_execution(execution_id, execution_info, code_expected=200)    

            t1 = time.time()

            self.run_step_async(execution_id, '', 202)

            # Wait until run is complete
            while True:
                run_time_elapsed = time.time() - t0
                print('run_time_elapsed:', run_time_elapsed, 'timeout:', timeout)
                if run_time_elapsed > timeout:
                    timed_out = True
                    print('return timed_out:', timed_out)
                    break
                time.sleep(1)
                
                execution = self.get_execution(execution_id)
                print(f'execution: {json.dumps(execution)}')
                if execution['status'] == 'IDLE':
                    break
                if execution['num_steps_failed'] > 0:
                    break    
                if execution['num_steps_errored'] > 0:
                    break    

            t2 = time.time()
        finally:
            print('venue_id:', venue_id, 'execution_id:', execution_id)
            print('set up (sec):', t1-t0, ' run (sec):', t2-t1)
            self.close_execution(execution_id)        
            t3 = time.time()
            print('close (sec):', t3-t2)
            return timed_out

    def run_procedures(self, procedure_id, version, num_runs, timeout):

        with open('out.txt', 'a+') as f:
            num_failures = 0
            num_successes = 0
            time_elapsed = 0

            t0 = time.time()
            
            venues = self.get_venues(offset=0, limit=1000)

            num_venues = len(venues)
            print('num_venues:', num_venues)

            venue_idx = 0
            for i in range(1, num_runs+1):
                print('run ', i)
                # refresh token for each run
                generate_token()

                venue_id = None
                venue_name = None
                for j in range(venue_idx, venue_idx+num_venues):
                    venue_idx = j % num_venues
                    print('venue_idx:', venue_idx)
                    venue = self.get_venue(venues[venue_idx]['venue_id'])
                    if venue['venue_status']['status'] == 'AVAILABLE':
                        venue_id = venue['venue_id']
                        venue = self.get_venue(venues[venue_idx]['venue_id'])
                        venue_name = venue['name']
                        venue_idx = (j+1) % num_venues
                        print('Selected venue:', venue_name, ' venue_id:', venue_id)     
                        print('venue_idx:', venue_idx)                
                        break

                if venue_id is None:
                    print('No venue is available.')
                    break
                
                time_taken = 0
                try:
                    t1 = time.time()
                    timed_out = self.run_procedure(venue_id, procedure_id, version, timeout)
                    print('timed_out:', timed_out)
                    if timed_out:
                        print('An execution timed out. Stop.')
                        return
                    t2 = time.time()
                    num_successes = num_successes + 1

                    time_taken = t2 - t1
                except:
                    num_failures = num_failures + 1

                time_elapsed = time.time() - t0
                out_line = '{}  {}  {}  {}  {}\n'.format(i, time_taken, time_elapsed, num_successes, num_failures) 
                print(out_line)
                f.write(out_line)
                f.flush()

    def run_procs(self, input):
        index, venue_id, procedure_id, version, num_runs, timeout = input

        out_file_name = f'out-{index}.txt'

        pid = current_process().pid

        print(f'run_proc index: {index} venue_id: {venue_id} procedure_id: {procedure_id} version: {version} num_runs: {num_runs} timeout: {timeout}')
        
        with open(out_file_name, 'a+') as f:
            num_successes = 0
            time_elapsed = 0

            t0 = time.time()
            
            for i in range(1, num_runs+1):
                # refresh token for each run
                # generate_token()

                time_taken = 0

                t1 = time.time()
                timed_out = self.run_procedure(venue_id, procedure_id, version, timeout)
                
                if timed_out:
                    print('An execution timed out. Stop.')
                    return
                
                t2 = time.time()
                num_successes = num_successes + 1

                time_taken = t2 - t1

                time_elapsed = time.time() - t0

                now = datetime.datetime.now()

                out_line = '{}  {}  {}  {}  {}  {}\n'.format(i, pid, now, time_taken, time_elapsed, num_successes) 
                print(out_line)
                f.write(out_line)
                f.flush()

    def run_procedures_multi_procs(self, procedure_id, version, num_runs, timeout, num_procs):
        venues = self.get_venues(offset=0, limit=1000)
        num_venues = len(venues)
        print('num_venues:', num_venues)

        venue_ids = []

        for venue in venues:
            venue_id = venue['venue_id']
            print('venue_id', venue_id)
            venue_info = self.get_venue(venue_id)
            print('venue_info', json.dumps(venue_info))
            if venue_info['venue_status']['status'] == 'AVAILABLE':
                venue_ids.append(venue_id)
                print(venue_ids)
                if len(venue_ids) == num_procs:
                    break

        if len(venue_ids) < num_procs:
            print(f'The number of available venues ({len(venue_ids)}) is less than the requested simultaneous executions ({num_procs})')
            sys.exit(1)

        inputs = []
        for index, venue_id in enumerate(venue_ids):
            inputs.append((index, venue_id, procedure_id, version, num_runs, timeout,))
       
        pool = multiprocessing.Pool(num_procs)
        pool.map(self.run_procs, inputs)    

    def get_venues(self, offset=0, limit=50, code_expected=200):
        url = '{0}/venues'.format(shared_dict['host'])
        params = {'offset': offset, 'limit': limit}
        result = requests.get(url,
            params = params,
            headers=shared_dict['headers'])

        return self.check_response(result, code_expected)             

def print_usage():
    print('USAGE: python run_procedures.py server create_venues num_venues')
    print('USAGE: python run_procedures.py server create_procedure num_sections num_steps_per_section')
    print('USAGE: python run_procedures.py server run_procedure venue_id procedure_id version timeout')
    print('USAGE: python run_procedures.py server run_procedures procedure_id version num_runs timeout')
    print('USAGE: python run_procedures.py server run_procedures_multi_procs procedure_id version num_runs timeout num_procs')    

if __name__ == "__main__":    

    logger.setLevel('ERROR')

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(-1)

    server = sys.argv[1]

    print(f'Connecting to: {server}')

    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    # print(login_url)
    current_user = getpass.getuser()
    username = input('username: %s' % current_user) or current_user
    password = getpass.getpass("password:")
    
    res = requests.get(login_url, auth=HTTPBasicAuth(username, password))    
    
    if res.status_code != 200:
        print('authentication failed. status_code:', res.status_code)
        sys.exit(-1)

    res_dict = json.loads(res.text)
    access_token = res_dict['access_token']
    jwt_token = 'Bearer {0}'.format(access_token)
    headers = {'Content-Type': 'application/json',
              'Accept': 'application/json'}
    headers['Authorization'] = jwt_token
    shared_dict['headers'] = headers   
    shared_dict['host'] = '%s/core_server/api/v5' % server

    if sys.argv[2] == 'create_venues':
        num_venues = int(sys.argv[3])
        rps = RunProcedures()
        venue_ids = rps.create_venues(num_venues)
        print(venue_ids)
    elif sys.argv[2] == 'create_procedure':
        num_sections = int(sys.argv[3])
        num_steps_per_section = int(sys.argv[4])    
        rps = RunProcedures()
        procedure_id, version = rps.create_test_procedure(num_sections, num_steps_per_section)
        print('procedure_id:', procedure_id, " version:", version)
    elif sys.argv[2] == 'run_procedure':
        venue_id = sys.argv[3]
        procedure_id = sys.argv[4]
        version = int(sys.argv[5])   
        timeout = int(sys.argv[6])      
        rps = RunProcedures()
        rps.run_procedure(venue_id, procedure_id, version, timeout) 
    elif sys.argv[2] == 'run_procedures':
        procedure_id = sys.argv[3]
        version = int(sys.argv[4]) 
        num_runs = int(sys.argv[5])   
        timeout = int(sys.argv[6])     
        rps = RunProcedures()
        rps.run_procedures(procedure_id, version, num_runs, timeout)                       
    elif sys.argv[2] == 'run_procedures_multi_procs':
        procedure_id = sys.argv[3]
        version = int(sys.argv[4]) 
        num_runs = int(sys.argv[5])   
        timeout = int(sys.argv[6])
        num_procs = int(sys.argv[7])
        rps = RunProcedures()
        rps.run_procedures_multi_procs(procedure_id, version, num_runs, timeout, num_procs)    
    else:
        print_usage()    



    
    