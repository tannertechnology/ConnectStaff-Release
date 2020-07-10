from http.server import HTTPServer, BaseHTTPRequestHandler
from base64 import b64encode
import config as cfg
import re
from requests import request
import logging
from os.path import exists
from os import makedirs

from hubstaff_api import CreateProject, ArchiveProject

# Initialize authentication/headers
authstring = cfg.config['companyname'] + "+" + cfg.config['publickey'] + ":" + cfg.config['privatekey']
baseurl = "https://" + cfg.config['baseurl'] + "/v4_6_release/apis/3.0/"
encoded = authstring.encode('utf-8')
auth = b64encode(encoded)
headers = {'Accept': 'application/vnd.connectwise.com+json; version='
           + cfg.config['api_version'],
           'clientid': cfg.config['clientid'],
           'Authorization': 'Basic ' + auth.decode()}

# Data structure for storing summary -> schedule id mappings
IDMap = {}
"""
    ConnectWise Schedule ID: hs_projectid
"""

# Configure Logger
if not exists('log'):
    makedirs('log')
loglevel = cfg.config['loglevel']
logging.basicConfig(filename='log\\server.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=loglevel, datefmt='%Y-%m-%d %H:%M:%S')


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.end_headers()

    def _html(self, message):
        # Blank response
        content = f""
        return content.encode("utf8")

    def do_GET(self):
        # Do not handle GET
        self._set_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        _post_data = post_data.decode('utf-8')
        CheckMember(_post_data)


def CheckMember(data):
    '''
    Checks data for member and passes to next function if data is valid

    :param str data: Full data blob recieved from ConnectWise (Schedule record)
    '''
    pattern = "\"MemberId\":\"=\","

    for member in cfg.members:
        logging.info("Checking member: " + member)
        _pattern = pattern.replace("=", member)
        rx = re.search(_pattern, data)
        if rx:
            ParseOperation(data, member)
            return 0
        else:
            logging.info("The data I recieved did not have a valid member, ignoring.")


def ParseOperation(scheduledata, member):
    '''
    Parses the CW blob for the operation to perform in Hubstaff and passes to GetTicketNumber if add, ArchiveProject if delete

    :param str scheduledata: Full data blob recieved from ConnectWise (Schedule record)
    :param int member: Hubstaff member ID to operate against
    '''
    Padd = "\"Action\":\"Added\","
    Pdel = "\"Action\":\"Deleted\","

    if(re.search(Padd, scheduledata)):
        GetTicketNumber(scheduledata, member)
        return 0
    elif(re.search(Pdel, scheduledata)):
        # Remove from hubstaff here

        # Find ScheduleID
        Pid = ",\"ID\":(\d*),"
        match = re.search(Pid, scheduledata)
        ScheduleID = match.group(1)
        hs_project_id = IDMap.pop(ScheduleID)
        ArchiveProject(hs_project_id)
        logging.info("Schedule removed for member " + member + " ScheduleID: " + str(ScheduleID))
        return 0
    else:
        logging.error("No ticket number found.")
        logging.error("Here is the scheduledata:\n")
        logging.error(scheduledata)
        # Alert here
        return 1


def GetTicketNumber(scheduledata, member) -> int:
    '''Calls ConnectWise API to get ticket number from schedule number.

    :param str scheduledata: Full data blob recieved from ConnectWise (Schedule record)
    :param str member: Hubstaff member ID to operate against

    :return: ConnectWise Ticket Number or nothing on error
    '''
    Pid = r",\"ID\":(\d*),"
    match = re.search(Pid, scheduledata)
    ScheduleID = match.group(1)
    Pticket = "\\\\\"ObjectId\\\\\":(\d*),"
    match = re.search(Pticket, scheduledata)

    if(match):
        logging.info("Found Ticket Number: " + match.group(1))
        GetTicketSummary(match, member, ScheduleID)
        return match.group(1)
    else:
        error = "While searching for a ticket number that should exist I failed. \n" + "Data: " + scheduledata + "\nMember: " + member
        logging.error(error)
        return


def GetTicketSummary(ticketnumber, member, ScheduleID):
    '''
    Calls ConnectWise API to get ticket summary
    
    :param int ticketnumber: ConnectWise ticket number
    :param int member: Hubstaff Member ID
    :param int ScheduleID: ConnectWise Schedule ID
    '''

    url = baseurl + "service/tickets/" + str(ticketnumber)
    Psummary = "\"summary\":([\"])(?:(?=(\\\\?))\\2.)*?\\1"
    r = request("GET", url, headers=headers)
    summary = re.search(Psummary, r.text)
    if(summary):
        parsedsummary = summary.group(0)
        parsedsummary = parsedsummary.split(":")
        parsedsummary = parsedsummary[1]
        summary = str(ticketnumber) + parsedsummary

        hsmember = cfg.members.get(member)
        hs_project_id = CreateProject(summary, hsmember)
        logging.info("Added project " + str(hs_project_id) + " to hubstaff and documented. All done.")
    return 0


def run(server_class=HTTPServer, handler_class=S,
        addr=cfg.config['listen_address'], port=cfg.config['port']):
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting http server on {addr}:{port}")
    httpd.serve_forever()


run()
