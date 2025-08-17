import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass
import time
from urllib3.exceptions import InsecureRequestWarning

from random import choice
from string import ascii_lowercase

# vary the number of spaces appended to adjust the probability
chars = ascii_lowercase + " " * 10

def random_string(n):
    return "".join(choice(chars) for _ in range(n))

# Add the parent folder path to the sys.path list
sys.path.append('..')

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('USAGE: python get_from_core.py server procedure_id')
        sys.exit(-1)

    server = sys.argv[1]
    procedure_id = sys.argv[2]
    
    login_url = '{0}/auth_server/api/v2/login'.format(server)
    
    print(login_url)
    

    username = input("username:")
    password = getpass.getpass("password:")

    elems = []

    while True:
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
        
        if len(elems) == 0:
            url = f'{server}/core_server/api/v5/procedures/{procedure_id}/elements'
            res = requests.get(url, headers=headers, params={'limit': 10000}, verify=False)
            print(f'GET url: {url}')

            print('result.status_code:', res.status_code)
            if res.status_code != 200:
                print(f'status_code: {res.status_code} error: {res.text}')
            elems = res.json()

        for elem in elems:
            number = elem['number']
            elem_id = elem['elem_id']
            url = f'{server}/core_server/api/v5/procedures/{procedure_id}/elements/{elem_id}'
            print(f'PATCH number: {number} elem_id: {elem_id}')

            res = requests.patch(url, json={'description': random_string(500)}, headers=headers, verify=False)
            if res.status_code != 200:
                print(f'status_code: {res.status_code} error: {res.text}')
    
    
