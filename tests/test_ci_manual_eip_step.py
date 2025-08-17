import xmlrunner
import os
import sys
import unittest
from config import shared_dict, logger
import json
from ingenium_client import CoreTestBase, StepTypes


class ManualEIPStepTest(CoreTestBase):
    def test_manual_eip_step(self):

        authoring_user_input = {
            'entries': [
                {
                    'signal_name': 'voltage 1',
                    'icds': 'cds-1',
                    'from': 'from-1',
                    'to': 'to-1',
                    'unit': 'Volt',
                    'min_value': '20.0',
                    'max_value': '40.0'
                },
                {
                    'signal_name': 'voltage 2',
                    'icds': 'cds-2',
                    'from': 'from-2',
                    'to': 'to-2',
                    'unit': 'Volt',
                    'min_value': '25',
                    'max_value': ''
                },     
                {
                    'signal_name': 'voltage 3',
                    'icds': 'cds-3',
                    'from': 'from-3',
                    'to': 'to-3',
                    'unit': 'Volt',
                    'min_value': '',
                    'max_value': '45'
                }                           
            ]
        }

        step = self.perform_step_operations(StepTypes.MANUAL_EIP, authoring_user_input, False, False, procedure=True)

        execution_user_input = {
            'entries': [
                {
                    'signal_name': 'voltage 1',
                    'icds': 'cds-1',
                    'from': 'from-1',
                    'to': 'to-1',
                    'unit': 'Volt',
                    'measured_unit': 'Volt',
                    'min_value': '20.0',
                    'max_value': '40.0',
                    'actual_value': '30.0'
                },
                {
                    'signal_name': 'voltage 2',
                    'icds': 'cds-2',
                    'from': 'from-2',
                    'to': 'to-2',
                    'unit': 'Volt',
                    'measured_unit': 'Volt',
                    'min_value': '25',
                    'max_value': '',
                    'actual_value': '30'
                }, 
                {
                    'signal_name': 'voltage 3',
                    'icds': 'cds-3',
                    'from': 'from-3',
                    'to': 'to-3',
                    'unit': 'Volt',
                    'measured_unit': 'Volt',
                    'min_value': '',
                    'max_value': '45',
                    'actual_value': '35'
                },                                        
            ]
        }

        step = self.perform_step_operations(StepTypes.MANUAL_EIP, execution_user_input, True, False, procedure=False)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
