import xmlrunner
import os
import sys
import requests
import unittest
from config import shared_dict
import json
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes


class GDSManualStepTest(CoreTestBase):
    def test_gds_manual_step(self):
        print('test_gds')

        user_input = {
            'default_cmd_string': 'AB', 
            'entries': [
                {
                    'data_path': 'side_a',
                    'session_id': 3242945
                },
                {
                    'data_path': 'side_b',
                    'session_id': 3242946
                }
            ]
        }


        step = self.perform_step_operations(StepTypes.GDS_MANUAL, user_input, False, False, procedure=True)

    def test_data_paths(self):

        rand_1 = random_string()
        procedure_title = 'title_' + rand_1
        procedure_dict = self.create_procedure(procedure_title, 'Test procedure for data path')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.GDS_MANUAL,
            insert_after_id='-1',
            level='CHILD'
            )
        step_1 = res['elem']
        step_1_id = step_1['elem_id']

        self.update_step(procedure_url, StepTypes.GDS_MANUAL, step_1_id, {'title': 'Step 1'})

        authoring_user_input = {
            'default_cmd_string': 'AB',
            'entries': [
                {
                    'data_path': 'TZ-A'
                },
                {
                    'data_path': 'TZ-B'
                }
            ]
        }
        self.set_step_input(procedure_url, StepTypes.GDS_MANUAL, step_1_id, authoring_user_input)

        #
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.GDS_MANUAL,
            insert_after_id=step_1_id,
            level='SIBLING'
            )
        step_2 = res['elem']
        step_2_id = step_2['elem_id']

        self.update_step(procedure_url, StepTypes.GDS_MANUAL, step_2_id, {'title': 'Step 2'})

        authoring_user_input = {
            'default_cmd_string': 'AB',
            'entries': [
                {
                    'data_path': 'TZ-B'
                },
                {
                    'data_path': 'SA'
                }
            ]
        }
        self.set_step_input(procedure_url, StepTypes.GDS_MANUAL, step_2_id, authoring_user_input)

        version_dict = self.create_procedure_version(procedure_id, 'version 1')
        version = version_dict['version']
        # check time constants
        url = '{0}/procedures/{1}/versions/{2}/data_paths'.format(shared_dict['host'],
                                              procedure_id, version_dict['version'])

        res = requests.get(url, headers=shared_dict['headers'])
        data_paths = json.loads(res.text)

        self.assertEqual(len(data_paths), 3)
        self.assertEqual(data_paths[0], 'TZ-A')
        self.assertEqual(data_paths[1], 'TZ-B')
        self.assertEqual(data_paths[2], 'SA')

        ###
        res_dict = self.create_venue('WSTS')
        venue_id = res_dict['venue_id']           
        execution_dict = self.create_execution(venue_id, 'Execution with data path')
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
        url = '{0}/executions/{1}/data_paths'.format(shared_dict['host'], execution_id)

        res = requests.get(url, headers=shared_dict['headers'])
        data_paths = json.loads(res.text)

        self.assertEqual(len(data_paths), 3)
        self.assertEqual(data_paths[0], 'TZ-A')
        self.assertEqual(data_paths[1], 'TZ-B')
        self.assertEqual(data_paths[2], 'SA')


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
