import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning # type: ignore
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json

PC_IP = '10.48.71.77'
username = 'admin'
password = 'nx2Tech651!'

cat_list=[]

def get_category_list():
    url = f'https://{PC_IP}:9440/api/nutanix/v3/categories/list'
    headers={'content-type':'application/json','accept':'application/json'}
    payload={'kind':'category'}
    response = requests.post(url,auth=(username,password),verify=False,headers=headers,data=json.dumps(payload))
    
    for i in response.json():
        cat_list.append(i['name'])
    return cat_list

def get_category_key(category_name):
    url=f'https://{PC_IP}:9440/api/nutanix/v3/categories/{category_name}'
    headers={'accept':'application/json'}
    response=requests.get(url,auth=(username,password),verify=False,headers=headers)

    if response.ok:
        print('works')
        # with open('cat_key_json_dump.json','w+') as f:
        #     f.write(json.dumps(response.json(),indent=4))
        print(response.json())
        
    else:
        print('Failed with status code :',response.status_code)

for cat_name in cat_list:
    get_category_key(cat_name)