import getpass
import requests
import urllib3
import uuid
from urllib.parse import urlencode

from Nutanix.config import (
    PRISM_CENTRAL_IP,
    USERNAME,
    PASSWORD
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_HEADERS = {
    "Accept": "application/json"
}

# -------------------- INPUT --------------------
def ask(prompt, default=None, secret=False):
    if secret:
        value = getpass.getpass(f"{prompt} [{default or ''}]: ").strip()
    else:
        value = input(f"{prompt} [{default or ''}]: ").strip()
    return value if value else default


# -------------------- AUTH CHECK --------------------
def check_authentication():
    try:
        resp = api_request(
            "GET",
            "clustermgmt",
            "v4.0",
            "config/clusters"
        )
        return resp.status_code == 200
    except Exception:
        return False


# -------------------- URL BUILDER --------------------
def build_url(namespace, version, endpoint, params=None):
    base = f"https://{PRISM_CENTRAL_IP}:9440/api/{namespace}/{version}/{endpoint}"
    if params:
        return f"{base}?{urlencode(params)}"
    return base


# -------------------- API REQUEST --------------------
def api_request(
    method,
    namespace,
    version,
    endpoint,
    payload=None,
    params=None,
    headers=None
):
    headers = headers or DEFAULT_HEADERS.copy()

    response = requests.request(
        method=method.upper(),
        url=build_url(namespace, version, endpoint, params),
        headers=headers,
        auth=(USERNAME, PASSWORD),
        json=payload,
        verify=False
    )

    response.raise_for_status()
    return response


# -------------------- GET LIST --------------------
def get_list(namespace, version, endpoint, select=None, filter=None):
    params = {}

    if select:
        params["$select"] = select
    if filter:
        params["$filter"] = filter

    resp = api_request(
        "GET",
        namespace,
        version,
        endpoint,
        params=params if params else None
    )

    return resp.json().get("data", [])


# -------------------- GET SINGLE ENTITY --------------------
def get_entity(
    namespace,
    version,
    endpoint,
    name=None,
    key_field="key",
    select=None
):
    """
    Universal single-entity fetcher.

    ✔ Fetch by name
    ✔ Fetch extId only
    ✔ Fetch name+extId
    ✔ Fetch full object
    ✔ Fetch direct UUID endpoint
    """

    params = {}

    if name:
        params["$filter"] = f"{key_field} eq '{name}'"

    if select:
        params["$select"] = select

    resp = api_request(
        "GET",
        namespace,
        version,
        endpoint,
        params=params if params else None
    )

    data = resp.json().get("data")

    # Direct object fetch (UUID endpoint)
    if isinstance(data, dict):
        return data

    if not data:
        raise Exception(f"No entity found for: {name}")

    item = data[0]

    # Projection
    if select:
        fields = [f.strip() for f in select.split(",")]
        return {field: item.get(field) for field in fields}

    return item


# -------------------- ETAG --------------------
def get_entity_etag(namespace, version, endpoint):
    resp = api_request("GET", namespace, version, endpoint)
    etag = resp.headers.get("ETag")
    if not etag:
        raise Exception("ETag missing")
    return etag


# -------------------- UPSERT --------------------
def upsert_entity(
    namespace,
    version,
    endpoint,
    payload=None,
    add_etag=False,
    method="POST"
):
    headers = DEFAULT_HEADERS.copy()
    headers["Content-Type"] = "application/json"
    headers["NTNX-Request-Id"] = str(uuid.uuid4())

    if add_etag:
        base_endpoint = endpoint.split("/$")[0]
        headers["If-Match"] = get_entity_etag(
            namespace,
            "v4.0",
            base_endpoint
        )

    resp = api_request(
        method,
        namespace,
        version,
        endpoint,
        payload=payload,
        headers=headers
    )

    return resp.json() if resp.text else {}