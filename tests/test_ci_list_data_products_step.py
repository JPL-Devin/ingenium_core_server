import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class ListDataProductsStepTest(CoreTestBase):
    def test_list_data_products_step_dummy(self):

        user_input = {
            "data_path": "SIDE A",
            "start_time": "2017-283T08:50:47",
            "end_time": "2017-283T08:51:00",
            "duration": "240",
            "time_type": "ERT",
            "timeout": 240,
            "entries": [
                {
                    "apid": 247,
                    "product_status_filter": "good stuff",
                    "verification_condition": "EQUAL",
                    "verification_value": 1
                }
            ]
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.LIST_DATA_PRODUCTS, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.LIST_DATA_PRODUCTS, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
