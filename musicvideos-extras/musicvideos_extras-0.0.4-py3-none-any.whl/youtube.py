import os
import logging
import httplib2

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.http import MediaFileUpload
from oauth2client.tools import run_flow

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='\033[92;1m| INFO | \033[0m%(message)s')

def upload(client_secrets=None, video_file=None, thumbnail=None, visibility='private',
            category='10', title='video title', description='video description', tags=[]):

    '''
    This function will upload a video to youtube,
    requires client_secrets.json file.
    If you do not have one, you can
    create an application in https://console.cloud.google.com/apis/dashboard
    and then download the client_secrets.json
    '''

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    api_service_name = "youtube"
    api_version = "v3"

    logger.debug('Checking arguments...')
    variables = [('client_secrets', client_secrets), ('video_file', video_file)]
    for i in variables:
        if i[1] is None:
            print(f'{i[0]} is not defined')
            return

    # Get credentials and create an API client
    logger.debug('Checking client_secrets...')
    missing_secrets = 'client_secrets missing'
    flow = flow_from_clientsecrets(client_secrets, scopes, message=missing_secrets)

    logger.debug('Getting oauth2 file thing...')
    storage = Storage(f'auto-login-oauth2.json')
    credentials = storage.get()

    logger.debug('Checking credentials...')
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    credentials_authorize = credentials.authorize(httplib2.Http())
    youtube =  googleapiclient.discovery.build(api_service_name, api_version, http=credentials_authorize)

    request = youtube.videos().insert(
        media_body=MediaFileUpload(video_file),
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category,

            },

            "status": {
                "privacyStatus": visibility
          }

        }

    )

    logger.info('Sending video insert request...')
    response = request.execute()

    if 'uploaded' in response['status']['uploadStatus']:
        if thumbnail is not None:
            thumbnail_request = youtube.thumbnails().set(videoId=response['id'], media_body=thumbnail)
            thumbnail_response = thumbnail_request.execute()

        print('Title: "{}"'.format(response['snippet']['title']))
        print('ID: {}'.format(response['id']))
        print('URL: https://youtu.be/{}'.format(response['id']))
        print('Status: {}'.format(response['status']['uploadStatus']))

'''

Exemple:

upload(client_secrets='client_secrets.json', video_file='video.mp4', thumbnail='thumbnail.png', category='10',
                title='gec', description='crazy description', tags=['t','a','g','s'])

'''