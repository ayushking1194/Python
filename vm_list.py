import json
import requests

PC_IP = input('Enter PC IP :- ')
url = f"https://{PC_IP}:9440/api/nutanix/v3/vms/list"
username='admin'
password=input('Enter PC password :- ')
payload={'kind':'vm'}
headers={'Content-Type':'application/json', 'Accept':'application/json'}

def fetch_vms(url, username, password,headers, payload):
    response=requests.post(url, auth=(username,password), verify=False, headers=headers,json=payload)
    print('vm names :-')
    for i in response.json()['entities']:
        print(i['status']['name'])

vms = fetch_vms(url,username,password,headers,payload)