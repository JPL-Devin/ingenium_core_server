import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class CheckVenueConfigStepTest(CoreTestBase):
    def test_check_venue_config_step_dummy(self):


        user_input = {"entries": [
            {
                "config_elem_name": "StarCamera",
                "field_name": "TYPE",
                "verification_condition": "EQUAL",
                "verification_value": "EM"
            },
            {
                "config_elem_name": "INSTRUMENT1",
                "field_name": "STATUS",
                "verification_condition": "EQUAL",
                "verification_value": "INSTALLED"
            }
        ]}

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.VENUE_CONFIG_CHECK, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.VENUE_CONFIG_CHECK, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
