import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning #type:ignore
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json

PC_IP = '10.48.71.77'
username = 'admin'
password = 'nx2Tech651!'

def get_category_list():
    url = f'https://{PC_IP}:9440/api/nutanix/v3/categories/list'
    headers={'content-type':'application/json','accept':'application/json'}
    payload={'kind':'category'}
    response = requests.post(url,auth=(username,password),verify=False,headers=headers,data=json.dumps(payload))

    if response.ok:
        print('fetching categories...')
        with open('vm_json_dump_cat_1.json','w+') as f:
            output_json = response.json()
            for i in output_json['entities']:
                f.write(i['name'])
                f.write(',')
        print('Categories :-')
        cnt=1
        for i in response.json()['entities']:
            print(cnt,i['name'])
            cnt+=1
    else:
        print('failed with status code :',response.status_code)

get_category_list()