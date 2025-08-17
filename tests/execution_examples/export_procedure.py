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
        print('USAGE: python export_procedure.py server procedure_id version')
        print('Example: python export_procedure.py https://ingenium-ci.cld.jpl.nasa.gov europa-procedure-10001 2')
        sys.exit(-1)

    server = sys.argv[1]
    procedure_id = sys.argv[2]
    version = sys.argv[3]
    
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
    
    url = '{0}/core_server/api/v5/procedures/{1}/versions/{2}/export'.format(server, procedure_id, version)
    # url = 'http://localhost/core_server/api/v5/procedures/clipper-procedure-10001/versions/2/export'
    print('export url:', url)

    headers = {}
    headers['Authorization'] = jwt_token
    res = requests.get(url, headers=headers)
    print('res.status_code:', res.status_code)    
    

    if res.status_code != 200:
        print('error res.text:', res.text) 
        sys.exit(-1)        

    # print('res.headers:', res.headers)
    zname = "procedure_version.tar.gz"
    zfile = open(zname, 'wb')
    zfile.write(res.content)
    zfile.close()
    
    print('exported as procedure_version.tar.gz')

 

    
    