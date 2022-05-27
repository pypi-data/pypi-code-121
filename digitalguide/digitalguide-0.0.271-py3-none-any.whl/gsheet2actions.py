import yaml
from openpyxl import load_workbook
import pickle
import os
from typing import DefaultDict, List
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
import datetime

from collections import defaultdict

from digitalguide.standardinteraktion.Interaktion import Interaktion


def Create_Service(client_secret_file, api_name, api_version, *scopes):
    print(client_secret_file, api_name, api_version, scopes, sep='-')
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    print(SCOPES)

    cred = None

    pickle_file = f'token_{API_SERVICE_NAME}_{API_VERSION}.pickle'
    # print(pickle_file)

    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            cred = flow.run_local_server()

        with open(pickle_file, 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
        print(API_SERVICE_NAME, 'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        return None

def sheed_id2excel(service, sheet_id, excel_file):
    byteData = service.files().export_media(
        fileId=sheet_id,
        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ).execute()

    with open(excel_file, "wb") as f:
        f.write(byteData)



def excel2dict(sheet, interaktion_spalte, poi_spalte, aktion_spalte, format_spalte, inhalt_spalte, max_row=None):

    excel_dict = defaultdict(
        lambda: defaultdict(
                list
            )
        )
    previous_interaktion=""
    previous_pio=""
    previous_aktion=""

    for row in sheet.iter_rows(min_row=2, max_row=max_row):
        if row[interaktion_spalte] or row[poi_spalte] or row[aktion_spalte] or row[format_spalte] or row[inhalt_spalte]:

            if row[interaktion_spalte].value == None:
                interaktion = previous_interaktion
            else:
                interaktion = row[interaktion_spalte].value
                previous_interaktion = interaktion

            if row[poi_spalte].value == None:
                poi = previous_pio
            else:
                poi = row[poi_spalte].value
                previous_pio = poi

            if row[aktion_spalte].value == None:
                aktion = previous_aktion
            else:
                aktion = row[aktion_spalte].value
                previous_aktion = aktion

            if row[format_spalte].value == None:
                ValueError("Empty Field in {}".format(row[format_spalte]))
            else:
                format = row[format_spalte].value

            if row[inhalt_spalte].value == None:
                ValueError("Empty Field in {}".format(row[inhalt_spalte]))
            else:
                inhalt = row[inhalt_spalte].value

            excel_dict[(poi, interaktion)][aktion].append((format, inhalt))
    
    return excel_dict