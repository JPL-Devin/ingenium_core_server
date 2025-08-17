import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class GraphEHAStepTest(CoreTestBase):
    def test_graph_eha_step_dummy(self):


        user_input = {
            "channel_id": "channel_id_1",
            "channel_name": "channel_name_1",
            "start_time": "2017-032T00:23:00",
            "end_time": "2017-032T00:28:00",
            "duration": "",    # -1 indicates that it is not set
            "time_type": "ERT",
            "timeout": 240,
            "channel_type": "FSW_RECORDED",
            "dn_eu": "EU",
            "data_path": "SIDE A"
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.GRAPH_EHA, user_input, True, True)

        self.assertEqual(step['execution']['results']['venue_id'], venue_id)
        self.assertEqual(step['execution']['results']['venue_name'], venue_name)
        self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.GRAPH_EHA, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
