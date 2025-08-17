import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
from datetime import datetime
import dateutil
import dateutil.tz
from ingenium_client import CoreTestBase, StepTypes
from ingenium_client.config import username

class ManualVerificationStepTest(CoreTestBase):
    def test_manual_verification_step(self):
        time_utc = datetime.now(dateutil.tz.tzutc())
        time_utc_str = time_utc.isoformat()[:-9] + 'Z'
        
        execution_user_input = {
            "verification_text": "HOW DOES THIS WORK",
            "verification_status": "PASS",
            "verified_by": username,
            "time_verified":time_utc_str
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.MANUAL_VERIFICATION, execution_user_input, True, False)
        logger.debug('step= %s', json.dumps(step, indent=4))
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        authoring_user_input = {
            "verification_text": "HOW DOES THIS WORK"
        }
        step = self.perform_step_operations(StepTypes.MANUAL_VERIFICATION, authoring_user_input, False, False, procedure=True)

    def test_run_step(self):
        res_dict = self.create_venue()
        venue_id = res_dict['venue_id']

        execution_description = 'Execution with procedure section'
        execution_dict = self.create_execution(venue_id, execution_description)
        execution_id = execution_dict['execution_id']
        execution_url = shared_dict['host'] + '/executions/' + execution_id

        # add step
        res_dict = self.add_step(base_url=execution_url,
            step_type=StepTypes.MANUAL_VERIFICATION,
            insert_after_id='-1',
            level='CHILD')
        step_id = res_dict['elem']['elem_id']

        self.update_step(execution_url, StepTypes.MANUAL_VERIFICATION, step_id, {'title': 'MV'})
        user_input_1 = {
            'verification_text': 'checked it'
        }
        self.set_step_input(execution_url, StepTypes.MANUAL_VERIFICATION, step_id, user_input_1) 
        step = self.get_step(execution_url, StepTypes.MANUAL_VERIFICATION, step_id)
        time_verified_1 = step['execution_user_input']['time_verified']
        
        self.assertEqual(step['execution_user_input']['verification_text'], user_input_1['verification_text'])
        self.assertEqual(step['execution_user_input']['verified_by'], username)
        self.assertTrue(len(time_verified_1) > 0)
        self.assertEqual(step['execution_user_input']['verification_status'], 'PENDING')

        user_input_2 = {
            'verification_text': 'checked again',
            'verification_status': 'PASS'
        }
        self.set_step_input(execution_url, StepTypes.MANUAL_VERIFICATION, step_id, user_input_2)
        step = self.get_step(execution_url, StepTypes.MANUAL_VERIFICATION, step_id)
        time_verified_2 = step['execution_user_input']['time_verified']
        
        self.assertEqual(step['execution_user_input']['verification_text'], user_input_2['verification_text'])
        self.assertEqual(step['execution_user_input']['verified_by'], username)
        self.assertTrue(len(time_verified_2) > 0)
        self.assertEqual(step['execution_user_input']['verification_status'], 'PASS')
        self.assertTrue(time_verified_2 > time_verified_1)

        time_utc = datetime.now(dateutil.tz.tzutc())
        time_utc_str = time_utc.isoformat()[:-9] + 'Z'
        user_input_3 = {
            'verification_text': 'it failed',
            'verification_status': 'FAIL',
            'verified_by': 'hpotter',
            'time_verified': time_utc_str
        }
        self.set_step_input(execution_url, StepTypes.MANUAL_VERIFICATION, step_id, user_input_3) 
        step = self.get_step(execution_url, StepTypes.MANUAL_VERIFICATION, step_id)

        time_verified_3 = step['execution_user_input']['time_verified']
        
        self.assertEqual(step['execution_user_input']['verification_text'], user_input_3['verification_text'])
        self.assertEqual(step['execution_user_input']['verified_by'], user_input_3['verified_by'])
        self.assertTrue(len(time_verified_3) > 0)
        self.assertEqual(step['execution_user_input']['verification_status'], 'FAIL')
        self.assertTrue(time_verified_3 > time_verified_2)

        # run the step
        step = self.run_step(execution_id, step_id)

        self.assertEqual(step['execution_user_input']['verification_text'], user_input_3['verification_text'])
        self.assertEqual(step['execution_user_input']['verified_by'], user_input_3['verified_by'])
        self.assertEqual(step['execution_user_input']['time_verified'], time_verified_3)
        self.assertEqual(step['execution_user_input']['verification_status'], 'FAIL')
        
        self.assertEqual(step['execution']['results']['verification_text'], user_input_3['verification_text'])
        self.assertEqual(step['execution']['results']['verified_by'], user_input_3['verified_by'])
        self.assertEqual(step['execution']['results']['time_verified'], time_verified_3)
        self.assertEqual(step['execution']['results']['verification_status'], 'FAIL')

        self.assertEqual(step['execution']['meta_data']['status'], 'FAIL')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
