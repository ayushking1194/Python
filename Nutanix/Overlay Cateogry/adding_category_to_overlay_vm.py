import requests
import urllib3
import uuid
from config import PRISM_CENTRAL_IP as DEFAULT_PC_IP, USERNAME as DEFAULT_USERNAME, PASSWORD as DEFAULT_PASSWORD, CATEGORY_NAME as DEFAULT_CATEGORY_NAME, HEADERS as DEFAULT_HEADERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ask(prompt, default):
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default

PRISM_CENTRAL_IP = ask("Enter Prism Central IP", DEFAULT_PC_IP)
USERNAME = ask("Enter Prism Central Username", DEFAULT_USERNAME)
PASSWORD = ask("Enter Prism Central Password", DEFAULT_PASSWORD)
CATEGORY_NAME = ask("Enter Category Name to Assign", DEFAULT_CATEGORY_NAME)

HEADERS = DEFAULT_HEADERS.copy()

# --------------------
# GET OVERLAY SUBNETS
# --------------------
def get_overlay_subnets():
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/networking/v4.0/config/subnets?$filter=subnetType%20eq%20Networking.Config.SubnetType'OVERLAY'"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    data = response.json().get("data", [])
    overlay_ids = [s["extId"] for s in data]

    print("Overlay Subnet extIds:", overlay_ids)
    return overlay_ids


# -----------------
# GET ALL VM UUIDs
# -----------------
def get_vm_ext_ids():
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/vmm/v4.0/ahv/config/vms?$select=extId"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    return [vm["extId"] for vm in response.json().get("data", [])]


# -----------------
# GET NICs OF A VM
# -----------------
def get_vm_nics(vm_extId):
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/vmm/v4.0/ahv/config/vms/{vm_extId}/nics"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    return response.json().get("data", [])


# -----------------------------------------------------
# GET VM ETag (required for v4.1 category association)
# -----------------------------------------------------
def get_vm_etag(vm_extId):
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/vmm/v4.0/ahv/config/vms/{vm_extId}"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    etag = response.headers.get("ETag")
    if not etag:
        raise Exception(f"ETag missing for VM {vm_extId}")
    return etag


# ---------------------------
# GET CATEGORY extId BY NAME
# ---------------------------
def get_category_extid(category_name):
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/prism/v4.0/config/categories?$filter=key%20eq%20'{category_name}'&$select=extId"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    items = response.json().get("data", [])
    if not items:
        raise Exception(f"Category '{category_name}' not found.")

    return items[0]["extId"]


# ----------------------------------------
# CHECK IF CATEGORY IS ALREADY ASSOCIATED 
# ----------------------------------------
def category_already_associated(vm_extId, category_extId):
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/vmm/v4.0/ahv/config/vms/{vm_extId}"
    response = requests.get(url, headers=HEADERS, auth=(USERNAME, PASSWORD), verify=False)
    response.raise_for_status()

    cat_list = response.json().get("categories", [])
    existing_ids = [c.get("extId") for c in cat_list]

    return category_extId in existing_ids


# --------------------------------
# ASSOCIATE CATEGORY VIA v4.1 API
# --------------------------------
def associate_category(vm_extId, category_extId):
    url = f"https://{PRISM_CENTRAL_IP}:9440/api/vmm/v4.1/ahv/config/vms/{vm_extId}/$actions/associate-categories"

    headers = HEADERS.copy()
    headers.update({
        "Content-Type": "application/json",
        "If-Match": get_vm_etag(vm_extId),
        "NTNX-Request-Id": str(uuid.uuid4())
    })

    payload = {
        "categories": [{"extId": category_extId}]
    }

    response = requests.post(url, headers=headers, auth=(USERNAME, PASSWORD), json=payload, verify=False)
    response.raise_for_status()
    return response.json()


# ------------------
# MAIN PROGRAM FLOW
# ------------------
def main():
    print("\n---- Fetching Overlay Subnets ----")
    overlay_subnets = get_overlay_subnets()

    print("\n---- Fetching Cluster VM UUIDs ----")
    vm_ids = get_vm_ext_ids()
    print(f"Found {len(vm_ids)} VMs.")

    print("\n---- Fetching Category extId ----")
    category_extId = get_category_extid(CATEGORY_NAME)
    print(f"Category '{CATEGORY_NAME}' extId:", category_extId)

    print("\n---- Processing VMs ----")
    for vm_extId in vm_ids:
        nics = get_vm_nics(vm_extId)

        # Extract NIC subnet extIds
        nic_subnet_ids = [
            nic.get("networkInfo", {}).get("subnet", {}).get("extId")
            for nic in nics
        ]

        # Check overlay NIC match
        has_overlay_nic = any(subnet_id in overlay_subnets for subnet_id in nic_subnet_ids)

        if not has_overlay_nic:
            print(f"[SKIP] VM {vm_extId} has no overlay NIC.")
            continue

        # Avoid duplicate association
        if category_already_associated(vm_extId, category_extId):
            print(f"[SKIP] VM {vm_extId} already has category '{CATEGORY_NAME}'.")
            continue

        print(f"[ADD] Associating VM {vm_extId} with category '{CATEGORY_NAME}'...")
        associate_category(vm_extId, category_extId)

    print("\nCompleted!")


if __name__ == "__main__":
    main()