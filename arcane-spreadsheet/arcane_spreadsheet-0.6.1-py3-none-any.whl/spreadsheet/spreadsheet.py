# coding=utf-8
import copy
from datetime import datetime
import json
from typing import Dict, Union, Any, List
import re

from arcane.core import IssueSpreadsheetDatabase

from googleapiclient import discovery, errors
from oauth2client.service_account import ServiceAccountCredentials
from google.cloud.exceptions import Forbidden


class SpreadSheetDB(object):
    def __init__(self, spreadsheet_id, adscale_key, sheet_id=None, sheet_name=None, headers: List[str] = None):
        if sheet_id is None and sheet_name is None:
            raise ValueError('SpreadSheetDB: sheet_id and sheet_name cannot be both None')
        self.spreadsheet_id = spreadsheet_id
        self.sheet_id = sheet_id
        self.adscale_key = adscale_key
        self.sheet_name = self.get_sheet_name() if sheet_name is None else sheet_name
        try:
            self.db, self.headers = get_dict_list_from_spreadsheet(spreadsheet_id, self.sheet_name, self.adscale_key)
        except IssueSpreadsheetDatabase as error:
            if headers is None:
                raise error
            self.db = []
            self.headers = headers
        self.new_rows = []

    def get_rows(self):
        return copy.deepcopy(self.db)

    def get_row(self, id_header, id_row):
        return copy.deepcopy(self.get_row_object(id_header, id_row))

    def get_row_object(self, id_header, id_row):
        for row in self.db:
            if id_row == row[id_header]:
                return row
        raise IssueSpreadsheetDatabase(
            reason='invalid_row',
            message="The id '" + id_row + "' does not exist in column '" + id_header + "' of spreadsheet '"
            + self.spreadsheet_id + "'")

    def update_row(self, id_header, id_row, row_dict):
        old_row = self.get_row_object(id_header, id_row)
        for key in row_dict.keys():
            old_row[key] = copy.copy(row_dict[key])

    def apply_updates(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.adscale_key,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        service = discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)

        sheet_range = "'" + self.sheet_name + "'!A2"
        updated_rows = []
        for row in self.db:
            updated_row = []
            for key in self.headers:
                if key not in row:
                    updated_row.append("")
                else:
                    updated_row.append(row[key])
            updated_rows.append(updated_row)

        value_range_body = {
            "values": updated_rows
        }
        request = service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id,
                                                         range=sheet_range,
                                                         body=value_range_body,
                                                         valueInputOption="RAW")
        request.execute()

    def create_row(self, row_dict):
        self.new_rows.append(row_dict)

    def get_sheet_name(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.adscale_key,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        service = discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)
        spreadsheet_info = service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id).execute()
        for sheet in spreadsheet_info['sheets']:
            if sheet['properties']['sheetId'] == self.sheet_id:
                return sheet['properties']['title']
        raise IssueSpreadsheetDatabase(reason='non_existent_sheet',
                                       message="The sheet with id '" + self.spreadsheet_id + "' does not exist")

    def apply_create(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.adscale_key,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
        service = discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)

        body = {
            'values': [list(self.headers)] + [[row.get(key, "") for key in self.headers] for row in self.new_rows]
        }
        range_ = "'" + self.sheet_name + "'"
        service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_,
            valueInputOption="RAW",
            body=body).execute()
        self.new_rows = []


def spreasheet_check_access(spreadsheet_id: str, adscale_key: str):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
            adscale_key,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
    service = discovery.build('sheets', 'v4', credentials=credentials)
    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id)
    try:
        request.execute()
    except errors.HttpError as e:
        error = json.loads(e.content).get('error', {})
        error_code = error.get('code')
        if error_code == 403:
            raise Forbidden('Bad authorization')
        elif error_code == 404:
            raise FileNotFoundError
        elif error_code == 400 and error.get('message') == 'This operation is not supported for this document':
            raise NotImplementedError
        raise Exception


def handle_duplicate_spreadsheet_headers(raw_headers):
    raw_keys_counter = {}
    keys_list = []
    for index, key in enumerate(raw_headers):
        if not raw_keys_counter.get(key):
            raw_keys_counter[key] = 1
            if key in raw_headers[index + 1:]:
                keys_list.append(f'{key}_1')
            else:
                keys_list.append(key)
        else:
            raw_keys_counter[key] += 1
            keys_list.append(f'{key}_{raw_keys_counter[key]}')
    return keys_list


