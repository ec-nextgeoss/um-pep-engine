from base64 import b64encode
from WellKnownHandler import TYPE_OIDC, KEY_OIDC_TOKEN_ENDPOINT

def get_new_pat(wkh, oidc_client, client_id: str, client_secret: str, verify_ssl: bool = False):
    """
    Returns a new PAT using the OIDC client credentials in config
    """
    # Get PAT
    client_creds = b64encode(bytes(client_id+":"+client_secret, 'utf-8')) # Basic auth
    token_endpoint =  wkh.get(TYPE_OIDC, KEY_OIDC_TOKEN_ENDPOINT)
    token = oidc_client.postRequestToken(token_endpoint , token = client_creds, verify = verify_ssl)
    if "access_token" in token:
        return token["access_token"]
    
    raise Exception("Unexpected error getting a PAT: "+str(token))
