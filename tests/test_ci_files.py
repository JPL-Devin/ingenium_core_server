import xmlrunner
import os
import sys
import unittest
import requests
import json
import random
from config import shared_dict, logger
import os.path
from os import listdir
import string
from dateutil import parser
from datetime import datetime
import math
import dateutil.tz
import time
from utils import random_string
import copy
from ingenium_client import CoreTestBase, StepTypes

class FileTest(CoreTestBase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_file_service(self):
        pass


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
