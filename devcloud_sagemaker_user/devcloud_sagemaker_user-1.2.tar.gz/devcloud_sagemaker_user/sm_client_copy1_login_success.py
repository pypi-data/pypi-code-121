import uuid
import sys
import requests
import json
import enum
import zipfile
import tarfile
import os
from multiprocessing import  Process, Pool
import urllib.parse as path_encoder
import time
import datetime


HELLO_WORLD_MESSAGE = 'Hello world! PyOhio Demo - 3! CLEpy'

API_GW = "https://aaw5kr39wf.execute-api.cn-north-1.amazonaws.com.cn/api/"

def test_login(username,password):
    headers = {
        'Content-Type': 'application/json'
    }
    
    account_info = {
        "username": username,
        "password": password
    }
    payload = json.dumps(account_info)
    print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/login", headers=headers, data=payload)
    print(json.loads(response.text))
    
    if json.loads(response.text)['Code'] == "InternalServerError":
        print("Incorrect Account or Password! Please login again!")
        return 0
    if json.loads(response.text)['Code'] == "201":
        print("Incorrect Password! Please login again!")
        return 0
    print("1")
    if json.loads(response.text)['Code']== "200":
        response_body = json.loads(response.text)

        print(response_body)
        token = response_body["data"]["token"]        
        file = open('token.txt','w')
        print("token ‘token.txt’ recorded in current folder!!")
        file.write(token)
        file.close()
        return 1

def create_account(acc_name,acc_email,acc_password,acc_count):
    headers = {'Content-Type': 'application/json'}
  

    account_info = {
        "account_name": acc_name,
        "account_email": acc_email,
        "account_password": acc_password,
        "account_type": "0",
        "token":"none"
    }  

    payload = json.dumps(account_info)
    print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/account/create", headers=headers, data=payload)
    print(response)
    return 1

def get_message():
    return HELLO_WORLD_MESSAGE
    
def submit_a_task():
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMyMDk4NTUuNzY2NjAzNywiaWF0IjoxNjUyNjA1MDU1Ljc2NjYwNjMsImlzcyI6IkludGVsIiwiZGF0YSI6eyJ1c2VybmFtZSI6InlhcnUiLCJ0aW1lc3RhbXAiOjE2NTI2MDUwNTUuNzY2NjA2Nn19._dPTz7Rg1TrI3pgMA12WzHZ-odBpoxO20TLDeRj8E54"
    task_id = str(uuid.uuid4())
    print(f"task id is: {task_id}")

    instance_type = "ml.m5.xlarge"
    instance_count = 1
    framework_version = "1.1.0"
    hyperparameters = {"epochs": "1", "backend": "gloo"}

    headers = {'Content-Type': 'application/json'}


    info = {
        "token": token,
        "task_id": task_id,
        "instance_type": instance_type,
        "instance_count": instance_count,
        "framework_version": framework_version,
        "hyperparameters": hyperparameters
    }
    payload = json.dumps(info)
    print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/task/submit", headers=headers, data=payload)
    print(response)
    response_body = json.loads(response.text)
    print(response_body)
    upload_one_file(task_id, "Code", "train.tar")
    upload_one_folder(task_id, "Traindata", "mnist")
    return task_id

def get_task_status(task_id):
    #task_id = "a403f523-79e8-4c31-919a-8cc6e7eb1748"    
    url = f"{API_GW}/task/status/{task_id}"
    response = requests.request("GET", url)

    response_body = json.loads(response.text)

    print(response)
    print(response_body[task_id])
    return response_body[task_id]

def download_trained_model(task_id):
    #task_id = "a403f523-79e8-4c31-919a-8cc6e7eb1748"
    
    url = f"{API_GW}/trainedmodel/url/{task_id}"

    response = requests.request("GET", url)
    print(response)

    response_body = json.loads(response.text)

    print(response_body["url"])
    # 下载训练好的模型
    r = requests.get(response_body["url"])
    with open(r"./model.tar.gz", "wb") as f:
        f.write(r.content)

# 上传数据集
# upload folder
def upload_one_folder(task_id, type, dir_name: str):
    file_list = list_files(dir_name)
    list_len = len(file_list)
    workers = 100
    worker_num = min(workers, 512)
    worker_num = 1 if list_len < workers else worker_num
    po = Pool(worker_num)
    for f in file_list:
        po.apply_async(func=upload_one_file, args=(task_id, type, f))
    po.close()
    po.join()


def list_files(dir_name):
    r = []
    subdirs = [x[0] for x in os.walk(dir_name)]
    for subdir in subdirs:
        files = os.walk(subdir).__next__()[2]
        if (len(files) > 0):
            for file in files:
                r.append(os.path.join(subdir, file))
    #print(r)
    return r


def upload_one_file(task_id, type, object_name):

    # request a s3 presigned URL
    object_name_encoded = path_encoder.quote(object_name, safe="") # by default / is recognized as safe
    url = f"{API_GW}/s3url/{task_id}/{type}/{object_name_encoded}"
    #print(f"getting url: {url}")
    response = requests.request("GET", url)
    #print(f"response: {response}")
    response_body = json.loads(response.text)
    #print(f"response_body: {response_body}")

    with open(object_name, 'rb') as f:
        files = {'file': (object_name, f)}
        http_response = requests.post(response_body['url'], data=response_body['fields'], files=files)
    # If successful, returns HTTP status code 204
    #print(f'File upload HTTP status code: {http_response.status_code}')







if __name__ == "__main__":
    #create_account("token","tese@intel.com","pd","0")
    test_login("tokentest","password")
    #taskid =submit_a_task()
    #print(taskid)
    #while get_task_status("6f44cce4-1223-4d7a-ad77-87e343727fc4") != 'Completed':
    #    get_task_status("6f44cce4-1223-4d7a-ad77-87e343727fc4")
    #    time.sleep(10)

    #download_trained_model("6f44cce4-1223-4d7a-ad77-87e343727fc4")
