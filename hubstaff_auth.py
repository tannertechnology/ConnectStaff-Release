# This file handles Hubstaff authentication.
# MMMMMMMM tasty spaghetti
from oic.oic import Client
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic import rndstr
from oic.utils.http_util import Redirect
from oic.oic.message import AuthorizationResponse, RegistrationResponse
from oic.oauth2.message import ErrorResponse

from http.server import HTTPServer, BaseHTTPRequestHandler
from requests import request
import re
from pathlib import Path
from sys import argv
from pickle import dump, load
from datetime import datetime, timedelta
from json import loads

import config as cfg


# TODO: Reorder this file
def Authorize(self, response):
    print("\n We have auth! Continuing...")
    aresp = client.parse_response(AuthorizationResponse, info=response, sformat="urlencoded")

#    code = aresp["code"] 
#    assert aresp["state"] == session["state"] # TODO: Remove this block
#    args = {"code": aresp["code"]}

    resp = client.do_access_token_request(state=aresp["state"],
                                          request_args=args)

    userinfo = client.do_user_info_request(state=aresp["state"])

    if(isinstance(userinfo, ErrorResponse)):
        resp = DoTokenRefresh(resp['refresh_token'])
        # Verify the token is a token here somehow, using pickle may be dangerous otherwise
        
        print("Wow we did it. Hubstaff initialized.")
        print("Writing access_token and refresh_token to file and testing the integration...")    
        
        expiry = datetime.now() + timedelta(seconds=85399)
        print("Token expires at: " + str(expiry))

        authdata = {
            "bearer": resp['access_token'],
            "refresh": resp['refresh_token'],
            "expire": expiry
        }
        
        with open("hubstaff.lock", "wb") as hs_lock:
            dump(authdata, hs_lock, protocol=4)

        print("Dumped auth data, enjoy!")
        print("EOF")


def DoTokenRefresh(refresh_token) -> dict:
    """Refreshes bearer token given refresh token"""
    # TODO: Actually check if provider_info has expired and refresh if so

    with open("provider_info", "rb") as discovery_cache:
        provider_info = load(discovery_cache)

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": cfg.config['scope']}

    r = request("POST", provider_info['token_endpoint'], 
                auth=(cfg.config['hs_clientid'], cfg.config['hs_clientsecret']),
                data=data)
    print("Successfully got new access token, info: \n")
    print(r.text)
    resp = loads(r.text)
    return resp


# Temporary server to get auth data from hubstaff
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.end_headers()

    def _html(self, message):
        # Blank response ( Aussie bandwidth is valuable! )
        # TODO: Test removal of these content statements, or change to None
        content = f""
        return content.encode("utf8")

    def do_GET(self):
        self._set_headers()

        match = re.match(r"\/auth\?(.*)", self.path)
        if(match):
            print("Auth attempt!\n")
            QUERY_STRING = match.group(1)
            Authorize(self, QUERY_STRING)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()


def WaitForAuth(server_class=HTTPServer, handler_class=S,
                addr="127.0.0.1", port=cfg.config['port']):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    print(f"Watching on {addr}:{port} for the auth response.\n")
    httpd.handle_request()


# Start of execution
if __name__ == "__main__":

    print("ConnectStaff :: hubstaff_auth.py by Tanner Anderson")
    print("Copyright 2020 Tanner Anderson")
    print("Licensed under GNU-AGPL-3.0")
    print("\n--------------------------------------------------\n")

    if(not Path('hubstaff.lock').exists()):
        print("Verified this is the first run.")
        Path('hubstaff.lock').touch()
    elif(argv.__len__() <= 1):
        print("You've run this before, run with './hubstaff_auth a' to force run.")
        exit()
    elif(argv.__len__() >= 1):
        if(argv[1] == "dev"):
            print("Development mode enabled")
            devmode = True
        print("You've decided to initialize hubstaff again. I wish you luck.")

    print("\n Performing first-time setup")

    redirect_uri = "http://" + cfg.config['redirect_uri'] + ":" + str(cfg.config['port']) + "/auth"
    session = {}
    client = Client(client_authn_method=CLIENT_AUTHN_METHOD)

    # Cache OIDC discovery for 1 week
    provider_info = client.provider_config(cfg.config['discover_url'])
    expiry = datetime.now() + timedelta(weeks=1)
    print("Discovery cache expires at: " + str(expiry))
    provider_info['expiry'] = expiry

    with open("provider_info", "wb") as discovery_cache:
        dump(provider_info, discovery_cache, protocol=4)

    args = {
        "redirect_uris": [redirect_uri]
    }

    # Manage out of band registration
    info = {"client_id": cfg.config['hs_clientid'],
            "client_secret": cfg.config['hs_clientsecret']}
    client_reg = RegistrationResponse(**info)
    client.store_registration_info(client_reg)

    session["state"] = rndstr()
    session["nonce"] = rndstr()
    args = {
        "client_id": client.client_id,
        "response_type": "code",
        "scope": [cfg.config['scope']],
        "nonce": session["nonce"],
        "redirect_uri": redirect_uri,
        "state": session["state"]
    }

    auth_req = client.construct_AuthorizationRequest(request_args=args)
    login_url = auth_req.request(client.authorization_endpoint)

    print("Now you need to copy-paste this to a browser on the machine this integration is running on.")
    print("Login url follows:\n")
    print(login_url)
    print("\n\n Waiting for successful authentication...")

    WaitForAuth()

    #TODO:  Think about calling all functions down here instead of from other fucntions for initial setup (init(), waitforauth(x, x), RefreshToken()
