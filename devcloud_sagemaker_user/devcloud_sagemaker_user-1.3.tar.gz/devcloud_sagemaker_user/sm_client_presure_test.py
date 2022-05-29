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
    #print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/login", headers=headers, data=payload)
    
    
    if json.loads(response.text)['Code'] == "InternalServerError":
        print("Incorrect Account or Password! Please login again!")
        return 0
    if json.loads(response.text)['Code'] == "201":
        print("Incorrect Password! Please login again!")
        return 0
    
    if json.loads(response.text)['Code']== "200":
        response_body = json.loads(response.text)
        print("\n login successfully, your account info:",json.loads(response.text))
        
        #print(response_body)
        token = response_body["data"]["token"]        
        file = open('token.txt','w')
        print("\n token ‘token.txt’ recorded in current folder!!")
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
    #print("Account created!!",f"payload {payloa}")
    print("Account created!")
    response = requests.request("POST", f"{API_GW}/account/create", headers=headers, data=payload)
    print("\n Account info:",f"payload {payloa}")
    return 1

def get_message():
    return HELLO_WORLD_MESSAGE
    
def submit_a_task(file_name,training_code,dataset):
    file=open(file_name,'r')#read token from "token.txt"
    token=file.read()
    #print("Your token is :",token)
    #token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NTMyMDk4NTUuNzY2NjAzNywiaWF0IjoxNjUyNjA1MDU1Ljc2NjYwNjMsImlzcyI6IkludGVsIiwiZGF0YSI6eyJ1c2VybmFtZSI6InlhcnUiLCJ0aW1lc3RhbXAiOjE2NTI2MDUwNTUuNzY2NjA2Nn19._dPTz7Rg1TrI3pgMA12WzHZ-odBpoxO20TLDeRj8E54"
    print("Your token is :",token)

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
    upload_one_file(task_id, "Code", training_code)
    upload_one_folder(task_id, "Traindata", dataset)
    print("Use get_task_status(task_id) to query the training status.")
    return task_id

def get_task_status(task_id):
    #task_id = "a403f523-79e8-4c31-919a-8cc6e7eb1748"    
    url = f"{API_GW}/task/status/{task_id}"
    response = requests.request("GET", url)

    response_body = json.loads(response.text)

    #print(response)
    print("Training Job status is:",response_body[task_id])
    while response_body[task_id] != 'Completed':
        response = requests.request("GET", url)
        response_body = json.loads(response.text)
        print("Training Job status now is:",response_body[task_id])
        time.sleep(10)
   
    return response_body[task_id]

def download_trained_model(task_id):
    #task_id = "a403f523-79e8-4c31-919a-8cc6e7eb1748"
    
    url = f"{API_GW}/trainedmodel/url/{task_id}"

    response = requests.request("GET", url)
    print(response)

    response_body = json.loads(response.text)

    print("Download trained model from:",response_body["url"])
    # 下载训练好的模型
    r = requests.get(response_body["url"])
    with open(r"./model.tar.gz", "wb") as f:
        f.write(r.content)
    f.close()
    print("Download completed!")
    
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

def platform_charge(target_account_name,operater_name,recharge_credits):
    headers = {
        'Content-Type': 'application/json'
    }
    if isinstance(recharge_credits,str) == True:
        
        credit=int(recharge_credits)
        #if the credits input is str
        info = {
            "target_account_name": target_account_name,
            "operater_name": operater_name,
            "recharge_credits":credit,
        }
    else:
        info = {
            "target_account_name": target_account_name,
            "operater_name": operater_name,
            "recharge_credits":recharge_credits,
        }#if the credits input is number


    payload = json.dumps(info)
    print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/account/recharge", headers=headers, data=payload)
    print("Successfully",recharge_credits,"Credits charged from",operater_name,"to",target_account_name,response)

def platform_query_account(platform_account_name):
    #account_name = "intel"
    url = f"{API_GW}/account/platform_query_account/{platform_account_name}"
    response = requests.request("GET", url)

    response_body = json.loads(response.text)

    print(response)
    print("Query completed,",platform_account_name,"platfrom contains below personal accounts:", response_body)
    
def query_account_info(account_name):
    #account_name = "yaru"
    url = f"{API_GW}/account/query/{account_name}"
    response = requests.request("GET", url)
    response_body = json.loads(response.text)
    print(response)
    print("Query completed, account:",account_name,"info",response_body)

def query_task_info(task_id):
    url = f"{API_GW}/task/query/{task_id}"
    response = requests.request("GET", url)
    response_body = json.loads(response.text)
    print(response)
    print(task_id," Task info:",response_body)

def query_task_log(task_id):
    log_url = f"{API_GW}/task/log/{task_id}"
    print("Printing task:",task_id," training log:")
    print(f"getting {log_url}")

    tmp_status = ["Completed", "Failed", "Stopped"]
    headers = {
        'Content-Type': 'application/json'
    }
    len_c = 0


    url = f"{API_GW}/task/status/{task_id}"
    response = requests.request("GET", url)

    response_body = json.loads(response.text)

    job_status = response_body[task_id]
    print(job_status)

    while True:
        response = requests.request("POST", log_url, headers=headers)
        contents = json.loads(response.text)
        len_cc = len(contents)

        if len_cc > len_c and len_cc!=2:
            contents = contents[len_c:len_cc]
            len_c = len_cc
            for content in contents:
                print(content)
        elif len_cc == len_c:
            pass
        else:
            print("waiting...")
        time.sleep(10)
        url = f"{API_GW}/task/status/{task_id}"
        response = requests.request("GET", url)
    
        response_body = json.loads(response.text)
    
        job_status = response_body[task_id]
    
        if job_status in tmp_status:
            break


def cancel_task(task_id):
    url = f"{API_GW}/task/cancel/{task_id}"
    response = requests.request("GET", url)
    print(json.loads(response.text))
    print("Task",task_id," canceled",response)
    

def update_account(username,password,update_username,update_password,update_email):
    headers = {
        'Content-Type': 'application/json'
    }
    
    account_info = {
        "username": username,
        "password": password,
        "update_username":update_username,
        "update_password":update_password,
        "update_email":update_email
    }
    payload = json.dumps(account_info)
    #print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/account/update", headers=headers, data=payload)

    
    if json.loads(response.text)['Code'] == "InternalServerError":
        print("Incorrect Account or Password! Please check your password!")
        return 0
    if json.loads(response.text)['Code'] == "201":
        print("Incorrect Password! Please check your password!!")
        return 0
        
    if json.loads(response.text)['Code']== "200":
        response_body = json.loads(response.text)
        print("Account update successfully,Your new account info:",json.loads(response.text))
        #print(response_body)
             
        return 1   


if __name__ == "__main__":
    #create_account("token_5","token@intel.com","123","0")
    #test_login("token_1","123")
    #test_login("token_2","123")
    test_login("tokentest","password")
    for i in range(int(sys.argv[1])):
        submit_a_task("token.txt","train.tar","mnist")
    
    #get_task_status("fc49bdab-fb61-4c6f-bdfd-63f2065fc25b")
    #download_trained_model("47036abc-05a6-4b8d-9652-8517ab7c9863")
    #platform_charge("tokentest","intel","10")
    #platform_query_account("intel") #show accounts' info in "intel" platform
    #query_account_info("yaru")
    #query_task_info("709b61a5-416f-4663-8c3b-46a997576cc6")
    #query_task_log("709b61a5-416f-4663-8c3b-46a997576cc6")
    #cancel_task("fc49bdab-fb61-4c6f-bdfd-63f2065fc25b")
    #update_account("token_1","123","token_4","1234","666@intel.com")
    
