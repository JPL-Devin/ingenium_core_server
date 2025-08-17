import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass
import time

# Add the parent folder path to the sys.path list
sys.path.append('..')
    
if __name__ == '__main__':
    server = sys.argv[1]
    
    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    print(login_url)
    
    current_user = getpass.getuser()
    username = input('username: %s' % current_user) or current_user    
    password = getpass.getpass('password:')
    
    res = requests.get(login_url, auth=HTTPBasicAuth(username, password))    
    
    if res.status_code != 200:
        print('authentication failed. status_code:', res.status_code)
        sys.exit(-1)
        
    res_dict = json.loads(res.text)
    access_token = res_dict['access_token']
    # print('access_token:', access_token) 
    
    jwt_token = 'Bearer {0}'.format(access_token)
    
    url = '{0}/core_server/api/v5/executions'.format(server)

    print('GET url:', url)    

    headers = {}
    headers['Authorization'] = jwt_token    
    
    paramss = [
        {},
        {
            'description': 'test'
        },
        {
            'status': 'CLOSED'
        },        
        {
            'venue_name': 'AAA eurcdeving1b'
        },
        {
            'procedure_id': 'clipper-procedure-12135',
            'version': 1
        },
        {
            'institutional_id': 'P',
        },                
        {
            'institutional_id': 'P',
            'institutional_release_id': 'Rev A'  
        },        
        {
            'test_conductor': 'hongmank'    
        },                   
        {
            'venue_type': 'WSTS'
        },      
        {
            'venue_type': 'WSTS',
            'procedure_id': 'clipper-procedure-12135'            
        }
    ]
        
    for params in paramss:
        print()
        time0 = time.time()
        result = requests.get(url, params=params, headers=headers)
        time_elapsed = time.time() - time0
            
        if result.status_code == 200:
            res_dict = json.loads(result.text)
            # print('result:', json.dumps(res_dict, indent=4))        
            print('params:', json.dumps(params, indent=4))  
            print('count:', len(res_dict))
        else:
            print('result.text:', result.text)        
        print('result.status_code: %s time_elapsed: %s' % (result.status_code, time_elapsed))


    
    