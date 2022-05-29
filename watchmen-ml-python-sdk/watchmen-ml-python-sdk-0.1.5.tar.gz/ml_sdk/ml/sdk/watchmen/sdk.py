import json
import pandas as pd
import requests


local_env_url = "http://localhost:8000"


def build_headers(token):
    headers = {"Content-Type": "application/json"}
    headers["authorization"] = "pat " + token
    return headers


def build_indicators(columns):
    indicators = []
    for column in columns:
        indicators.append({"columnId": column["columnId"],"name":column["alias"]})
    return indicators


def load_dataset_by_name(token, name):
    response = requests.get(local_env_url+"/subject/name",params={"name":name},headers=build_headers(token))
    subject =  response.json()
    ## TODO  columns type
    indicators_list = build_indicators(subject["dataset"]["columns"])
    criteria ={
        "subjectId":subject["subjectId"],
        "indicators":indicators_list
    }
    response = requests.post(local_env_url+"/subject/data/criteria",data=json.dumps(criteria),headers=build_headers(token))
    dataset = response.json()["data"]
    return pd.DataFrame(dataset,columns =list(map(lambda x: x["name"], indicators_list)))









