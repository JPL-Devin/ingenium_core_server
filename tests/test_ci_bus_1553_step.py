import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
import requests
from ingenium_client import CoreTestBase, StepTypes
from utils import random_string


class Bus1553StepTest(CoreTestBase):
    def test_query_evr_step_dummy(self):
        user_input = {
            "start_time": "0555401349",
            "end_time": "0555401369",
            "lookback": 0,
            "timeout": 240,
            "time_type": "SCET",
            "verify_wait": "VERIFY",
            "entries": [
                {
                    "bus_1553_var": "var1",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "RECORD",
                    "verification_values": []                                                                                                                               
                }
            ],
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.BUS_1553, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.BUS_1553, user_input, False, False, procedure=True)
                

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
