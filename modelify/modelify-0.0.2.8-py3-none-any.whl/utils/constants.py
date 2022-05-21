import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()


MODELIFY_API_URL = os.getenv("MODELIFY_API_URL", "https://api.modelify.ai/v1")
MODELIFY_TOKEN_VALIDATION_URL = MODELIFY_API_URL + "/registry/me"
MODELIFY_INFO_URL = MODELIFY_API_URL + "/info"
MODELIFY_DEPLOY_URL =  MODELIFY_API_URL + "/registry/deploy"
MODELIFY_UPLOAD_URL = MODELIFY_API_URL + "/registry/upload-url"
MODELIFY_DOWNLOAD_URL = MODELIFY_API_URL + "/registry/download-url"


def get_app_folder() -> str:
  return os.getenv("MODELIFY_APP_FOLDER", os.path.join(os.getcwd(), "modelify_application"))

APP_FOLDER = get_app_folder()

class ModelifyFile(Enum):

    def __new__(cls, value, file_name, content_type ):
        t = object.__new__(cls)
        t._value_ = value
        t._filename = file_name
        t._content_type = content_type
        return t

    
    MODEL = ("MODEL", "model.onnx","application/octet-stream")
    CONFIG = ("CONFIG", "config.yaml", "text/yaml")
    PREPROCESS = ("PREPROCESS", "preprocess.pkl", "application/octet-stream")
    POSTPROCESS = ("POSTPROCESS", "postprocess.pkl", "application/octet-stream")
    REQUIREMENTS = ("REQUIREMENTS", "requirements.txt", "text/plain")
    EXTERNAL_FILE = ("EXTERNAL_FILE", "external.py" , "text/x-python-script")


    def __repr__(self):
        return str(self.name)

    @property
    def file_name(self):
        return self._filename
    
    @property
    def content_type(self):
        return self._content_type
