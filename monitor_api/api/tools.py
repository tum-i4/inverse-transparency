# encoding=utf-8
""" Low-level tools """

import flask
import requests
import werkzeug.datastructures as wz_ds


def requests_Response_to_flask_Response(
    req_response: requests.Response
) -> flask.Response:
    """ Convert a `requests.Response` object to a `flask.Response` object. """

    status_code: int = req_response.status_code

    # headers:werkzeug.datastructures.Headers
    headers = wz_ds.Headers()
    for k, v in req_response.headers.items():
        if k not in ["Expires", "Server", "Cache-Control"]:
            continue
        headers.add(k, v)

    content_type: str = req_response.headers["content-type"]

    return flask.Response(
        response=req_response.content,
        status=status_code,
        headers=headers,
        mimetype=None,  # Not sure how to resolve – is automatically set anyways
        content_type=content_type,
        direct_passthrough=False,  # Probably better left as False
    )


def requests_Response_is_json(req_response: requests.Response) -> bool:
    """ Safely determine whether the given response consists of JSON data. """

    if not req_response.headers["content-type"] == "application/json":
        return False

    try:
        req_response.json()
    except ValueError:
        return False

    return True
