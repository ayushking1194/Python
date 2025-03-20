import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json

PC_IP = input('Enter PC IP :- ')
username = 'admin'
password = input('Enter PC password :- ')
header={'Accept': 'application/json','Content-Type': 'application/json'}
payload = {"kind" : "vm"}

cluster_names = []
url = f"https://{PC_IP}:9440/api/nutanix/v3/clusters/list"
def fetch_clusters(url, username, password,headers, payload):
    response=requests.post(url, auth=(username,password), verify=False, headers=header,json={"kind":"cluster"})
    
    for i in response.json()['entities']:
        cluster_names.append(i['status']['name'])
fetch_clusters(url,username,password,header,payload)

def get_entity(entity_type, entity_name):
    vmurl=f"https://{PC_IP}:9440/api/nutanix/v3/{entity_type}s/list"
    method="post"
    
    payload={"kind":f"{entity_type}" }
    resp=requests.post(vmurl,auth=(username,password),headers=header,verify=False,data=json.dumps(payload))
    if resp.ok:
            for i in resp.json()['entities']:
                if i['status']['name'] == entity_name:
                    res=i['metadata']['uuid']
                    print(res)
                    return res
                else:
                    print("entity not found")
            return
def provision_vm(vm_name, cluster_uuid):
    vm_create_url = f"https://{PC_IP}:9440/api/nutanix/v3/vms"
    payload = {
    # "spec": {
    #     "name": f"{vm_name}",
    #     "description": "for testing a VM creation script",
    #     "resources": {
    #         "num_threads_per_core": 1,
    #         "num_vcpus_per_socket": 2,
    #         "num_sockets": 2,
    #         "apc_config": {
    #             "enabled": False
    #         },
    #         "is_agent_vm": False,
    #         "memory_size_mib": 6144,
    #         "boot_config": {
    #             "boot_device": {
    #                 "disk_address": {
    #                     "device_index": 0,
    #                     "adapter_type": "IDE"
    #                 }
    #             },
    #             "boot_type": "LEGACY"
    #         },
    #         "enable_cpu_passthrough": False,
    #         "hardware_clock_timezone": "UTC",
    #         "vtpm_config": {
    #             "vtpm_enabled": False
    #         },
    #         "vga_console_enabled": True,
    #         "memory_overcommit_enabled": False,
    #         "disk_list": [
    #             {
    #                 "device_properties": {
    #                     "disk_address": {
    #                         "device_index": 0,
    #                         "adapter_type": "IDE"
    #                     },
    #                     "device_type": "DISK"
    #                 },
    #                 "data_source_reference": {
    #                     "kind": "image",
    #                     "uuid": f"{image_uuid}"
    #                 },
    #                 "disk_size_mib": 40960,
    #                 "disk_size_bytes": 42949672960
    #             }
    #         ],
    #         "vnuma_config": {
    #             "num_vnuma_nodes": 0
    #         },
    #         "nic_list": [
    #             {
    #                 "nic_type": "NORMAL_NIC",
    #                 "ip_endpoint_list": [],
    #                 "num_queues": 1,
    #                 "vlan_mode": "ACCESS",
    #                 "subnet_reference": {
    #                     "kind": "subnet",
    #                     "uuid": f"{subnet_uuid}"
    #                 },
    #                 "is_connected": True,
    #                 "trunked_vlan_list": []
    #             }
    #         ],
    #         "serial_port_list": [],
    #         "hardware_virtualization_enabled": False,
    #         "gpu_console_enabled": False,
    #         "is_vcpu_hard_pinned": False,
    #         "disable_branding": False
    #     },
    #     "cluster_reference": {
    #         "kind": "cluster",
    #         "uuid": f"{cluster_uuid}"
    #     }
    # },
    "spec": {
                "resources": {
                    "num_threads_per_core": 1,
                    "machine_type": "PC",
                    "num_vcpus_per_socket": 1,
                    "num_sockets": 2,
                    "apc_config": {
                        "enabled": False
                    },
                    "is_agent_vm": False,
                    "gpu_list": [],
                    "memory_size_mib": 8192,
                    "boot_config": {
                        "boot_device_order_list": [
                            "CDROM",
                            "DISK",
                            "NETWORK"
                        ],
                        "boot_type": "LEGACY"
                    },
                    "enable_cpu_passthrough": False,
                    "hardware_clock_timezone": "UTC",
                    "power_state_mechanism": {
                        "guest_transition_config": {
                            "should_fail_on_script_failure": False,
                            "enable_script_exec": False
                        },
                        "mechanism": "HARD"
                    },
                    "vtpm_config": {
                        "vtpm_enabled": False
                    },
                    "vga_console_enabled": True,
                    "memory_overcommit_enabled": False,
                    "disk_list": [
                        {
                            # "data_source_reference": {
                            #     "kind": "image",
                            #     "uuid": f"{image_uuid}"
                            # },
                            "disk_size_mib": 83968,
                            "disk_size_bytes": 88046829568
                        }
                    ],
                    "vnuma_config": {
                        "num_vnuma_nodes": 0
                    },
                    # "nic_list": [
                    #     {
                    #         "nic_type": "NORMAL_NIC",
                    #         "uuid": f"{subnet_uuid}",
                    #         "num_queues": 1,
                    #         "vlan_mode": "ACCESS",
                    #         "subnet_reference": {
                    #             "kind": "subnet",
                    #             "uuid": f"{subnet_uuid}"
                    #         },
                    #         "is_connected": True,
                    #         "trunked_vlan_list": []
                    #     }
                    # ],
                    "serial_port_list": [],
                    "hardware_virtualization_enabled": False,
                    "gpu_console_enabled": False,
                    "is_vcpu_hard_pinned": False,
                    "disable_branding": False
                },
                "cluster_reference": {
                    "kind": "cluster",
                    "uuid": f"{cluster_uuid}"
                },
                "name":f"{vm_name}"
            },
    "metadata": {
        "kind": "vm",
        "spec_version": 0
        }
    }
    print("before api calling")
    response = requests.post(url=vm_create_url, verify=False, headers=header, data=json.dumps(payload),auth=(username,password))
    # print(response.json())
    if response.ok:
        print("Starting VM provisioning 🎉")
    else:
        print(response.status_code)
        print(response.json())


for i in cluster_names:
    print(i)
cluster_name = input("Enter the name of the cluster: ")
cluster_uuid = get_entity("cluster", cluster_name) #"Trigonometry"
# image_name = input("Enter the name of the image: ")
# image_uuid = get_entity("image", image_name) #"karbon-ntnx-1.0"
# subnet_name = input("Enter the name of the subnet:")
# subnet_uuid = get_entity("subnet",subnet_name ) #"Native-136"
vm_name = input("Enter the name of the new VM:")
# provision_vm(vm_name, cluster_uuid, image_uuid, subnet_uuid)
provision_vm(vm_name, cluster_uuid)