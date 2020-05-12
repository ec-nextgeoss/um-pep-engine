#!/usr/bin/env python3

from eoepca_oidc import OpenIDClient
from eoepca_uma import rpt, resource
from WellKnownHandler import WellKnownHandler, TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT
from WellKnownHandler import TYPE_OIDC, KEY_OIDC_TOKEN_ENDPOINT
from WellKnownHandler import KEY_UMA_V2_INTROSPECTION_ENDPOINT, KEY_UMA_V2_PERMISSION_ENDPOINT

from flask import Flask, request
from json import load
from random import choice
from string import ascii_lowercase
from base64 import urlsafe_b64encode

### INITIAL SETUP
# Done in a global context to be able to access the handlers from any point
config = {}
with open("config/config.json") as j:
    config = load(j)

resources_cfg = {}
# setup config
with open("config/resources.json") as j:
    resources_cfg = load(j)

authserver_url=config["auth_server_url"]
wkh = WellKnownHandler(authserver_url, secure=False)

print("OIDC CLIENT TODO")
# Register as OIDC Client with uma_protection, permission scopes.
# Flow = client_credentials
oidc_client = OpenIDClient(issuer = authserver_url,
                            scope = 'openid uma_protection permission',
                            redirect_uri = None, # TODO
                            authType = "Basic")
print("OIDC CLIENT DONE")
# Register a default resource "ADES Service". UMA scope "Authenticated", and endpoint URI.
pat = "" # TODO
name = "ADES Service"
resource_registration_endpoint = wkh.get(TYPE_UMA_V2, KEY_UMA_V2_RESOURCE_REGISTRATION_ENDPOINT)
print(resource_registration_endpoint)
scopes = [""] # TODO
icon_uri = "" # TODO
resource.create(pat, resource_registration_endpoint, name, scopes, icon_uri, secure = config["check_ssl_certs"])

# Start reverse proxy for x endpoint
app = Flask(__name__)
app.secret_key = ''.join(choice(ascii_lowercase) for i in range(30)) # Random key
app.run(
    debug=config["debug_mode"],
    threaded=config["use_threads"],
    port=config["service_port"],
    host=config["service_host"]
)

###########

def get_new_pat(client_id: str, client_secret: str, verify_ssl: bool = False):
    """
    Returns a new PAT using the OIDC client credentials in config
    """
    # Get PAT
    uri_list = [{"token_endpoint" : wkh.get(TYPE_OIDC, KEY_OIDC_TOKEN_ENDPOINT) }]
    client_creds = urlsafe_b64encode(client_id+":"+client_secret) # Basic auth

    oidc_client.postRequestToken(uri_list, token = client_creds, verify = verify_ssl)
    return oidc_client.token

@app.route(config["proxy_endpoint"], methods=["GET"])
def resource_request():
    # Check for token
    pat = "" # TODO
    rpt = request.headers.get('authorization')
    if not rpt:
        # Generate ticket if token is not present
        permission_endpoint = wkh.get(TYPE_UMA_V2, KEY_UMA_V2_PERMISSION_ENDPOINT)
        resources = [] # TODO
        ticket = resource.request_access_ticket(pat, permission_endpoint, resources, secure = config["check_ssl_certs"])

        # Return ticket
        # TODO:

    else:
        rpt = rpt.replace("Bearer ","").strip()
        # validate token for access.
        introspection_endpoint = wkh.get(TYPE_UMA_V2, KEY_UMA_V2_INTROSPECTION_ENDPOINT)
        if rpt.is_valid_now(rpt, pat, introspection_endpoint, time_margin= config["s_margin_rpt_valid"] ,secure= config["check_ssl_certs"] ):
            print("RPT valid")
            # TODO: redirect to resource
