from requests import request
from pickle import load, dump
from datetime import datetime, timedelta
from random import randrange

import config as cfg
from hubstaff_auth import DoTokenRefresh

#import logging
#logging.basicConfig(filename='log\\hubstaff_api.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=cfg.config['loglevel'], datefmt='%Y-%m-%d %H:%M:%S')


def RetrieveToken() -> str:
    """Load hubstaff.lock, check token expiry, retrieve/refresh."""

    with open("hubstaff.lock", "rb") as hs_lock:
        authdata = load(hs_lock)
        print("Checking expiry...")
        if(authdata['expire'] <= datetime.now()):
            print("Token expired!\n Refreshing...")
            newauthdata = DoTokenRefresh(authdata['refresh'])
            print("We have new auth! Dumping...")

            expiry = datetime.now() + timedelta(seconds=85399)
            print("Token expires at: " + str(expiry))
            authdata = {
                "bearer": newauthdata['access_token'],
                "refresh": newauthdata['refresh_token'],
                "expire": expiry
            }

            with open("hubstaff.lock", "wb") as hs_lock:
                dump(authdata, hs_lock, protocol=4)
            return authdata['bearer']

        else:
            print("Token appears not to have expired. Returning token")  
            return authdata['bearer']


def CreateProject(summary, member) -> int:
    '''
    Create project in HubStaff

    :param str summary: Title of HubStaff Project as it will appear in the time tracking client
    :param int member: HubStaff Member ID to assign
    :return: ID of new HubStaff project
    :rtype: int
    '''

    hs_org_id = cfg.config['hs_org_id']
    url = cfg.config['hs_api_version'] + "organizations/" + str(hs_org_id) + "/projects"
    headers = {
        'Authorization': 'Bearer ' + RetrieveToken(),
        'Content-Type': 'application/json'
    }
    summary = summary[0:12]
    data = r"""{
    "name": %s",
    "members": [{
        "user_id": %d,
        "role": "user"
    }]
    }"""

    data = data % (summary, member)
    r = request("POST", url, headers=headers, data=data)
    hs_response = r.json().get('project')

    if(hs_response.get('error') == "Project name already exists"):
        print("Attempted to create a project that already exists!")
        # TODO: Handle this.
        raise Exception

    hs_project_id = hs_response.get('id')
    print("Hubstaff project ID: " + str(hs_project_id))
    return hs_project_id


def ArchiveProject(hs_project_id) -> bool:
    '''
    Archive project in HubStaff

    :param int hs_project_id: HubStaff Project ID for removal
    :return: Boolean value indicating success or failure
    '''

#    hs_org_id = cfg.config['hs_org_id']
    url = cfg.config['hs_api_version'] + "projects/" + str(hs_project_id)
    headers = {
        'Authorization': 'Bearer ' + RetrieveToken(),
        'Content-Type': 'application/json'
    }
    data = r"""{
        "status": "archived"
        }"""

    r = request("PUT", url, headers=headers, data=data)
    r = r.json()
    if(r.get('project').get('status') == 'archived'):
        print("Project archived!")
        return True
    else:
        print("There was an issue!")
        return False
        # TODO: Alert here
