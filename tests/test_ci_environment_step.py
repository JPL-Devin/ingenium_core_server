import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
from ingenium_client import CoreTestBase, StepTypes


class EnvironmentStepTest(CoreTestBase):
    def test_environment_step(self):

        authoring_user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': []
            }
        }

        step = self.perform_step_operations(StepTypes.ENVIRONMENT_MANUAL, authoring_user_input, False, False, procedure=True)

        execution_user_input = {
            'temperature': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 60.0
            },
            'humidity': {
                'verify_on': 'VALUE',
                'verification_condition': 'RECORD',
                'verification_values': [],
                'actual_value': 40.0
            }
        }

        step = self.perform_step_operations(StepTypes.ENVIRONMENT_MANUAL, execution_user_input, True, False, procedure=False)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
