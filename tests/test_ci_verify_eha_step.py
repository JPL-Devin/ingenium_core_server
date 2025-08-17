import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes

class VerifyEHAStepTest(CoreTestBase):
    def test_verify_eha_step_dummy(self):
        user_input = {
            "start_time": "2017-032T00:23:03",
            "lookback": 240,
            "timeout": 60,
            "entries": [{
                "channel_type": "SSE",
                "channel_id": "THERM-001",
                "channel_name": "thermometer",
                "data_path": "SIDE A",
                "dn_eu": "EU",
                "verify_on": "VALUE",
                "verification_condition": "GREATER_THAN",
                "verification_values": ["100"]
            }]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.VERIFY_EHA, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.VERIFY_EHA, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
