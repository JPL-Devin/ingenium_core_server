import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class CmdSCMFStepTest(CoreTestBase):
    def test_cmd_scmf_step_dummy(self):
        print('test_cmd_scmf_step_dummy')

        user_input = {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": "0",
                "timeout": 120,
                "file_path": "/home/directory/path.sh",
                "verify": True
                }
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.CMD_SCMF, user_input, True, True)

        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.CMD_SCMF, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
