#!/usr/bin/env python3

from WellKnownHandler import WellKnownHandler

from flask import Flask, request, Response
from random import choice
from string import ascii_lowercase
from requests import get
import json

from config import load_config, save_config
from eoepca_scim import EOEPCA_Scim, ENDPOINT_AUTH_CLIENT_POST
from custom_oidc import OIDCHandler
from custom_uma import UMA_Handler

### INITIAL SETUP
# Global config objects
g_config = load_config("config/config.json")

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
    print("NEW CLIENT created with ID '"+new_client["client_id"]+"', since no client config was found on config.json")

    g_config["client_id"] = new_client["client_id"]
    g_config["client_secret"] = new_client["client_secret"]
    save_config("config/config.json", g_config)
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


@app.route(g_config["proxy_endpoint"], defaults={'path': ''})
@app.route(g_config["proxy_endpoint"]+"/<path:path>", methods=["GET"])
def resource_request(path):
    # Check for token
    print("Processing path: '"+path+"'")
    rpt = request.headers.get('Authorization')
    # Get resource
    resource_id, scopes = uma_handler.resource_exists("/"+path) # TODO: Request all scopes? How can a user set custom scopes?
    response = Response()
    if rpt:
        print("Token found: "+rpt)
        rpt = rpt.replace("Bearer ","").strip()
        # Validate for a specific resource
        if uma_handler.validate_rpt(rpt, [{"resource_id": resource_id, "resource_scopes": scopes }], g_config["s_margin_rpt_valid"]) or not api_rpt_uma_validation:
            print("RPT valid, accesing ")
            # redirect to resource
            try:
                cont = get(g_config["resource_server_endpoint"]+"/"+path).content
                return cont
            except Exception as e:
                print("Error while redirecting to resource: "+str(e))
                response.status_code = 500
                return response

        print("Invalid RPT!, sending ticket")
        # In any other case, we have an invalid RPT, so send a ticket.
        # Fallthrough intentional

    print("No auth token, or auth token is invalid")
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

    rpt = request.headers.get('Authorization')
    # Get resource scopes from resource_id
    scopes = uma_handler.get_resource_scopes(resource_id)
    if rpt:
        #Token was found, check for validation
        print("Found rpt in request, validating...")
        rpt = rpt.replace("Bearer ","").strip()
        if uma_handler.validate_rpt(rpt, [{"resource_id": resource_id, "resource_scopes": scopes }], g_config["s_margin_rpt_valid"]) or not api_rpt_uma_validation:
            print("RPT valid, proceding...")
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
    #Scopes have already been queried at this time, so if they are not None, we know the resource has been found. This is to avoid a second query.
    if scopes is not None:
        print("Matched resource: "+str(resource_id))
        # Generate ticket if token is not present
        ticket = uma_handler.request_access_ticket([{"resource_id": resource_id, "resource_scopes": scopes }])

        # Return ticket
        response.headers["WWW-Authenticate"] = "UMA realm="+g_config["realm"]+",as_uri="+g_config["auth_server_url"]+",ticket="+ticket
        response.status_code = 401 # Answer with "Unauthorized" as per the standard spec.
        return response
    else:
        print("Error, resource not found!")
        response.status_code = 500
        return response
    


# Start reverse proxy for x endpoint
app.run(
    debug=g_config["debug_mode"],
    threaded=g_config["use_threads"],
    port=g_config["service_port"],
    host=g_config["service_host"]
)
