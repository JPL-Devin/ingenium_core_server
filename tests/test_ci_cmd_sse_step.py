import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class CmdSSEStepTest(CoreTestBase):
    def test_cmd_sse_step_dummy(self):
        print('test_cmd_sse_step_dummy')

        user_input = {
            "data_path": "SIDE A",
            "entries": [
                {
                "timeout": 10,
                "cmd_string": "flight 123 1 23.1"
                }
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.CMD_SSE, user_input, True, True)

        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.CMD_SSE, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
