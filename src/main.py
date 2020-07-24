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
from custom_mongo import Mongo_Handler
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
# Demo: register a new resource if it doesn't exist
try:
    uma_handler.create("ADES Service", ["Authenticated"], description="", icon_uri="/ADES")
except Exception as e:
    if "already exists" in str(e):
        print("Resource already existed, moving on")
    else: raise e

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

def proxy_request(request, new_header):
    try:
        if request.method == 'POST':
            res = post(g_config["resource_server_endpoint"]+"/"+request.full_path, headers=new_header, data=request.data, stream=False)           
        elif request.method == 'GET':
            res = get(g_config["resource_server_endpoint"]+"/"+request.full_path, headers=new_header, stream=False)
        elif request.method == 'PUT':
            res = put(g_config["resource_server_endpoint"]+"/"+request.full_path, headers=new_header, data=request.data, stream=False)           
        elif request.method == 'DELETE':
            res = delete(g_config["resource_server_endpoint"]+"/"+request.full_path, headers=new_header, stream=False)
        else:
            response = Response()
            response.status_code = 501
            return response
        excluded_headers = ['transfer-encoding']
        headers = [(name, value) for (name, value) in     res.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(res.content, res.status_code, headers)
        return response
    except Exception as e:
        response = Response()
        print("Error while redirecting to resource: "+ traceback.format_exc(),file=sys.stderr)
        response.status_code = 500
        response.content = "Error while redirecting to resource: "+str(e)
        return response

@app.route(g_config["proxy_endpoint"], defaults={'path': ''})
@app.route(g_config["proxy_endpoint"]+"/<path:path>", methods=["GET","POST","PUT","DELETE"])
def resource_request(path):
    # Check for token
    print("Processing path: '"+path+"'")
    custom_mongo = Mongo_Handler()
    rpt = request.headers.get('Authorization')
    # Get resource
    resource_id = custom_mongo.get_id_from_uri(path)
    scopes = uma_handler.get_resource_scopes(resource_id)
    if rpt:
        print("Token found: "+rpt)
        rpt = rpt.replace("Bearer ","").strip()
        # Validate for a specific resource
        if uma_handler.validate_rpt(rpt, [{"resource_id": resource_id, "resource_scopes": scopes }], int(g_config["s_margin_rpt_valid"])) or not api_rpt_uma_validation:
            print("RPT valid, accesing ")
            introspection_endpoint=g_wkh.get(TYPE_UMA_V2, KEY_UMA_V2_INTROSPECTION_ENDPOINT)
            pat = oidc_client.get_new_pat()
            rpt_class = class_rpt.introspect(rpt=rpt, pat=pat, introspection_endpoint=introspection_endpoint, secure=False)
            jwt_rpt_response = create_jwt(rpt_class, private_key)

            headers_splitted = split_headers(str(request.headers))
            headers_splitted['Authorization'] = "Bearer "+str(jwt_rpt_response)

            new_header = Headers()
            for key, value in headers_splitted.items():
                new_header.add(key, value)
            # redirect to resource
            return proxy_request(request, new_header)
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
        print("No matched resource, passing through to resource server to handle")
        # In this case, the PEP doesn't have that resource handled, and just redirects to it.
        try:
            cont = get(g_config["resource_server_endpoint"]+"/"+path).content
            return cont
        except Exception as e:
            print("Error while redirecting to resource: "+str(e))
            response.status_code = 500
            return response
            
@app.route("/resources", methods=["GET"])
def getResourceList():
    print("Retrieving all registed resources...")
    resources = uma_handler.get_all_resources()
    rpt = request.headers.get('Authorization')
    response = Response()
    resourceListToReturn = []
    resourceListToValidate = []
    if rpt:
        print("Token found: " + rpt)
        rpt = rpt.replace("Bearer ","").strip()
        #Token was found, check for validation
        for rID in resources:
            #In here we will use the loop for 2 goals: build the resource list to validate (all of them) and the potential reply list of resources, to avoid a second loop
            scopes = uma_handler.get_resource_scopes(rID)
            resourceListToValidate.append({"resource_id": rID, "resource_scopes": scopes })
            r = uma_handler.get_resource(rID)
            entry = {'_id': r["_id"], 'name': r["name"]}
            resourceListToReturn.append(entry)
        if uma_handler.validate_rpt(rpt, resourceListToValidate, g_config["s_margin_rpt_valid"]) or not api_rpt_uma_validation:
            return json.dumps(resourceListToReturn)
    print("No auth token, or auth token is invalid")
    if resourceListToValidate:
        # Generate ticket if token is not present
        ticket = uma_handler.request_access_ticket(resourceListToValidate)

        # Return ticket
        response.headers["WWW-Authenticate"] = "UMA realm="+g_config["realm"]+",as_uri="+g_config["auth_server_url"]+",ticket="+ticket
        response.status_code = 401 # Answer with "Unauthorized" as per the standard spec.
        return response
    response.status_code = 500
    return response

@app.route("/resources/<resource_id>", methods=["GET", "PUT", "POST", "DELETE"])
def resource_operation(resource_id):
    print("Processing " + request.method + " resource request...")
    response = Response()

    #add resource is outside of rpt validation, as it only requires a client pat to register a new resource
    try:
        if request.method == "POST":
            if request.is_json:
                data = request.get_json()
                if data.get("name") and data.get("resource_scopes") and data.get("name") == resource_id:
                    return uma_handler.create(data.get("name"), data.get("resource_scopes"), data.get("description"), data.get("icon_uri"))
                else:
                    response.status_code = 500
                    response.headers["Error"] = "Invalid data or incorrect resource name passed on URL called for resource creation!"
                    return response
    except Exception as e:
        print("Error while creating resource: "+str(e))
        response.status_code = 500
        response.headers["Error"] = str(e)
        return response

    pat = request.headers.get('Authorization')
    if pat:
        #Token was found, check for validation
        print("Found pat in request, validating...")
        pat = pat.replace("Bearer ","").strip()
        if oidc_client.is_pat_valid(pat):
            print("PAT valid, proceding...")
            try:
                #retrieve resource
                if request.method == "GET":
                    return uma_handler.get_resource(resource_id)
                #update resource
                elif request.method == "PUT":
                    if request.is_json:
                        data = request.get_json()
                        if data.get("name") and data.get("resource_scopes"):
                            uma_handler.update(resource_id, data.get("name"), data.get("resource_scopes"), data.get("description"), data.get("icon_uri"))
                            response.status_code = 200
                            return response
                #delete resource
                elif request.method == "DELETE":
                    uma_handler.delete(resource_id)
                    response.status_code = 204
                    return response
            except Exception as e:
                print("Error while redirecting to resource: "+str(e))
                response.status_code = 500
                return response
        
    print("No auth token, or auth token is invalid")
    response.status_code = 401
    return response
    


# Start reverse proxy for x endpoint
app.run(
    debug=g_config["debug_mode"],
    threaded=g_config["use_threads"],
    port=int(g_config["service_port"]),
    host=g_config["service_host"]
)
