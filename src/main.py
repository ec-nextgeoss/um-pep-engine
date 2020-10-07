#!/usr/bin/env python3

from WellKnownHandler import WellKnownHandler
from WellKnownHandler import TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT, KEY_UMA_V2_PERMISSION_ENDPOINT, KEY_UMA_V2_INTROSPECTION_ENDPOINT

from flask import Flask, request, Response
from werkzeug.datastructures import Headers
from random import choice
from string import ascii_lowercase
from requests import get, post, put, delete
import json

from config import load_config, save_config
from eoepca_scim import EOEPCA_Scim, ENDPOINT_AUTH_CLIENT_POST
from custom_oidc import OIDCHandler
from custom_uma import UMA_Handler, resource
from custom_uma import rpt as class_rpt
import os
import sys
import traceback

from jwkest.jws import JWS
from jwkest.jwk import RSAKey, import_rsa_key_from_file, load_jwks_from_url, import_rsa_key
from jwkest.jwk import load_jwks
from Crypto.PublicKey import RSA
### INITIAL SETUP

env_vars = [
"PEP_REALM",
"PEP_AUTH_SERVER_URL",
"PEP_PROXY_ENDPOINT",
"PEP_SERVICE_HOST",
"PEP_SERVICE_PORT",
"PEP_S_MARGIN_RPT_VALID",
"PEP_CHECK_SSL_CERTS",
"PEP_USE_THREADS",
"PEP_DEBUG_MODE",
"PEP_RESOURCE_SERVER_ENDPOINT",
"PEP_API_RPT_UMA_VALIDATION"]

use_env_var = True

for env_var in env_vars:
    if env_var not in os.environ:
        use_env_var = False

g_config = {}
# Global config objects
if use_env_var is False:
    g_config = load_config("config/config.json")
else:
    for env_var in env_vars:
        env_var_config = env_var.replace('PEP_', '')

        if "true" in os.environ[env_var].replace('"', ''):
            g_config[env_var_config.lower()] = True
        elif "false" in os.environ[env_var].replace('"', ''):
            g_config[env_var_config.lower()] = False
        else:
            g_config[env_var_config.lower()] = os.environ[env_var].replace('"', '')

# Global handlers
g_wkh = WellKnownHandler(g_config["auth_server_url"], secure=False)

# Global setting to validate RPTs received at endpoints
api_rpt_uma_validation = g_config["api_rpt_uma_validation"]
if api_rpt_uma_validation: print("UMA RPT validation is ON.")
else: print("UMA RPT validation is OFF.")

# Generate client dynamically if one is not configured.
if "client_id" not in g_config or "client_secret" not in g_config:
    print ("NOTICE: Client not found, generating one... ")
    scim_client = EOEPCA_Scim(g_config["auth_server_url"])
    new_client = scim_client.registerClient("PEP Dynamic Client",
                                grantTypes = ["client_credentials"],
                                redirectURIs = [""],
                                logoutURI = "",
                                responseTypes = ["code","token","id_token"],
                                scopes = ['openid', 'uma_protection', 'permission'],
                                token_endpoint_auth_method = ENDPOINT_AUTH_CLIENT_POST)
    print("NEW CLIENT created with ID '"+new_client["client_id"]+"', since no client config was found on config.json or environment")

    g_config["client_id"] = new_client["client_id"]
    g_config["client_secret"] = new_client["client_secret"]
    if use_env_var is False:
        save_config("config/config.json", g_config)
    else:
        os.environ["PEP_CLIENT_ID"] = new_client["client_id"]
        os.environ["PEP_CLIENT_SECRET"] = new_client["client_secret"]
    print("New client saved to config!")
else:
    print("Client found in config, using: "+g_config["client_id"])

oidc_client = OIDCHandler(g_wkh,
                            client_id = g_config["client_id"],
                            client_secret = g_config["client_secret"],
                            redirect_uri = "",
                            scopes = ['openid', 'uma_protection', 'permission'],
                            verify_ssl = g_config["check_ssl_certs"])

uma_handler = UMA_Handler(g_wkh, oidc_client, g_config["check_ssl_certs"])
uma_handler.status()

app = Flask(__name__)
app.secret_key = ''.join(choice(ascii_lowercase) for i in range(30)) # Random key

