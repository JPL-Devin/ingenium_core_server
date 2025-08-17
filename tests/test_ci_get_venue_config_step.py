import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class GetVenueConfigStepTest(CoreTestBase):
    def test_get_venue_config_step_dummy(self):


        #
        user_input = {
            "get_all": False,
            "entries": [
                {"config_elem_name": "elem_name_1"},
                {"config_elem_name": "elem_name_2"},
                {"config_elem_name": "elem_name_3"}
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.VENUE_CONFIG_GET, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.VENUE_CONFIG_GET, user_input, False, False, procedure=True)

    @unittest.skip
    def test_get_venue_config_step(self):


        user_input = {
            "get_all": True,
            "entries": [
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.VENUE_CONFIG_GET, user_input, True, False)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
