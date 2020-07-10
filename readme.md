There is a lot more work to do on this, currently it syncs assignments (press assign me in cw and the ticket appears in hubstaff, delete (not mark done) the assignment and hubstaff will delete the associated project.)

Consider it abandoned as we finally left ConnectWise back in December and I only just got around to uploading my progress. I am happy to help but would need access to a test instance of ConnectWise Manage. 


# ConnectStaff by Tanner Anderson
###  Connects ConnectWise Manage and HubStaff for better time tracking for all! 

The current release is v0.1a


## Setup Instructions:
Step 1: Callback is configured in CW -> Integrator Login, create a new member, you don't need to save or use the creds, and select the schedule callback. Point it to http://localhost:11103/sched if running on your cw server.

Step 2: Modify sample_config.py and save as config.py

Step 3: Run hubstaff.py and ensure the tests pass

Step 4: Run server.py, this should be daemonized somehow (windows service)

## Config options:
* baseurl: URL of your connectwise instance without protocol or trailing slack (connectwise.domain.com)
* companyname: The company name you use to log in
* Public and Private keys: Keys you generate against an API member in ConnectWise
* ClientID: New ConnectWise requirement, link to generate: https://developer.connectwise.com/ClientID
* callback_domain: domain name that the callback listener is hosted behind. Following the same rules as baseurl. 
* Port: default is 11103, if you change it here ensure you change the port number when entering in ConnectWise
* hs_org_id and the user mapping: See [Hubstaff ID Config](#Hubstaff-IDS)
* hs_clientid and secret: https://developer.hubstaff.com/apps | For redirect urls specify http://localhost:8081/auth

<hr />

### Hubstaff IDS
1) You need your org id, this is found by logging in and checking the url, if you go to the dashboard the numbers between /dashboard/ and /team are your org id /dashboard/000000/team

2) Find your user IDs, in Hubstaff go to Activity -> Screenshots and filter to the member you want. Check the end of the URL for [user]=000000

3) Now fill the member mapping in config.py. First the CW member's login username, second the id number that correlates in hubstaff.

<br />
<hr />
<br />

### Extra details:
#### Supported Python versions:
Any officially supported version.

Tested on Windows, all code is platform agnostic

This application should be firewalled, it should not be considered secure.

### TODO:
* Ability to shut down and start this application without losing the IDMap (but also ideally without excessive IO cycles)
* Move this list to github issues/a project board
* Move a bunch of the other stuff to a github wiki
* Standardize naming
* Squash commits to remove creds I published
* Add time note syncing
* Select a license (Maybe using apache 2.0 license, more research needed.)
* create requirements.txt and package for pip
* This may be able to be made more efficient moving the actual api calling out of server.py, I am not sure.
* Exception handling
* Coverage > 0%
* Move archive folder to a branch or another repo

### Not planned:

* Implement repsonse verification (https://developer.connectwise.com/Best_Practices/Manage_Callbacks?mt-learningpath=manage)
* Replace regex with a json library where applicable

### See requirements.txt for the software this project utilizes

