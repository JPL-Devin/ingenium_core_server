import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes

class WaitStepTest(CoreTestBase):
    def test_wait_step(self):
        user_input = {
            "wait_type": "DURATION",
            "time_value": "5"
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.WAIT, user_input, True, False)

        # Wait step does not need venue
        # self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        # self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.WAIT, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
