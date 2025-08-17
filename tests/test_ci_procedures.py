import xmlrunner
import os
import sys
import unittest
import requests
import json
import copy
import random
import time
import string
from dateutil import parser
from datetime import datetime
import math
import dateutil.tz
from config import shared_dict, logger
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes


class ProcedureTest(CoreTestBase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_procedure(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        res_dict = self.create_procedure(title_1, '')

        procedure_id = res_dict['procedure_id']

        procedure_dict = self.get_procedure(procedure_id)

        self.assertEqual(procedure_dict['procedure_id'], procedure_id)
        self.assertEqual(procedure_dict['title'], title_1)

        title_new = 'Updated title'
        self.update_procedure(procedure_id, {'title': title_new})
        procedure_dict = self.get_procedure(procedure_id)
        self.assertEqual(procedure_dict['title'], title_new)

        self.delete_procedure(procedure_id)

        # should not be found
        self.get_procedure(procedure_id, 400)

    def test_get_procedures(self):
        # use this to find procedures created only from this test
        rand_0 = random_string()

        rand_1 = random_string()
        title_1 = 'title_{0}_{1}'.format(rand_0, rand_1)
        institutional_id_1 = 'pbat-101-' + rand_1
        procedure_dict = self.create_procedure(title_1, 'First procedure', institutional_id_1)
        procedure_id_1 = procedure_dict['procedure_id']

        rand_2 = random_string()
        title_2 = 'title_{0}_{1}'.format(rand_0, rand_2)
        author_2 = 'author_{0}'.format(rand_2)
        institutional_id_2 = 'pbat-120-' + rand_2
        description_2 = 'Second procedure ' + rand_2
        procedure_dict = self.create_procedure(title_2, description_2, institutional_id_2)
        procedure_id_2 = procedure_dict['procedure_id']

        self.update_procedure(procedure_id_2, {'author': author_2, 'obsolete': True})

        rand_3 = random_string()
        title_3 = 'title_{0}_{1}'.format(rand_0, rand_3)
        institutional_id_3 = 'pbat-121-' + rand_3
        procedure_dict = self.create_procedure(title_3, 'Third procedure', institutional_id_3)
        procedure_id_3 = procedure_dict['procedure_id']

        version_dict_3 = self.create_procedure_version(procedure_id_3, 'v1')

        rand_4 = random_string()
        title_4 = 'title_{0}_{1}'.format(rand_0, rand_4)
        institutional_id_4 = 'pbat-123-' + rand_4
        procedure_dict = self.create_procedure(title_4, 'Fourth procedure', institutional_id_4)
        procedure_id_4 = procedure_dict['procedure_id']

        version_dict_4 = self.create_procedure_version(procedure_id_4, 'v1')
        self.update_procedure_version(procedure_id_4, 1, {'institutional_release_id': 'r1'})
        self.update_procedure_version_status(procedure_id_4, 1, {'action': 'RELEASE'})

        url = shared_dict['host'] + '/procedures'
        params = {'limit': 10000, 'title': rand_0}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        venue_count = len(res_dict)
        self.assertEqual(len(res_dict), 4)

        # check for the default sort
        self.assertEqual(res_dict[0]['title'], title_4)

        # filter by title
        params = {'title': rand_1}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['title'], title_1)

        # filter by author
        params = {'title': rand_0, 'author': rand_2}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['author'], author_2)

        # filter by description
        params = {'title': rand_0, 'description': rand_2}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['description'], description_2)

        # filter by institutional_id
        params = {'title': rand_0, 'institutional_id': rand_4}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['institutional_id'], institutional_id_4)

        # filter by versioned
        params = {'title': rand_0, 'versioned': 'true'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)

        params = {'title': rand_0, 'versioned': 'false'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)

        # filter by released
        params = {'title': rand_0, 'released': 'true'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)

        params = {'title': rand_0, 'released': 'false'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 3)

        # filter by obsolete
        params = {'title': rand_0, 'obsolete': 'true'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)

        params = {'title': rand_0, 'obsolete': 'false'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 3)


        # unset institutional_release_id
        self.update_procedure_version_status(procedure_id_4, version_dict_4['version'], {'action': 'UNRELEASE'})
        # filter by released
        params = {'title': rand_0, 'released': 'true'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 0)

        params = {'title': rand_0, 'released': 'false'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 4)

        # check for the sort
        params = {'limit': 10000, 'title': rand_0, 'sort': 'DESC'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[0]['title'], title_4)

        params = {'limit': 10000, 'title': rand_0, 'sort': 'ASC'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['title'], title_4)
        self.assertEqual(res_dict[-2]['title'], title_3)
        self.assertEqual(res_dict[-3]['title'], title_2)
        self.assertEqual(res_dict[-4]['title'], title_1)

        params = {'limit': 10000, 'title': rand_0, 'sort': 'ASC', 'sort_by': 'TIME_CREATED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['title'], title_4)
        self.assertEqual(res_dict[-2]['title'], title_3)
        self.assertEqual(res_dict[-3]['title'], title_2)
        self.assertEqual(res_dict[-4]['title'], title_1)

        params = {'limit': 10000, 'title': rand_0, 'sort': 'ASC', 'sort_by': 'INSTITUTIONAL_ID'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['institutional_id'], institutional_id_4)
        self.assertEqual(res_dict[-2]['institutional_id'], institutional_id_3)
        self.assertEqual(res_dict[-3]['institutional_id'], institutional_id_2)
        self.assertEqual(res_dict[-4]['institutional_id'], institutional_id_1)

        params = {'limit': 10000, 'title': rand_0, 'sort': 'DESC', 'sort_by': 'INSTITUTIONAL_ID'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['institutional_id'], institutional_id_1)
        self.assertEqual(res_dict[-2]['institutional_id'], institutional_id_2)
        self.assertEqual(res_dict[-3]['institutional_id'], institutional_id_3)
        self.assertEqual(res_dict[-4]['institutional_id'], institutional_id_4)
        self.assertEqual(len(res_dict), 4)

        # get total count
        params = {'limit': 10000, 'title': rand_0, 'sort': 'DESC', 'sort_by': 'INSTITUTIONAL_ID'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        total_count = len(res_dict)

        # offset and limit
        params = {'limit': 2, 'title': rand_0}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(int(result.headers['x-total-count']), total_count)

        params = {'offset': 1, 'limit': 2, 'title': rand_0}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(int(result.headers['x-total-count']), 4)
        self.assertEqual(res_dict[0]['title'], title_3)
        self.assertEqual(res_dict[1]['title'], title_2)

    def test_create_procedure(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')
        procedure_id = procedure_dict['procedure_id']

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section 1
        res_dict = self.add_section(base_url=procedure_url,
            insert_after_id='-1',
            level='',
            description='Section 1')

        section_1 = res_dict['elem']
        section_1_id = section_1['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], '')


        new_description = 'Updated Section 1'
        self.update_section(base_url=procedure_url, elem_id=section_1_id, section_dict={'description': new_description})

        section_1 = self.get_section(base_url=procedure_url, elem_id=section_1_id)
        self.assertEqual(section_1['description'], new_description)

        # Add section 2
        res_dict = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='SIBLING',
            description='Section 2')

        section_2 = res_dict['elem']
        section_2_id = section_2['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], '')

        # add paragraph
        res_dict = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            description='Paragraph 1-1')

        paragraph_1_1 = res_dict['elem']
        paragraph_1_1_id = paragraph_1_1['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], section_1_id)

        new_description = 'Updated Paragraph 1-1'
        self.update_paragraph(base_url=procedure_url,
            elem_id=paragraph_1_1_id, paragraph_dict={'description': new_description})

        paragraph_1_1 = self.get_paragraph(base_url=procedure_url, elem_id=paragraph_1_1_id)
        self.assertEqual(paragraph_1_1['description'], new_description)

        # add step 1-2
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=paragraph_1_1_id,
            level='SIBLING')

        logger.debug('new step res_dict= %s', json.dumps(res_dict, indent=4))

        step_1_2 = res_dict['elem']
        step_1_2_id = step_1_2['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], section_1_id)

        new_description = 'Updated Step 1-2'
        self.update_step(procedure_url,
            StepTypes.MANUAL_INPUT, step_1_2_id, {'description': new_description})

        step_1_2 = self.get_step(base_url=procedure_url, step_type=StepTypes.MANUAL_INPUT,
            elem_id=step_1_2_id)
        self.assertEqual(step_1_2['description'], new_description)

        authoring_user_input = {
            'entries': [
                {
                    'name': 'step_function_name',
                    'type': 'STRING',
                    'verify_on': 'VALUE',
                    'verification_condition': 'RECORD',
                    'verification_values': [],
                    'actual_value': 'run_dummy'
                }
            ]
        }
        res_dict = self.set_step_input(procedure_url, StepTypes.MANUAL_INPUT,
            step_1_2_id, authoring_user_input)
        self.set_step_input(procedure_url, StepTypes.MANUAL_INPUT, step_1_2_id, authoring_user_input)

        res_dict = self.get_step_input(procedure_url, StepTypes.MANUAL_INPUT, step_1_2_id)

        self.assertDictEqual(res_dict, authoring_user_input)

        # add step 1-3
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=step_1_2_id,
            level='SIBLING')

        step_1_3 = res_dict['elem']
        step_1_3_id = step_1_3['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], section_1_id)

        res = self.update_element(procedure_url, step_1_3_id, {'title': 'Step 1-3'}) 
        self.assertEqual(res['title'], 'Step 1-3')              

        # get elements
        elems = self.get_elements(procedure_url)
        logger.debug('elems: %s', json.dumps(elems, indent=4))
        self.assertEqual(len(elems), 5)

        sections = self.get_sections(base_url=procedure_url)
        self.assertEqual(len(sections), 2)

        paragraphs = self.get_paragraphs(base_url=procedure_url)
        self.assertEqual(len(paragraphs), 1)

        steps = self.get_steps(procedure_url, StepTypes.MANUAL_INPUT)

        self.assertEqual(len(sections), 2)

        # get structure
        res_dict = self.get_structure(procedure_id)

        self.assertEqual(res_dict['children'][0]['children'][2]['elem_id'], step_1_3_id)
        self.assertEqual(res_dict['children'][0]['children'][2]['number'], '1-3')

        # move element
        self.move_element(procedure_url, section_1_id, section_2_id, 'CHILD')
        res_dict = self.get_structure(procedure_id)


        self.assertEqual(res_dict['children'][0]['children'][0]['children'][2]['elem_id'], step_1_3_id)
        self.assertEqual(res_dict['children'][0]['children'][0]['children'][2]['number'], '1-1-3')

        # move it back
        self.move_element(procedure_url, section_1_id, '-1', 'CHILD')
        res_dict = self.get_structure(procedure_id)

        self.assertEqual(res_dict['children'][0]['children'][2]['elem_id'], step_1_3_id)
        self.assertEqual(res_dict['children'][0]['children'][2]['number'], '1-3')

        # delete elements
        res_dict = self.delete_element(procedure_url, paragraph_1_1_id)

        res_dict = self.delete_element(procedure_url, section_1_id)

        res_dict = self.delete_element(procedure_url, section_2_id)


        # get structure
        res_dict = self.get_structure(procedure_id)


        sections = self.get_sections(procedure_url)
        self.assertEqual(len(sections), 0)

        paragraphs = self.get_paragraphs(procedure_url)
        self.assertEqual(len(paragraphs), 0)

        steps = self.get_steps(procedure_url, StepTypes.MANUAL_INPUT)
        self.assertEqual(len(steps), 0)

    def test_update_step(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')
        procedure_id = procedure_dict['procedure_id']

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # add step 1
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VENUE_CONFIG_MANUAL,
            insert_after_id='-1',
            level='')

        logger.debug('new step res_dict= %s', json.dumps(res_dict, indent=4))

        step_1 = res_dict['elem']
        step_1_id = step_1['elem_id']

        new_description = 'Once updated step'
        self.update_step(procedure_url,
            StepTypes.VENUE_CONFIG_MANUAL, step_1_id, {'description': new_description})
        res_dict = self.get_step(procedure_url, StepTypes.VENUE_CONFIG_MANUAL, step_1_id)
        self.assertEqual(res_dict['description'], new_description)

        new_description_2 = 'Twice updated step'
        step_1['description'] = new_description_2
        self.update_step(procedure_url,
            StepTypes.VENUE_CONFIG_MANUAL, step_1_id, step_1)
        res_dict = self.get_step(procedure_url, StepTypes.VENUE_CONFIG_MANUAL, step_1_id)
        self.assertEqual(res_dict['description'], new_description_2)            

        # add step 2
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.GDS_MANUAL,
            insert_after_id=step_1_id,
            level='SIBLING')

        logger.debug('new step res_dict= %s', json.dumps(res_dict, indent=4))

        step_2 = res_dict['elem']
        step_2_id = step_2['elem_id']

        new_description = 'Once updated step'
        self.update_step(procedure_url,
            StepTypes.GDS_MANUAL, step_2_id, {'description': new_description})
        res_dict = self.get_step(procedure_url, StepTypes.GDS_MANUAL, step_2_id)
        self.assertEqual(res_dict['description'], new_description)

        new_description_2 = 'Twice updated step'
        step_2['description'] = new_description_2
        self.update_step(procedure_url,
            StepTypes.GDS_MANUAL, step_2_id, step_2)
        res_dict = self.get_step(procedure_url, StepTypes.GDS_MANUAL, step_2_id)
        self.assertEqual(res_dict['description'], new_description_2)      

        # add step 3
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.WAIT,
            insert_after_id=step_2_id,
            level='SIBLING')

        logger.debug('new step res_dict= %s', json.dumps(res_dict, indent=4))

        step_3 = res_dict['elem']
        step_3_id = step_3['elem_id']

        new_description = 'Once updated step'
        self.update_step(procedure_url,
            StepTypes.WAIT, step_3_id, {'description': new_description})
        res_dict = self.get_step(procedure_url, StepTypes.WAIT, step_3_id)
        self.assertEqual(res_dict['description'], new_description)

        new_description_2 = 'Twice updated step'
        step_3['description'] = new_description_2
        self.update_step(procedure_url,
            StepTypes.WAIT, step_3_id, step_3)
        res_dict = self.get_step(procedure_url, StepTypes.WAIT, step_3_id)
        self.assertEqual(res_dict['description'], new_description_2)         
  

    def test_move_element(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section 1
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            title='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            title='Section 1-1')

        section_1_1 = res['elem']
        section_1_1_id = section_1_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_1_id,
            level='SIBLING',
            title='Section 1-2')

        section_1_2 = res['elem']
        section_1_2_id = section_1_2['elem_id']

        # Add section 2
        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='SIBLING',
            title='Section 2')

        section_2 = res['elem']
        section_2_id = section_2['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_2_id,
            level='CHILD',
            title='Section 2-1')

        section_2_1 = res['elem']
        section_2_1_id = section_2_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_2_1_id,
            level='SIBLING',
            title='Section 2-2')

        section_2_2 = res['elem']
        section_2_2_id = section_2_2['elem_id']
        
        # Cannot move to itself
        res_dict = self.move_element(procedure_url, section_1_1_id, section_1_1_id, 'CHILD', code_expected=400)
        logger.debug('move res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['details']), 2)
        self.assertEqual(res_dict['details'][0], 'Cannot move an element to itself or its child')
        
        # Cannot move to itself
        res_dict = self.move_element(procedure_url, section_1_id, section_1_1_id, 'SIBLING', code_expected=400)
        logger.debug('move res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['details']), 2)
        self.assertEqual(res_dict['details'][0], 'Cannot move an element to itself or its child')        
        
        # Cannot move to its child
        res_dict = self.move_element(procedure_url, section_1_id, section_1_1_id, 'CHILD', code_expected=400)
        logger.debug('move res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['details']), 2)
        self.assertEqual(res_dict['details'][0], 'Cannot move an element to itself or its child')          

        structure_dict = self.get_structure(procedure_id)
        # logger.debug('orig structure_dict: %s', json.dumps(structure_dict, indent=4))

        res_dict = self.move_element(procedure_url, section_2_1_id, section_1_1_id, 'SIBLING')
        logger.debug('move res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['numbers']), 3)
        self.assertEqual(res_dict['numbers'][0]['elem_id'], section_2_1_id)
        self.assertEqual(res_dict['numbers'][0]['number'], '1-2')
        self.assertEqual(res_dict['numbers'][1]['elem_id'], section_1_2_id)
        self.assertEqual(res_dict['numbers'][1]['number'], '1-3')
        self.assertEqual(res_dict['numbers'][2]['elem_id'], section_2_2_id)
        self.assertEqual(res_dict['numbers'][2]['number'], '2-1')

        structure_dict = self.get_structure(procedure_id)
        logger.debug('moved structure_dict: %s', json.dumps(structure_dict, indent=4))

        self.assertEqual(structure_dict['children'][0]['title'], 'Section 1')
        self.assertEqual(structure_dict['children'][0]['number'], '1')
        self.assertEqual(structure_dict['children'][0]['children'][0]['title'], 'Section 1-1')
        self.assertEqual(structure_dict['children'][0]['children'][0]['number'], '1-1')
        self.assertEqual(structure_dict['children'][0]['children'][1]['title'], 'Section 2-1')
        self.assertEqual(structure_dict['children'][0]['children'][1]['number'], '1-2')
        self.assertEqual(structure_dict['children'][0]['children'][2]['title'], 'Section 1-2')
        self.assertEqual(structure_dict['children'][0]['children'][2]['number'], '1-3')
        self.assertEqual(structure_dict['children'][1]['title'], 'Section 2')
        self.assertEqual(structure_dict['children'][1]['number'], '2')
        self.assertEqual(structure_dict['children'][1]['children'][0]['title'], 'Section 2-2')
        self.assertEqual(structure_dict['children'][1]['children'][0]['number'], '2-1')


    def create_procedure_example(self):
        id_dict = {}

        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section 1
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            title='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            title='Section 1-1')

        section_1_1 = res['elem']
        section_1_1_id = section_1_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_1_id,
            level='SIBLING',
            title='Section 1-2')

        section_1_2 = res['elem']
        section_1_2_id = section_1_2['elem_id']

        # Add section 2
        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='SIBLING',
            title='Section 2')

        section_2 = res['elem']
        section_2_id = section_2['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_2_id,
            level='CHILD',
            title='Section 2-1')

        section_2_1 = res['elem']
        section_2_1_id = section_2_1['elem_id']

        res = self.add_section(base_url=procedure_url,
            insert_after_id=section_2_1_id,
            level='SIBLING',
            title='Section 2-2')

        section_2_2 = res['elem']
        section_2_2_id = section_2_2['elem_id']

        id_dict['procedure_url'] = procedure_url
        id_dict['procedure_id'] = procedure_id     
        id_dict['version_id'] = section_1['version_id']               
        id_dict['section_1_id'] = section_1_id 
        id_dict['section_1_1_id'] = section_1_1_id    
        id_dict['section_1_2_id'] = section_1_2_id    
        id_dict['section_2_id'] = section_2_id 
        id_dict['section_2_1_id'] = section_2_1_id    
        id_dict['section_2_2_id'] = section_2_2_id                        

        return id_dict     

    def test_copy_element(self):
        id_dict = self.create_procedure_example()

        procedure_url = id_dict['procedure_url'] 
        procedure_id = id_dict['procedure_id']     
        version_id = id_dict['version_id']      
        section_1_id = id_dict['section_1_id'] 
        section_1_1_id = id_dict['section_1_1_id']    
        section_1_2_id = id_dict['section_1_2_id']    
        section_2_id = id_dict['section_2_id']
        section_2_1_id = id_dict['section_2_1_id']
        section_2_2_id = id_dict['section_2_2_id']

        res_dict = self.copy_element(procedure_url, section_2_1_id, section_1_1_id, 'SIBLING')
        logger.debug('copy res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['numbers']), 2)
        self.assertEqual(res_dict['numbers'][0]['number'], "1-2")
        self.assertEqual(res_dict['numbers'][1]['number'], "1-3")


        self.assertEqual(len(res_dict['elements']), 1)
        self.assertEqual(res_dict['elements'][0]['title'], 'Section 2-1')
        self.assertEqual(res_dict['elements'][0]['number'], '1-2')

        res_dict = self.get_version_elements(procedure_id=procedure_id, version=0)
        logger.debug('copied elements res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict), 7)
        self.assertEqual(res_dict[0]['title'], "Section 1")
        self.assertEqual(res_dict[1]['title'], "Section 1-1")
        self.assertEqual(res_dict[2]['title'], "Section 2-1")        
        self.assertEqual(res_dict[3]['title'], "Section 1-2")
        self.assertEqual(res_dict[4]['title'], "Section 2")
        self.assertEqual(res_dict[5]['title'], "Section 2-1")                        
        self.assertEqual(res_dict[6]['title'], "Section 2-2") 

        self.assertEqual(res_dict[0]['number'], "1")
        self.assertEqual(res_dict[1]['number'], "1-1")
        self.assertEqual(res_dict[2]['number'], "1-2")
        self.assertEqual(res_dict[3]['number'], "1-3")
        self.assertEqual(res_dict[4]['number'], "2")
        self.assertEqual(res_dict[5]['number'], "2-1")
        self.assertEqual(res_dict[6]['number'], "2-2")

    def test_copy_elements(self):
        id_dict = self.create_procedure_example()

        procedure_url = id_dict['procedure_url'] 
        procedure_id = id_dict['procedure_id']     
        version_id = id_dict['version_id']      
        section_1_id = id_dict['section_1_id'] 
        section_1_1_id = id_dict['section_1_1_id']    
        section_1_2_id = id_dict['section_1_2_id']    
        section_2_id = id_dict['section_2_id']
        section_2_1_id = id_dict['section_2_1_id']
        section_2_2_id = id_dict['section_2_2_id']  

        ## copy element
        res_dict = self.copy_elements(procedure_url, [section_2_1_id], section_1_1_id, 'SIBLING')
        logger.debug('copy res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict['numbers']), 2)
        self.assertEqual(res_dict['numbers'][0]['number'], "1-2")
        self.assertEqual(res_dict['numbers'][1]['number'], "1-3")

        self.assertEqual(len(res_dict['elements']), 1)
        self.assertEqual(res_dict['elements'][0]['title'], 'Section 2-1')
        self.assertEqual(res_dict['elements'][0]['number'], '1-2')                

        copied_elem_infos = res_dict['elements']

        self.assertEqual(len(res_dict['elem_ids']), 7)
        self.assertEqual(res_dict['elem_ids'][0], section_1_id)
        self.assertEqual(res_dict['elem_ids'][1], section_1_1_id)
        self.assertEqual(res_dict['elem_ids'][2], copied_elem_infos[0]['elem_id'])
        self.assertEqual(res_dict['elem_ids'][3], section_1_2_id)
        self.assertEqual(res_dict['elem_ids'][4], section_2_id)
        self.assertEqual(res_dict['elem_ids'][5], section_2_1_id)
        self.assertEqual(res_dict['elem_ids'][6], section_2_2_id)                                              

        res_dict = self.get_version_elements(procedure_id=procedure_id, version=0)
        logger.debug('copied elements res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict), 7)
        self.assertEqual(res_dict[0]['title'], "Section 1")
        self.assertEqual(res_dict[1]['title'], "Section 1-1")
        self.assertEqual(res_dict[2]['title'], "Section 2-1")        
        self.assertEqual(res_dict[3]['title'], "Section 1-2")
        self.assertEqual(res_dict[4]['title'], "Section 2")
        self.assertEqual(res_dict[5]['title'], "Section 2-1")                        
        self.assertEqual(res_dict[6]['title'], "Section 2-2") 

        self.assertEqual(res_dict[0]['number'], "1")
        self.assertEqual(res_dict[1]['number'], "1-1")
        self.assertEqual(res_dict[2]['number'], "1-2")
        self.assertEqual(res_dict[3]['number'], "1-3")
        self.assertEqual(res_dict[4]['number'], "2")
        self.assertEqual(res_dict[5]['number'], "2-1")
        self.assertEqual(res_dict[6]['number'], "2-2")

        # reset
        for copied_elem_info in copied_elem_infos:
            self.delete_element(procedure_url, copied_elem_info['elem_id'], code_expected=200)

        ## copy two elements
        res_dict = self.copy_elements(procedure_url, [section_2_1_id, section_2_2_id], section_1_1_id, 'SIBLING')
        logger.debug('copy res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict['numbers']), 3)
        self.assertEqual(res_dict['numbers'][0]['number'], "1-2")
        self.assertEqual(res_dict['numbers'][1]['number'], "1-3")
        self.assertEqual(res_dict['numbers'][2]['number'], "1-4")

        self.assertEqual(len(res_dict['elements']), 2)
        self.assertEqual(res_dict['elements'][0]['title'], 'Section 2-1')
        self.assertEqual(res_dict['elements'][0]['number'], '1-2')       
        self.assertEqual(res_dict['elements'][1]['title'], 'Section 2-2')
        self.assertEqual(res_dict['elements'][1]['number'], '1-3')  

        copied_elem_infos = res_dict['elements']

        self.assertEqual(len(res_dict['elem_ids']), 8)
        self.assertEqual(res_dict['elem_ids'][0], section_1_id)
        self.assertEqual(res_dict['elem_ids'][1], section_1_1_id)
        self.assertEqual(res_dict['elem_ids'][2], copied_elem_infos[0]['elem_id'])
        self.assertEqual(res_dict['elem_ids'][3], copied_elem_infos[1]['elem_id'])
        self.assertEqual(res_dict['elem_ids'][4], section_1_2_id)
        self.assertEqual(res_dict['elem_ids'][5], section_2_id)
        self.assertEqual(res_dict['elem_ids'][6], section_2_1_id)
        self.assertEqual(res_dict['elem_ids'][7], section_2_2_id)                                              

        res_dict = self.get_version_elements(procedure_id=procedure_id, version=0)
        logger.debug('copied elements res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict), 8)
        self.assertEqual(res_dict[0]['title'], "Section 1")
        self.assertEqual(res_dict[1]['title'], "Section 1-1")
        self.assertEqual(res_dict[2]['title'], "Section 2-1")    
        self.assertEqual(res_dict[3]['title'], "Section 2-2")    
        self.assertEqual(res_dict[4]['title'], "Section 1-2")
        self.assertEqual(res_dict[5]['title'], "Section 2")
        self.assertEqual(res_dict[6]['title'], "Section 2-1")                        
        self.assertEqual(res_dict[7]['title'], "Section 2-2") 

        self.assertEqual(res_dict[0]['number'], "1")
        self.assertEqual(res_dict[1]['number'], "1-1")
        self.assertEqual(res_dict[2]['number'], "1-2")
        self.assertEqual(res_dict[3]['number'], "1-3")
        self.assertEqual(res_dict[4]['number'], "1-4")
        self.assertEqual(res_dict[5]['number'], "2")
        self.assertEqual(res_dict[6]['number'], "2-1")
        self.assertEqual(res_dict[7]['number'], "2-2")

        # reset
        for copied_elem_info in copied_elem_infos:
            self.delete_element(procedure_url, copied_elem_info['elem_id'], code_expected=200)        

    def test_copy_element_across_procedures(self):
        logger.debug('test_copy_across_procedures')

        source_id_dict = self.create_procedure_example()
        source_procedure_url = source_id_dict['procedure_url']         
        source_procedure_id = source_id_dict['procedure_id']   
        source_version_id = source_id_dict['version_id']         
        source_section_1_id = source_id_dict['section_1_id'] 
        source_section_1_1_id = source_id_dict['section_1_1_id']    
        source_section_1_2_id = source_id_dict['section_1_2_id']    
        source_section_2_id = source_id_dict['section_2_id']
        source_section_2_1_id = source_id_dict['section_2_1_id']
        source_section_2_2_id = source_id_dict['section_2_2_id']  

        target_id_dict = self.create_procedure_example()
        target_procedure_url = target_id_dict['procedure_url']         
        target_procedure_id = target_id_dict['procedure_id']
        target_version_id = target_id_dict['version_id']           
        target_section_1_id = target_id_dict['section_1_id'] 
        target_section_1_1_id = target_id_dict['section_1_1_id']    
        target_section_1_2_id = target_id_dict['section_1_2_id']    
        target_section_2_id = target_id_dict['section_2_id']
        target_section_2_1_id = target_id_dict['section_2_1_id']
        target_section_2_2_id = target_id_dict['section_2_2_id']  

        self.assertNotEqual(source_version_id, target_version_id)

        res_dict = self.copy_element_across(target_procedure_url, source_section_1_id, target_section_1_id, 'SIBLING', 
            None, source_procedure_id, 0)
        logger.debug('element copied res_dict: %s', json.dumps(res_dict, indent=4))            

        added_elements = res_dict['elements']
        self.assertEqual(len(added_elements), 3)

        for added_element in added_elements:
            self.assertEqual(added_element['procedure_id'], target_procedure_id)

        numbers = res_dict['numbers']
        self.assertEqual(len(numbers), 6)

        self.assertEqual(numbers[0]['number'], '2')
        self.assertEqual(numbers[1]['number'], '2-1')
        self.assertEqual(numbers[2]['number'], '2-2')
        self.assertEqual(numbers[3]['number'], '3')
        self.assertEqual(numbers[4]['number'], '3-1')
        self.assertEqual(numbers[5]['number'], '3-2')        

        elements = self.get_elements(target_procedure_url)
        logger.debug('after copy elements elements= %s', json.dumps(elements, indent=4))   

        self.assertEqual(len(elements), 9)

        for element in elements:
            self.assertEqual(element['procedure_id'], target_procedure_id)
            self.assertEqual(element['version_id'], target_version_id)    

        self.assertEqual(elements[0]['number'], '1')
        self.assertEqual(elements[1]['number'], '1-1')
        self.assertEqual(elements[2]['number'], '1-2')
        self.assertEqual(elements[3]['number'], '2')
        self.assertEqual(elements[4]['number'], '2-1')
        self.assertEqual(elements[5]['number'], '2-2')
        self.assertEqual(elements[6]['number'], '3')
        self.assertEqual(elements[7]['number'], '3-1')
        self.assertEqual(elements[8]['number'], '3-2')   
        
        # Test the behavior of comment for copy operation

        # add version
        version_dict = self.create_procedure_version(source_procedure_id, 'First version', 'hongmank')
        self.assertEqual(version_dict['version'], 1)
        
        res_dict = self.get_version_elements(procedure_id=source_procedure_id, version=1)
        logger.debug('copied elements res_dict: %s', json.dumps(res_dict, indent=4))     
        
        source_section_id_v1_1 = res_dict[0]['elem_id']
        procedure_version_url = shared_dict['host'] + '/procedures/' + source_procedure_id + '/versions/1'
        logger.debug('procedure_version_url: %s', procedure_version_url)

        # only generic comment is allowed for procedure
        res_dict = self.add_conversation(procedure_version_url, source_section_id_v1_1, {'type': 'DATA_REVIEW_COMMENT'}, code_expected=400)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        
        # Add comment to section                
        content = 'This is the first comment for the section'
        res_dict = self.add_conversation(procedure_version_url, source_section_id_v1_1, {'type': 'COMMENT'})
        conversation_id = res_dict['conversation_id']
        comment = res_dict['comments'][0]
        comment_id = comment['comment_id']        
        res_dict = self.update_comment(procedure_version_url, source_section_id_v1_1, conversation_id, comment_id, content)
    
        # copy
        res_dict = self.copy_element_across(target_procedure_url, source_section_id_v1_1, '-1', 'CHILD', 
            None, source_procedure_id, 1)
        logger.debug('element copied res_dict: %s', json.dumps(res_dict, indent=4))  
        
        res_dict = self.get_version_elements(procedure_id=target_procedure_id, version=0)
        logger.debug('copied elements res_dict: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict[0]['conversations']), 0)
        self.assertEqual('comments' in res_dict[0], False)            

    def test_copy_elements_across_procedures(self):
        logger.debug('test_copy_across_procedures')

        source_id_dict = self.create_procedure_example()
        source_procedure_url = source_id_dict['procedure_url']         
        source_procedure_id = source_id_dict['procedure_id']   
        source_version_id = source_id_dict['version_id']         
        source_section_1_id = source_id_dict['section_1_id'] 
        source_section_1_1_id = source_id_dict['section_1_1_id']    
        source_section_1_2_id = source_id_dict['section_1_2_id']    
        source_section_2_id = source_id_dict['section_2_id']
        source_section_2_1_id = source_id_dict['section_2_1_id']
        source_section_2_2_id = source_id_dict['section_2_2_id']  

        target_id_dict = self.create_procedure_example()
        target_procedure_url = target_id_dict['procedure_url']         
        target_procedure_id = target_id_dict['procedure_id']
        target_version_id = target_id_dict['version_id']           
        target_section_1_id = target_id_dict['section_1_id'] 
        target_section_1_1_id = target_id_dict['section_1_1_id']    
        target_section_1_2_id = target_id_dict['section_1_2_id']    
        target_section_2_id = target_id_dict['section_2_id']
        target_section_2_1_id = target_id_dict['section_2_1_id']
        target_section_2_2_id = target_id_dict['section_2_2_id']  

        self.assertNotEqual(source_version_id, target_version_id)

        res_dict = self.copy_elements_across(target_procedure_url, [source_section_1_2_id, source_section_2_id], target_section_1_id, 'SIBLING', 
            None, source_procedure_id, 0)
        logger.debug('element copied res_dict: %s', json.dumps(res_dict, indent=4))            

        added_elements = res_dict['elements']
        self.assertEqual(len(added_elements), 4)

        for added_element in added_elements:
            self.assertEqual(added_element['procedure_id'], target_procedure_id)

        numbers = res_dict['numbers']
        self.assertEqual(len(numbers), 7)

        self.assertEqual(numbers[0]['number'], '2')
        self.assertEqual(numbers[1]['number'], '3')
        self.assertEqual(numbers[2]['number'], '3-1')
        self.assertEqual(numbers[3]['number'], '3-2')
        self.assertEqual(numbers[4]['number'], '4')
        self.assertEqual(numbers[5]['number'], '4-1')
        self.assertEqual(numbers[6]['number'], '4-2')        

        elements = self.get_elements(target_procedure_url)
        logger.debug('after copy elements elements= %s', json.dumps(elements, indent=4))   

        self.assertEqual(len(elements), 10)

        for element in elements:
            self.assertEqual(element['procedure_id'], target_procedure_id)
            self.assertEqual(element['version_id'], target_version_id)    

        self.assertEqual(elements[0]['number'], '1')
        self.assertEqual(elements[1]['number'], '1-1')
        self.assertEqual(elements[2]['number'], '1-2')
        self.assertEqual(elements[3]['number'], '2')
        self.assertEqual(elements[4]['number'], '3')
        self.assertEqual(elements[5]['number'], '3-1')
        self.assertEqual(elements[6]['number'], '3-2')
        self.assertEqual(elements[7]['number'], '4')
        self.assertEqual(elements[8]['number'], '4-1')
        self.assertEqual(elements[9]['number'], '4-2') 
        
    def test_get_procedure_versions(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')
        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        rand_1 = random_string()
        description_1 = 'description_' + rand_1
        institutional_release_id_1 = 'institutional_release_id_1_' + rand_1
        self.create_procedure_version(procedure_id, description_1)
        self.update_procedure_version(procedure_id, 1, {'institutional_release_id': institutional_release_id_1})
        self.update_procedure_version_status(procedure_id, 1, {'action': 'RELEASE'})

        rand_2 = random_string()
        description_2 = 'description_' + rand_2
        institutional_release_id_2 = 'institutional_release_id_2_' + rand_2
        author_2 = 'author_' + rand_2
        self.create_procedure_version(procedure_id, description_2)
        self.update_procedure_version(procedure_id, 2, {'institutional_release_id': institutional_release_id_2})
        self.update_procedure_version_status(procedure_id, 2, {'action': 'RELEASE'})

        rand_3 = random_string()
        description_3 = 'description_' + rand_3
        institutional_release_id_3 = 'institutional_release_id_3_' + rand_3
        self.create_procedure_version(procedure_id, description_3)
        self.update_procedure_version(procedure_id, 3, {'institutional_release_id': institutional_release_id_3})
        self.update_procedure_version_status(procedure_id, 3, {'action': 'RELEASE'})

        rand_4 = random_string()
        description_4 = 'description_' + rand_4
        institutional_release_id_4 = 'institutional_release_id_4_' + rand_4
        self.create_procedure_version(procedure_id, description_4)
        self.update_procedure_version(procedure_id, 4, {'institutional_release_id': institutional_release_id_4})
        self.update_procedure_version_status(procedure_id, 4, {'action': 'RELEASE'})

        url = '{0}/procedures/{1}/versions'.format(shared_dict['host'], procedure_id)
        params = {'limit': 10000}
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        venue_count = len(res_dict)
        self.assertGreater(len(res_dict), 4)    # including the working copy

        # check for the default sort
        self.assertEqual(res_dict[0]['version_description'], description_4)

        # filter by title
        params = {'version_description': rand_1}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['version_description'], description_1)

        # filter by author
        # params = {'version_author': rand_2}
        # result = requests.get(url, params=params, headers=shared_dict['headers'])
        # self.assertEqual(result.status_code, 200)
        # res_dict = json.loads(result.text)
        # self.assertEqual(len(res_dict), 1)
        # self.assertEqual(res_dict[0]['version_author'], author_2)

        # filter by institutional_release_id
        params = {'institutional_release_id': rand_2}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['version_description'], description_2)

        # filter by versioned
        params = {'status': 'VERSIONED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        logger.debug('versions: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 0)
        
        # filter by submitted
        params = {'status': 'SUBMITTED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        logger.debug('versions: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 0)

        # filter by approved
        params = {'status': 'APPROVED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        logger.debug('versions: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 0)        

        # filter by released
        params = {'status': 'RELEASED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 4)

        self.update_procedure_version_status(procedure_id, 4, {'action': 'UNRELEASE'})

        params = {'status': 'RELEASED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 3)

        self.update_procedure_version(procedure_id, 4, {'institutional_release_id': 'r4'})
        self.update_procedure_version_status(procedure_id, 4, {'action': 'RELEASE'})

        params = {'status': 'RELEASED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 4)

        # filter by obsolete
        params = {'status': 'OBSOLETE'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 0)

        self.update_procedure_version_status(procedure_id, 3, {'action': 'OBSOLETE'})

        params = {'status': 'OBSOLETE'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 1)

        self.update_procedure_version_status(procedure_id, 3, {'action': 'UNOBSOLETE'})

        params = {'status': 'OBSOLETE'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 0)

        # check for the sort
        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'DESC'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[0]['version_description'], description_4)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['version_description'], description_4)
        self.assertEqual(res_dict[-2]['version_description'], description_3)
        self.assertEqual(res_dict[-3]['version_description'], description_2)
        self.assertEqual(res_dict[-4]['version_description'], description_1)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'TIME_VERSIONED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['version_description'], description_4)
        self.assertEqual(res_dict[-2]['version_description'], description_3)
        self.assertEqual(res_dict[-3]['version_description'], description_2)
        self.assertEqual(res_dict[-4]['version_description'], description_1)
        self.assertEqual(res_dict[-5]['version_description'], 'Working Version')

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'DESC', 'sort_by': 'TIME_VERSIONED'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['version_description'], 'Working Version')
        self.assertEqual(res_dict[-2]['version_description'], description_1)
        self.assertEqual(res_dict[-3]['version_description'], description_2)
        self.assertEqual(res_dict[-4]['version_description'], description_3)
        self.assertEqual(res_dict[-5]['version_description'], description_4)
        total_count = len(res_dict)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'INSTITUTIONAL_RELEASE_ID'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict[-1]['version_description'], description_4)
        self.assertEqual(res_dict[-2]['version_description'], description_3)
        self.assertEqual(res_dict[-3]['version_description'], description_2)
        self.assertEqual(res_dict[-4]['version_description'], description_1)
        self.assertEqual(res_dict[-5]['version_description'], 'Working Version')

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'VERSION'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 5)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'API_VERSION'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 5)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'FLIGHT_DICTIONARY_VERSION'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 5)

        params = {'limit': 10000, 'procedure_id': procedure_id, 'sort': 'ASC', 'sort_by': 'SSE_DICTIONARY_VERSION'}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 5)


        # offset and limit

        params = {'limit': 2}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(int(result.headers['x-total-count']), total_count)

        params = {'offset': 1, 'limit': 2}
        result = requests.get(url, params=params, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(int(result.headers['x-total-count']), total_count)
        self.assertEqual(res_dict[0]['version_description'], description_3)
        self.assertEqual(res_dict[1]['version_description'], description_2)

    def test_procedure_version(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            description='Paragraph A')

        paragraph_a = res['elem']
        paragraph_a_id = paragraph_a['elem_id']

        # add step

        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=section_1_id,
            level='CHILD')

        step_1_1 = res['elem']
        step_1_1_id = step_1_1['elem_id']

        # add version
        version_dict = self.create_procedure_version(procedure_id, 'First version')
        self.assertEqual(version_dict['version'], 1)

        # add another version
        version_dict = self.create_procedure_version(procedure_id, 'Second version')
        self.assertEqual(version_dict['version'], 2)

        # check version 1
        version_dict_1 = self.get_procedure_version(procedure_id, 1)
        self.assertEqual(version_dict_1['version'], 1)

        structure_version_1 = self.get_version_structure(procedure_id, 1)

        self.assertEqual(structure_version_1['children'][0]['children'][0]['step_type'], 'MANUAL_INPUT')
        self.assertEqual(structure_version_1['children'][0]['children'][0]['number'], '1-1')
        self.assertEqual(structure_version_1['children'][0]['children'][1]['description'], 'Paragraph A')

        elements_version_1 = self.get_version_elements(procedure_id, 1)
        self.assertEqual(len(elements_version_1), 3)
        self.assertEqual(elements_version_1[0]['number'], '1')
        self.assertEqual(elements_version_1[1]['number'], '1-1')
        
        # Cannot modify a versioned element
        res_dict = self.update_element(procedure_url, elements_version_1[1]['elem_id'], {'title': 'modified title'}, code_expected=400)
        self.assertEqual(res_dict['details'][0], 'Cannot modify element of versioned procedure')
                
        # Cannot delete a versioned element
        res_dict = self.delete_element(procedure_url, elements_version_1[1]['elem_id'], code_expected=400)    
        self.assertEqual(res_dict['details'][0], 'Cannot delete element of versioned procedure')        

        # check version 2
        version_dict_2 = self.get_procedure_version(procedure_id, 2)
        self.assertEqual(version_dict_2['version'], 2)

        structure_version_2 = self.get_version_structure(procedure_id, 2)

        self.assertEqual(structure_version_2['children'][0]['children'][0]['step_type'], 'MANUAL_INPUT')
        self.assertEqual(structure_version_2['children'][0]['children'][0]['number'], '1-1')
        self.assertEqual(structure_version_2['children'][0]['children'][1]['description'], 'Paragraph A')
        
    def test_procedure_version_status(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure', '', 'hongmank')
        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        rand_1 = random_string()
        description_1 = 'description_' + rand_1
        institutional_release_id_1 = 'institutional_release_id_1_' + rand_1
        self.create_procedure_version(procedure_id, description_1, 'hongmank')

        # test if the meta data of working version is copied over
        version_dict = self.get_procedure_version(procedure_id, 1)
        version = version_dict['version']
        self.assertEqual(version_dict['status'], 'VERSIONED')

        # submit
        data = {'action': 'SUBMIT'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertEqual(res_dict['time_approved'], '')  
        self.assertEqual(res_dict['time_released'], '')  
        self.assertEqual(res_dict['institutional_release_id'], '')
        self.assertEqual(res_dict['status'], 'SUBMITTED')
        
        # approve
        data = {'action': 'APPROVE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertTrue(len(res_dict['time_approved']) > 0)
        self.assertEqual(res_dict['time_released'], '')  
        self.assertEqual(res_dict['institutional_release_id'], '')
        self.assertEqual(res_dict['status'], 'APPROVED')
        
        # release
        res_dict = self.update_procedure_version(procedure_id, version, {'institutional_release_id': 'Initial Release'})
        data = {'action': 'RELEASE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertTrue(len(res_dict['time_approved']) > 0)
        self.assertTrue(len(res_dict['time_released']) > 0)
        self.assertEqual(res_dict['institutional_release_id'], 'Initial Release')
        self.assertEqual(res_dict['status'], 'RELEASED')
        
        # obsolete
        data = {'action': 'OBSOLETE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertTrue(len(res_dict['time_approved']) > 0)
        self.assertTrue(len(res_dict['time_released']) > 0)
        self.assertEqual(res_dict['institutional_release_id'], 'Initial Release')
        self.assertEqual(res_dict['status'], 'OBSOLETE')        
        
        # unobsolete
        data = {'action': 'UNOBSOLETE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertTrue(len(res_dict['time_approved']) > 0)
        self.assertTrue(len(res_dict['time_released']) > 0)
        self.assertEqual(res_dict['status'], 'RELEASED')
        
        # unrelease
        data = {'action': 'UNRELEASE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertTrue(len(res_dict['time_approved']) > 0)
        self.assertEqual(res_dict['time_released'], '')  
        self.assertEqual(res_dict['institutional_release_id'], 'Initial Release')
        self.assertEqual(res_dict['status'], 'APPROVED')

        # unapprove
        data = {'action': 'UNAPPROVE'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertTrue(len(res_dict['time_submitted']) > 0)
        self.assertEqual(res_dict['time_approved'], '')
        self.assertEqual(res_dict['time_released'], '')  
        self.assertEqual(res_dict['institutional_release_id'], 'Initial Release')
        self.assertEqual(res_dict['status'], 'SUBMITTED')

        # unsubmit
        data = {'action': 'UNSUBMIT'}
        res_dict = self.update_procedure_version_status(procedure_id, version, data)
        self.assertEqual(res_dict['time_submitted'], '') 
        self.assertEqual(res_dict['time_approved'], '')  
        self.assertEqual(res_dict['time_released'], '')  
        self.assertEqual(res_dict['institutional_release_id'], 'Initial Release')
        self.assertEqual(res_dict['status'], 'VERSIONED')        

    def test_procedure_tags(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure', '', 'hongmank')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            description='Paragraph A')         

        paragraph_a = res['elem']
        paragraph_a_id = paragraph_a['elem_id']
        
        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=paragraph_a_id,
            level='SIBLING',
            description='Paragraph B')   
        paragraph_b = res['elem']
        paragraph_b_id = paragraph_b['elem_id']        
        
        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='SIBLING',
            description='Paragraph C')   
        paragraph_c = res['elem']
        paragraph_c_id = paragraph_c['elem_id']                
            
        ### Tags            
        tag1 = {
            'name': 'Tag 1',
            'description': 'First Tag'
        }
        tag2 = {
            'name': 'Tag 2',
            'description': 'Second Tag'
        }        
        tag3 = {
            'name': 'Tag 3',
            'description': 'Third Tag'
        }        
        
        res_dict = self.procedure_create_tag(procedure_id, tag1)
        logger.debug('procedure_create_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['name'], tag1['name'])
        self.assertEqual(res_dict[0]['description'], tag1['description'])
        self.assertTrue(len(res_dict[0]['tag_id']) > 0)
        tag_id_1 = res_dict[0]['tag_id']
        
        res_dict = self.procedure_create_tag(procedure_id, tag2)
        logger.debug('procedure_create_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(res_dict[0]['name'], tag1['name'])
        self.assertEqual(res_dict[0]['description'], tag1['description'])
        self.assertTrue(len(res_dict[0]['tag_id']) > 0)
        self.assertEqual(res_dict[1]['name'], tag2['name'])
        self.assertEqual(res_dict[1]['description'], tag2['description'])
        self.assertTrue(len(res_dict[1]['tag_id']) > 0)
        self.assertEqual(res_dict[0]['tag_id'], tag_id_1)
        tag_id_2 = res_dict[1]['tag_id']
        
        res_dict = self.procedure_create_tag(procedure_id, tag3)
        logger.debug('procedure_create_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['name'], tag1['name'])
        self.assertEqual(res_dict[0]['description'], tag1['description'])
        self.assertTrue(len(res_dict[0]['tag_id']) > 0)
        self.assertEqual(res_dict[1]['name'], tag2['name'])
        self.assertEqual(res_dict[1]['description'], tag2['description'])
        self.assertTrue(len(res_dict[1]['tag_id']) > 0)            
        self.assertEqual(res_dict[2]['name'], tag3['name'])
        self.assertEqual(res_dict[2]['description'], tag3['description'])
        self.assertTrue(len(res_dict[2]['tag_id']) > 0)
        tag_id_3 = res_dict[2]['tag_id']
        
        tag2b = {
            'name': 'Tag 2 B',
            'description': 'Updated description'            
        }
        res_dict = self.procedure_update_tag(procedure_id, tag_id_2, tag2b)
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['name'], tag1['name'])
        self.assertEqual(res_dict[0]['description'], tag1['description'])
        self.assertTrue(len(res_dict[0]['tag_id']) > 0)
        self.assertEqual(res_dict[1]['name'], tag2b['name'])
        self.assertEqual(res_dict[1]['description'], tag2b['description'])
        self.assertTrue(len(res_dict[1]['tag_id']) > 0)            
        self.assertEqual(res_dict[2]['name'], tag3['name'])
        self.assertEqual(res_dict[2]['description'], tag3['description'])
        self.assertTrue(len(res_dict[2]['tag_id']) > 0)
        
        res_dict = self.procedure_delete_tag(procedure_id, tag_id_2)
        logger.debug('procedure_delete_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict['tags']), 2)
        self.assertEqual(len(res_dict['elems']), 0)
        self.assertEqual(res_dict['tags'][0]['name'], tag1['name'])
        self.assertEqual(res_dict['tags'][0]['description'], tag1['description'])
        self.assertEqual(res_dict['tags'][0]['tag_id'], tag_id_1)     
        self.assertEqual(res_dict['tags'][1]['name'], tag3['name'])
        self.assertEqual(res_dict['tags'][1]['description'], tag3['description'])
        self.assertEqual(res_dict['tags'][1]['tag_id'], tag_id_3)

        # tagging and untagging elements
        res_dict = self.procedure_element_apply_tag(procedure_id, paragraph_a_id, tag_id_1)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(res_dict[0]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_1)
        
        res_dict = self.procedure_element_remove_tag(procedure_id, paragraph_a_id, tag_id_1)
        logger.debug('procedure_element_remove_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 1)   
        self.assertEqual(res_dict[0]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 0)
        
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_1)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[2]['elem_id'], paragraph_b_id)
        self.assertEqual(len(res_dict[2]['tag_ids']), 1)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1)        
        
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_2, 400)
        
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_3)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 2)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[0]['tag_ids'][1], tag_id_3)
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 2)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[1]['tag_ids'][1], tag_id_3)   
        self.assertEqual(res_dict[2]['elem_id'], paragraph_b_id)
        self.assertEqual(len(res_dict[2]['tag_ids']), 2)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[2]['tag_ids'][1], tag_id_3)           
        
        # applying a tag again should result in no change
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_3)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 0)
        
        res_dict = self.procedure_element_remove_tag(procedure_id, paragraph_a_id, tag_id_1)
        logger.debug('procedure_element_remove_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_3)
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_3)   
        
        res_dict = self.procedure_element_remove_tag(procedure_id, section_1_id, tag_id_3)
        logger.debug('procedure_element_remove_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 0)     
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 0)
        self.assertEqual(res_dict[2]['elem_id'], paragraph_b_id)
        self.assertEqual(len(res_dict[2]['tag_ids']), 1)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1)           
        
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_1)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_1)   
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1)    
        
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_3)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 3)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 2)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[0]['tag_ids'][1], tag_id_3)
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 2)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[1]['tag_ids'][1], tag_id_3)              
        self.assertEqual(res_dict[2]['elem_id'], paragraph_b_id)
        self.assertEqual(len(res_dict[2]['tag_ids']), 2)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1)
        self.assertEqual(res_dict[2]['tag_ids'][1], tag_id_3)     
        
        res_dict = self.procedure_element_remove_tag(procedure_id, paragraph_a_id, tag_id_1)
        logger.debug('procedure_element_apply_tag res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(res_dict[0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_3)
        self.assertEqual(res_dict[1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict[1]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_3)               
        
        ### create a version
        version_dict = self.create_procedure_version(procedure_id, 'First version', 'hongmank')
        logger.debug('create_procedure_version version_dict: %s', json.dumps(version_dict, indent=4))
        self.assertEqual(len(version_dict['tags']), 2)
        self.assertNotEqual(version_dict['tags'][0]['tag_id'], tag_id_1)
        self.assertNotEqual(version_dict['tags'][1]['tag_id'], tag_id_3)
        
        tag_id_1_v1 = version_dict['tags'][0]['tag_id']
        tag_id_3_v1 = version_dict['tags'][1]['tag_id']
        
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        logger.debug('elements: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 4)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[0]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(len(res_dict[1]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_3_v1)   
        self.assertEqual(len(res_dict[2]['tag_ids']), 2)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1_v1)
        self.assertEqual(res_dict[2]['tag_ids'][1], tag_id_3_v1)
        self.assertEqual(len(res_dict[3]['tag_ids']), 0)  
        
        outline_elems = self.get_outline(procedure_url, 1)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['selected'], False)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(len(outline_elems[1]['tag_ids']), 1)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(outline_elems[1]['selected'], False)
        self.assertEqual(len(outline_elems[2]['tag_ids']), 2)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v1)
        self.assertEqual(outline_elems[2]['tag_ids'][1], tag_id_3_v1)
        self.assertEqual(outline_elems[2]['selected'], False)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)      
        
        tag_ids = [tag_id_1_v1]
        outline_elems = self.get_outline(procedure_url, 1, tag_ids)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(outline_elems[0]['selected'], False)        
        self.assertEqual(len(outline_elems[1]['tag_ids']), 1)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_3_v1)  
        self.assertEqual(outline_elems[1]['selected'], False)        
        self.assertEqual(len(outline_elems[2]['tag_ids']), 2)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v1)
        self.assertEqual(outline_elems[2]['tag_ids'][1], tag_id_3_v1)
        self.assertEqual(outline_elems[2]['selected'], False)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)     
        
        tag_ids = [tag_id_3_v1]
        outline_elems = self.get_outline(procedure_url, 1, tag_ids)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(outline_elems[0]['selected'], True)        
        self.assertEqual(len(outline_elems[1]['tag_ids']), 1)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_3_v1)  
        self.assertEqual(outline_elems[1]['selected'], True)        
        self.assertEqual(len(outline_elems[2]['tag_ids']), 2)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v1)
        self.assertEqual(outline_elems[2]['tag_ids'][1], tag_id_3_v1)
        self.assertEqual(outline_elems[2]['selected'], False)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)               
        
        tag_ids = [tag_id_1_v1, tag_id_3_v1]
        outline_elems = self.get_outline(procedure_url, 1, tag_ids)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_3_v1)
        self.assertEqual(outline_elems[0]['selected'], True)
        self.assertEqual(len(outline_elems[1]['tag_ids']), 1)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_3_v1)  
        self.assertEqual(outline_elems[1]['selected'], True)
        self.assertEqual(len(outline_elems[2]['tag_ids']), 2)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v1)
        self.assertEqual(outline_elems[2]['tag_ids'][1], tag_id_3_v1)     
        self.assertEqual(outline_elems[2]['selected'], True)        
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)       
        
        ## Tag/untag elements again
        res_dict = self.procedure_element_remove_tag(procedure_id, section_1_id, tag_id_1) 
        res_dict = self.procedure_element_remove_tag(procedure_id, section_1_id, tag_id_3) 
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_1)
        res_dict = self.procedure_element_apply_tag(procedure_id, section_1_id, tag_id_3)
        res_dict = self.procedure_element_remove_tag(procedure_id, paragraph_b_id, tag_id_3)      
       
        version_dict = self.create_procedure_version(procedure_id, 'Second version', 'hongmank')
        logger.debug('create_procedure_version version_dict: %s', json.dumps(version_dict, indent=4))
        self.assertEqual(len(version_dict['tags']), 2)
        self.assertNotEqual(version_dict['tags'][0]['tag_id'], tag_id_1)
        self.assertNotEqual(version_dict['tags'][1]['tag_id'], tag_id_3) 
        
        tag_id_1_v2 = version_dict['tags'][0]['tag_id']
        tag_id_3_v2 = version_dict['tags'][1]['tag_id']        
        
        # Check outline      
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=2)
        logger.debug('elements: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(len(res_dict), 4)
        self.assertEqual(len(res_dict[0]['tag_ids']), 1)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(len(res_dict[1]['tag_ids']), 2)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(res_dict[1]['tag_ids'][0], tag_id_1_v2)   
        self.assertEqual(len(res_dict[2]['tag_ids']), 1)
        self.assertEqual(res_dict[2]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(len(res_dict[3]['tag_ids']), 0)  
        
        outline_elems = self.get_outline(procedure_url, 2)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[0]['selected'], False)
        self.assertEqual(len(outline_elems[1]['tag_ids']), 2)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[1]['tag_ids'][1], tag_id_3_v2)
        self.assertEqual(outline_elems[1]['selected'], False)
        self.assertEqual(len(outline_elems[2]['tag_ids']), 1)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[2]['selected'], False)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)      
        
        tag_ids = [tag_id_1_v2]
        outline_elems = self.get_outline(procedure_url, 2, tag_ids)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[0]['selected'], True)
        self.assertEqual(len(outline_elems[1]['tag_ids']), 2)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[1]['tag_ids'][1], tag_id_3_v2)
        self.assertEqual(outline_elems[1]['selected'], False)
        self.assertEqual(len(outline_elems[2]['tag_ids']), 1)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[2]['selected'], True)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)         
        
        tag_ids = [tag_id_3_v2]
        outline_elems = self.get_outline(procedure_url, 2, tag_ids)
        logger.debug('outline_elems: %s', json.dumps(outline_elems, indent=4))
        self.assertEqual(len(outline_elems), 4)
        self.assertEqual(len(outline_elems[0]['tag_ids']), 1)
        self.assertEqual(outline_elems[0]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[0]['selected'], False)
        self.assertEqual(len(outline_elems[1]['tag_ids']), 2)
        self.assertEqual(outline_elems[1]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[1]['tag_ids'][1], tag_id_3_v2)
        self.assertEqual(outline_elems[1]['selected'], False)
        self.assertEqual(len(outline_elems[2]['tag_ids']), 1)
        self.assertEqual(outline_elems[2]['tag_ids'][0], tag_id_1_v2)
        self.assertEqual(outline_elems[2]['selected'], False)
        self.assertEqual(len(outline_elems[3]['tag_ids']), 0)
        self.assertEqual(outline_elems[3]['selected'], True)                
        
        ## remove tags from working version
        res_dict = self.procedure_delete_tag(procedure_id, tag_id_1)
        logger.debug('procedure_delete_tag res_dict: %s', json.dumps(res_dict, indent=4))        
        self.assertEqual(len(res_dict['tags']), 1)
        self.assertEqual(res_dict['tags'][0]['name'], tag3['name'])
        self.assertEqual(res_dict['tags'][0]['description'], tag3['description'])
        self.assertEqual(res_dict['tags'][0]['tag_id'], tag_id_3)     
        self.assertEqual(len(res_dict['elems']), 3)
        self.assertEqual(res_dict['elems'][0]['elem_id'], section_1_id)
        self.assertEqual(len(res_dict['elems'][0]['tag_ids']), 0)
        self.assertEqual(res_dict['elems'][1]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict['elems'][1]['tag_ids']), 1)
        self.assertEqual(res_dict['elems'][1]['tag_ids'][0], tag_id_3)
        self.assertEqual(res_dict['elems'][2]['elem_id'], paragraph_b_id)
        self.assertEqual(len(res_dict['elems'][2]['tag_ids']), 0)        
        
        res_dict = self.procedure_delete_tag(procedure_id, tag_id_3)
        logger.debug('procedure_delete_tag res_dict: %s', json.dumps(res_dict, indent=4))        
        self.assertEqual(len(res_dict['tags']), 0)   
        self.assertEqual(len(res_dict['elems']), 1)
        self.assertEqual(res_dict['elems'][0]['elem_id'], paragraph_a_id)
        self.assertEqual(len(res_dict['elems'][0]['tag_ids']), 0)

    def test_comments(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure', '', 'hongmank')
        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1 source')

        section_1 = res['elem']
        section_id_1 = section_1['elem_id']
        logger.debug('working copy section_id_1: %s', section_id_1)
        
        # cannot add comment to a working copy
        procedure_version_url = shared_dict['host'] + '/procedures/' + procedure_id + '/versions/0'
        res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'COMMENT'}, code_expected=400)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        # add version
        version_dict = self.create_procedure_version(procedure_id, 'First version', 'hongmank')
        self.assertEqual(version_dict['version'], 1)
        
        procedure_version_url = shared_dict['host'] + '/procedures/' + procedure_id + '/versions/1'
        logger.debug('procedure_version_url: %s', procedure_version_url)
                
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        logger.debug('elements: %s', json.dumps(res_dict, indent=4))

        self.assertEqual(len(res_dict), 1)
        section_id_1 = res_dict[0]['elem_id']
        logger.debug('version 1 section_id_1: %s', section_id_1)
        
        # only generic comment is allowed for procedure
        res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'DATA_REVIEW_COMMENT'}, code_expected=400)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))        

        # Add comment to section
        content1 = 'This is the first comment for the section'
        res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'COMMENT'})
        conversation_id_1 = res_dict['conversation_id']
        # should have an empty comment
        self.assertEqual(len(res_dict['comments']), 1)
        comment_1 = res_dict['comments'][0]
        comment_id_1 = comment_1['comment_id']
        time_updated_1 = comment_1['time_updated']
        self.assertEqual(comment_1['content'], '')
        self.assertEqual('type' in comment_1, False)
        self.assertTrue(len(comment_1['user_name']) > 0)     
        
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        logger.debug('elements: %s', json.dumps(res_dict, indent=4))
        
        res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1, content1)
        self.assertEqual(res_dict['content'], content1)
        
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        logger.debug('elements: %s', json.dumps(res_dict, indent=4))

        time.sleep(0.01)

        # update comment
        content1b = 'This is the first comment for the section and updated'

        res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1, content1b)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(res_dict['content'], content1b)        
        time_updated_1b = res_dict['time_updated']      
        self.assertGreater(time_updated_1b, time_updated_1)   
        self.assertTrue(len(res_dict['user_name']) > 0)        

        # set it back
        res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1, content1)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        self.assertEqual(res_dict['content'], content1)                   

        # check the section
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        section_dict = res_dict[0]
        logger.debug('section_dict: %s', json.dumps(section_dict, indent=4))
        self.assertEqual(len(section_dict['conversations']), 1)
        self.assertEqual(len(section_dict['conversations'][0]['comments']), 1)
        
        self.assertEqual(section_dict['conversations'][0]['comments'][0]['content'], content1)

        # Add another comment to section
        content2 = 'This is the second comment for the section'
        res_dict = self.add_comment(procedure_version_url, section_id_1, conversation_id_1, content2)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        comment_id_2 = res_dict['comment_id']
        self.assertEqual(res_dict['content'], content2)

        # check the section
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
        section_dict = res_dict[0]
        logger.debug('section_dict: %s', json.dumps(section_dict, indent=4))
        self.assertEqual(len(section_dict['conversations']), 1)
        self.assertEqual(len(section_dict['conversations'][0]['comments']), 2)        
        self.assertEqual(section_dict['conversations'][0]['comments'][0]['content'], content1)
        self.assertEqual(section_dict['conversations'][0]['comments'][1]['content'], content2)

        # get comments
        comments_dict = self.get_comments(procedure_version_url, section_id_1, conversation_id_1)
        logger.debug('comments_dict: %s', json.dumps(comments_dict, indent=4))
        self.assertEqual(len(comments_dict), 2)
        self.assertEqual(comments_dict[0]['content'], content1)
        self.assertEqual(comments_dict[1]['content'], content2)

        # get comment
        comment1_dict = self.get_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1)
        logger.debug('comment1_dict: %s', json.dumps(comment1_dict, indent=4))
        self.assertEqual(comment1_dict['content'], content1)

        # get comment
        comment2_dict = self.get_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_2)
        logger.debug('comment2_dict: %s', json.dumps(comment2_dict, indent=4))
        self.assertEqual(comment2_dict['content'], content2)

        # delete comment
        self.delete_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1)

        # delete a non-existing comment
        self.delete_comment(procedure_version_url, 'not_an_elem_id', conversation_id_1, 'not_a_comment_id', 400)

        # delete a non-existing comment
        self.delete_comment(procedure_version_url, section_id_1, conversation_id_1, 'not_a_comment_id', 400)

        # get comments
        comments_dict = self.get_comments(procedure_version_url, section_id_1, conversation_id_1)
        logger.debug('comments_dict: %s', json.dumps(comments_dict, indent=4))
        self.assertEqual(len(comments_dict), 1)
        self.assertEqual(comments_dict[0]['content'], content2)
        
        # add another conversation
        content_2_1 = 'This is the first comment of the second conversation'
        res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'COMMENT'})
        conversation_id_2 = res_dict['conversation_id']
        comment_2_1 = res_dict['comments'][0]
        comment_id_2_1 = comment_2_1['comment_id']        
         
        res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id_2, comment_id_2_1, content_2_1)
        self.assertEqual(res_dict['content'], content_2_1)         
        
        # add another comment
        content_2_2 = 'This is the second comment of the second conversation'
        res_dict = self.add_comment(procedure_version_url, section_id_1, conversation_id_2, content_2_2)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        comment_id_2_2 = res_dict['comment_id']
        self.assertEqual(res_dict['content'], content_2_2)
        
        # get conversations
        res_dict = self.get_conversations(procedure_version_url, section_id_1)
        self.assertEqual(len(res_dict), 2)
        self.assertEqual(len(res_dict[1]['comments']), 2)
        self.assertEqual(res_dict[1]['comments'][0]['content'], content_2_1)
        self.assertEqual(res_dict[1]['comments'][1]['content'], content_2_2)
        
        # get conversation
        res_dict = self.get_conversation(procedure_version_url, section_id_1, conversation_id_2)
        self.assertEqual(len(res_dict['comments']), 2)
        self.assertEqual(res_dict['comments'][0]['content'], content_2_1)
        self.assertEqual(res_dict['comments'][1]['content'], content_2_2)     
        self.assertEqual(res_dict['status'], 'UNRESOLVED') 
        self.assertEqual(res_dict['time_resolved'], '')
        self.assertEqual(res_dict['resolved_by'], '')
        
        # resolve conversation
        res_dict = self.update_conversation(procedure_version_url, section_id_1, conversation_id_2, {'status': 'RESOLVED'})
        # check conversation
        res_dict = self.get_conversation(procedure_version_url, section_id_1, conversation_id_2)
        self.assertEqual(len(res_dict['comments']), 2)
        self.assertEqual(res_dict['comments'][0]['content'], content_2_1)
        self.assertEqual(res_dict['comments'][1]['content'], content_2_2)     
        self.assertEqual(res_dict['status'], 'RESOLVED') 
        self.assertTrue(len(res_dict['time_resolved']) > 0)
        self.assertTrue(len(res_dict['resolved_by']) > 0) 
        
        # unresolve conversation
        res_dict = self.update_conversation(procedure_version_url, section_id_1, conversation_id_2, {'status': 'UNRESOLVED'})
        # check conversation
        res_dict = self.get_conversation(procedure_version_url, section_id_1, conversation_id_2)
        self.assertEqual(len(res_dict['comments']), 2)
        self.assertEqual(res_dict['comments'][0]['content'], content_2_1)
        self.assertEqual(res_dict['comments'][1]['content'], content_2_2)     
        self.assertEqual(res_dict['status'], 'UNRESOLVED') 
        self.assertEqual(res_dict['time_resolved'], '')
        self.assertEqual(res_dict['resolved_by'], '')
        
        # delete conversation
        res_dict = self.delete_conversation(procedure_version_url, section_id_1, conversation_id_1)
        
        # check conversations
        res_dict = self.get_conversations(procedure_version_url, section_id_1)
        self.assertEqual(len(res_dict), 1)
        self.assertEqual(len(res_dict[0]['comments']), 2)
        self.assertEqual(res_dict[0]['comments'][0]['content'], content_2_1)
        self.assertEqual(res_dict[0]['comments'][1]['content'], content_2_2)
        
    def test_comments_filter(self):
        
        id_dict = self.create_procedure_example()
        procedure_url = id_dict['procedure_url']         
        procedure_id = id_dict['procedure_id']
        
        version_dict = self.create_procedure_version(procedure_id, 'First version', '')
        
        procedure_version_url = shared_dict['host'] + '/procedures/' + procedure_id + '/versions/' + str(version_dict['version'])
        logger.debug('procedure_version_url: %s', procedure_version_url)        
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1)
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 6)
        
        section_id_1 = elements[0]['elem_id']
        section_id_1_1 = elements[1]['elem_id']
        section_id_1_2 = elements[2]['elem_id']
        section_id_2 = elements[3]['elem_id']
        section_id_2_1 = elements[4]['elem_id']
        section_id_2_2 = elements[5]['elem_id']   
        
        res_dict = self.add_conversation(procedure_version_url, section_id_1_1, {'type': 'COMMENT'})
        res_dict = self.add_conversation(procedure_version_url, section_id_2, {'type': 'COMMENT'})
        res_dict = self.add_conversation(procedure_version_url, section_id_2_1, {'type': 'COMMENT'})
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'comment_filter': 'ON'})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]['elem_id'], section_id_1_1)
        self.assertEqual(elements[1]['elem_id'], section_id_2)
        self.assertEqual(elements[2]['elem_id'], section_id_2_1)     
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'comment_filter': 'OFF'})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 6)
        self.assertEqual(elements[0]['elem_id'], section_id_1)
        self.assertEqual(elements[1]['elem_id'], section_id_1_1)
        self.assertEqual(elements[2]['elem_id'], section_id_1_2)    
        self.assertEqual(elements[3]['elem_id'], section_id_2)
        self.assertEqual(elements[4]['elem_id'], section_id_2_1)
        self.assertEqual(elements[5]['elem_id'], section_id_2_2)              
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'comment_filter': 'ON', 'limit': 2})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0]['elem_id'], section_id_1_1)
        self.assertEqual(elements[1]['elem_id'], section_id_2)          
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'comment_filter': 'ON', 'offset': 1, 'limit': 2})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0]['elem_id'], section_id_2)
        self.assertEqual(elements[1]['elem_id'], section_id_2_1)    
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'all_elements': 'ON', 'comment_filter': 'OFF'})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 6)
        self.assertEqual(elements[0]['elem_id'], section_id_1)
        self.assertEqual(elements[1]['elem_id'], section_id_1_1)
        self.assertEqual(elements[2]['elem_id'], section_id_1_2)    
        self.assertEqual(elements[3]['elem_id'], section_id_2)
        self.assertEqual(elements[4]['elem_id'], section_id_2_1)
        self.assertEqual(elements[5]['elem_id'], section_id_2_2)   
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'all_elements': 'ON', 'comment_filter': 'ON'})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 6)
        self.assertEqual(elements[0]['elem_id'], section_id_1)
        self.assertEqual(elements[1]['elem_id'], section_id_1_1)
        self.assertEqual(elements[2]['elem_id'], section_id_1_2)    
        self.assertEqual(elements[3]['elem_id'], section_id_2)
        self.assertEqual(elements[4]['elem_id'], section_id_2_1)
        self.assertEqual(elements[5]['elem_id'], section_id_2_2)            
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'all_elements': 'ON', 'comment_filter': 'ON', 'limit': 2})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0]['elem_id'], section_id_1)
        self.assertEqual(elements[1]['elem_id'], section_id_1_1)
        
        elements = self.get_version_elements(procedure_id=procedure_id, version=1, params={'all_elements': 'ON', 'comment_filter': 'ON', 'offset': 1, 'limit': 2})
        # logger.debug('elements: %s', json.dumps(elements, indent=4))
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements[0]['elem_id'], section_id_1_1)
        self.assertEqual(elements[1]['elem_id'], section_id_1_2)         
            
        
    def test_files(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure', '', 'hongmank')
        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1 source')

        section_1 = res['elem']
        section_id_1 = section_1['elem_id']
        logger.debug('working copy section_id_1: %s', section_id_1)
        
        # Assume that the test is running from "tests" folder
        with open('rocket.png','rb') as file:         
            files = {'file_content': file}

            file_info_1 = self.add_elem_file(procedure_url, section_id_1, files, "testfile")

            file.seek(0)
            file_info_2 = self.add_elem_file(procedure_url, section_id_1, files)

            file.seek(0)
            file_info_3 = self.add_elem_file(procedure_url, section_id_1, files)
            
            logger.debug('file_info_1: %s', json.dumps(file_info_1, indent=4))
            logger.debug('file_info_2: %s', json.dumps(file_info_2, indent=4))
            logger.debug('file_info_3: %s', json.dumps(file_info_3, indent=4))

            file_info = self.get_elem_file(procedure_url, section_id_1, file_info_1['file_id'])
            self.assertEqual(file_info, file_info_1)

            url = '{0}/procedures/{1}/elements/{2}/files'.format(shared_dict['host'], procedure_id, section_id_1)
            result = requests.get(url,
                params = {'offset': 1, 'limit' : 2},
                headers=shared_dict['headers'])
            res_dict = json.loads(result.text)
            logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
            self.assertEqual(int(result.headers['x-total-count']), 3)
            self.assertEqual(len(res_dict), 2)
            self.assertEqual(res_dict[0]['file_id'], file_info_2['file_id'])

            self.delete_elem_file(procedure_url, section_id_1, file_info_1['file_id'], 204)
            self.delete_elem_file(procedure_url, section_id_1, file_info_2['file_id'], 204)
            self.delete_elem_file(procedure_url, section_id_1, file_info_3['file_id'], 204)

            file.seek(0)
            file_info_1 = self.add_procedure_file(procedure_id, files, "testfile") 
            file.seek(0)
            file_info_2 = self.add_procedure_file(procedure_id, files)
            file.seek(0)
            file_info_3 = self.add_procedure_file(procedure_id, files)

            file_info = self.get_procedure_file(procedure_id, file_info_1['file_id'])
            self.assertEqual(file_info, file_info_1)

            url = '{0}/procedures/{1}/files'.format(shared_dict['host'], procedure_id)
            result = requests.get(url,
                params = {'offset': 1, 'limit' : 2},
                headers=shared_dict['headers'])
            res_dict = json.loads(result.text)
            self.assertEqual(int(result.headers['x-total-count']), 3)
            self.assertEqual(res_dict[0]['file_id'], file_info_2['file_id'])

            self.delete_procedure_file(procedure_id, file_info_1['file_id'], 204)
            self.delete_procedure_file(procedure_id, file_info_2['file_id'], 204)
            self.delete_procedure_file(procedure_id, file_info_3['file_id'], 204)
        
        with open('rocket.png','rb') as file:         
            files = {'file_content': file}
            
            # add version
            version_dict = self.create_procedure_version(procedure_id, 'First version', 'hongmank')
            self.assertEqual(version_dict['version'], 1)
            
            procedure_version_url = shared_dict['host'] + '/procedures/' + procedure_id + '/versions/1'
            logger.debug('procedure_version_url: %s', procedure_version_url)
                    
            res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)
            logger.debug('elements: %s', json.dumps(res_dict, indent=4))

            self.assertEqual(len(res_dict), 1)
            section_id_1 = res_dict[0]['elem_id']
            logger.debug('version 1 section_id_1: %s', section_id_1)

            # Add comment to section
            content1 = 'This is the first comment for the section'
            res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'COMMENT'})
            conversation_id = res_dict['conversation_id']
            # should have an empty comment
            self.assertEqual(len(res_dict['comments']), 1)
            comment = res_dict['comments'][0]
            comment_id = comment['comment_id']
            time_updated_1 = comment['time_updated']     
            
            res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id, comment_id, content1)
            self.assertEqual(res_dict['content'], content1)
            
            time.sleep(0.01)            

            file.seek(0)
            logger.debug(f'conversation_id : {conversation_id} comment_id: {comment_id}')
            file_info_1 = self.add_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, files, "testfile") # section_id_1, execution_id, url, code_expected, name=""
            file.seek(0)
            file_info_2 = self.add_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, files)
            file.seek(0)
            file_info_3 = self.add_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, files)

            file_info = self.get_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, file_info_1['file_id'])
            self.assertEqual(file_info, file_info_1)

            url = '{0}/procedures/{1}/versions/1/elements/{2}/conversations/{3}/comments/{4}/files'.format(shared_dict['host'],
                procedure_id, section_id_1, conversation_id, comment_id)
            result = requests.get(url,
                params = {'offset': 1, 'limit' : 2},
                headers=shared_dict['headers'])
            logger.debug(result.text)
            res_dict = json.loads(result.text)
            self.assertEqual(int(result.headers['x-total-count']), 3)
            self.assertEqual(len(res_dict), 2)
            self.assertEqual(res_dict[0]['file_id'], file_info_2['file_id'])

            self.delete_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, file_info_1['file_id'], 204)
            # self.assertEqual(os.path.isfile(file_info_1['url']), False)

            self.delete_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, file_info_2['file_id'], 204)
            # self.assertEqual(os.path.isfile(file_info_2['url']), False)

            self.delete_comment_file(procedure_version_url, section_id_1, conversation_id, comment_id, file_info_3['file_id'], 204)
            # self.assertEqual(os.path.isfile(file_info_3['url']), False)

           

    def test_procedure_export_import(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, section_1_id, file_data)    

        section_1 = self.get_procedure_section(procedure_url, section_1_id)
        description_1 = '<p>'
        for file in section_1['files']:
            file_url = file['url']
            link_segment = '''<a class=\"fr-file\" href=\"{0}\" target=\"_blank\">file</a>'''.format(file_url)
            description_1 = description_1 + link_segment

        description_1 = description_1 + '</p>'

        self.update_procedure_section(procedure_url, section_1_id, {'description': description_1})         

        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            description='Paragraph A')

        paragraph_a = res['elem']
        paragraph_a_id = paragraph_a['elem_id']

        # add step

        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=section_1_id,
            level='CHILD')

        step_1_1 = res['elem']
        step_1_1_id = step_1_1['elem_id']

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)    

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)      

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)                
  
        step_1_1 = self.get_step(base_url=procedure_url, step_type=StepTypes.MANUAL_INPUT, elem_id=step_1_1_id) 
        title_1_1 = 'First step title'
        description_1_1 = '<p>'
        for file in step_1_1['files']:
            file_url = file['url']
            link_segment = '''<a class=\"fr-file\" href=\"{0}\" target=\"_blank\">file</a>'''.format(file_url)
            description_1_1 = description_1_1 + link_segment

        description_1_1 = description_1_1 + '</p>'

        self.update_step(base_url=procedure_url, step_type=StepTypes.MANUAL_INPUT, elem_id=step_1_1_id, 
            step_dict={'description': description_1_1, 'title': title_1_1})    

        # Add VI Step
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=step_1_1_id,
            level='SIBLING')

        step_1_2 = res['elem']
        step_1_2_id = res['elem']['elem_id']

        vi_name = 'first vi'
        vi_id = 'vi_1'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name,                
                    'vi_id': vi_id,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        }              
                    ]
                }         
            ]          
        }
        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM, step_1_2_id, user_input)
        
        # Add VI Status Step
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=step_1_2_id,
            level='SIBLING')

        step_1_3 = res['elem']
        step_1_3_id = res['elem']['elem_id']

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name,                
                    'vi_id': vi_id,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        }              
                    ]
                }         
            ],
            'steps': [
                {
                    'elem_id': step_1_1_id,
                    'title': title_1_1,
                    'number': '1-1'
                }            
            ]            
        }
        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, step_1_3_id, user_input)   
            
        # add version
        version_dict = self.create_procedure_version(procedure_id, 'First version')
        self.assertEqual(version_dict['version'], 1)

        # export version 1
        url = '{0}/versions/{1}/export'.format(procedure_url, 1)
        logger.debug('export url: %s', url)

        logger.debug('headers: %s', shared_dict['headers'])
        res = requests.get(url, headers=shared_dict['headers'])

        if res.status_code != 200:
            logger.debug('res.status_code: %s', res.status_code)
            logger.debug('res.text: %s', res.text)
            self.assertEqual(res.status_code, 200)
        logger.debug('res.headers: %s', res.headers)
        zname = "procedure_version.tar.gz"
        zfile = open(zname, 'wb')
        zfile.write(res.content)
        zfile.close()

        ##### import
        rand_2 = random_string()
        title_2 = 'title_' + rand_2
        procedure_dict = self.create_procedure(title_2, 'Target procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        url = '{0}/import'.format(procedure_url)
        logger.debug('import url: %s', url)

        with open(zname,'rb') as file:         
            file_payload = {'procedure_version_file': file}        

            headers =  copy.deepcopy(shared_dict['headers'])
            headers.pop('Content-Type', None)
            # headers['content-encoding'] = 'gzip'
            logger.debug('headers: %s', headers)
            result = requests.post(url,
                headers=headers,
                files=file_payload)

            logger.info('result.text: %s', result.text)
            self.assertEqual(result.status_code, 200)
            res_dict = json.loads(result.text)
            logger.debug('result: %s', json.dumps(res_dict, indent=4))
            self.assertEqual(res_dict['procedure_info']['procedure_id'], procedure_id)
            self.assertEqual(len(res_dict['version_infos']), 1)
            self.assertEqual(res_dict['version_infos'][0]['version'], 0)
            self.assertEqual(len(res_dict['messages']), 0)

        version_dict_0 = self.get_procedure_version(procedure_id, 0)
        self.assertEqual(version_dict_0['version'], 0)
        
        structure_version_0 = self.get_version_structure(procedure_id, 0)
        self.assertEqual(structure_version_0['children'][0]['children'][0]['step_type'], 'MANUAL_INPUT')
        self.assertEqual(structure_version_0['children'][0]['children'][0]['number'], '1-1')
        self.assertEqual(structure_version_0['children'][0]['children'][3]['description'], 'Paragraph A')

        elements_version_0 = self.get_version_elements(procedure_id, 0)
        self.assertEqual(len(elements_version_0), 5)
        self.assertEqual(elements_version_0[0]['number'], '1')
        self.assertEqual(elements_version_0[0]['elem_type'], 'SECTION')
        self.assertEqual(elements_version_0[1]['number'], '1-1')
        self.assertEqual(elements_version_0[1]['elem_type'], 'STEP')
        self.assertEqual(elements_version_0[1]['step_type'], 'MANUAL_INPUT')
        self.assertNotEqual(elements_version_0[1]['elem_id'], step_1_1_id)
        self.assertEqual(elements_version_0[2]['number'], '1-2')
        self.assertEqual(elements_version_0[2]['elem_type'], 'STEP')
        self.assertEqual(elements_version_0[2]['step_type'], 'VERIFICATION_ITEM')
        self.assertEqual(len(elements_version_0[2]['authoring_user_input']['vis']), 1)
        self.assertEqual(elements_version_0[2]['authoring_user_input']['vis'][0]['vi_id'], vi_id)
        self.assertEqual(elements_version_0[2]['authoring_user_input']['vis'][0]['vi_name'], vi_name)
        self.assertEqual(elements_version_0[3]['number'], '1-3')
        self.assertEqual(elements_version_0[3]['elem_type'], 'STEP')
        self.assertEqual(elements_version_0[3]['step_type'], 'VERIFICATION_ITEM_STATUS')
        self.assertEqual(len(elements_version_0[3]['authoring_user_input']['vis']), 1)
        self.assertEqual(len(elements_version_0[3]['authoring_user_input']['steps']), 1)
        self.assertEqual(elements_version_0[3]['authoring_user_input']['vis'][0]['vi_id'], vi_id)
        self.assertEqual(elements_version_0[3]['authoring_user_input']['vis'][0]['vi_name'], vi_name)        
        self.assertEqual(elements_version_0[3]['authoring_user_input']['steps'][0]['elem_id'], elements_version_0[1]['elem_id'])
        self.assertEqual(elements_version_0[4]['number'], '1-4')
        self.assertEqual(elements_version_0[4]['elem_type'], 'PARAGRAPH')

        logger.debug('elements_version_0: %s', json.dumps(elements_version_0, indent=4))

    def compare_procedure_info(self, procedure_info, procedure_info_predict):
        self.assertEqual(procedure_info['procedure_id'], procedure_info_predict['procedure_id'])
        self.assertEqual(procedure_info['title'], procedure_info_predict['title'])
        self.assertEqual(procedure_info['description'], procedure_info_predict['description']) 
        self.assertEqual(procedure_info['institutional_id'], procedure_info_predict['institutional_id']) 
        self.assertEqual(procedure_info['author'], procedure_info_predict['author']) 

    def test_procedure_versions_export_import(self):
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')

        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section
        res = self.add_section(base_url=procedure_url,
            insert_after_id=-1,
            level='CHILD',
            description='Section 1')

        section_1 = res['elem']
        section_1_id = section_1['elem_id']

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, section_1_id, file_data)    

        section_1 = self.get_procedure_section(procedure_url, section_1_id)
        description_1 = '<p>'
        for file in section_1['files']:
            file_url = file['url']
            link_segment = '''<a class=\"fr-file\" href=\"{0}\" target=\"_blank\">file</a>'''.format(file_url)
            description_1 = description_1 + link_segment

        description_1 = description_1 + '</p>'

        self.update_procedure_section(procedure_url, section_1_id, {'description': description_1})     

        # first version
        version_dict = self.create_procedure_version(procedure_id, 'First version')
        self.assertEqual(version_dict['version'], 1)

        # add paragraph
        res = self.add_paragraph(base_url=procedure_url,
            insert_after_id=section_1_id,
            level='CHILD',
            description='Paragraph A')

        paragraph_a = res['elem']
        paragraph_a_id = paragraph_a['elem_id']

        # second version
        version_dict = self.create_procedure_version(procedure_id, 'Second version')
        self.assertEqual(version_dict['version'], 2)

        # add step
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.MANUAL_INPUT,
            insert_after_id=section_1_id,
            level='CHILD')

        step_1_1 = res['elem']
        step_1_1_id = step_1_1['elem_id']

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)    

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)      

        with open('rocket.png','rb') as file:         
            file_data = {'file_content': file}
            self.add_elem_file(procedure_url, step_1_1_id, file_data)                
  
        step_1_1 = self.get_step(base_url=procedure_url, step_type=StepTypes.MANUAL_INPUT, elem_id=step_1_1_id) 
        title_1_1 = 'First step title'
        description_1_1 = '<p>'
        for file in step_1_1['files']:
            file_url = file['url']
            link_segment = '''<a class=\"fr-file\" href=\"{0}\" target=\"_blank\">file</a>'''.format(file_url)
            description_1_1 = description_1_1 + link_segment

        description_1_1 = description_1_1 + '</p>'

        self.update_step(base_url=procedure_url, step_type=StepTypes.MANUAL_INPUT, elem_id=step_1_1_id, 
            step_dict={'description': description_1_1, 'title': title_1_1})    

        # third version
        version_dict = self.create_procedure_version(procedure_id, 'Third version')
        self.assertEqual(version_dict['version'], 3)

        # Add VI Step
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM,
            insert_after_id=step_1_1_id,
            level='SIBLING')

        step_1_2 = res['elem']
        step_1_2_id = res['elem']['elem_id']

        vi_name = 'first vi'
        vi_id = 'vi_1'  

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name,                
                    'vi_id': vi_id,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        }              
                    ]
                }         
            ]          
        }
        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM, step_1_2_id, user_input)
        
        # Add VI Status Step
        res = self.add_step(base_url=procedure_url,
            step_type=StepTypes.VERIFICATION_ITEM_STATUS,
            insert_after_id=step_1_2_id,
            level='SIBLING')

        step_1_3 = res['elem']
        step_1_3_id = res['elem']['elem_id']

        user_input = {
            'vis': [
                {
                    'vi_name': vi_name,                
                    'vi_id': vi_id,
                    'vi_owner': 'hongmank',
                    'vi_type': 'REQUIREMENT',
                    'vi_text': 'some requirement 1',
                    'vi_additional_procs': '',
                    'vas': [
                        {
                            'va_name': 'first va',
                            'va_id': 'va_1',
                            'va_poc': 'hongmank',
                            'vac_name': 'first vac',
                            'vac_id': 'vac_1'
                        }              
                    ]
                }         
            ],
            'steps': [
                {
                    'elem_id': step_1_1_id,
                    'title': title_1_1,
                    'number': '1-1'
                }            
            ]            
        }
        self.set_step_input(procedure_url, StepTypes.VERIFICATION_ITEM_STATUS, step_1_3_id, user_input)   
            
        # add version
        version_dict = self.create_procedure_version(procedure_id, 'Fourth version')
        self.assertEqual(version_dict['version'], 4)

        # export all versions
        zname = self.export_procedure_versions(procedure_id, None, False)

        # 
        procedure_info = self.get_procedure(procedure_id)
        version_info_0 = self.get_procedure_version(procedure_id, 0)
        version_info_1 = self.get_procedure_version(procedure_id, 1)
        version_info_2 = self.get_procedure_version(procedure_id, 2)
        version_info_3 = self.get_procedure_version(procedure_id, 3)
        version_info_4 = self.get_procedure_version(procedure_id, 4)

        #
        structure_version_0 = self.get_version_structure(procedure_id, 0)
        structure_version_1 = self.get_version_structure(procedure_id, 1)
        structure_version_2 = self.get_version_structure(procedure_id, 2)
        structure_version_3 = self.get_version_structure(procedure_id, 3)
        structure_version_4 = self.get_version_structure(procedure_id, 4)

        # delete
        self.delete_procedure(procedure_id)

        ##### import
        res_dict = self.import_procedure_versions(zname)

        self.assertEqual(res_dict['procedure_info']['procedure_id'], 
            procedure_info['procedure_id'])
        self.assertEqual(len(res_dict['version_infos']), 5)
        self.assertEqual(res_dict['version_infos'][0]['version'], 0)
        self.assertEqual(res_dict['version_infos'][1]['version'], 1)
        self.assertEqual(res_dict['version_infos'][2]['version'], 2)
        self.assertEqual(res_dict['version_infos'][3]['version'], 3)
        self.assertEqual(res_dict['version_infos'][4]['version'], 4)
    
        self.assertEqual(len(res_dict['messages']), 0)

        # check procedure
        procedure_info_ = self.get_procedure(procedure_id)
        self.compare_procedure_info(procedure_info_, procedure_info)

        version_info_0_ = self.get_procedure_version(procedure_id, 0)
        version_info_1_ = self.get_procedure_version(procedure_id, 1)
        version_info_2_ = self.get_procedure_version(procedure_id, 2)
        version_info_3_ = self.get_procedure_version(procedure_id, 3)
        version_info_4_ = self.get_procedure_version(procedure_id, 4)
        
        self.assertDictEqual(version_info_0, version_info_0_)
        self.assertDictEqual(version_info_1, version_info_1_)
        self.assertDictEqual(version_info_2, version_info_2_)
        self.assertDictEqual(version_info_3, version_info_3_)
        self.assertDictEqual(version_info_4, version_info_4_)

        structure_version_0_ = self.get_version_structure(procedure_id, 0)
        structure_version_1_ = self.get_version_structure(procedure_id, 1)
        structure_version_2_ = self.get_version_structure(procedure_id, 2)
        structure_version_3_ = self.get_version_structure(procedure_id, 3)
        structure_version_4_ = self.get_version_structure(procedure_id, 4)

        self.assertDictEqual(structure_version_0, structure_version_0_)
        self.assertDictEqual(structure_version_1, structure_version_1_)
        self.assertDictEqual(structure_version_2, structure_version_2_)
        self.assertDictEqual(structure_version_3, structure_version_3_)  
        self.assertDictEqual(structure_version_4, structure_version_4_)   



    def test_procedure_sections(self):
        rand = random_string()
        title = 'title_' + rand
        procedure_dict = self.create_procedure(title, 'Test procedure')
        procedure_id_1 = procedure_dict['procedure_id']
        procedure_url_1 = shared_dict['host'] + '/procedures/' + procedure_id_1

        rand = random_string()
        description = 'description_' + rand
        version_dict_1 = self.create_procedure_version(procedure_id_1, description)
        self.assertEqual(version_dict_1['version'], 1)

        rand = random_string()
        title = 'title_' + rand
        procedure_dict = self.create_procedure(title, 'Test procedure')
        procedure_id_2 = procedure_dict['procedure_id']
        procedure_url_2 = shared_dict['host'] + '/procedures/' + procedure_id_2

        rand = random_string()
        description = 'description_' + rand
        version_dict_2 = self.create_procedure_version(procedure_id_2, description)
        self.assertEqual(version_dict_2['version'], 1)

        rand = random_string()
        title = 'title_' + rand
        procedure_dict = self.create_procedure(title, 'Test procedure')
        procedure_id_3 = procedure_dict['procedure_id']
        procedure_url_3 = shared_dict['host'] + '/procedures/' + procedure_id_3

        procedure_section_data_1 = {"reference_procedure_id" : procedure_id_1, "reference_procedure_version" : version_dict_1['version'], 'description': "this is a description", 'title': 'this is a section title'}
        res = self.add_procedure_section(base_url=procedure_url_3,
            insert_after_id="-1",
            level='CHILD',
            procedure_section=procedure_section_data_1)

        procedure_section_1_id = res['elem']['elem_id']
        procedure_section_1 = self.get_procedure_section(procedure_url_3, procedure_section_1_id)

        self.assertEqual(procedure_section_1['title'], procedure_section_data_1['title'])


        procedure_section_data_2 = {"reference_procedure_id" : procedure_id_2, "reference_procedure_version" : version_dict_2['version'], 'description': "this is a description", 'title': 'this is a section title'}
        res = self.add_procedure_section(base_url=procedure_url_3,
            insert_after_id=procedure_section_1_id,
            level='SIBLING',
            procedure_section=procedure_section_data_2)

        procedure_sections = self.get_procedure_sections(procedure_url_3)
        self.assertEqual(len(procedure_sections), 2)


        procedure_section_update = {'description': "this is a NEW description"}
        self.update_procedure_section(procedure_url_3, procedure_section_1_id, procedure_section_update)

        procedure_section_1 = self.get_procedure_section(procedure_url_3, procedure_section_1_id)
        self.assertEqual(procedure_section_1['title'], procedure_section_data_1['title'])
        self.assertEqual(procedure_section_1['description'], procedure_section_update['description'])


        outline_elems = self.get_outline(procedure_url_2, 1)
        # input test
        procedure_section_input = {
            'callable': False,
            'reference_procedure_id': procedure_id_2,
            'reference_procedure_version': 1,
            'elements': outline_elems,
            'reference_procedure_version_description': '',
            'reference_procedure_institutional_id': '',
            'reference_procedure_institutional_release_id': '',            
            'reference_procedure_title': '',
            'tag_selections': []
        }

        self.update_procedure_section_input(procedure_url_3, procedure_section_1_id, procedure_section_input)

        user_input = self.get_procedure_section_input(procedure_url_3, procedure_section_1_id)

        logger.debug('procedure_section_input= %s', json.dumps(procedure_section_input, indent=4))
        logger.debug('user_input= %s', json.dumps(user_input, indent=4))

        self.assertDictEqual(procedure_section_input, user_input)
        #
        self.delete_element(procedure_url_3, procedure_section_1_id)

        procedure_sections = self.get_procedure_sections(procedure_url_3)
        self.assertEqual(len(procedure_sections), 1)


    def test_search(self):
        procedure_dict = self.create_procedure('Procedure for Search', 'Test procedure')
        procedure_id = procedure_dict['procedure_id']

        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        # Add section 1
        res_dict = self.add_section(base_url=procedure_url,
            insert_after_id='-1',
            level='',
            title='description has two abc and one Abc',
            description='Section 1')

        section_1 = res_dict['elem']
        section_id_1 = section_1['elem_id']
        self.assertEqual(res_dict['elem']['parent_id'], '')

        new_description = 'This is abc 1.\nThis is abc 2.\nThis is Abc 3.'
        self.update_section(base_url=procedure_url, elem_id=section_id_1, section_dict={'description': new_description})
        
        # Add step
        user_input = {
            "evr_name": "EVR_PROCESS_CMD",
            "evr_id": "1879113732",
            "evr_type": "SSE",
            "evr_level": "ACTIVITY_LO",
            "start_time": "0555401349",
            "end_time": "0555401369",
            "duration": "20",
            "time_type": "SCLK",
            "message_filter": "",
            "timeout": 240,
            "verification_condition": "RECORD",
            "verification_value": -1,
            "data_path": "SIDE B"
        }
        res_dict = self.add_step(base_url=procedure_url,
            step_type=StepTypes.QUERY_EVR,
            insert_after_id=section_id_1,
            level='CHILD')
        step_id_1_1 = res_dict['elem']['elem_id']

        res_dict = self.set_step_input(procedure_url, StepTypes.QUERY_EVR, step_id_1_1, user_input)
            
        # Add section 2
        res_dict = self.add_section(base_url=procedure_url,
            insert_after_id=section_id_1,
            level='SIBLING',
            description='Section 2')

        section_2 = res_dict['elem']
        section_id_2 = section_2['elem_id']
        new_description = '<h1>This is head 1: abc 1</h1><h2>This is head 1-1</h2><h1>This is head 2: abc 2</h1>'
        self.update_section(base_url=procedure_url, elem_id=section_id_2, section_dict={'description': new_description})
        
        
        # add version
        version_dict = self.create_procedure_version(procedure_id, 'First version', 'hongmank')
        procedure_version_url = shared_dict['host'] + '/procedures/' + procedure_id + '/versions/1'
        
        ### Search version 0
        url = '{0}/versions/{1}/search'.format(procedure_url, 0)

        search_input = {
            'search_for': 'abc',
            'match_case': False,
            'match_whole_word': False,
            'step_type_filters': [],
            'field_filters': ['TITLE', 'DESCRIPTION', 'COMMENT'],
            'start_elem_id': '',
            'end_elem_id': ''
        }        
        res = requests.post(url, json=search_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res= %s', json.dumps(res_dict, indent=4))
        self.assertEqual(res_dict['total_count'], 3)
        
        self.assertEqual(res_dict['matches'][0]['elem_id'], section_id_1)
        self.assertEqual(res_dict['matches'][0]['number'], '1')
        self.assertEqual(res_dict['matches'][0]['field_path'], 'title')
        self.assertEqual(res_dict['matches'][0]['is_html'], False)
        self.assertEqual(res_dict['matches'][0]['replaceable'], True)
        self.assertEqual(len(res_dict['matches'][0]['match_texts']), 2)
        
        self.assertEqual(res_dict['matches'][1]['elem_id'], section_id_1)
        self.assertEqual(res_dict['matches'][1]['number'], '1')
        self.assertEqual(res_dict['matches'][1]['field_path'], 'description')
        self.assertEqual(res_dict['matches'][1]['is_html'], True)
        self.assertEqual(res_dict['matches'][1]['replaceable'], True)
        self.assertEqual(len(res_dict['matches'][1]['match_texts']), 3)        

        self.assertEqual(res_dict['matches'][2]['elem_id'], section_id_2)
        self.assertEqual(res_dict['matches'][2]['number'], '2')
        self.assertEqual(res_dict['matches'][2]['field_path'], 'description')
        self.assertEqual(res_dict['matches'][2]['is_html'], True)
        self.assertEqual(res_dict['matches'][2]['replaceable'], True)        
        self.assertEqual(len(res_dict['matches'][2]['match_texts']), 2)  
        
        ### Replace texts in version 0
        url = '{0}/replace'.format(procedure_url)

        matches = res_dict['matches']
        replacements = []
        for match in matches:
            replacements.append({
                'elem_id': match['elem_id'],
                'number': match['number'],
                'field_path': match['field_path'],
                'is_html': match['is_html']                
            })
        
        replace_input = {
            'search_for': 'abc',
            'replace_with': 'A AND BC',
            'match_case': False,
            'match_whole_word': False,
            'replacements': replacements
        }
        logger.debug('res=%s', json.dumps(replace_input, indent=4))
        res = requests.post(url, json=replace_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res= %s', json.dumps(res_dict, indent=4))
        
        self.assertEqual(len(res_dict), 3)
        
        self.assertEqual(res_dict[0]['elem_id'], section_id_1)
        self.assertEqual(res_dict[0]['number'], '1')
        self.assertEqual(res_dict[0]['field_path'], 'title')
        self.assertEqual(res_dict[0]['field_value'], 'description has two A AND BC and one A AND BC')

        self.assertEqual(res_dict[1]['elem_id'], section_id_1)
        self.assertEqual(res_dict[1]['number'], '1')
        self.assertEqual(res_dict[1]['field_path'], 'description')
        self.assertEqual(res_dict[1]['field_value'], 'This is A AND BC 1.\nThis is A AND BC 2.\nThis is A AND BC 3.')
      
        self.assertEqual(res_dict[2]['elem_id'], section_id_2)
        self.assertEqual(res_dict[2]['number'], '2')
        self.assertEqual(res_dict[2]['field_path'], 'description')
        self.assertEqual(res_dict[2]['field_value'], '<h1>This is head 1: A AND BC 1</h1><h2>This is head 1-1</h2><h1>This is head 2: A AND BC 2</h1>')

        ### Search version 1        
        
        res_dict = self.get_version_elements(procedure_id=procedure_id, version=1)

        self.assertEqual(len(res_dict), 3)
        section_id_1 = res_dict[0]['elem_id']
        step_id_1_1 = res_dict[1]['elem_id']
        section_id_2 = res_dict[2]['elem_id']
     
        # Add comment to section
        content1 = 'This is the first abc comment for the section'
        res_dict = self.add_conversation(procedure_version_url, section_id_1, {'type': 'COMMENT'})
        conversation_id_1 = res_dict['conversation_id']
        # should have an empty comment

        comment_1 = res_dict['comments'][0]
        comment_id_1 = comment_1['comment_id']          
        res_dict = self.update_comment(procedure_version_url, section_id_1, conversation_id_1, comment_id_1, content1)

        # Add another comment to section
        content2 = '<h1>This is HTML comment</h1><p>This is a paragraph</p>'
        res_dict = self.add_comment(procedure_version_url, section_id_1, conversation_id_1, content2)
        comment_id_2 = res_dict['comment_id']      
        
        # Add another comment to section
        content3 = '<h1>This is HTML comment</h1><p>This is abc 1</p>'
        res_dict = self.add_comment(procedure_version_url, section_id_1, conversation_id_1, content3)
        comment_id_3 = res_dict['comment_id']
        
        # Search
        url = '{0}/versions/{1}/search'.format(procedure_url, 1)

        search_input = {
            'search_for': 'EVR_PROCESS_CMD',
            'match_case': False,
            'match_whole_word': False,
            'step_type_filters': [],
            'field_filters': ['DESCRIPTION', 'EVR_NAME'],
            'start_elem_id': '',
            'end_elem_id': ''
        }        
        res = requests.post(url, json=search_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res_dict= %s', json.dumps(res_dict, indent=4))
        self.assertEqual(res_dict['total_count'], 1)
        
        self.assertEqual(res_dict['matches'][0]['number'], '1-1')
        self.assertEqual(res_dict['matches'][0]['field_path'], 'authoring_user_input.evr_name')
        self.assertEqual(len(res_dict['matches'][0]['match_texts']), 1)
      
        
        # Search
        url = '{0}/versions/{1}/search'.format(procedure_url, 1)

        search_input = {
            'search_for': 'abc',
            'match_case': False,
            'match_whole_word': False,
            'step_type_filters': [],
            'field_filters': ['TITLE', 'DESCRIPTION', 'COMMENT'],
            'start_elem_id': '',
            'end_elem_id': ''
        }        
        res = requests.post(url, json=search_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res= %s', json.dumps(res_dict, indent=4))   
        self.assertEqual(res_dict['total_count'], 5)
        
        self.assertEqual(res_dict['matches'][0]['number'], '1')
        self.assertEqual(res_dict['matches'][0]['field_path'], 'title')
        self.assertEqual(len(res_dict['matches'][0]['match_texts']), 2)
        
        self.assertEqual(res_dict['matches'][1]['number'], '1')
        self.assertEqual(res_dict['matches'][1]['field_path'], 'description')
        self.assertEqual(len(res_dict['matches'][1]['match_texts']), 3)
        
        self.assertEqual(res_dict['matches'][2]['number'], '1')
        self.assertEqual(res_dict['matches'][2]['field_path'], 'conversations[0].comments[0].content')
        self.assertEqual(len(res_dict['matches'][2]['match_texts']), 1)
        
        self.assertEqual(res_dict['matches'][3]['number'], '1')
        self.assertEqual(res_dict['matches'][3]['field_path'], 'conversations[0].comments[2].content')
        self.assertEqual(len(res_dict['matches'][3]['match_texts']), 1)    

        self.assertEqual(res_dict['matches'][4]['number'], '2')
        self.assertEqual(res_dict['matches'][4]['field_path'], 'description')
        self.assertEqual(len(res_dict['matches'][4]['match_texts']), 2)          
        
        # Search within a step range
        url = '{0}/versions/{1}/search'.format(procedure_url, 1)

        search_input = {
            'search_for': 'abc',
            'match_case': False,
            'match_whole_word': False,
            'step_type_filters': [],
            'field_filters': ['TITLE', 'DESCRIPTION', 'COMMENT'],
            'start_elem_id': step_id_1_1,
            'end_elem_id': section_id_2
        }        
        res = requests.post(url, json=search_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res= %s', json.dumps(res_dict, indent=4))   
        self.assertEqual(res_dict['total_count'], 1)
        
        self.assertEqual(res_dict['matches'][0]['elem_id'], section_id_2)
        self.assertEqual(res_dict['matches'][0]['number'], '2')
        self.assertEqual(res_dict['matches'][0]['field_path'], 'description')
        self.assertEqual(len(res_dict['matches'][0]['match_texts']), 2)        
        
        # Search globally
        url = '{0}/versions/{1}/search'.format(procedure_url, 1)

        search_input = {
            'search_for': 'abc',
            'match_case': False,
            'match_whole_word': False,
            'step_type_filters': [],
            'field_filters': [],
            'start_elem_id': '',
            'end_elem_id': ''
        }        
        res = requests.post(url, json=search_input, headers=shared_dict['headers'])
        logger.debug('status_code: %s', res.status_code)
        res_dict = json.loads(res.text)
        logger.debug('res= %s', json.dumps(res_dict, indent=4))
        self.assertEqual(res_dict['total_count'], 5)         
        
        self.assertEqual(res_dict['matches'][0]['number'], '1')
        self.assertEqual(res_dict['matches'][0]['field_path'], 'title')
        self.assertEqual(len(res_dict['matches'][0]['match_texts']), 2)
        
        self.assertEqual(res_dict['matches'][1]['number'], '1')
        self.assertEqual(res_dict['matches'][1]['field_path'], 'description')
        self.assertEqual(len(res_dict['matches'][1]['match_texts']), 3)
        
        self.assertEqual(res_dict['matches'][2]['number'], '1')
        self.assertEqual(res_dict['matches'][2]['field_path'], 'conversations[0].comments[0].content')
        self.assertEqual(len(res_dict['matches'][2]['match_texts']), 1)
        
        self.assertEqual(res_dict['matches'][3]['number'], '1')
        self.assertEqual(res_dict['matches'][3]['field_path'], 'conversations[0].comments[2].content')
        self.assertEqual(len(res_dict['matches'][3]['match_texts']), 1)    

        self.assertEqual(res_dict['matches'][4]['number'], '2')
        self.assertEqual(res_dict['matches'][4]['field_path'], 'description')
        self.assertEqual(len(res_dict['matches'][4]['match_texts']), 2)          

    def test_invalid_http_method(self):
        url = shared_dict['host'] + '/procedures'
        result = requests.delete(url, headers=shared_dict['headers'])

        self.assertEqual(result.status_code, 405)

        # should not have crashed service
        # check a few times in case there are replicated services
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, 200)

    def export_procedure_versions(self, procedure_id, version, released_only, code_expected=200):
        url = '{0}/procedures/{1}/export_versions'.format(shared_dict['host'], procedure_id)
        params = {}

        if version is not None:
            params['version'] = version
        if released_only is not None:
            params['released_only'] = 'true' if released_only else 'false'

        logger.debug('headers: %s', shared_dict['headers'])
        res = requests.get(url,
            params = params,
            headers=shared_dict['headers'])
        logger.debug('res.headers: %s', res.headers)
        self.assertEqual(res.status_code, code_expected)

        zname = f'procedure-{procedure_id}.tar.gz'
        zfile = open(zname, 'wb')
        zfile.write(res.content)
        zfile.close()       

        return zname 

    def import_procedure_versions(self, zname, code_expected=200):
        url = '{0}/procedures/import'.format(shared_dict['host'])
        with open(zname,'rb') as file:         
            file_payload = {'procedure_versions_file': file}

            headers =  copy.deepcopy(shared_dict['headers'])
            headers.pop('Content-Type', None)
            # headers['content-encoding'] = 'gzip'
            logger.debug('headers: %s', headers)
            res = requests.post(url,
                headers=headers,
                files=file_payload)
            logger.debug('res.headers: %s', res.headers)
            self.assertEqual(res.status_code, code_expected)
            self.assertEqual(res.status_code, 200)
            res_dict = json.loads(res.text)
            return res_dict

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
