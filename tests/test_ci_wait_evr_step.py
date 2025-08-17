import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
from ingenium_client import CoreTestBase, StepTypes

user_input = {
    "data_path": "SIDE A",
    "start_time": "2017-032T00:23:03",
    "lookback": 0,
    "timeout": 60,
    "entries": [
        {
            "evr_name": "core_speed",
            "evr_id": "1234",
            "evr_type": "FSW_RECORDED",
            "evr_level": "ACTIVITY_LO",
            "message_filter": "cool evr bro",
            "verification_condition": "EXISTS"
        }
    ]
}

class WaitEVRStepTest(CoreTestBase):

    def test_wait_evr_step_dummy(self):
        venue_id, venue_name, step = self.perform_step_operations(StepTypes.WAIT_EVR, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')


    def test_wait_evr_step_procedure(self):
        step = self.perform_step_operations(StepTypes.WAIT_EVR, user_input, False, False, procedure=True)        

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
