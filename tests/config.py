import requests
import json
import time
import os
import jwt

from ingenium_client import shared_dict, logger

server = os.environ.get('CORE_SERVER_URL', 'http://localhost:8002')
archive_server = os.environ.get('ARCHIVE_ING_URL', 'http://127.0.0.1:8010') 
venue_config_server = os.environ.get('VENUE_CONFIG_URL', 'http://127.0.0.1:5151') 

api_path = '{0}/api/v5'.format(server)     
archive_api_path = '{0}/api/v5'.format(archive_server)     
venue_config_api_path = '{0}/api/v1'.format(venue_config_server) 

logger.debug('api_path: %s', api_path)    
shared_dict['host'] = api_path
shared_dict['archive_host'] = archive_api_path
shared_dict['venue_config_host'] = venue_config_api_path


