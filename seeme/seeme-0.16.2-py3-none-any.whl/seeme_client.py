import os
import json
import requests
import http
import zipfile
from requests_toolbelt.multipart.encoder import MultipartEncoder
from urllib.error import HTTPError
from requests import ConnectionError
import random
from dotenv import load_dotenv

REGISTER_ENDPOINT = 'register'
LOGIN_ENDPOINT = 'login'
MODELS_ENDPOINT = 'models'
TRAINING_REQUESTS_ENDPOINT = 'trainingrequests'
INFERENCE_ENDPOINT = 'inferences'
DATASETS_ENDPOINT = 'datasets'
VERSIONS_ENDPOINT = 'versions'
LABELS_ENDPOINT = 'labels'
SPLITS_ENDPOINT = 'splits'
ITEMS_ENDPOINT = 'items'
ANNOTATIONS_ENDPOINT = 'annotations'
SHARES_ENDPOINT = 'share'
APPLICATIONS_ENDPOINT = 'applications'
SUPPORTED_DOWNLOAD_EXTENSIONS = [ "pkl", "mlmodel", "tflite", "onnx", "names", "labels", "weights", "cfg", "conversion_cfg" ]

ID = "id"
DATASET_CONTENT_TYPE_IMAGES = "images"
DATASET_CONTENT_TYPE_TEXT = "text"
DATASET_CONTENT_TYPE_TABULAR = "tabular"
DATASET_CONTENT_TYPE_NER = "ner"

DATASET_FORMAT_FOLDERS = "folders"
DATASET_FORMAT_YOLO = "yolo"
DATASET_FORMAT_CSV = "csv"
DATASERT_FORMAT_NER = "ner"

load_dotenv()

