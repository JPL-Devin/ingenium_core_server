import requests
import json
import random
import os

from config import shared_dict, logger

from test_ci_executions import ExecutionsTest
from utils import random_string
from ingenium_client import StepTypes

class ProcedureSectionExample(ExecutionsTest):
    def create_proc_section(self):
        
        rand_1 = random_string()
        title_1 = 'my title ' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')     

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id
        
        # Add sections
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            title='Section 1'
            )
        
        section_1 = res['elem']
        section_1_id = section_1['elem_id']
        
        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='SIBLING',
            title='Section 2'
            )
        
        section_2 = res['elem']
        section_2_id = section_2['elem_id']             
        
        ###
        
        # add paragraph to section 1
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            title='Paragraph A'
            )
        
        paragraph_a = res['elem']
        paragraph_a_id = paragraph_a['elem_id']
                
        # add steps to section 1
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=paragraph_a_id,
            level='SIBLING'
            )
        step_1_1 = res['elem']
        step_1_1_id = step_1_1['elem_id']             
        logger.debug('res= %s', json.dumps(res, indent=4))   
           
        self.update_step(procedure_url, StepTypes.ENVIRONMENT_MANUAL, step_1_1_id, {'title': 'Step 1-1'})             

        authoring_user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []  
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []       
            }
        }        
        self.set_step_input(procedure_url, step_1_1_id, authoring_user_input)        
        
        # add step to section 1
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,
            insert_after_id=step_1_1_id,
            level='SIBLING'
            )
        step_1_2 = res['elem']
        step_1_2_id = step_1_2['elem_id']          
        self.update_step(procedure_url, StepTypes.ENVIRONMENT_MANUAL, step_1_2_id, {'title': 'Step 1-2'})            
        
        
        # add step to section 2
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,                            
            insert_after_id=section_2_id,
            level='CHILD'      
            )
        
        step_2_1 = res['elem']
        step_2_1_id = step_2_1['elem_id']
        self.update_step(procedure_url, StepTypes.ENVIRONMENT_MANUAL, step_2_1_id, {'title': 'Step 2-1'})        
        
        # add step to section 2
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.ENVIRONMENT_MANUAL,    
            insert_after_id=step_2_1_id,
            level='SIBLING'      
            )
        
        step_2_2 = res['elem']
        step_2_2_id = step_2_2['elem_id']      
        self.update_step(procedure_url, StepTypes.ENVIRONMENT_MANUAL, step_2_2_id, {'title': 'Step 2-2'})                   
                
        # add version 1       
        version_dict = self.create_procedure_version(procedure_id, 'First version')
        version = version_dict['version']        
        self.assertEqual(version, 1)        
        
        
        ### Create an execution
        
        random_name = random_string(8)
        description = 'My execution with procedure section ' + random_name
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']
        venue_name = res_dict['name']  
        execution_dict = self.create_execution(venue_id, description)            
    
        execution_id = execution_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        # add a procedure section
        procedure_section_data = {'elem_type': 'PROCEDURE_SECTION', 
                                    'title': 'Procedure Section 1'}
        res = self.add_procedure_section(base_url=execution_url,
            insert_after_id="-1",
            level='CHILD',
            procedure_section=procedure_section_data)

        procedure_section_id = res['elem']['elem_id']
        procedure_section = self.get_procedure_section(shared_dict['host'], procedure_section_id)
        self.assertEqual(procedure_section['title'], procedure_section_data['title'])
        
        outline_elems = self.get_outline(procedure_url, version)

        procedure_section_input = {
            'reference_procedure_id': procedure_id,
            'reference_procedure_version': version,
            'elements': outline_elems,
            'reference_procedure_version_description': '',
            'reference_procedure_institutional_id': '',
            'reference_procedure_institutional_release_id': '',
            'reference_procedure_title': ''            
        }
        
        self.update_procedure_section_input(execution_url, procedure_section_id, procedure_section_input)

        user_input = self.get_procedure_section_input(execution_url, procedure_section_id)
        
        self.assertDictEqual(procedure_section_input, user_input)    
                       
        return execution_id
    
if __name__ == "__main__":
    
    if os.environ.get('JWT_SECRET') is None:
        print('JWT_SECRET env variable must be set')
        exit(-1)
        
    if os.environ.get('CORE_API_PATH') is None:
        print('CORE_API_PATH env variable must be set. For example, http://localhost:8002/api/v5')        
        exit(-1)
        
    p = ProcedureSectionExample()
    
    execution_id = p.create_proc_section()
    
    print('execution_id:', execution_id)
    
    