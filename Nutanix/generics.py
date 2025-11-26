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


# -------------------------
# GENERIC input function
# -------------------------
def ask(prompt, default=None):
    value = input(f"{prompt} [{default}]: ").strip()
    return value if value else default


# -------------------------
# GENERIC base URL builder
# -------------------------
def build_url(namespace, version, endpoint, params=None):
    base = f"https://{PRISM_CENTRAL_IP}:9440/api/{namespace}/{version}/{endpoint}"
    if params:
        return f"{base}?{urlencode(params)}"
    return base


# -------------------------
# GENERIC API request
# -------------------------
def api_request(method, namespace, version, endpoint,
                payload=None, params=None, headers=None):
    headers = headers or DEFAULT_HEADERS.copy()
    url = build_url(namespace, version, endpoint, params)

    response = requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        auth=(USERNAME, PASSWORD),
        json=payload,
        verify=False
    )

    response.raise_for_status()
    return response


# -------------------------
# GENERIC GET entity
# -------------------------
def get_entity(namespace, version, endpoint, filter=None, select=None, single=False):
    """
    Fetch entities from Nutanix API.
    - single=True: returns a dict (single entity)
    - single=False: returns a list of dicts
    - select: comma-separated fields to return (default: 'name')
    - filter: Nutanix $filter string
    """
    params = {}
    if filter:
        params["$filter"] = filter
    params["$select"] = select if select else "name"

    resp = api_request("GET", namespace, version, endpoint, params=params)
    data = resp.json().get("data", [])

    if single:
        # API may return list or dict
        if isinstance(data, list):
            return data[0] if data else {}
        elif isinstance(data, dict):
            return data
        else:
            return {}
    else:
        # Project only selected fields
        fields = [f.strip() for f in params["$select"].split(",")]
        result = []
        for item in data:
            projected = {field: item.get(field) for field in fields}
            result.append(projected)
        return result


# -------------------------
# GENERIC get extId based on name
# -------------------------
def get_entity_extId(namespace, version, endpoint, name,
                     key_field="key"):
    filter_exp = f"{key_field} eq '{name}'"
    items = get_entity(namespace, version, endpoint,
                       filter=filter_exp, select="extId")
    if not items:
        raise Exception(f"No entity found matching: {name}")
    return items[0]["extId"]


# -------------------------
# GENERIC get ETag
# -------------------------
def get_entity_etag(namespace, version, endpoint):
    resp = api_request("GET", namespace, version, endpoint)
    etag = resp.headers.get("ETag")
    if not etag:
        raise Exception(f"ETag missing for endpoint: {endpoint}")
    return etag


# -------------------------
# GENERIC POST entity
# -------------------------
def post_entity(namespace, version, endpoint, payload=None, add_etag=False):
    headers = DEFAULT_HEADERS.copy()
    headers["NTNX-Request-Id"] = str(uuid.uuid4())
    headers["Content-Type"] = "application/json"

    if add_etag:
        base_endpoint = endpoint.split("/$")[0]
        headers["If-Match"] = get_entity_etag(namespace, version, base_endpoint)

    resp = api_request(
        "POST", namespace, version, endpoint,
        payload=payload, headers=headers
    )
    return resp.json()