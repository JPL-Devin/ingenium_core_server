import requests
import json
import random
from string import ascii_lowercase
import os
import time
import datetime
import sys
import multiprocessing
from multiprocessing import current_process
# Add the ptdraft folder path to the sys.path list

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

class ProcedureTest(ExecutionsTest):
    def create_test_procedure(self, num_sections, num_steps_per_section):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id    

        # Add sections and steps
        insert_after_id = '-1'
        level = 'CHILD'
        for i in range(num_sections):
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
                res = self.add_step(base_url=procedure_url,
                    step_type=StepTypes.ENVIRONMENT_MANUAL,
                    insert_after_id=insert_after_id,
                    level=level
                    )
                step = res['elem']
                step_id = step['elem_id']          

                insert_after_id = step_id
                level = 'SIBLING'

                self.update_step(procedure_url, StepTypes.MANUAL_EIP, step_id, 
                {'title': 'Step {}-{}'.format(i+1, j+1), 'description': random_text(5, 80)})                    
            
            insert_after_id = section_id
            level = 'SIBLING'    
 

        return procedure_id

def print_usage():
    print('USAGE: python create_eip_procedure.py num_sections num_steps_per_section')
    print('Example: python create_env_procedure.py 100 10')

if __name__ == "__main__":    
    logger.setLevel('ERROR')

    if len(sys.argv) < 3:
        print_usage()
        sys.exit(-1)

    num_sections = int(sys.argv[1])
    num_steps_per_section = int(sys.argv[2]) 
       
    pt = ProcedureTest()
    procedure_id = pt.create_test_procedure(num_sections, num_steps_per_section)
    print('procedure_id:', procedure_id)

