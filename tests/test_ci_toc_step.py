import xmlrunner
import os
import sys
import unittest
from config import shared_dict
import json
from ingenium_client import CoreTestBase, StepTypes


class TOCStepTest(CoreTestBase):
    def test_toc_step_dummy(self):

        user_input = {
        }

        venue_id, venue_name, step = self.perform_step_operations(StepTypes.TOC, user_input, False, True)
        # TODO: implement evaluation logic in core
        # self.assertEqual(step['execution']['meta_data']['status'], 'PASS')
        step = self.perform_step_operations(StepTypes.TOC, user_input, False, False, procedure=True)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
