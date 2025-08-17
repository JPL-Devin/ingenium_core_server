import requests
import json
import getpass

url = 'https://100.64.153.42/api/v1/login'

user_name = raw_input('user name:')
password = getpass.getpass('password:')
# print password

result = requests.get(url, auth=requests.auth.HTTPBasicAuth(user_name, password), verify=False)
print result.status_code
print result.text
