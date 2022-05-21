
import os
import re
import requests
import json
from modelify.utils.constants import APP_FOLDER, MODELIFY_UPLOAD_URL, MODELIFY_DEPLOY_URL, MODELIFY_DOWNLOAD_URL
from modelify.utils.credential import Credential
from modelify.utils import message
from modelify.utils.constants import ModelifyFile
from tqdm import tqdm


class ModelifyClient:
    def __init__(self):
        self.credential = Credential()
 
    def upload_pipeline(self, upload_types: dict, app_uid, configs):
        # filter upload types
        filetypes = list(map(lambda x: x[0], filter(lambda item: item[1]==True, upload_types.items())))
        upload_urls = self.get_upload_url(app_uid, filetypes)
        for item in upload_urls:
            self.upload_model_storage(item["url"], item["type"], configs)
        message("Model files uploaded successfully")
        self.register_model(app_uid, configs)

    def get_upload_url(self ,app_uid, filetypes:list):
        data = {'app_uid': app_uid, 'filetypes': filetypes}
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.post(MODELIFY_UPLOAD_URL, json=data, headers = headers)

        if req.status_code == 200:
            return req.json()["urls"]
        raise Exception("Upload url could not generated")

    def get_download_urls(self ,app_uid, version=None):
        data = {'app_uid': app_uid}
        if version is not None:
            data["version_number"] = version
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.post(MODELIFY_DOWNLOAD_URL, json=data, headers = headers)

        if req.status_code == 200:
            return req.json()["urls"]
        raise Exception("Download url could not generated")

    def upload_model_storage(self,url, file_type, configs):

        blob_name = ModelifyFile[file_type].file_name
        content_type = ModelifyFile[file_type].content_type
        
        file_path = os.path.join(APP_FOLDER, blob_name)
        req = requests.put(url, open(file_path, 'rb') , headers= {'Content-Type': content_type})
        
        if req.status_code != 200:
            print(req.text)
            raise Exception("There is something wrong in model upload stage")


    def register_model(self, app_uid, configs):
        message("Model is registering to your account")
        data = {'app_uid': app_uid,  'model_metadata': configs}
        headers = {"api-token": f"{self.credential.api_key}", "Content-Type": "application/json"}
        req = requests.post(MODELIFY_DEPLOY_URL, json=data, headers = headers)
        if req.status_code == 201:
            print("Model has been sent.")
        else:
            print(req.text)
            response_dict = json.loads(req.text)

            for i in response_dict:
                print("key: ", i, "val: ", response_dict[i])
            print("Something went wrong while model sending.")

    def pull_model(self, app_uid, version=None):   
        urls = self.get_download_urls(app_uid=app_uid, version=version)
        for url in urls:
            response = requests.get(url, stream=True)
            fname = re.findall("[^\/]+(?=\?[^\/]*$)", url)[0]
            file_path = os.path.join(APP_FOLDER, fname)
            with open(file_path, "wb") as handle:
                for data in tqdm(response.iter_content()):
                    handle.write(data)

