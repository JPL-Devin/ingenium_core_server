import requests
from requests.auth import HTTPBasicAuth
import json
import os
import sys
import getpass

# Add the parent folder path to the sys.path list
sys.path.append('..')
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('USAGE: python import_procedure.py server procedure_id procedure_gz_file')
        print('Example: python import_procedure.py https://ingenium-ci.cld.jpl.nasa.gov europa-procedure-10001 procedure_version.tar.gz')
        sys.exit(-1)    

    server = sys.argv[1]
    procedure_id = sys.argv[2]
    procedure_gz = sys.argv[3]
    
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
    
    url = '{0}/core_server/api/v5/procedures/{1}/import'.format(server, procedure_id)
    # url = 'http://localhost/core_server/api/v5/procedures/clipper-procedure-10001/import'
    print('import url:', url)    

    headers = {}
    headers['Authorization'] = jwt_token

    with open(procedure_gz,'rb') as file:         
        file_payload = {'procedure_version_file': file}        

        result = requests.post(url,
            headers=headers,
            files=file_payload)

        print('result.status_code:', result.status_code)
        if result.status_code == 200:
            res_dict = json.loads(result.text)
            print('result:', json.dumps(res_dict, indent=4))          
        else:
            print('result.text:', result.text)    
 






    
    