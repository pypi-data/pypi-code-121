from pmanager.res import *


def initialize(namespace):

    try:
        with open("pmanager/changelog","r") as f:
            psuccess(f.read())
            f.close()
    except:
        perror("changelog file not found")