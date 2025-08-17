import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass

# Add the parent folder path to the sys.path list
sys.path.append('..')
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('USAGE: python get_element.py server /executions/{execution_id}/elements/{elem_id}')
        print('USAGE: python get_element.py server /procedures/{procedure_id}/elements/{elem_id}')
        print('USAGE: python get_element.py server /procedures/{procedure_id}/versions/{version}/elements/{elem_id}')
        sys.exit(-1)

    server = sys.argv[1]
    input_url = sys.argv[2]
    
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
    
    url = '{0}/core_server/api/v5{1}'.format(server, input_url)

    print('GET url:', url)    

    headers = {}
    headers['Authorization'] = jwt_token    

    result = requests.get(url, headers=headers)
        
    print('result.status_code:', result.status_code)
    if result.status_code == 200:
        res_dict = json.loads(result.text)
        print('result:', json.dumps(res_dict, indent=4))          
    else:
        print('result.text:', result.text)        


    
    