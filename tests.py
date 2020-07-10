from hubstaff_api import CreateProject, ArchiveProject
from random import randrange

import config as cfg


def test_hubstaff_projects():
    if(ArchiveProject(CreateProject("Testttt" + str(randrange(0, 101, 2)), cfg.members.get('tanner')))):
        print("Test suite for Hubstaff projects completed sucessfully!")
    else:
        raise Exception
    