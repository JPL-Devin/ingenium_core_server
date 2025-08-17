import xmlrunner
import os
import sys
import unittest
import requests
import json
import random
from config import shared_dict, logger
import os.path
from os import listdir
import string
from dateutil import parser
from datetime import datetime
import math
import dateutil.tz
import time
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes


class ProcedureFileTest(CoreTestBase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    #@unittest.skip("This test fails on CI env. Disabled until we figure it out.")
    def test_file_service(self):
        #
        rand_1 = random_string()
        title_1 = 'title_' + rand_1
        procedure_dict = self.create_procedure(title_1, 'Test procedure')
        procedure_id = procedure_dict['procedure_id']
        procedure_url = shared_dict['host'] + '/procedures/' + procedure_id

        res_dict = self.get_procedure_files(procedure_id)
        self.assertEqual(len(res_dict), 0)

        with open('rocket.png','rb') as f:
            files = {'file_content': f}
            file_info = self.add_procedure_file(procedure_id, files)
            logger.debug('file_info= %s', json.dumps(file_info, indent=4))

        with open('rocket.png','rb') as f:
            files = {'file_content': f}
            file_info_2 = self.add_procedure_file(procedure_id, files, "swag")
            logger.debug('file_info_2= %s', json.dumps(file_info_2, indent=4))

        file_info_proc = self.get_procedure_file(procedure_id, file_info['file_id'])
        logger.debug('file_info_2= %s', json.dumps(file_info_2, indent=4))

        self.assertEqual(file_info, file_info_proc)

        res_dict = self.add_section(base_url=procedure_url,
            insert_after_id='-1',
            level='',
            title='Section 1',
            description='Section 1')

        section_1 = res_dict['elem']
        section_1_id = section_1['elem_id']
        # Assume that the test is running from "tests" folder
        rand_1 = random_string()
        description_1 = 'description_' + rand_1
        institutional_release_id_1 = 'institutional_release_id_1_' + rand_1
        self.create_procedure_version(procedure_id, description_1, institutional_release_id_1)

        with open('rocket.png','rb') as f:
            files = {'file_content': f}
            file_info_section = self.add_elem_file(procedure_url, section_1_id, files)

        logger.debug('file_info_section= %s', json.dumps(file_info_section, indent=4))
        file_info = self.get_elem_file(procedure_url, section_1_id, file_info_section['file_id'])

        self.assertEqual(file_info, file_info_section)
        self.delete_elem_file(procedure_url, section_1_id, file_info_section['file_id'], 204)

        url = '{0}/procedures/{1}/load'.format(shared_dict['host'], procedure_id)
        loadInfo = {"version": 1, "procedure_id": procedure_id}
        result = requests.post(url,
            headers=shared_dict['headers'],
            json=loadInfo)

        self.delete_procedure_file(procedure_id, file_info_2['file_id'], 204)
        
        # protection against modifying versioned element
        versioned_elems = self.get_version_elements(procedure_id=procedure_id, version=1)
        versioned_section_1_id = versioned_elems[0]['elem_id']
        
        with open('rocket.png','rb') as f:
            files = {'file_content': f}
            res_dict = self.add_elem_file(procedure_url, versioned_section_1_id, files, code_expected=400)     
            self.assertEqual(res_dict['details'][0], 'Cannot modify element of versioned procedure')  
        
        res_dict = self.delete_elem_file(procedure_url, versioned_section_1_id, file_info_section['file_id'], code_expected=400)
        self.assertEqual(res_dict['details'][0], 'Cannot modify element of versioned procedure')


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
