import requests
from requests import Session
from typing import Dict
from .gopay_types import token_or_credentials


def api_call(
    url: str,
    method: str,
    auth: token_or_credentials,
    body: Dict = None,
    content: str = None,
    session: Session = None,
) -> Dict:
    """
    Wrapper around the request method from the request library. Can optionally
    be called on a requests Session
    """
    headers = {
        "Accept": "application/json",
        "User-Agent": "GoPay Client, https://github.com/geeshta",
    }
    request = {"method": method, "url": url, "headers": headers}

    if content == "JSON":
        request["json"] = body
        headers["Content-Type"] = "application/json"
    elif content == "FORM":
        request["data"] = body
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    if isinstance(auth, str):
        headers["Authorization"] = f"Bearer {auth}"
    else:
        request["auth"] = auth

    response = session.request(**request) if session else requests.request(**request)

    try:
        response_body = response.json()
    except:
        response_body = response.text

    result = {
        "success": response.ok,
        "status": response.status_code,
        "body": response_body,
        "content_type": response.headers.get("content-type"),
    }
    print(f"{request['method']} {request['url']} {result['status']}")
    return result
