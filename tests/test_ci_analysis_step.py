import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class AnalysisStepTest(CoreTestBase):
    def test_analysis_step_dummy(self):

        user_input = {
            'analysis_text': 'some text',
            'verification_status': 'PASS'
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.ANALYSIS, user_input, False, True)
        # TODO: implement evaluation logic in core
        # self.assertEqual(step['execution']['meta_data']['status'], 'PASS')

        step = self.perform_step_operations(StepTypes.ANALYSIS, user_input, False, False, procedure=True)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
