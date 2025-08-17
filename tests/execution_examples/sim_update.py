import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass
import time
import jwt
from multiprocessing import Pool

# Add the parent folder path to the sys.path list
sys.path.append('..')

username = os.environ.get("USER")

def generate_token(scopes=['execute:wsts', 'execute:testbed', 'execute:sit', 'basic', 'author', 'admin']):
    iat = int(time.time()) - 60
    exp = iat + (30*60)
    headers = {'Content-Type': 'application/json',
              'Accept': 'application/json'}
    private_pem = os.environ.get('PRIVATE_PEM')
    encoded_token = jwt.encode({'scopes': scopes,
                        'exp':exp,
                        'iat':iat,
                        'username': username},
                         private_pem,
                         algorithm='RS256')
   
    token_str = encoded_token.decode('utf-8')
    auth_header = 'Bearer {0}'.format(token_str)
    headers['Authorization'] = auth_header
    return headers    

def update_section(headers, server, procedure_id, elem_id, description):
    url = '{0}/core_server/api/v5/procedures/{1}/sections/{2}'.format(server, procedure_id, elem_id)

    res = requests.patch(url, json={'description': description}, headers=headers)

    print(res.status_code)
    print(res.text)
    
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('USAGE: python sim_update.py server procedure_id elem_id description')
        sys.exit(-1)

    server = sys.argv[1]
    procedure_id = sys.argv[2]
    elem_id = sys.argv[3]
    description = sys.argv[4]
    
    headers = generate_token()

    with Pool(2) as p:
        p.starmap(update_section, [(headers, server, procedure_id, elem_id, description),
        (headers, server, procedure_id, elem_id, description + '1')]) 


    
    