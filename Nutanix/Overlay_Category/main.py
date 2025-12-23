// Author: Ayush Srivastava
// Created: 2025-26-11
// Repository: https://github.com/ayushking1194/Python

import logging
from Nutanix.generics import (
    ask,
    check_authentication,
    get_entity,
    get_list,
    upsert_entity
)
from Nutanix.config import (
    PRISM_CENTRAL_IP as DEFAULT_PC_IP,
    USERNAME as DEFAULT_USERNAME,
    PASSWORD as DEFAULT_PASSWORD
)

# ------------------------ LOGGER SETUP ------------------------
logger = logging.getLogger("overlay_category")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# ------------------------ USER INPUT ------------------------
PRISM_CENTRAL_IP = ask("Enter Prism Central IP", DEFAULT_PC_IP)
USERNAME = ask("Enter Prism Central Username", DEFAULT_USERNAME)
PASSWORD = ask("Enter Prism Central Password", DEFAULT_PASSWORD, secret=True)

# ------------------------ AUTH CHECK ------------------------
if not check_authentication():
    logger.error("Failed to authenticate with Prism Central. Please check your credentials.")
    exit(1)

CATEGORY_NAME = ask("Enter Category Name to Assign")

def main():

    # -------------------- FETCH OVERLAY SUBNETS --------------------
    try:
        logger.info("---- Fetching Overlay Subnets ----")

        overlay_subnets = get_list(
            namespace="networking",
            version="v4.0",
            endpoint="config/subnets",
            select="extId,subnetType"
        )

        overlay_subnets = [
            s for s in overlay_subnets
            if s.get("subnetType") == "OVERLAY"
        ]

        overlay_ids = [s["extId"] for s in overlay_subnets]
        logger.debug(f"Found {len(overlay_ids)} overlay subnets.")

    except Exception as e:
        logger.error(f"Failed to fetch overlay subnets: {e}")
        return

    # -------------------- FETCH VMS --------------------
    try:
        logger.info("---- Fetching Cluster VMs ----")

        vm_list = get_list(
            namespace="vmm",
            version="v4.0",
            endpoint="ahv/config/vms",
            select="extId,name"
        )

        vm_ids = [vm["extId"] for vm in vm_list]
        vm_name_map = {vm["extId"]: vm.get("name", "unknown") for vm in vm_list}

        logger.debug(f"Found {len(vm_ids)} VMs.")

    except Exception as e:
        logger.error(f"Failed to fetch VMs: {e}")
        return

    # -------------------- FETCH CATEGORY EXTID --------------------
    try:
        logger.info("---- Fetching Category extId ----")

        category_obj = get_entity(
            namespace="prism",
            version="v4.0",
            endpoint="config/categories",
            name=CATEGORY_NAME,   
            key_field="key",
            select="extId"
        )

        category_extId = category_obj.get("extId")

        if not category_extId:
            raise Exception("Category extId missing")

        logger.debug(f"Category '{CATEGORY_NAME}' extId: {category_extId}")

    except Exception as e:
        logger.error(f"Failed to fetch category '{CATEGORY_NAME}': {e}")
        return

    # -------------------- PROCESS VMS --------------------
    logger.info("---- Processing VMs ----")

    for vm_extId in vm_ids:
        vm_name = vm_name_map.get(vm_extId, "unknown")

        # ---- Fetch NICs ----
        try:
            nics = get_list(
                namespace="vmm",
                version="v4.0",
                endpoint=f"ahv/config/vms/{vm_extId}/nics",
                select="networkInfo"
            )

        except Exception as e:
            logger.error(f"Failed to fetch NICs for VM '{vm_name}': {e}")
            continue

        nic_subnet_ids = [
            nic.get("networkInfo", {}).get("subnet", {}).get("extId")
            for nic in nics
        ]

        if not any(sid in overlay_ids for sid in nic_subnet_ids):
            logger.info(f"[SKIP] VM '{vm_name}' has no overlay NIC.")
            continue

        # ---- Fetch VM (Single Object) ----
        try:
            vm_info = get_entity(
                namespace="vmm",
                version="v4.0",
                endpoint=f"ahv/config/vms/{vm_extId}"  
            )

            vm_categories = vm_info.get("categories", [])
            existing_ids = [c["extId"] for c in vm_categories]

        except Exception as e:
            logger.error(f"Failed to fetch categories for VM '{vm_name}': {e}")
            continue

        if category_extId in existing_ids:
            logger.info(f"[SKIP] VM '{vm_name}' already has category '{CATEGORY_NAME}'.")
            continue

        # ---- Associate Category ----
        try:
            logger.info(f"[ADD] Associating VM '{vm_name}' with category '{CATEGORY_NAME}'...")

            upsert_entity(
                namespace="vmm",
                version="v4.1",
                endpoint=f"ahv/config/vms/{vm_extId}/$actions/associate-categories",
                payload={"categories": [{"extId": category_extId}]},
                add_etag=True,
                method="POST"
            )

        except Exception as e:
            logger.error(f"Failed to associate category for VM '{vm_name}': {e}")
            continue

    logger.info("Completed!")

if __name__ == "__main__":
    main()
