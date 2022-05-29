import uuid
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

def test_login():
    headers = {
        'Content-Type': 'application/json'
    }
    API_GW = "https://aaw5kr39wf.execute-api.cn-north-1.amazonaws.com.cn/api/"
    account_info = {
        "username": "yaru",
        "password": "intelpass"
    }
    payload = json.dumps(account_info)
    print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/login", headers=headers, data=payload)
    print(response)
    response_body = json.loads(response.text)
    token = response_body["data"]["token"]
    print(token)
    return 1


def get_message():
    return HELLO_WORLD_MESSAGE


def print_hello_world():
    print(get_message())

class FileType(enum.Enum):
    Train = 1
    Weights= 2
    EntryPoint = 3
    Code = 4
    Inputs = 5
    mnist = 6
    MNIST = 7
    processed = 8
    output = 9
    Traindata =10


def create_training_job(local_data, source_code, weights, hyper_param):
    # create job id

    job_id = str(uuid.uuid4())
    print(f"job id is: {job_id}")

    # upload data and code to s3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    
    if local_data is not None:
        if local_data.startswith('s3://'):
            with open("s3_public_dataset.txt", 'w') as f:
                f.write(local_data)
            __upload_one_file(job_id, FileType.Traindata.name, "s3_public_dataset.txt")
            print(f"use s3 public datasets  {local_data}")
        else:
            datasets_start_time = datetime.datetime.now()
            __upload_one_folder(job_id, FileType.Traindata.name, local_data)
            datasets_end_time = datetime.datetime.now()
            print(f"uploaded {local_data}")
            print("datasets upload time: %s Seconds"%(datasets_end_time-datasets_start_time))

    if source_code is not None:
        code_start_time = datetime.datetime.now()
        __upload_one_file(job_id, FileType.Code.name, source_code)
        code_end_time = datetime.datetime.now()
        print(f"uploaded {source_code}")
        print("code upload time: %s Seconds"%(code_end_time-code_start_time))

    if weights is not None:
        weights_start_time = datetime.datetime.now()
        __upload_one_file(job_id, FileType.Weights.name, weights)
        weights_end_time = datetime.datetime.now()
        print(f"uploaded {weights}")
        print("weights upload time: %s Seconds"%(weights_end_time-weights_start_time))

    # put hyper param to Dynamodb through API Gateway
    headers = {
        'Content-Type': 'application/json'
    }
    hyper_param.update({"jobid": job_id})
    payload = json.dumps(hyper_param)
    #print(f"payload {payload}")
    response = requests.request("POST", f"{API_GW}/job", headers=headers, data=payload)

    #print(response)
    get_training_job_logstream(job_id)
    return job_id


def make_tar(source_dir):
    output_filename = os.path.basename(source_dir).split('.')[0] + ".tar"
    with tarfile.open(output_filename, "w") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def get_training_job_status(job_id):

    # read status from API Gateay - backed by Dynamodb
    url = f"{API_GW}/jobs/{job_id}"
    #print(f"getting {url}")
    response = requests.request("GET", url)
    #print(f"response {response}")
    response_body = json.loads(response.text)
    #print(response.text)
    if len(response_body) == 2:
        return print("waiting...")
    else:
        if response_body[job_id] == "InProgress":
            pass
        else:
            print(response_body[job_id])
    return response_body[job_id]

def get_model(job_id, model):
    url = f"{API_GW}/s3urld/{job_id}/{FileType.output.name}/{model}"
    response = requests.get(url, allow_redirects=True)

    response_s3 = requests.get(response.__dict__['_content'])
    #print(f"getting {url}")

    if response.status_code == 200:
        size = 2**10
        with open("./model.tar.gz", 'wb') as tar:
            for chunk in response_s3.iter_content(chunk_size=size):
                tar.write(chunk)
        tar.close()


