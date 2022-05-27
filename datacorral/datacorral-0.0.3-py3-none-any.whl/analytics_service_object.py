import httplib2
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client import tools
#import argparse


def prepare_credentials(token_file_name):
    #parser = argparse.ArgumentParser(parents=[tools.argparser])
    #flags = parser.parse_args()
    # Retrieve existing credendials
    storage = Storage(token_file_name)
    credentials = storage.get()
    # If no credentials exist, we create new ones
    #if credentials is None or credentials.invalid:
    #    credentials = tools.run_flow(FLOW, storage, flags)
    return credentials


def initialize_service(token_file_name):
    # Creates an http object and authorize it using
    # the function prepare_creadentials()
    http = httplib2.Http()
    credentials = prepare_credentials(token_file_name)
    http = credentials.authorize(http)
    # Build the Analytics Service Object with the authorized http object
    return build('analytics', 'v3', http=http)

#if __name__ == '__main__':
#    service = initialize_service(token_file_name)
