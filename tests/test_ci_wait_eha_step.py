import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes

class WaitEHAStepTest(CoreTestBase):
    def test_wait_eha_step_dummy(self):
        user_input = {
            "start_time": "2017-254T12:00:00",
            "lookback": 0,
            "timeout": 60,
            "entries": [
                {
                  "channel_type": "SSE",
                  "channel_id": "1231",
                  "channel_name": "SSE-1234",
                  "data_path": "SIDE A",
                  "dn_eu": "DN",
                  "verify_on": "VALUE",
                  "verification_condition": "GREATER_THAN",
                  "verification_values": [
                    "9999"
                  ]
                }
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.WAIT_EHA, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.WAIT_EHA, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