class Client():
  """ 
  Client class to interact with the SeeMe.ai backend, allowing you to manage models, datasets, predictions and training requests.
  
  Parameters:
  ---
  
  username (optional) : the username for the account you want to use;
  apikey (optional) : the API key for the username you want user;
  backend (prefilled): the backend the client communicates with.

  Note: 
  username and apikey are optional but they need to used together in order to be authenticated. Authentication will be used on subsequent requests.
  Alternatively, you can use the login method (see below)
  """
  def __init__(self, username:str=None, apikey:str=None, backend:str=None):
    self.headers = {}

    env_api_key = os.getenv("SEEME_API_KEY")
    env_username = os.getenv("SEEME_USERNAME")
    env_backend = os.getenv("SEEME_BACKEND")

    if env_username is not None and env_api_key is not None:
      self.username = env_username
      self.update_auth_header(env_username, env_api_key)
      self.backend = env_backend

    if username is not None and apikey is not None:
      self.username = username
      self.update_auth_header(username, apikey)

    if env_backend is None:
      self.backend = "https://api.seeme.ai/api/v1/"

    if backend is not None:
      if not backend.endswith("/"):
        backend = backend + "/"
      self.backend = backend
      
    self.endpoints = {
      REGISTER_ENDPOINT: self.crud_endpoint(REGISTER_ENDPOINT),
      LOGIN_ENDPOINT: self.crud_endpoint(LOGIN_ENDPOINT),
      MODELS_ENDPOINT: self.crud_endpoint(MODELS_ENDPOINT),
      TRAINING_REQUESTS_ENDPOINT: self.crud_endpoint(TRAINING_REQUESTS_ENDPOINT),
      INFERENCE_ENDPOINT: self.crud_endpoint(INFERENCE_ENDPOINT),
      DATASETS_ENDPOINT: self.crud_endpoint(DATASETS_ENDPOINT),
      APPLICATIONS_ENDPOINT: self.crud_endpoint(APPLICATIONS_ENDPOINT)
    }
    self.applications = []
    self.supported_dataset_export_formats = [ DATASET_FORMAT_FOLDERS, DATASET_FORMAT_YOLO, DATASET_FORMAT_CSV ]
    self.supported_dataset_import_formats = [ DATASET_FORMAT_FOLDERS, DATASET_FORMAT_YOLO, DATASET_FORMAT_CSV ]


    if self.is_logged_in():
      self.applications = self.get_applications()

  # -- Login / Registration --

  def register(self, username:str, email:str, password:str, firstname:str, name:str):
    """  
    Register a new user with a username, email and password. 
    
    Optionally, you can add a first and last name.
    """
    register_api = self.endpoints[REGISTER_ENDPOINT]
    register_data = {
      'username': username,
      'email': email,
      'password': password,
      'firstname': firstname,
      'name': name,
    }

    r = requests.post(register_api, data=json.dumps(register_data), headers=self.headers)

    registered_user = r.json()

    if "message" in registered_user:
      raise ValueError(registered_user["message"])
    
    return registered_user

  def login(self, username:str, password:str):
    """ 
    Log in with a username and password.
    
    The username and password will be used to get the API key from the backend. 
    The method will fail if the user is not known, the password is incorrect, or the service cannot be reached.
    """
    login_api = self.endpoints[LOGIN_ENDPOINT]
    login_data = {
      'username': username,
      'password': password
    }
    
    logged_in = self.api_post(login_api, login_data)

    username = logged_in["username"]
    apikey = logged_in["apikey"]

    user_id = logged_in["id"]

    self.update_auth_header(username, apikey)
    self.username = username
    self.user_id = user_id

    self.applications =  self.get_applications()

    return logged_in
      
  def logout(self):
    """ Log out the current user."""
    self.update_auth_header("", "")

  def get_application_id(self, base_framework="pytorch", framework="", base_framework_version="1.10.0", framework_version="", application="image_classification"):
    """ Returns the application_id for the application you want to deploy:
    
    Parameters
    ---

    base_framework: the base_framework for the application (e.g. "pytorch", ...)
    base_framework_version: the version of the base_framework (e.g. "1.9.0", ...)
    framework: the framework for the application (e.g. "fastai", ...)
    framework_version: the version of the framework (e.g. "2.5.2", ...)
    application: the type of application you want to deply (e.g. "image_classification", "object_detection", "text_classification", "structured")

    Note
    ---

    To get a list of all the supported applications, see the "get_applications" method.
    """
    if self.applications == []:
      self.applications = self.get_applications()

    for f in self.applications:
      if f["base_framework"] == base_framework \
        and f["framework"] == framework \
        and f["base_framework_version"] == base_framework_version \
        and f["framework_version"] == framework_version \
        and f["application"] == application:
          return f["id"]
    
    for f in self.applications:
      if f["base_framework"] == base_framework \
        and f["framework"] == framework \
        and f["base_framework_version"] in base_framework_version \
        and f["framework_version"] == framework_version \
        and f["application"] == application:
          return f["id"]
    
    err_msg = f"\n\nYour config is not supported:\n\n--- \n\nBase framework: {base_framework} (v{base_framework_version})\nFramework:      {framework} (v{framework_version}) \nApplication:    {application} \n\n---\n\n is not supported.\n\nPlease contact: support@seeme.ai."
      
    raise NotImplementedError(err_msg)
    
  # -- CRUD models --

  def get_models(self):
    self.requires_login()

    model_api = self.endpoints[MODELS_ENDPOINT]

    return self.api_get(model_api)

  def create_full_model(self, model):
    return self.create_model(model)

  def create_model(self, model):
    self.requires_login()

    if not "auto_convert" in model:
      model["auto_convert"] = True

    model_api = self.endpoints[MODELS_ENDPOINT]

    return self.api_post(model_api, model)

  def get_model(self, model_id:str):
    self.requires_login()

    model_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id

    return self.api_get(model_api)

  def update_model(self, model):
    self.requires_login()

    assert model
    assert model[ID]
    model_api = self.endpoints[MODELS_ENDPOINT] + "/" + model[ID]
    return self.api_put(model_api, model)

  def delete_model(self, model_id:str):
    self.requires_login()
    delete_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id

    return self.api_delete(delete_api)

  def upload_model(self, model_id:str, folder:str="data", filename:str="export.pkl"):
    model_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/upload"

    return self.upload(model_upload_api, folder, filename, 'application/octet-stream')
  
  def upload_logo(self, model_id:str, folder:str="data", filename:str="logo.jpg"):
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"

    model_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/upload"

    return self.upload(model_upload_api, folder, filename,  content_type)
  
  def get_logo(self, model):
    logo_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + model["id"] + "/download/logo"
    return self.api_download(logo_endpoint, model["logo"])
  
  def download_active_model(self, model, asset_type="pkl"):
    """
      asset_type: mlmodel, tflite, onnx, pkl, labels, names
    """

    if asset_type not in SUPPORTED_DOWNLOAD_EXTENSIONS:
      raise NotImplementedError

    model_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + model["id"] + "/download/" + asset_type

    extension = asset_type

    if asset_type == "labels":
      extension = "txt"

    name = model["active_version_id"]+"." + extension

    if asset_type == "conversion_cfg":
      name = model["active_version_id"]+"_conversion.cfg"

    return self.api_download(model_endpoint, name)

  def upload(self, url:str, folder:str, filename:str, content_type:str):
    self.requires_login()

    data = MultipartEncoder(
                fields={
                    'file': (filename, open(folder + "/" + filename, 'rb'), content_type)}
                       )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(url, data=data, headers=content_headers)

  # -- CRUD Model Versions

  def get_model_versions(self, model_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}"

    return self.api_get(model_version_api)

  def get_model_version(self, model_id, version_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}/{version_id}"

    return self.api_get(model_version_api)

  def create_model_version(self, model_id, version):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}"

    return self.api_post(model_version_api, version)
  
  def update_model_version(self, version):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{version['model_id']}/{VERSIONS_ENDPOINT}/{version['id']}"

    return self.api_put(model_version_api, version)

  def delete_model_version(self, model_id, version_id):
    self.requires_login()

    model_version_api = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{VERSIONS_ENDPOINT}/{version_id}"

    return self.api_delete(model_version_api)

  def upload_model_version(self, version, folder:str="data", filename:str="export.pkl"):

    model_version_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + version['model_id']  + "/"+ VERSIONS_ENDPOINT + "/" + version["id"] + "/upload"

    return self.upload(model_version_upload_api, folder, filename, 'application/octet-stream')

  def upload_model_version_logo(self, model_id, version_id, folder:str="data", filename:str="logo.jpg"):
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"

    model_version_upload_api = self.endpoints[MODELS_ENDPOINT] + "/" + model_id  + "/"+ VERSIONS_ENDPOINT + version["id"] + "/upload"

    return self.upload(model_version_upload_api, folder, filename, content_type)
  
  def download_version(self, version, asset_type):
    """
      asset_type: mlmodel, tflite, onnx, pkl, labels, names, txt
    """

    if asset_type not in SUPPORTED_DOWNLOAD_EXTENSIONS:
      raise NotImplementedError()

    extension = asset_type

    if asset_type == "labels":
      extension = "txt"

    name = version["id"]+"." + extension

    if asset_type == "conversion_cfg":
      name = version["id"]+"_conversion.cfg"

    version_endpoint = self.endpoints[MODELS_ENDPOINT] + "/" + version["model_id"] + "/" + VERSIONS_ENDPOINT + "/" + version["id"] + "/download/" + asset_type
    return self.api_download(version_endpoint, name)
  
  # -- Share model --
  def share_model(self, model_id, email, send_invite=False):
    self.requires_login()

    share = {
      "email": email,
      "entity_type": MODELS_ENDPOINT,
      "entity_id": model_id,
      "without_invite": not send_invite
    }

    share_url = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{SHARES_ENDPOINT}"

    return self.api_post(share_url, share)

  def get_model_shares(self, model_id):
    self.requires_login()

    share_url = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{SHARES_ENDPOINT}"

    return self.api_get(share_url)

  def delete_model_share(self, model_id, share_id):
    self.requires_login()

    share_url = f"{self.endpoints[MODELS_ENDPOINT]}/{model_id}/{SHARES_ENDPOINT}/{share_id}"

    return self.api_delete(share_url)

  # -- CRUD requests --

  def get_training_requests(self, applicationId="", started="", finished=""):
    self.requires_login()

    training_requests_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT]

    if applicationId != "":
      training_requests_api += f"?applicationId={applicationId}&started={started}&finished={finished}"

    return self.api_get(training_requests_api)
  
  def create_training_request(self, version):
    self.requires_login()

    req_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT]
    req_data = {
      'dataset_id': version["dataset_id"],
      'dataset_version_id': version["id"]
    }

    return self.api_post(req_api, req_data)

  def update_training_request(self, training_request):
    self.requires_login()

    assert training_request
    assert training_request[ID]
    training_request_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT] + "/" + training_request[ID]
    return self.api_put(training_request_api, training_request)

  def delete_training_request(self, id:str):
    self.requires_login()
    delete_api = self.endpoints[TRAINING_REQUESTS_ENDPOINT] + "/" + id

    return self.api_delete(delete_api)

  # -- CRUD Inference --

  def predict(self, model_id:str, item, input_type="image_classification", params={}):
      return self.inference(model_id, item, input_type, params)

  def inference(self, model_id:str, item, input_type="image_classification", params={}):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + model_id

    if input_type=="image_classification" or input_type=="object_detection" or input_type=="ocr":

      item_name = os.path.basename(item)
      data = MultipartEncoder(
                  fields={
                      'file': (item_name, open(item, 'rb'), 'application/octet-stream')}
                        )

      content_headers = self.headers

      content_headers['Content-Type'] = data.content_type

      return self.api_upload(inference_api, data=data, headers=content_headers)
    elif input_type=="text_classification" or input_type=="language_model" or input_type=="ner":
      data = {
        'input_text': item
      }

      return self.api_post(inference_api, data)
    elif input_type=="structured":
      data = {
              'input_text': item
      }

      return self.api_post(inference_api, data)
    else:
      raise NotImplementedError

  def version_predict(self, version, item, input_type="image_classification"):
    return self.version_inference(version, item, input_type)

  # Obsolete, will be replaced by version_predict
  def version_inference(self, version, item, input_type="image_classification"):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + version['model_id'] + "/" + VERSIONS_ENDPOINT + "/" + version['id']

    if input_type=="image_classification":

      item_name = os.path.basename(item)
      data = MultipartEncoder(
                  fields={
                      'file': (item_name, open(item, 'rb'), 'application/octet-stream')}
                        )

      content_headers = self.headers

      content_headers['Content-Type'] = data.content_type

      return self.api_upload(inference_api, data=data, headers=content_headers)
    elif input_type=="text_classification":
        data = {
          'input_text': item
        }

        return self.api_post(inference_api, data)
    elif input_type=="structured":
      data = {
              'input_text': item
      }

      return self.api_post(inference_api, data)
    else:
      raise NotImplementedError

  def update_inference(self, inference):
    self.requires_login()

    inference_api = self.endpoints[INFERENCE_ENDPOINT] + "/" + inference["id"]

    return self.api_put(inference_api, inference)

  # -- CRUD applicationS --
  def get_applications(self):
    self.requires_login()

    application_api = self.endpoints[APPLICATIONS_ENDPOINT]

    return self.api_get(application_api)

  # -- CRUD DATASETS --

  def get_datasets(self):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT]

    return self.api_get(dataset_api)

  def create_dataset(self, dataset):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT]

    return self.api_post(dataset_api, dataset)

  def get_dataset(self, dataset_id:str):
    self.requires_login()

    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset_id

    return self.api_get(dataset_api)

  def update_dataset(self, dataset):
    self.requires_login()

    assert dataset
    assert dataset[ID]
    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset[ID]
    return self.api_put(dataset_api, dataset)

  def upload_dataset_logo(self, dataset_id:str, folder:str="data", filename:str="logo.jpg"):
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"

    datasets_upload_api = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset_id  + "/upload"

    return self.upload(datasets_upload_api, folder, filename,  content_type)

  def get_dataset_logo(self, dataset):
    logo_endpoint = self.endpoints[DATASETS_ENDPOINT] + "/" + dataset["id"] + "/logo"
    return self.api_download(logo_endpoint, dataset["logo"])

  def delete_dataset(self, id:str):
    self.requires_login()
    dataset_api = self.endpoints[DATASETS_ENDPOINT] + "/" + id

    return self.api_delete(dataset_api)
  
  # -- Share Dataset --
  def share_dataset(self, dataset_id, email, send_invite=False):
    self.requires_login()

    share = {
      "email": email,
      "entity_type": DATASETS_ENDPOINT,
      "entity_id": dataset_id,
      "without_invite": not send_invite
    }

    share_url = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{SHARES_ENDPOINT}"

    return self.api_post(share_url, share)

  def create_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}"

    return self.api_post(dataset_version_api, dataset_version)

  def get_dataset_versions(self, dataset_id):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}"

    return self.api_get(dataset_version_api)
  
  def get_dataset_version(self, dataset_id, dataset_version_id):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}"

    return self.api_get(dataset_version_api)

  def update_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version['id']}"

    return self.api_put(dataset_version_api, dataset_version)

  def delete_dataset_version(self, dataset_id, dataset_version):
    self.requires_login()

    dataset_version_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version['id']}"

    return self.api_delete(dataset_version_api)
  
  def create_dataset_label(self, dataset_id, dataset_version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}"

    return self.api_post(labels_api, label)

  def get_dataset_labels(self, dataset_id, dataset_version_id):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}"

    return self.api_get(labels_api)
  
  def get_dataset_label(self, dataset_id, dataset_version_id, label_id):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}/{label_id}"

    return self.api_get(labels_api)

  def update_dataset_label(self, dataset_id, dataset_version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}/{label['id']}"

    return self.api_put(labels_api, label)

  def delete_dataset_label(self, dataset_id, dataset_version_id, label):
    self.requires_login()

    labels_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}/{label['id']}"

    return self.api_delete(labels_api)
  
  def get_label_stats(self, dataset_id, dataset_version_id, split_id):
    self.requires_login()

    label_stats_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{LABELS_ENDPOINT}/{SPLITS_ENDPOINT}/{split_id}"
    
    return self.api_get(label_stats_api) 
  
  def create_dataset_split(self, dataset_id, dataset_version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}"

    return self.api_post(splits_api, split)

  def get_dataset_splits(self, dataset_id, dataset_version_id):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}"

    return self.api_get(splits_api)
  
  def get_dataset_split(self, dataset_id, dataset_version_id, split_id):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}/{split_id}"

    return self.api_get(splits_api)

  def update_dataset_split(self, dataset_id, dataset_version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}/{split['id']}"

    return self.api_put(splits_api, split)

  def delete_dataset_split(self, dataset_id, dataset_version_id, split):
    self.requires_login()

    splits_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}/{split['id']}"

    return self.api_delete(splits_api)
  
  def get_dataset_items(self, dataset_id, dataset_version_id, params=None):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}"

    return self.api_get(items_api, params=params)

  def create_dataset_item(self, dataset_id, dataset_version_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}"

    return self.api_post(items_api, item)

  def get_dataset_item(self, dataset_id, dataset_version_id, item_id):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}/{item_id}"

    return self.api_get(items_api)

  def update_dataset_item(self,  dataset_id, dataset_version_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}/{item['id']}"

    return self.api_put(items_api, item)

  def delete_dataset_item(self, dataset_id, dataset_version_id, split_id, item):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{SPLITS_ENDPOINT}/{split_id}/{ITEMS_ENDPOINT}/{item['id']}"

    return self.api_delete(items_api)

  def upload_dataset_item_image(self, dataset_id, dataset_version_id, item_id, folder, filename):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}/{item_id}/upload"
    
    if filename.endswith("jpg"):
      content_type="image/jpg"
    elif filename.endswith("jpeg"):
      content_type="image/jpeg"
    elif filename.endswith("png"):
      content_type="image/png"
    else:
      print("Image type not supported")
      return

    data = MultipartEncoder(
                fields={
                    'file': (filename, open(folder + "/" + filename, 'rb'), content_type)}
                       )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(items_api, data=data, headers=content_headers)

  def download_dataset_item_image(self, dataset_id, dataset_version_id, item_id, download_location, thumbnail=False):
    self.requires_login()

    items_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ITEMS_ENDPOINT}/{item_id}/download"
  
    if thumbnail:
      items_api += "?thumbnail=true"

    return self.api_download(items_api, download_location)
  
  def annotate(self, dataset_id, dataset_version_id, annotation):
    self.requires_login()

    annotation_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ANNOTATIONS_ENDPOINT}"

    return self.api_post(annotation_api, annotation)

  def update_annotation(self, dataset_id, dataset_version_id, annotation):
    self.requires_login()

    annotation_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ANNOTATIONS_ENDPOINT}/{annotation['id']}"

    return self.api_put(annotation_api, annotation)

  def delete_annotation(self, dataset_id, dataset_version_id, annotation_id):
    self.requires_login()

    annotation_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/{ANNOTATIONS_ENDPOINT}/{annotation_id}"

    return self.api_delete(annotation_api)

  def download_dataset(self, dataset_id, dataset_version_id, split_id="", extract_to_folder="data", download_file="dataset.zip", remove_download_file=True, export_format=""):
    self.requires_login()

    dataset_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/download"

    if split_id != "":
      dataset_api = f"{dataset_api}/{split_id}"

    params = None

    if len(export_format) > 0:
      if export_format not in self.supported_dataset_export_formats:
        print(f"WARNING: Requested export format: '{export_format}' not supported. Returning the default export format.")

    params = {
      "format": export_format
    }

    self.api_download(dataset_api, download_file, params=params)

    with zipfile.ZipFile(download_file, 'r') as zip_ref:
      zip_ref.extractall(extract_to_folder)

    if remove_download_file:
      os.remove(download_file)
    
  def upload_dataset_version(self, dataset_id, dataset_version_id, folder="data", filename="dataset.zip", format=""):
    self.requires_login()

    dataset_api = f"{self.endpoints[DATASETS_ENDPOINT]}/{dataset_id}/{VERSIONS_ENDPOINT}/{dataset_version_id}/upload"

    if len(format) > 0:
      if format in self.supported_dataset_import_formats:
        dataset_api = f"{dataset_api}/{format}"
      else:
        print("Supported import formats")
        print(self.supported_dataset_import_formats)
        raise NotImplementedError()

    content_type="application/x-zip-compressed"

    data = MultipartEncoder(
            fields={
                'file': (filename, open(folder + "/" + filename, 'rb'), content_type)
            }
          )

    content_headers = self.headers

    content_headers['Content-Type'] = data.content_type

    return self.api_upload(dataset_api, data=data, headers=content_headers)

  # Convenience methods

  def get_apikey(self):
    return self.apikey
  
  def random_color(self):
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    rgb = (r,g,b)

    return '#%02x%02x%02x' % rgb

  # Helpers

  def requires_login(self):
    if not self.is_logged_in():
      raise Exception("You need to be logged in for this.")

  def update_applications(self):
    self.applications = get_applications()

  def update_auth_header(self, username:str=None, apikey:str=None):
    if username == None or apikey == None:
      return

    self.apikey = apikey
    
    self.headers = {
      "Authorization": f"{username}:{apikey}"
    }
  
  def is_logged_in(self):
    if "Authorization" in self.headers:
      return True

    return False

  def crud_endpoint(self, endpoint:str):
    return f"{self.backend}{endpoint}"

  ## CRUD API methods

  def api_get(self, api:str, params=None):
    try:
      r = requests.get(api, headers=self.headers, params=params)
      r.raise_for_status()
      return r.json()
    except HTTPError as err:
      print(err)
      print(err.code)

  def api_post(self, api:str, data, params=None):
    data = json.dumps(data)

    try:
      r = requests.post(api, data=data, headers=self.headers)
      r.raise_for_status()
      return r.json()
    except HTTPError as err:
      print(err)
      print(err.code)

  def api_upload(self, api:str, data, headers):
    try:
      r = requests.post(api, data=data, headers=headers)
      r.raise_for_status()
      return r.json()
    except BrokenPipeError as con_err:
      print(con_err)
    except HTTPError as err:
      print(err)
      print(err.code)
  
  def api_put(self, api:str, data):
    try:
      data = json.dumps(data)
      r = requests.put(api, data=data, headers=self.headers)
      r.raise_for_status()
      return r.json()
    except HTTPError as err:
      print(err)
      print(err.code)
  
  def api_delete(self, api:str):
    try:
      r = requests.delete(api, headers=self.headers)
      r.raise_for_status()
      return r.json()
    except HTTPError as err:
      print(err)
      print(err.code)

  def api_download(self, api:str, filename:str, params=None):
    try:
      r = requests.get(api, allow_redirects=True, headers=self.headers, params=params)
      r.raise_for_status()
      open(filename, "wb").write(r.content)
    except HTTPError as err:
      print(err)
      print(err.code)