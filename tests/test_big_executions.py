"""
Usage:
 - Run all tests
   $ python executions_test.py

 - Run a class
   $ python executions_test.py ExecutionsTest

 - Run a method
   $ python executions_test.py ExecutionDeleteTest.test_delete_executions

"""

import xmlrunner
import os
import sys
import unittest
import requests
import json
import random
import time
import string
from dateutil import parser
from datetime import datetime
import math
import dateutil.tz
from config import shared_dict, renew_token
from utils import random_string
from ingenium_client import CoreTestBase, StepTypes


class BigExecutionsTest(CoreTestBase):
    def test_create_big_executions(self):

        num_steps = 10


        count = 0
        indices = list(range(1, 10)) + list(range(10, 200, 20))

        for num_sections in indices:
            renew_token()
            execution_id, metrics = self.create_big_execution(count, num_sections, num_steps)
            count = count + 1
            self.close_execution(execution_id, 202)

        # Check the last metric. This is what we are interested in. How is the performance after we have sizable data in DB.
        time_per_elem = metrics[4]
        time_get_as_run_per_elem = metrics[6]

        self.assertLess(time_per_elem, 0.2)
        self.assertLess(time_get_as_run_per_elem, 0.005)

    def test_create_many_executions(self):
        num_executions = 100
        num_sections = 10
        num_steps = 2


        for i in range(num_executions):
            renew_token()
            execution_id, metrics = self.create_big_execution(i, num_sections, num_steps)
            self.close_execution(execution_id, 202)

        # Check the last metric. This is what we are interested in. How is the performance after we have sizable data in DB.
        time_per_elem = metrics[4]
        time_get_as_run_per_elem = metrics[6]

        self.assertLess(time_per_elem, 0.2)
        self.assertLess(time_get_as_run_per_elem, 0.005)

    def create_big_execution(self, index, num_sections, num_steps):

        time0 = time.time()

        id_dict = {}

        ## Add a venue
        venue_id, venue_name = create_venue()
        time1 = time.time()

        ## Add an execution
        description = 'My new big execution'
        res_dict = self.create_execution(venue_id, description)
        time2 = time.time()
        execution_id = res_dict['execution_id']

        execution_url = shared_dict['host'] + '/executions/' + execution_id

        res_dict = self.add_section(base_url=execution_url,
            insert_after_id='-1',
            level='',
            description='Section 0')
        section_id = res_dict['elem']['elem_id']

        for i in range(1, num_sections):
            res_dict = self.add_section(base_url=execution_url,
                insert_after_id=section_id,
                level='SIBLING',
                description='Section ')
            section_id = res_dict['elem']['elem_id']

            # add step
            res_dict = self.add_step(base_url=execution_url,
                step_type=StepTypes.MANUAL_INPUT,
                insert_after_id=section_id,
                level='CHILD')
            step_id = res_dict['elem']['elem_id']

            for j in range(1, num_steps):
                res_dict = self.add_step(base_url=execution_url,
                    step_type=StepTypes.MANUAL_INPUT,
                    insert_after_id=step_id,
                    level='SIBLING')

                step_id = res_dict['elem']['elem_id']

                res_dict = self.add_step(base_url=execution_url,
                    step_type=StepTypes.VENUE_CONFIG_MANUAL,
                    insert_after_id=step_id,
                    level='SIBLING')
                step_id = res_dict['elem']['elem_id']

                res_dict = self.add_step(base_url=execution_url,
                    step_type=StepTypes.GDS_MANUAL,
                    insert_after_id=step_id,
                    level='SIBLING')
                step_id = res_dict['elem']['elem_id']

                res_dict = self.add_step(base_url=execution_url,
                    step_type=StepTypes.ENVIRONMENT_MANUAL
                    insert_after_id=step_id,
                    level='SIBLING')
                step_id = res_dict['elem']['elem_id']

        time3 = time.time()

        res_dict = self.get_as_run(execution_id)

        time4 = time.time()

        num_elems = num_sections * num_steps * 4
        time_create_venue = time1-time0
        time_create_execution = time2-time1
        time_create_elems = time3-time2
        time_per_elem = time_create_elems / num_elems
        time_get_as_run = time4-time3
        time_get_as_run_per_elem = time_get_as_run / num_elems


        metrics = [num_elems, time_create_venue, time_create_execution, time_create_elems, time_per_elem, time_get_as_run, time_get_as_run_per_elem]

        #

        return (execution_id, metrics)

    def create_execution(self, venue_id, description='', code_expected=200):
        execution_dict = {'venue_id': venue_id, 'description': description}

        url = shared_dict['host'] + '/executions'
        #
        result = requests.post(url,
            headers=shared_dict['headers'],
            data=json.dumps(execution_dict))

        #
        self.assertEqual(result.status_code, code_expected)

        res_dict = json.loads(result.text)

        return res_dict

    def get_as_run(self, execution_id, code_expected=200):
        url = shared_dict['host'] + '/executions/' + execution_id + '/as_run'
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, code_expected)
        return json.loads(result.text)

    def get_history(self, execution_id, code_expected=200):
        url = shared_dict['host'] + '/executions/' + execution_id + '/history'
        result = requests.get(url, headers=shared_dict['headers'])
        self.assertEqual(result.status_code, code_expected)
        return json.loads(result.text)

    def close_execution(self, execution_id, code_expected=202):
        url = '{0}/executions/{1}/halt'.format(shared_dict['host'], execution_id)
        #
        params = {'execution': 'true'}
        result = requests.post(url,
            headers=shared_dict['headers'],
            params=params)
        #
        #

        self.assertEqual(result.status_code, code_expected)

        return None

def create_venue():
    url = shared_dict['host'] + '/venues'

    idx_str = random_string(10)
    venue_name = 'wsts-' + idx_str
    venue_dict = {'name': venue_name, 'description': 'WSTS machine in Bld ' + idx_str}

    #
    result = requests.post(url,
        headers=shared_dict['headers'],
        data=json.dumps(venue_dict))

    #
    res_dict = json.loads(result.text)
    #
    venue_id = res_dict['venue_id']
    return (venue_id, venue_name)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