def get_training_job_logstream(job_id):
    url = f"{API_GW}/jobs/{job_id}"
    #print(f"getting {url}")

    tmp_status = ["Completed", "Failed", "Stopped"]
    headers = {
        'Content-Type': 'application/json'
    }
    #print(f"reponse {response}")
    len_c = 0
    job_status = get_training_job_status(job_id)
    while True:
        response = requests.request("POST", url, headers=headers)

        contents = json.loads(response.text)

        len_cc = len(contents)
        #print(len_c,len_cc)

        if len_cc > len_c and len_cc!=2:
            #len_d = len_cc- len_c
            contents = contents[len_c:len_cc]
            len_c = len_cc
            for content in contents:
                print(content)
        elif len_cc == len_c:
            pass
        else:
            print("waiting...")
        time.sleep(10)
        job_status = get_training_job_status(job_id)

        if job_status in tmp_status:
            break
    return response
    

def cancel_training_job_status(job_id):
    """
    If a job status is submited then it can be cancled.
    """
    pass



# upload folder
def __upload_one_folder(job_id, type, dir_name: str):
    file_list = __list_files(dir_name)
    list_len = len(file_list)
    workers = 100
    worker_num = min(workers, 512)
    worker_num = 1 if list_len < workers else worker_num
    po = Pool(worker_num)
    for f in file_list:
        po.apply_async(func=__upload_one_file, args=(job_id, type, f))
    po.close()
    po.join()
    


def __list_files(dir_name):
    r = []
    subdirs = [x[0] for x in os.walk(dir_name)]
    for subdir in subdirs:
        files = os.walk(subdir).__next__()[2]
        if (len(files) > 0):
            for file in files:
                r.append(os.path.join(subdir, file))
    #print(r)
    return r




##############################################
# Helpers
##############################################

def __upload_one_file(job_id, type, object_name):

    # request a s3 presigned URL
    object_name_encoded = path_encoder.quote(object_name, safe="") # by default / is recognized as safe
    url = f"{API_GW}/s3url/{job_id}/{type}/{object_name_encoded}"
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
    #__upload_one_file("11112222", "mnist/MNIST/processed", "buffer1.txt")
    #create_training_job("training.pt", "test.pt", "buffer1.txt", None, {"epoch":"10"})
    #get_zipfile("./test","./test.zip")
    #folder_upload("test")
    #get_training_job_status("125cddd2-6686-44c2-8e14-1e4fe882ad94")
    #get_model("125cddd2-6686-44c2-8e14-1e4fe882ad94", "model.tar.gz")
    
    #__upload_one_file("repo", "source", "yolov5.tar")
    #__upload_one_folder(uuid.uuid4(), "code", "/home/ubuntu/repo/intel_devcloud/yolov5")
    #__upload_one_folder("repo", "test", "yolov5")
    #r=[]
    #__list_files("test")
    #getFloderFiles("test")
    #print(files)

    #make_tar("yolov5") 
    #s3://code-devcloud/jobs/05ec9d2d-8862-49c1-9d1c-a39125e23fc2/Traindata/datasets_simple/
    
    #create_training_job("s3://code-devcloud/jobs/05ec9d2d-8862-49c1-9d1c-a39125e23fc2/Traindata/datasets_simple/",
    #                    "yolov5.tar",
    #                    "yolov5s.pt",
    #                    {"instance_type":"ml.p3.2xlarge",
    #                    "instance_count":"1",
    #                    "framework_version":"1.8.1",
    #                    "hyperparameters":{"imgsz":"64", "epochs":"10"}})
    
    
    #make_tar("train.py")
    #s3://code-devcloud/jobs/090e3c81-804a-4a34-abfb-33d67d77bfa8/Traindata/mnist/
    """
    create_training_job("s3://code-devcloud/jobs/090e3c81-804a-4a34-abfb-33d67d77bfa8/Traindata/mnist/",
                        "train.tar",
                        None,
                        {"instance_type":"ml.m5.xlarge",
                        "instance_count":"1",
                        "framework_version":"1.1.0",   
                        "hyperparameters":{"epochs":"4","backend":"gloo", "hidden_channels":"2", "dropout":"0.2","kernel_size":"5", "optimizer":"sgd"}})
    """
