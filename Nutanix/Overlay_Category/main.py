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

# -------------------- LOGGER --------------------
logger = logging.getLogger("overlay_category")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(ch)

# -------------------- INPUT --------------------
PRISM_CENTRAL_IP = ask("Enter Prism Central IP", DEFAULT_PC_IP)
USERNAME = ask("Enter Prism Central Username", DEFAULT_USERNAME)
PASSWORD = ask("Enter Prism Central Password", DEFAULT_PASSWORD, secret=True)

# -------------------- AUTH --------------------
if not check_authentication():
    logger.error("Authentication failed")
    exit(1)

CATEGORY_NAME = ask("Enter Category Name to Assign")


def main():

    # -------- OVERLAY SUBNETS --------
    overlay_subnets = get_list(
        namespace="networking",
        version="v4.0",
        endpoint="config/subnets",
        select="extId,subnetType"
    )

    overlay_ids = {
        s["extId"]
        for s in overlay_subnets
        if s.get("subnetType") == "OVERLAY"
    }

    logger.info(f"Overlay subnets found: {len(overlay_ids)}")

    # -------- VMS --------
    vms = get_list(
        namespace="vmm",
        version="v4.0",
        endpoint="ahv/config/vms",
        select="extId,name"
    )

    # -------- CATEGORY --------
    category = get_entity(
        namespace="prism",
        version="v4.0",
        endpoint="config/categories",
        name=CATEGORY_NAME,
        key_field="key",
        select="extId"
    )

    category_extId = category["extId"]

    # -------- PROCESS --------
    for vm in vms:
        vm_id = vm["extId"]
        vm_name = vm.get("name", "unknown")

        nics = get_list(
            namespace="vmm",
            version="v4.0",
            endpoint=f"ahv/config/vms/{vm_id}/nics",
            select="networkInfo"
        )

        subnet_ids = {
            nic.get("networkInfo", {})
               .get("subnet", {})
               .get("extId")
            for nic in nics
        }

        if not subnet_ids & overlay_ids:
            logger.info(f"[SKIP] {vm_name} (no overlay NIC)")
            continue

        vm_info = get_entity(
            namespace="vmm",
            version="v4.0",
            endpoint=f"ahv/config/vms/{vm_id}"
        )

        existing = {c["extId"] for c in vm_info.get("categories", [])}

        if category_extId in existing:
            logger.info(f"[SKIP] {vm_name} (already categorized)")
            continue

        logger.info(f"[ADD] {vm_name} → {CATEGORY_NAME}")

        upsert_entity(
            namespace="vmm",
            version="v4.1",
            endpoint=f"ahv/config/vms/{vm_id}/$actions/associate-categories",
            payload={"categories": [{"extId": category_extId}]},
            add_etag=True
        )

    logger.info("Completed")


if __name__ == "__main__":
    main()