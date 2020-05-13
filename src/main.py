#!/usr/bin/env python3

from eoepca_oidc import OpenIDClient
from eoepca_uma import rpt, resource
from WellKnownHandler import WellKnownHandler, TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT
from WellKnownHandler import KEY_UMA_V2_INTROSPECTION_ENDPOINT, KEY_UMA_V2_PERMISSION_ENDPOINT

from flask import Flask, request
from random import choice
from string import ascii_lowercase

from config import load_config
from custom_oidc import OIDCHandler
### INITIAL SETUP
# Global config objects
g_config, g_resources_cfg = load_config("config/config.json", "config/resources.json")

# Global handlers
g_wkh = WellKnownHandler(g_config["auth_server_url"], secure=False)
oidc_client = OIDCHandler(g_wkh,
                            client_id = g_config["client_id"],
                            client_secret = g_config["client_secret"],
                            redirect_uri = "None", # TODO
                            scopes = ['openid', 'uma_protection', 'permission'],
                            verify_ssl = g_config["check_ssl_certs"])

pat = oidc_client.get_new_pat()
print("GOT PAT: "+str(pat))

# Register a default resource "ADES Service". UMA scope "Authenticated", and endpoint URI.
name = "ADES Service"
resource_registration_endpoint = g_wkh.get(TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT)
scopes = ["Authenticated"]
icon_uri = "/ADES" # TODO
new_resource_id = resource.create(pat, resource_registration_endpoint, name, scopes, icon_uri= icon_uri, secure = g_config["check_ssl_certs"])
print("Created:")
print(new_resource_id)

# Start reverse proxy for x endpoint
app = Flask(__name__)
app.secret_key = ''.join(choice(ascii_lowercase) for i in range(30)) # Random key
app.run(
    debug=g_config["debug_mode"],
    threaded=g_config["use_threads"],
    port=g_config["service_port"],
    host=g_config["service_host"]
)

###########

@app.route(g_config["proxy_endpoint"], methods=["GET"])
def resource_request():
    # Check for token
    pat = "" # TODO
    rpt = request.headers.get('authorization')
    if not rpt:
        # Generate ticket if token is not present
        permission_endpoint = g_wkh.get(TYPE_UMA_V2, KEY_UMA_V2_PERMISSION_ENDPOINT)
        resources = [] # TODO
        ticket = resource.request_access_ticket(pat, permission_endpoint, resources, secure = g_config["check_ssl_certs"])

        # Return ticket
        # TODO:

    else:
        # TODO: Validate for a specific resource
        rpt = rpt.replace("Bearer ","").strip()
        # validate token for access.
        introspection_endpoint = g_wkh.get(TYPE_UMA_V2, KEY_UMA_V2_INTROSPECTION_ENDPOINT)
        if rpt.is_valid_now(rpt, pat, introspection_endpoint, time_margin= g_config["s_margin_rpt_valid"] ,secure= g_config["check_ssl_certs"] ):
            print("RPT valid")
            # TODO: redirect to resource
