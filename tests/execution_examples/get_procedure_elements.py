import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass
import time

# Add the parent folder path to the sys.path list
sys.path.append('..')
    
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('USAGE: python get_procedure_elements.py server procedure_id version [limit]')
        sys.exit(-1)

    server = sys.argv[1]
    procedure_id = sys.argv[2]
    version = sys.argv[3]
    
    if len(sys.argv) > 4:
        limit = int(sys.argv[4])
    else:
        limit = 100000

    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    print(login_url)
    
    username = input("username:")
    password = getpass.getpass("password:")
    
    res = requests.get(login_url, auth=HTTPBasicAuth(username, password))    
    
    if res.status_code != 200:
        print('authentication failed. status_code:', res.status_code)
        sys.exit(-1)
        
    res_dict = json.loads(res.text)
    access_token = res_dict['access_token']
    # print('access_token:', access_token) 
    
    jwt_token = 'Bearer {0}'.format(access_token)
    
    url = '{0}/core_server/api/v5/procedures/{1}/versions/{2}/elements'.format(server, procedure_id, version)

    print('GET url:', url)    

    headers = {}
    headers['Authorization'] = jwt_token    

    t0 = time.time()
    result = requests.get(url, params={'limit': limit}, headers=headers)
    t1 = time.time()

    print('result.status_code:', result.status_code)
    if result.status_code == 200:
        t2 = time.time()
        elements = json.loads(result.text)
        t3 = time.time()
        # print('result:', json.dumps(elements, indent=4))          
    else:
        print('result.text:', result.text)        
        sys.exit(-1)
        
    for element in elements:
        element.pop('elem_id')
        element.pop('version_id')
        element.pop('parent_id')
        
    with open(f'{procedure_id}-v{version}.json', 'w') as file:
        json.dump(elements, file, indent=4)

    print('num elems: ', len(elements))
    print('request time: ', t1-t0)
    print('json time: ', t3-t2)
    