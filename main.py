#!/usr/bin/env python3

import time
import json
import sys
import requests


from flask import Flask, request, jsonify, request, Response
app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@app.route('/<path:path>', methods=['HEAD', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def catch_all(path):
    if request.args:
        args = []
        for k in request.args:
            args.append("{}={}".format(k, request.args[k]))
        args = "&".join(args)
        proxy_path = "{}?{}".format(path, args)
    else:
        proxy_path = path

    request_data = request.get_data()

    app.logger.warning("request {} proxy_path {} data {} headers {}".format(
        request, proxy_path, request_data, request.headers))

    headers = {}
    scim_hack = False

    for (key, value) in request.headers:
        if key.lower() == "content-type":
            if "application/scim+json" in value.lower():
                scim_hack = True
                headers[key] = value.replace(
                    "application/scim+json", "application/json")
            else:
                headers[key] = value
        else:
            headers[key] = value

    match request.method:
        case 'HEAD':
            response = requests.head(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case 'GET':
            response = requests.get(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case 'POST':
            response = requests.post(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case 'PUT':
            response = requests.put(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case 'PATCH':
            response = requests.patch(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case 'DELETE':
            response = requests.delete(
                "{}/{}".format(sys.argv[1], proxy_path),
                headers=headers,
                data=request_data,
            )
        case _:
            response = {
                "method": request.method,
                "message": "method not recognized",
            }

            response = json.dumps(response, indent=2, default=str)

            resp = Response(response)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.status_code = 404
            return resp

    if scim_hack:
        for key in response.headers:
            if key.lower() == "content-type":
                header = response.headers[key]
                header.replace("application/json", "application/scim+json")
                response.headers[key] = header

    app.logger.warning("response {} status {} text {} headers {}".format(
        response, response.status_code, response.text, response.headers))

    resp = Response(
        response=response.text,
        status=response.status_code,
        headers=response.headers,
    )
    return resp


if __name__ == "__main__":
    # app.debug = True
    app.run(host="::", port=12224)
