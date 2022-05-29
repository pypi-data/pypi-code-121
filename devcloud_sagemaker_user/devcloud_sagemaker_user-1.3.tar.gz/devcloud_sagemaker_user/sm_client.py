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


def create_account(acc_name,acc_email,acc_password,placeholder=""):
    headers = {'Content-Type': 'application/json'}
  
    if placeholder == "register_platform":
        account_info = {
            "account_name": acc_name,
            "account_email": acc_email,
            "account_password": acc_password,
            "account_type": 1
        }

    elif placeholder == "":
        account_info = {
        "account_name": acc_name,
        "account_email": acc_email,
        "account_password": acc_password,
        "account_type": 0
        }
    else:
        account_info = {
        "account_name": acc_name,
        "account_email": acc_email,
        "account_password": acc_password,
        "account_type": 0,
        "corresponding_platform_name":placeholder
        }


    payload = json.dumps(account_info)
    #print("Account created!!",f"payload {payloa}")
    
    response = requests.request("POST", f"{API_GW}/account/create", headers=headers, data=payload)
    print("Your Account info:",f"payload {payload}")
    print(json.loads(response.text)["info"])
    return 1

def login(username,password):
    headers = {
        'Content-Type': 'application/json'
    }
    
    account_info = {
        "username": username,
        "password": password,
    }
    payload = json.dumps(account_info)
    
    response = requests.request("POST", f"{API_GW}/login", headers=headers, data=payload)
    

    
    if json.loads(response.text)['Code'] == "InternalServerError":
        print("Incorrect Account or Password! Please login again!")
        return 0
    if json.loads(response.text)['Code'] == "201":
        print("Incorrect Password! Please login again!")
        return 0
    
    if json.loads(response.text)['Code']== "200":
        response_body = json.loads(response.text)
        print("\n login successfully \n your account info:",json.loads(response.text))
        
        #print(response_body)
        token = response_body["data"]["token"]        
        file = open('.token','w')
        print("\n token ‘.token’ recorded in current folder!!")
        file.write(token)
        file.close()
        return 1

def platform_charge_to_account(target_account_name,recharge_credits):
    headers = {
        'Content-Type': 'application/json'
    }

    file=open('.token','r')#read token from "token.txt"
    token=file.read()
# 进行充值操作前 需要登录拿到token
# token是平台账号intel登录生成的
    info = {
        "target_account_name": target_account_name,
        "token": token,
        "recharge_credits": recharge_credits,
    }   
    payload = json.dumps(info)
    #print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/account/recharge", headers=headers, data=payload)
    response_body = json.loads(response.text)

    print("Account:",target_account_name,"has been charged",recharge_credits,"points!")


def query_device_list():
    url = f"{API_GW}/device/query"
    response = requests.request("GET", url)
    #print(response)

    response_body = json.loads(response.text)
    
    total_device =len(response_body['list'])
   
    for i in range(total_device):
        print(response_body['list'][i])
    #print(len(response_body['Items']))

def submit_a_task(training_code,dataset,instance_type,epochs):
    file=open('.token','r')#read token from "token.txt"
    token=file.read()
    #print("Your token is :",token)

    task_id = str(uuid.uuid4())
    print(f"task id is: {task_id}")

    instance_type = instance_type #"ml.m5.xlarge"
    instance_count = 1
    framework_version = "1.1.0"
    hyperparameters = {"epochs": epochs, "backend": "gloo"}

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
    
    if dataset.startswith('s3://'):
        with open("s3_public_dataset.txt", 'w') as f:
            f.write(dataset)
        upload_one_file(task_id, "Traindata", "s3_public_dataset.txt")
        print(f"use s3 public datasets  {dataset}")
    else:
        upload_one_folder(task_id, "Traindata", dataset)
    upload_one_file(task_id, "Code", training_code)
    print("Use get_task_status(task_id) to query the training status.")
    return task_id

    
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


def query_task_log(task_id):
    log_url = f"{API_GW}/task/log/{task_id}"

    headers = {
        'Content-Type': 'application/json'
    }
    
    len_c = 0
    
    status_url = f"{API_GW}/task/status/{task_id}"
    response = requests.request("GET", status_url)
    response_body = json.loads(response.text)
    job_status = response_body[task_id]
    print(job_status)
    
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
        print("Waiting log output, Please try it again in 10 seconds...")


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
   
def platform_query_account(platform_account_name):
    #account_name = "intel"
    url = f"{API_GW}/account/platform_query_account/{platform_account_name}"
    response = requests.request("GET", url)

    response_body = json.loads(response.text)

    print(response)
    print("Query completed,",platform_account_name,"platfrom contains below personal accounts:", response_body)
    

def query_task_info(task_id):
    url = f"{API_GW}/task/query/{task_id}"
    response = requests.request("GET", url)
    response_body = json.loads(response.text)
    print(response)
    print("Task Id:",task_id,"\nTask info:",response_body)

def query_account_info(account_name):
    #account_name = "yaru"
    url = f"{API_GW}/account/query/{account_name}"
    response = requests.request("GET", url)
    response_body = json.loads(response.text)
   # print(response)
    print("Query completed, account:",account_name,"info",response_body)


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



def cancel_task(task_id):
    url = f"{API_GW}/task/cancel/{task_id}"
    response = requests.request("GET", url)
    print(json.loads(response.text))
    print("Task",task_id," canceled",response)
    

#if __name__ == "__main__":
   	#create_account("platform_account","pa@intel.com","123","register_platform")#platform account
	#create_account("coresponding_platform_account_2","cpa_2@intel.com","123","platform_account")#realted platfrom account create
    	#create_account("abc","abc@132.com","password")#normal account  
   	#login("coresponding_platform_account_2","123")
    	#platform_charge_to_account("coresponding_platform_account_2",1)
	#query_device_list()
	#submit_a_task("train.tar","s3://code-devcloud/jobs/090e3c81-804a-4a34-abfb-33d67d77bfa8/Traindata/mnist/","ml.m5.xlarge","1")
        #get_task_status("bd15ebb6-a683-4b83-b2f9-3d8d36616a03")
   	#query_task_log("bd15ebb6-a683-4b83-b2f9-3d8d36616a03")
   	#download_trained_model("bd15ebb6-a683-4b83-b2f9-3d8d36616a03")
    	#platform_query_account("platform_account") #show accounts' info in "intel" platform
    	#query_task_info("bd15ebb6-a683-4b83-b2f9-3d8d36616a03")
   	#query_account_info("coresponding_platform_account_2")
	#update_account("test","intelpass","token_4","1234","666@intel.com")
 	#cancel_task("platform_account")



   
