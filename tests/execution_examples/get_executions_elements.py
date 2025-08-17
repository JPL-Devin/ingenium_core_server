import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass
import time
from urllib3.exceptions import InsecureRequestWarning

# Add the parent folder path to the sys.path list
sys.path.append('..')

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('USAGE: python get_executions_elements.py server')
        sys.exit(-1)

    server = sys.argv[1]
    
    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    print(login_url)
    

    username = input("username:")
    password = getpass.getpass("password:")

    elems = []

    res = requests.get(login_url, auth=HTTPBasicAuth(username, password), verify=False)    
    if res.status_code != 200:
        print('authentication failed. status_code:', res.status_code)
        sys.exit(-1)
        
    res_dict = json.loads(res.text)
    access_token = res_dict['access_token']
    # print('access_token:', access_token) 
    
    jwt_token = 'Bearer {0}'.format(access_token)
    headers = {}
    headers['Authorization'] = jwt_token
    
    url = f'{server}/core_server/api/v5/executions'
    res = requests.get(url, headers=headers, params={'limit': 10000, 'sort_by': 'EXECUTION_ID', 'sort': 'DESC'}, verify=False)
    print(f'GET url: {url} status_code: {res.status_code}')
    if res.status_code != 200:
        print(f'status_code: {res.status_code} error: {res.text}')
    executions = res.json()

    while True:
        for execution in executions:
            res = requests.get(login_url, auth=HTTPBasicAuth(username, password), verify=False)    
            if res.status_code != 200:
                print('authentication failed. status_code:', res.status_code)
                sys.exit(-1)
                
            res_dict = json.loads(res.text)
            access_token = res_dict['access_token']
            # print('access_token:', access_token) 
            
            jwt_token = 'Bearer {0}'.format(access_token)
            headers = {}
            headers['Authorization'] = jwt_token

            execution_id = execution['execution_id']
            url = f'{server}/core_server/api/v5/executions/{execution_id}/elements'
            res = requests.get(url, headers=headers, params={'limit': 10000}, verify=False)
            print(f'GET url: {url} status_code: {res.status_code}')
            if res.status_code != 200:
                print(f'status_code: {res.status_code} error: {res.text}')
            else:
                elems = res.json()
                print(f'execution_id: {execution_id} elems count: {len(elems)}')


