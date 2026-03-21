import requests
from flask import request, Response
from .config import Config

def forward_request():
    """
    Forwards the incoming Flask request to the configured BACKEND_URL.
    """
    url = f"{Config.BACKEND_URL}{request.full_path}"
    
    headers = {key: value for (key, value) in request.headers if key != 'Host'}

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error forwarding request: {e}")
        return Response("Bad Gateway", status=502)
