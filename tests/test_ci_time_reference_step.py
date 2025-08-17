import xmlrunner
import os
import sys
import requests
import unittest
from config import shared_dict, logger
from utils import random_string
import json
from ingenium_client import CoreTestBase, StepTypes

class TimeReferenceStepTest(CoreTestBase):
    def test_time_reference_step(self):
        user_input = {
            "name": "Time Ref One",
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.TIME_REFERENCE, user_input, True, False)

        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.TIME_REFERENCE, user_input, False, False, procedure=True)

    def test_time_references(self):

        rand_1 = random_string()
        procedure_title = 'title_' + rand_1
        procedure_dict = self.create_procedure(procedure_title, 'Test procedure for time reference')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.TIME_REFERENCE,
            insert_after_id='-1',
            level='CHILD'
            )
        step_1 = res['elem']
        step_1_id = step_1['elem_id']

        self.update_step(procedure_url, StepTypes.TIME_REFERENCE, step_1_id, {'title': 'Step 1'})

        authoring_user_input = {
            'name': 'time ref one'
        }
        self.set_step_input(procedure_url, StepTypes.TIME_REFERENCE, step_1_id, authoring_user_input)

        version_dict = self.create_procedure_version(procedure_id, 'version 1')
        version = version_dict['version']
        # check time constants
        url = '{0}/procedures/{1}/versions/{2}/time_references'.format(shared_dict['host'],
                                              procedure_id, version_dict['version'])

        res = requests.get(url, headers=shared_dict['headers'])
        time_refs = json.loads(res.text)
        self.assertEqual(len(time_refs), 14)
        self.assertEqual(time_refs[13], 'time ref one')

        ###
        res_dict = self.create_venue('WSTS')
        venue_id = res_dict['venue_id']           
        execution_dict = self.create_execution(venue_id, 'Execution with time reference')
        execution_id = execution_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        procedure_title = 'this is a section title'
        procedure_description = 'this is a description'
        procedure_section_data = {
            'title': procedure_title,
            'description': procedure_description
        }
        res = self.add_procedure_section(base_url=execution_url,
            insert_after_id="-1",
            level='CHILD',
            procedure_section=procedure_section_data)

        procedure_section_id = res['elem']['elem_id']

        outline_elems = self.get_outline(procedure_url, version)

        procedure_section_input = {
            'reference_procedure_id': procedure_id,
            'reference_procedure_version': version,
            'elements': outline_elems,
            'reference_procedure_version_description': '',
            'reference_procedure_institutional_id': '',
            'reference_procedure_institutional_release_id': '',            
            'reference_procedure_title': procedure_title,
            'run_for_score': False
        }

        self.update_procedure_section_input(execution_url, procedure_section_id, procedure_section_input)

        # 
        self.import_procedure_section(execution_id, procedure_section_id)

        # check time constants
        url = '{0}/executions/{1}/time_references'.format(shared_dict['host'], execution_id)

        res = requests.get(url, headers=shared_dict['headers'])
        time_refs = json.loads(res.text)

        self.assertEqual(len(time_refs), 14)
        self.assertEqual(time_refs[13], 'time ref one')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
