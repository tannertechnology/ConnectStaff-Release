config = {
    'baseurl': '', # Connectwise instance url (connectwise.dorks.com.au for example)
    'companyname': '',
    'publickey': '',
    'privatekey': '',
    'clientid': '',
    'api_version': '2019.5',
    'callback_domain': '',
    'port': 11103,
    'listen_address': '0.0.0.0',

    # Hubstaff follows
    'hs_clientid': '',
    'hs_clientsecret': '',
    'redirect_uri': 'localhost',  # Domain only here, will always call http://{redirect_uri}:{port}/auth
    'hs_org_id':  ,

    # More stuff not to touch
    'scope': 'openid hubstaff:write hubstaff:read',
    'discover_url': 'https://account.hubstaff.com',
    'hs_api_version': 'https://api.hubstaff.com/v2/',
    'loglevel': 'INFO'
  }


members = {'tanner': 000000}
