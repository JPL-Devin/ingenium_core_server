import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes

class UpdateVenueConfigStepTest(CoreTestBase):

    def test_update_venue_config_step_dummy(self):
        user_input = {"entries": [
            {
                "config_elem_name": "StarCamera",
                "type": "EM",
                "status": "INSTALLED",
                "serial": "SN 20323232",
                "notes": "Installed to support test X"
            },
            {
                "config_elem_name": "INSTRUMENT1",
                "type": "SIMULATOR",
                "status": "INSTALLED",
                "serial": "V3.2",
                "notes": "Installed to support test X"
            },
            {
                "config_elem_name": "FSW_IMAGE_1",
                "type": "FLIGHT",
                "status": "INSTALLED",
                "serial": "3.0.1",
                "notes": "Installed to support test X"
            }
        ]}

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.VENUE_CONFIG_UPDATE, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')
        step = self.perform_step_operations(StepTypes.VENUE_CONFIG_UPDATE, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