def generateRSAKeyPair():
    _rsakey = RSA.generate(2048)
    private_key = _rsakey.exportKey()
    public_key = _rsakey.publickey().exportKey()

    file_out = open("config/private.pem", "wb+")
    file_out.write(private_key)
    file_out.close()

    file_out = open("config/public.pem", "wb+")
    file_out.write(public_key)
    file_out.close()

    return private_key, public_key

private_key, public_key = generateRSAKeyPair()

def create_jwt(payload, p_key):
    rsajwk = RSAKey(kid="RSA1", key=import_rsa_key(p_key))
    jws = JWS(payload, alg="RS256")
    return jws.sign_compact(keys=[rsajwk])

def split_headers(headers):
    headers_tmp = headers.splitlines()
    d = {}

    for h in headers_tmp:
        h = h.split(': ')
        if len(h) < 2:
            continue
        field=h[0]
        value= h[1]
        d[field] = value

    return d

def resolve_endpoint(proxy_path):
    base_url = proxy_path.split('/')[0]
    endpoints = g_config["proxy_endpoints"]
    for e in endpoints:
        if e["base_url"] == base_url:
            return e["resource_server_endpoint"]
    return None

def proxy_request(request,resource_server_endpoint):#, new_header):
    try:
        if request.method == 'POST':
            res = post(resource_server_endpoint+request.full_path, data=request.data, stream=False, verify=g_config["check_ssl_certs"])
        elif request.method == 'GET':
            res = get(resource_server_endpoint+request.full_path, stream=False, verify=g_config["check_ssl_certs"])
        elif request.method == 'PUT':
            res = put(resource_server_endpoint+request.full_path, data=request.data, stream=False, verify=g_config["check_ssl_certs"])
        elif request.method == 'DELETE':
            res = delete(resource_server_endpoint+request.full_path, stream=False, verify=g_config["check_ssl_certs"])
        else:
            response = Response()
            response.status_code = 501
            return response
        response = Response(res.content, res.status_code)
        return response
    except Exception as e:
        response = Response()
        print("Error while redirecting to resource: "+ traceback.format_exc(),file=sys.stderr)
        response.status_code = 500
        response.content = "Error while redirecting to resource: "+str(e)
        return response

@app.route("/<path:path>", methods=["GET","POST","PUT","DELETE"])
def resource_request(path):
    # Check for token
    print("Processing path: '"+path+"'")
    resource_server_endpoint = resolve_endpoint(path)
    if resource_server_endpoint is None:
        response = Response()
        response.status_code = 404
        return response
    rpt = request.headers.get('Authorization')
    # Get resource
    resource_id = uma_handler.get_resource_from_uri(resource_server_endpoint)
    print("FOUND RSID: "+resource_id)
    scopes = uma_handler.get_resource_scopes(resource_id)
    if rpt and resource_id is not None:
        print("Token found: "+rpt)
        rpt = rpt.replace("Bearer ","").strip()
        # Validate for a specific resource
        if uma_handler.validate_rpt(rpt, [{"resource_id": resource_id, "resource_scopes": scopes }], int(g_config["s_margin_rpt_valid"])) or not api_rpt_uma_validation:
            print("RPT valid, accessing...")
            request.full_path = request.full_path.replace(g_config["proxy_endpoint"], "")
            return proxy_request(request)
        print("Invalid RPT!, sending ticket")
        # In any other case, we have an invalid RPT, so send a ticket.
        # Fallthrough intentional
    print("No auth token, or auth token is invalid")
    response = Response()
    if resource_id is not None:
        print("Matched resource: "+str(resource_id))
        # Generate ticket if token is not present
        ticket = uma_handler.request_access_ticket([{"resource_id": resource_id, "resource_scopes": scopes }])
        # Return ticket
        response.headers["WWW-Authenticate"] = "UMA realm="+g_config["realm"]+",as_uri="+g_config["auth_server_url"]+",ticket="+ticket
        response.status_code = 401 # Answer with "Unauthorized" as per the standard spec.
        return response
    else:
        print("Could not find resource: "+str(e))
        response.status_code = 404
        return response


# Start reverse proxy for x endpoint
app.run(
    debug=g_config["debug_mode"],
    threaded=g_config["use_threads"],
    port=int(g_config["service_port"]),
    host=g_config["service_host"]
)
