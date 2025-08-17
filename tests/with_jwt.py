import requests
import json
import getpass

auth_url = 'https://100.64.153.42/api/v1/login'

if __name__ == '__main__':
    user_name = input('username:')
    password = getpass.getpass('password:')

    headers = {}

    print('login to:', auth_url)
    result = requests.get(auth_url, auth=requests.auth.HTTPBasicAuth(user_name, password), verify=False)
    if result.status_code == 200:
        res_dict = json.loads(result.text)
        headers['Authorization'] = 'Bearer {0}'.format(res_dict['access_token'])
    else:
        raise Exception('Authentication failed. status_code: {0}'.format(result.status_code))

    result = requests.get('http://100.64.153.38:8010/api/v1/executions/m2020-ingenium-10001/as_run', headers=headers)

    print(result.status_code)
    res_dict = json.loads(result.text)

    print(json.dumps(res_dict, indent=4))