def get_dict_list_from_spreadsheet(spreadsheet_id, sheet_name, adscale_key):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        adscale_key,
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
    service = discovery.build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    range_ = "'" + sheet_name + "'"
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_)
    sheet_values = request.execute().get('values')
    if not sheet_values:
        raise IssueSpreadsheetDatabase(reason='empty_spreadsheet',
                                       message="The sheet named '"+sheet_name+"' in spreadsheet with id '" + spreadsheet_id + "' is empty ")
    raw_keys_list = sheet_values[0]
    keys_list = handle_duplicate_spreadsheet_headers(raw_keys_list)

    list_of_dicts = []
    # To List of dict
    for row_list in sheet_values[1:]:
        i = 0
        row_dict = {}
        for key in keys_list:
            try:
                row_dict[key] = row_list[i]
            except IndexError:
                row_dict[key] = None
            i = i + 1
        list_of_dicts.append(row_dict)
    return list_of_dicts, keys_list


def get_boolean_from_string(content: str) -> bool:
    """ takes in a string and transforms it to a boolean"""
    # Default value
    if content.strip().lower() == 'true':
        return True
    elif content.strip().lower() != 'false':
        print(f'got a value {content} that is neither true nor false. returning false by default')
    return False


def get_object_from_schema(data_dict: Dict[str, str], data_model: Dict[str, Dict[str, Union[str, Any]]]) -> Dict:
    """ create an object with the correct types according to data_model """
    new_obj = {}
    for key in data_model.keys():
        if data_model[key]["type"] == "string":
            new_obj[key] = data_dict[key]
        elif data_model[key]["type"] == "boolean":
            new_obj[key] = get_boolean_from_string(data_dict[key])
        elif data_model[key]["type"] == "float":
            new_obj[key] = float(data_dict[key])
        elif data_model[key]["type"] == "integer":
            new_obj[key] = int(data_dict[key])
        elif data_model[key]["type"] == "datetime":
            if data_dict[key] != '':
                new_obj[key] = datetime.strptime(
                    data_dict[key], "%Y-%m-%d %H:%M:%S")
            else:
                new_obj[key] = None
        elif data_model[key]["type"] == "none":
            new_obj[key] = None
        elif data_model[key]["type"] == "object":
            embedded_object = data_dict[key]
            embedded_entity = {}
            for embedded_key in list(data_model[key]["properties"].keys()):
                embedded_entity[embedded_key] = recursive_object_creation(embedded_object[embedded_key],
                                                                          data_model[key]["properties"][
                                                                              embedded_key])
            new_obj[key] = embedded_entity
        elif data_model[key]["type"] == "array":
            embedded_schema = data_model[key]["items"]
            embedded_entity = []
            for embedded_item in data_dict[key]:
                embedded_entity.append(recursive_object_creation(
                    embedded_item, embedded_schema))
            new_obj[key] = embedded_entity
    return new_obj


def recursive_object_creation(item: Union[Dict[str, Any], str], schema: Dict[str, Any]) -> Any:
    """ create an object with the correct types according to data_model recursively """
    if schema["type"] == "string":
        return item
    elif schema["type"] == "boolean":
        return get_boolean_from_string(item)
    elif schema["type"] == "float":
        return float(item)
    elif schema["type"] == "integer":
        return int(item)
    elif schema["type"] == "datetime":
        if item != '':
            return datetime.strptime(item, "%Y-%m-%d %H:%M:%S")
        else:
            return None
    elif schema["type"] == "none":
        return None
    elif schema["type"] == "array":
        embedded_schema = schema["items"]
        returned_array = []
        for embedded_item in item:
            returned_array.append(recursive_object_creation(
                embedded_item, embedded_schema))
        return returned_array
    elif schema["type"] == "object":
        returned_object = {}
        for embedded_key in list(schema["properties"].keys()):
            returned_object[embedded_key] = recursive_object_creation(item[embedded_key],
                                                                      schema["properties"][embedded_key])
        return returned_object


def getIdFromSpreadsheetUrl(spreadsheet_url: str) -> str:
    try:
        spreasheet_id = re.search(r'd/([-\w]{25,})', spreadsheet_url).group(1)
    except (IndexError, AttributeError):
        raise ValueError(f'Spreadsheet url {spreadsheet_url} is incorrect formatted') from None
    return spreasheet_id
