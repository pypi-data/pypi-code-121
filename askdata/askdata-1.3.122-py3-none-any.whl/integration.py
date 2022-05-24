import pandas as pd

import requests

from oauth2client.service_account import ServiceAccountCredentials

from googleapiclient.discovery import build
from requests.adapters import HTTPAdapter
from urllib3 import Retry

import json


""" 
Read google sheet as dataframe


If you read with API, you need to use spreadsheetId and credentials (it is the json file in same notebook folder).
you also need to add the account email associated to the credentials as user shared in the google sheet.

"""
def read_gsheet(spreadsheetId, credentials = None, sheet = None, 

                valueRenderOption = 'FORMATTED_VALUE', dateTimeRenderOption = 'SERIAL_NUMBER'):
    

    if credentials is None:

        post_url = "https://api.askdata.com/smartnotebook/readGsheet"
        
        body = {
            "spreadsheetId": spreadsheetId,
            "sheet": sheet,
            "valueRenderOption": valueRenderOption,
            "dateTimeRenderOption": dateTimeRenderOption
        }
        
        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))
        headers = {
            "Content-Type": "application/json"
        }
        r = s.post(url=post_url, json=body, headers=headers)
        r.raise_for_status()
        
        df = pd.DataFrame(json.loads(r.json()))

    else: 

        scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        cred = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        
        service = build('sheets', 'v4', credentials=cred)
    
        sheet_service = service.spreadsheets()
        
        range = 'A1:WWW500000'
        
        if sheet is not None:
            
            range = '%s!%s'%(sheet, range)
        
        result_input = sheet_service.values().get(spreadsheetId = spreadsheetId,
                                          range = range,
                                          valueRenderOption = valueRenderOption,
                                          dateTimeRenderOption = dateTimeRenderOption).execute()
        
        values_input = result_input.get('values', [])
        
        df = pd.DataFrame(values_input[1:], columns=values_input[0])

    return df


""" 
Read hubspot contacts as dataframe
Usage example: read_hubspot_contacts(api_key)
"""


def read_hubspot_contacts(api_key, offset=100):
    from askdata.integrations import hubspot
    return hubspot.get_contacts_df(api_key, offset)


""" 
Read alpha vantage api
Usage example: read_alphavantage_stock(api_key, symbols)
"""


def read_alphavantage_stock(symbols, api_key):
    from askdata.integrations import alphavantage
    return alphavantage.get_daily_adjusted_df(symbols, api_key)


def normalize_columns(df: pd.DataFrame):
    problematicChars = [",", ";", ":", "{", "}", "(", ")", "=", ">", "<", ".", "!", "?"]
    new_cols = {}
    for column in df.columns:

        columnName = column.lower()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        columnName = columnName.replace(" ", "_")
        columnName = columnName.replace("-", "_")
        columnName = columnName.replace("/", "_")
        columnName = columnName.replace("\\", "_")
        columnName = columnName.replace("%", "perc")
        columnName = columnName.replace("+", "plus")
        columnName = columnName.replace("&", "and")
        columnName = columnName.replace("cross", "cross_pass")
        columnName = columnName.replace("authorization", "authoriz")
        columnName = columnName.strip()

        for p_char in problematicChars:
            columnName = columnName.replace(p_char, "")

        new_cols[column] = columnName

    return df.rename(columns=new_cols)


def read(type, settings):
    if type == "CSV":
        return __read_csv(settings)
    if type == "EXCEL":
        return __read_excel(settings)
    if type == "PARQUET":
        return __read_parquet(settings)
    if type == "GOOGLE_SHEETS":
        return __read_gsheet(settings)
    if type == "Hubspot":
        return __read_hubspot(settings)
    else:
        raise TypeError("Dataset type not supported yet")


def __read_csv(settings: dict):
    
    # Handle thousands
    if settings["thousands"] == "None":
       settings["thousands"] = None

    # Read source file
    df = pd.read_csv(filepath_or_buffer=settings["path"], sep=settings["separator"], encoding=settings["encoding"], thousands=settings["thousands"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    # Exec custom post-processing
    if "processing" in settings and settings["processing"] != "" and settings["processing"] != None:
        exec(settings["processing"])

    return df

def __read_parquet(settings: dict):
    
    df = pd.read_parquet(path=settings["path"])

    return df

def __read_excel(settings: dict):
    df = pd.read_excel(settings["path"])

    # Detect if any column is a date-time
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                pass

    return df

def __read_gsheet(settings: dict):
    df = read_gsheet(spreadsheetId=settings["spreadsheetId"], credentials=settings["credentials"], sheet=settings["sheet"],
    
                    valueRenderOption = settings['valueRenderOption'],  dateTimeRenderOption = settings['dateTimeRenderOption'])
                    
    return df

def __read_hubspot(settings: dict):
    df = read_hubspot_contacts(settings["fields"]["token"])

    return df




##################################
########## FACEBOOK ADS ##########
##################################


def read_fb_ads(my_app_id, my_app_secret, my_access_token, start_date, end_date, account_name):
    
    from askdata.integrations import facebook_api
    
    fb_ads = facebook_api.get_fb_ads(my_app_id, my_app_secret, my_access_token, start_date, end_date, account_name)

    return fb_ads



#################################
########## GOOGLE ADS ##########
################################


def read_google_ads(start_date, end_date, admin_account,
                   
                   yaml_file_path = 'googleads.yaml'):
    
    
    from askdata.integrations import google_api
    
    google_ads = google_api.get_google_ads(start_date, end_date, admin_account, yaml_file_path)
    
    return google_ads
    
    
    
    
###################################
########## AIRCALL CALLS ##########
###################################



def read_aircall_calls(token, api_key, #mandatory
                      
                      start = 7, end = 0 #optional
                     ):
    
    from askdata.integrations import aircall_api
    
    aircall_calls = aircall_api.get_aircall_calls(token, api_key, start, end)
    
    return aircall_calls
    
    
    
#############################
########## HUBSPOT ##########
#############################
    

## hubspot deals

def read_hubspot_deals(API_KEY, start_date, end_date):
    
    
    from askdata.integrations import hubspot_api
    
    deals_all_fiels = hubspot_api.get_hubspot_deals_all_fields(API_KEY, start_date, end_date)
    
    return deals_all_fiels
 

    
## hubspot contact

def read_hubspot_contact(API_KEY, start_date, end_date):
    
    from askdata.integrations import hubspot_api
    
    hubspot_contact = hubspot_api.get_hubspot_contact(API_KEY, start_date, end_date)
    
    return hubspot_contact
                         
           
        
## hubspot pipelines

def read_hubspot_pipelines(API_KEY):
    
    
    from askdata.integrations import hubspot_api
    
    hubspot_pipelines = hubspot_api.get_hubspot_pipelines(API_KEY)
    
    return hubspot_pipelines
                         
                         
    
## hubspot users

def read_hubspot_users(API_KEY):
    
    from askdata.integrations import hubspot_api
    
    hubspot_users = hubspot_api.get_hubspot_users(API_KEY)
    
    return hubspot_users
    