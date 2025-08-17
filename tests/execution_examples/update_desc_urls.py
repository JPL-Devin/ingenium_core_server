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
    server = 'https://ingenium-ci.cld.jpl.nasa.gov'
    procedure_id = 'europa-procedure-10170'
    version = 0
    
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
    
    elems = []
    to_update_elems = []    
    for element in elements:
        elem_id = element['elem_id']
        number = element['number']        
        description = element['description']

        if description.find('file_server/') > -1:  
            elems.append({
                'number': number,
                'description': description
            })
        
        if description.find('ingenium-media-prod-psyche/') > -1:        
            to_update_elem = {
                'elem_id': elem_id,
                'number': number,
                'description': description.replace('ingenium-media-prod-psyche/', 'ingenium-media-ci/').replace('https://ingenium-psyche.jpl.nasa.gov/file_server',
                    'https://ingenium-ci.cld.jpl.nasa.gov/file_server')
            }
            to_update_elems.append(to_update_elem)

    with open('elems.json', 'w') as file:
        json.dump(elems, file, indent=4)
                            
    with open('to_update_elems.json', 'w') as file:
        json.dump(to_update_elems, file, indent=4)
        
    for to_update_elem in to_update_elems:
        elem_id = to_update_elem['elem_id']
        del to_update_elem['number']
        del to_update_elem['elem_id']
        
        url = '{0}/core_server/api/v5/procedures/{1}/elements/{2}'.format(server, procedure_id, elem_id)
        # print(url)
        # print(to_update_elem)
        res = requests.patch(url, to_update_elem, headers=headers)
        print(res.status_code)
        


    