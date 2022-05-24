import json
import jsons
import operator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random
import logging
import requests
import pandas as pd
import os
import yaml
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

ops = {
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    '>=': operator.ge,
    '>': operator.gt
}

root_dir = os.path.abspath(os.path.dirname(__file__))
# retrieving base url
yaml_path = os.path.join(root_dir, '../askdata/askdata_config/base_url.yaml')
with open(yaml_path, 'r') as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    url_list = yaml.load(file, Loader=yaml.FullLoader)


def ask_dataframe(dataframe: pd.DataFrame, query: str):
    human2sql_request = {
        "dataframe": dataframe.to_dict(),
        "query": query
    }

    human2sql_url = url_list['BASE_URL_HUMAN2SQL_DEV']

    human2sql_response = requests.post(human2sql_url, json=human2sql_request)
    response_df = []
    if human2sql_response.ok:
        res = human2sql_response.json()
        if 'result' in res:
            all_dfs = res['result']
            for df in all_dfs:
                response_df.append(pd.DataFrame(df))
        if 'messages' in res and res['messages']:
            for mex in res['messages']:
                print(mex)
    else:
        print("Error: " + str(human2sql_response))

    return response_df


def get_conditional_phrases(conditions, phrase1, phrase2):
    bool_array = []
    for condition in conditions:
        for op in ops:
            if op in condition:
                splitted = condition.split(' ' + op + ' ')
                operator = ops[op]
                bool_array.append(operator(splitted[0], splitted[1]))
        # bool_array.append(eval(condition))
    if False in bool_array:
        return phrase2
    else:
        return phrase1


def get_random_synonymous(synonyms):
    random.seed()
    nKeys = len(synonyms.keys())
    pickedItem = random.randint(0, nKeys - 1)
    synPicked = synonyms[pickedItem]
    return synPicked


def words_to_digits(phrase):
    words = phrase.split(" ")
    num = []
    for word in words:
        if "." in word:
            word = word.replace(".", "")
        if "," in word:
            word = word.replace(",", "")
        if word.isdigit():
            num.append(int(word))
    return num


def add_random_synonymous_to_sentence(phrase, placeholder, synonyms):
    random.seed()
    nKeys = len(synonyms.keys())
    pickedItem = random.randint(0, nKeys - 1)
    synPicked = synonyms[pickedItem]
    phrase = phrase.replace(placeholder, synPicked)
    return phrase


def data2nl(df, base_sentence=None):
    # The parameter "df" is a dataframe, but it will be converted into a dict, and called df in each case

    if not df.empty:

        response_df = pd.DataFrame()

        headers = {
            "Content-Type": "application/json"
        }
        dict_df = df.to_dict(orient='records')

        s = requests.Session()
        s.keep_alive = False
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        s.mount('https://', HTTPAdapter(max_retries=retries))

        url = url_list['BASE_URL_DATA2NL_DEV'] + "/data2nl"

        for el in dict_df:

            row = "Data: " + str(el)

            if base_sentence is not None:
                row = "BaseString: " + base_sentence + "\n" + row

            data = {"data": row}

            r = s.post(url=url, headers=headers, json=data)
            r.raise_for_status()

            try:
                nl = r.json()['nl']
                el['nl'] = nl
            except Exception as e:
                logging.error(str(e))
                el['generated_nl'] = ""
            tmp_df = pd.DataFrame()
            tmp_df = tmp_df.append(el, ignore_index=True)
            response_df = pd.concat([response_df, tmp_df], ignore_index=True, axis=0)
        return response_df
    else:
        print("Input DataFrame is empty!")
        df_response = pd.DataFrame()
        return df_response


def query2sql(smartquery, driver):
    # Google Pod
    headers = {
        "Content-Type": "application/json"
    }

    s = requests.Session()
    s.keep_alive = False
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    url = url_list['BASE_URL_QUERY2SQL_DEV'] + "/query_to_sql"

    stringed_smartquery = jsons.dumps(smartquery, strip_nulls=True)
    smartquery = json.loads(stringed_smartquery)

    data = {
        "smartquery": smartquery,
        "driver": driver
    }

    r = s.post(url=url, headers=headers, json=data)
    r.raise_for_status()

    try:
        dict_response = r.json()
        sql = dict_response['sql']
        return sql
    except Exception as e:
        logging.error(str(e))


def nl2query(nl, language="en-US"):
    # Google Pod
    headers = {
        "Content-Type": "application/json"
    }

    s = requests.Session()
    s.keep_alive = False
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    url = url_list['BASE_URL_NL2QUERY_DEV'] + "/query"

    if "it" in language:
        language = "it-IT"
    else:
        language = "en-US"

    data = {
        "nl_ner": nl,
        "lang": language
    }

    r = s.post(url=url, headers=headers, json=data)
    r.raise_for_status()

    try:
        response = r.json()
        smartquery, version = response['smartquery'], response['model_version']
        return smartquery, version
    except Exception as e:
        logging.error(str(e))


def complex_field_calculator(smartquery, driver):
    # Google Pod
    headers = {
        "Content-Type": "application/json"
    }

    s = requests.Session()
    s.keep_alive = False
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    url = url_list['BASE_URL_QUERY2SQL_DEV'] + "/query_to_sql"

    stringed_smartquery = jsons.dumps(smartquery, strip_nulls=True)
    smartquery = json.loads(stringed_smartquery)

    data = {
        "smartquery": smartquery,
        "driver": driver
    }

    r = s.post(url=url, headers=headers, json=data)
    r.raise_for_status()

    try:
        dict_response = r.json()
        sql = dict_response['sql']
        return sql
    except Exception as e:
        logging.error(str(e))


def complex_filter_calculator(smartquery, driver):
    # Google Pod
    headers = {
        "Content-Type": "application/json"
    }

    s = requests.Session()
    s.keep_alive = False
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retries))

    url = url_list['BASE_URL_QUERY2SQL_DEV'] + "/query_to_sql"

    stringed_smartquery = jsons.dumps(smartquery, strip_nulls=True)
    smartquery = json.loads(stringed_smartquery)

    data = {
        "smartquery": smartquery,
        "driver": driver
    }

    r = s.post(url=url, headers=headers, json=data)
    r.raise_for_status()

    try:
        dict_response = r.json()
        sql = dict_response['sql']
        return sql
    except Exception as e:
        logging.error(str(e))
