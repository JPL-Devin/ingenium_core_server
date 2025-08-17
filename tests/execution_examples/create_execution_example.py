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

meta_data_template = {
    "test_conductor": "",    
    "time_started": "",
    "time_completed": "",    
    "status": "NONE",    
    "error": {}
}

class CreateExecution(ExecutionsTest):
    def create_execution_from_json(self):        
        ### Create an execution
        
        random_name = random_string(8)
        description = 'My execution with pass, fail, and error ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        execution_dict = self.create_execution(venue_id, description)            
    
        self.execution_id = execution_dict['execution_id']
        self.execution_url = shared_dict['host'] + '/executions/' + self.execution_id
        self.archive_execution_url = shared_dict['archive_host'] + '/executions/' + self.execution_id

        # add a procedure section

        with open('as_run.json') as file:
            as_run_input = json.load(file)                
           
        self.add_children(as_run_input, "-1")

        as_run = self.get_as_run(self.execution_id)

        logger.debug('as_run: %s', json.dumps(as_run, indent=4)) 

    def add_children(self, parent, insert_after_id):

        if 'children' in parent:
            for elem in reversed(parent['children']):
                elem_type = elem['elem_type']
                logger.debug('original elem_id: %s', elem['elem_id'])

                if elem_type == "SECTION" or elem_type == "PROCEDURE_SECTION":
                    res_dict = self.add_section(base_url=self.execution_url,
                        insert_after_id=insert_after_id,
                        level='CHILD',
                        title=elem['title'],
                        description=elem['description'])

                    # logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))  

                    section = res_dict['elem']    
                    self.add_children(elem, section['elem_id'])

                elif elem_type == "PARAGRAPH":
                    res_dict = self.add_paragraph(base_url=self.execution_url,
                        insert_after_id=insert_after_id,
                        level='CHILD',
                        title=elem['title'],
                        description=elem['description'])   

                elif elem_type == "STEP":
                    step_type = elem['step_type']
                    res_dict = self.add_step(base_url=self.execution_url,
                        step_type=StepTypes[step_type],
                        insert_after_id=insert_after_id,
                        level='CHILD')
                    step = res_dict['elem']
                    step_id = step['elem_id']

                    if elem.get('run_records') and len(elem.get('run_records')) > 0:
                        for run_record in elem.get('run_records'):
                            self.set_step_input_output(run_record, step)
                            self.create_new_run(self.execution_id, step_id)          
                        del step['run_records']

                    self.set_step_input_output(elem, step)
                else:
                    logger.warning('unexpected elem_type: %s', elem_type)       



    def set_step_input_output(self, elem, step):
        step_type = elem['step_type']
        if ('execution' in elem) and ('meta_data' in elem['execution']):
            meta_data = {**meta_data_template, **(elem['execution']['meta_data'])}
        else:
            meta_data = meta_data_template

        if ('execution' in elem) and ('results' in elem['execution'] and isinstance(elem['execution']['results'], dict)):
            results = {**(step['specification']['results']), **(elem['execution']['results'])}
        else:
            results = step['specification']['results']                        

        execution_data = {
            'meta_data': meta_data,
            'results': results
        }
        
        step_dict = {
            'specification': step['specification'],     # update the old specification in the orginal data
            'authoring_user_input': elem['authoring_user_input'],    # set input, output
            'execution_user_input': elem['execution_user_input'],
            'execution': execution_data                     
        }

        logger.debug('step_dict: %s', json.dumps(step_dict, indent=4)) 

        self.update_step(base_url=self.execution_url, 
            step_type=StepTypes[step_type],
            elem_id=step['elem_id'], 
            step_dict=step_dict)        

        if elem['executed']:
            # Core does not allow changing 'executed' flag since it is managed internally.
            # Use Archive API to get around it.
            self.update_element(base_url=self.archive_execution_url, 
                elem_id=step['elem_id'], 
                elem_input={'executed': True},
                code_expected=200)              
    
if __name__ == "__main__":
    
        
    c = CreateExecution()
    
    c.create_execution_from_json()

    print('execution_id:', c.execution_id)
    
    