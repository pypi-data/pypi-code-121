import requests
import json
import os
import pandas as pd

class EaseApi():
  def __init__(self, username=None, password=None, token=None, device_token=None):
    self.host = "https://app-backend.ease-x.com"
    self.token = token
    self.device_token = device_token
    self.username = username
    self.password = password
    self.bucket_resource_uuid = None
    if self.token == None and self.username != None and self.password != None:
      self._retrive_token()

  def _retrive_token(self):
    endpoint = f'{self.host}/api/commonauth/tokens'
    headers = {"content-type": "application/json"}
    data = {
      "username": self.username,
      "password": self.password,
      "method": "password"
    }
    r = requests.post(endpoint, json=data, headers=headers)
    self.token = r.json()["data"]["token"]

  def _get_project(self, project_uuid):
    endpoint = f'{self.host}/api/project/projects/{project_uuid}'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    r = requests.get(endpoint, headers=headers)
    data = r.json()["data"]
    if len(data["owner"]) > 0:
      return data["owner"][0]
    else:
      return data["member"][0]

  def _get_bucket_resource_uuid(self, project_uuid):
    if self.bucket_resource_uuid == None:
      project = self._get_project(project_uuid)
      for resource in project["resources"]:
        if resource["resource_type"] == "S3_BUCKET":
          return resource["uuid"]

  def list_folders(self, project_uuid):
    bucket_resource_uuid = self._get_bucket_resource_uuid(project_uuid)    
    endpoint = f'{self.host}/api/s3/folders'
    headers = {"Authorization": f"Bearer {self.token}"}
    params = {
      "parent_resource_uuid": bucket_resource_uuid,
      "project_uuid": project_uuid
    }
    return requests.get(endpoint, params=params, headers=headers)

  def list_maplayers(self, project_uuid, mapset_resource_uuid): 
    endpoint = f'{self.host}/api/s3/maplayers'
    headers = {"Authorization": f"Bearer {self.token}"}
    params = {
      "parent_resource_uuid": mapset_resource_uuid,
      "project_uuid": project_uuid
    }
    return requests.get(endpoint, params=params, headers=headers)

  def create_maplayer(self, project_uuid, mapset_resource_uuid, maplayer_name, settings=""):
    endpoint = f'{self.host}/api/s3/maplayers'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "parent_resource_uuid": mapset_resource_uuid,
      "maplayer_name": maplayer_name,
      "project_uuid": project_uuid,
      "settings": settings
    }
    return requests.post(endpoint, json=data, headers=headers)

  def delete_maplayer(self, project_uuid, maplayer_resource_uuid):
    endpoint = f'{self.host}/api/s3/maplayers'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "resource_uuid": maplayer_resource_uuid,
      "project_uuid": project_uuid,
    }
    return requests.delete(endpoint, json=data, headers=headers)

  def list_mapsets(self, project_uuid, folder_resource_uuid):
    endpoint = f'{self.host}/api/s3/mapsets'
    headers = {"Authorization": f"Bearer {self.token}"}
    params = {
      "parent_resource_uuid": folder_resource_uuid,
      "project_uuid": project_uuid
    }
    return requests.get(endpoint, params=params, headers=headers)

  def create_mapset(self, project_uuid, folder_resource_uuid, mapset_name):
    endpoint = f'{self.host}/api/s3/mapsets'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "parent_resource_uuid": folder_resource_uuid,
      "mapset_name": mapset_name,
      "project_uuid": project_uuid,
    }
    return requests.post(endpoint, json=data, headers=headers)

  def delete_mapset(self, project_uuid, mapset_resource_uuid):
    endpoint = f'{self.host}/api/s3/mapsets'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "resource_uuid": mapset_resource_uuid,
      "project_uuid": project_uuid,
    }
    return requests.delete(endpoint, json=data, headers=headers)

  def create_folder(self, project_uuid, folder_name):
    bucket_resource_uuid = self._get_bucket_resource_uuid(project_uuid)
    endpoint = f'{self.host}/api/s3/folders'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "parent_resource_uuid": bucket_resource_uuid,
      "folder_name": folder_name,
      "project_uuid": project_uuid,
    }
    return requests.post(endpoint, json=data, headers=headers)

  def delete_folder(self, project_uuid, folder_resource_uuid):
    endpoint = f'{self.host}/api/s3/folders'
    headers = {"Authorization": f"Bearer {self.token}", "content-type": "application/json"}
    data = {
      "resource_uuid": folder_resource_uuid,
      "project_uuid": project_uuid,
    }
    return requests.delete(endpoint, json=data, headers=headers)

  def upload_maplayer_data(self, file_abs_location, filename, project_uuid, maplayer_resource_uuid):
    file_abs_path = "{}/{}".format(file_abs_location, filename)
    endpoint = f'{self.host}/api/s3/maplayer/data'
    files = [
      ('maplayer', (filename, open(file_abs_path,'rb'), 'application/octet-stream'))      
    ]
    data = {     
      "project_uuid": project_uuid,
      "resource_uuid": maplayer_resource_uuid
      }    
    headers = {"Authorization": f"Bearer {self.token}"}
    return requests.put(endpoint, files=files, data=data, headers=headers)

  def get_maplayer(self, project_uuid, maplayer_resource_uuid):
    endpoint = f'{self.host}/api/s3/maplayers'
    headers = {"Authorization": f"Bearer {self.token}"}
    params = {
      "resource_uuid": maplayer_resource_uuid,
      "project_uuid": project_uuid
    }
    return requests.get(endpoint, params=params, headers=headers)

  def fetch_data(self, project_uuid, maplayer_resource_uuid, is_json=False, output_filename=None):
    endpoint = f'{self.host}/api/s3/maplayer/data'
    headers = {"Authorization": f"Bearer {self.token}"}
    params = {
      "resource_uuid": maplayer_resource_uuid,
      "project_uuid": project_uuid,
    }
    if output_filename == None:
      output_filename = maplayer_resource_uuid
    with requests.get(endpoint, params=params, headers=headers, stream=True) as r:
      r.raise_for_status()
      with open(output_filename, 'wb+') as f:
        for chunk in r.iter_content(chunk_size=8192): 
          f.write(chunk)
    data = {}
    if is_json == True:
      f = open(output_filename, "r")
      data = json.load(f)
    return data

    
  def fetch_dataframe(self, project_uuid, measurement_resource_uuid, range=[], tags=[], fields=[], limit=100, keep=True):
    endpoint = f'{self.host}/api/influx/data'
    headers = {"Authorization": f"Bearer {self.token}"}
    data = {
      "resource_uuid": measurement_resource_uuid,
      "project_uuid": project_uuid,
      "start": range[0],
      "stop": range[1],
      "tags": tags,
      "fields": fields,
      "limit": limit
    }
    if os.path.isfile(measurement_resource_uuid) != True:
      r = requests.get(endpoint, json=data, headers=headers)
      if r.status_code == 200:     
        with open(measurement_resource_uuid, 'w') as f:        
          f.write(r.json()["data"])          
      else:
        raise Exception(r, "fetch error")

    with open(measurement_resource_uuid, 'r') as f:
      data = f.read()
      if data != "":
        data = pd.read_json(data, orient='index')

    if keep != True:
      os.remove(measurement_resource_uuid)
    return data

  def write_points(self, project_uuid, measurement_resource_uuid, points=[]):
    endpoint = f'{self.host}/api/influx/data'
    headers = {"Authorization": f"Bearer {self.device_token}", "content-type": "application/json"}
    data = {      
      "project_uuid": project_uuid,
      "resource_uuid": measurement_resource_uuid,
      "points": points
    }
    return requests.post(endpoint, json=data, headers=headers)