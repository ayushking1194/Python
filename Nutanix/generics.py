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

# input
def ask(prompt, default=None, secret=False):
    if secret:
        value = getpass.getpass(
            f"{prompt} [{default if default else ''}]: "
        ).strip()
    else:
        value = input(
            f"{prompt} [{default if default else ''}]: "
        ).strip()

    return value if value else default


# check authentication
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


# build URL
def build_url(namespace, version, endpoint, params=None):
    base = f"https://{PRISM_CENTRAL_IP}:9440/api/{namespace}/{version}/{endpoint}"
    if params:
        return f"{base}?{urlencode(params)}"
    return base


# api request
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
    url = build_url(namespace, version, endpoint, params)

    response = requests.request(
        method=method.upper(),
        url=url,
        headers=headers,
        auth=(USERNAME, PASSWORD),
        json=payload,
        verify=False,
        timeout=60
    )

    response.raise_for_status()
    return response


# get list of entities
def get_list(
        namespace,
        version,
        endpoint,
        filter=None,
        select=None,
        limit=100
):
    """
    Pagination-safe list fetcher.
    Returns FULL list across all pages.
    """

    results = []
    params = {
        "$limit": limit
    }

    if filter:
        params["$filter"] = filter

    if select:
        params["$select"] = select

    next_cursor = None

    while True:
        if next_cursor:
            params["$page"] = next_cursor

        resp = api_request(
            "GET",
            namespace,
            version,
            endpoint,
            params=params
        )

        body = resp.json()
        data = body.get("data", [])
        metadata = body.get("metadata", {})

        results.extend(data)

        # Pagination handling (cursor-based)
        next_cursor = metadata.get("cursor")

        if not next_cursor:
            break

    # Projection (only if select provided)
    if select:
        fields = [f.strip() for f in select.split(",")]
        projected = []
        for item in results:
            projected.append({field: item.get(field) for field in fields})
        return projected

    return results

# get entity by name or UUID
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

    - Fetch by name
    - Fetch extId only
    - Fetch name+extId
    - Fetch full object

    Examples:
      get_entity(..., name="Linux", select="extId")
      get_entity(..., name="Linux", select="name,extId")
      get_entity(..., name="Linux")
      get_entity(... "/vms/{uuid}")
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

    # Direct object fetch (by UUID endpoint)
    if isinstance(data, dict):
        return data

    if not data:
        raise Exception(f"No entity found for: {name}")

    item = data[0]

    # Projection (select fields)
    if select:
        fields = [f.strip() for f in select.split(",")]
        return {field: item.get(field) for field in fields}

    return item

# get entity ETag
def get_entity_etag(namespace, version, endpoint):
    resp = api_request(
        "GET",
        namespace,
        version,
        endpoint
    )

    etag = resp.headers.get("ETag")
    if not etag:
        raise Exception(f"ETag missing for endpoint: {endpoint}")

    return etag

# upsert entity (post/put)
def upsert_entity(
        namespace,
        version,
        endpoint,
        payload=None,
        add_etag=False,
        method="POST"
):
    headers = DEFAULT_HEADERS.copy()
    headers["NTNX-Request-Id"] = str(uuid.uuid4())
    headers["Content-Type"] = "application/json"

    if add_etag:
        base_endpoint = endpoint.split("/$")[0]
        headers["If-Match"] = get_entity_etag(
            namespace,
            version,
            base_endpoint
        )

    resp = api_request(
        method=method,
        namespace=namespace,
        version=version,
        endpoint=endpoint,
        payload=payload,
        headers=headers
    )

    return resp.json() if resp.content else {}