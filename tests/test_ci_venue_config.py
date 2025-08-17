import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes

class CheckVenueConfigStepTest(CoreTestBase):
    def test_venue_config_procedure(self):

        user_input = {
        "fsw_version": "The version of FSW that is running for a given test",
        "sse_version": "The version of SSE that is running for a given test",
        "fsw_dictionary": "The flight dictionary version of that is used for a given test",
        "sse_dictionary":"The SSE dictionary version of that is used for a given test",
        "gds_version":"18"
        }

        step = self.perform_step_operations(StepTypes.VENUE_CONFIG_MANUAL, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
