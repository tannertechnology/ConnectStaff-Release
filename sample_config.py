# Rename this to config.py and fill the values according to readme.md
config = {
    'baseurl': 'support.domain.test',  # This is the domain pointing at your connectwise instance without protocol or trailing slash.
    'companyname': 'yourmsp',  # The company name you use to log into CW
    'publickey': 'cwpublickey',  # Your ConnectWise public key attached to an API member
    'privatekey': 'cwprivatekey', # Your ConnectWise private key attached to an API member
    'clientid': 'cwclientid',  # A client ID generated at: https://developer.connectwise.com/ClientID CW requires this now for reporting
    'callback_domain': 'cs.domain.test', # The doman pointing to this callback, again no protocol or trailing slash. Currently this does not support SSL but could be modified.

    # Usually don't need to touch these
    'port': 11103,  # Port callback listener runs on
    'listen_address': 'localhost',  # Address callback listener runs on
    'api_version': '2019.5'  # API Version this is compatible with, will try to keep an eye out for breaking changes.
  }
  
# A mapping between ConnectWise and HubStaff users. Supports as many users as you want. If a user has the same name between both services you must still fill both fields.
members = {'johncw': 'johnhubstaff',
           'user1': 'user1'}