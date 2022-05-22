from importlib.resources import path
import json
import requests
import tornado
import os
import tarfile
import threading
from urllib.parse import urljoin
from uuid import uuid4
import subprocess

from io import BytesIO
from jupyter_server.base.handlers import APIHandler
import base64


TRANSFORM_NB_ROUTE = "TRANSFORM_NB"


def create_file_packet(nb_filename: str) -> dict:
    """Create a file packet for the transform docker container
    Args:
      filename: the name of the file to be sent to the transform docker container
    Returns:
      A dict that is the file packet for the transform docker container
    """
    f = open(nb_filename, "rb").read()
    data = {
        "file_name": nb_filename,
        "file_data": base64.b64encode(f).decode("utf-8"),
    }
    return data


def call_transform_nb(
    filename: str, api_key: str, domain: str, mode: str, instruction: str = ""
) -> dict:
    """Call the transform docker container
    Args:
      filename: the name of the file to be sent to the transform docker container
    Returns:
      A dict that is the response from the transform docker container
    """
    data = create_file_packet(filename)
    data["mode"] = mode

    if instruction:
        data["instruction"] = instruction
    url = urljoin("https://" + domain, TRANSFORM_NB_ROUTE)
    response = requests.post(
        url=url,
        json=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
    )
    return response


def threaded_transform(input_data, dirname, uid):
    nb_filename = input_data["name"]
    instruction = input_data.get("instruction", "")

    api_key, domain, mode = (
        input_data["apiKey"],
        input_data["transformDomain"],
        input_data["mode"],
    )

    response = call_transform_nb(nb_filename, api_key, domain, mode, instruction)
    json_response = response.json()

    new_path = os.path.join(dirname, "." + uid)
    if not os.path.exists(new_path):
        if os.name is "nt":
            subprocess.call(["attrib", "+H", new_path])
        else:
            os.makedirs(new_path)

    # untar the tar file
    tar_file_content = base64.b64decode(json_response["tar_file_data"])

    # extract tar without writing to disk
    tar_file = tarfile.open(fileobj=BytesIO(tar_file_content), mode="r:gz")

    # save and extract to disk
    tar_file.extractall(path=new_path)


class TransformJupyterRouteHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps({"data": "This is /jlab-ext-example/TRANSFORM_NB endpoint!"})
        )

    @tornado.web.authenticated
    def post(self):

        # input_data is a dictionary with a key "name"
        input_data = self.get_json_body()

        nb_filename = input_data["name"]

        # get dirname of nb_filename
        dirname = os.path.dirname(nb_filename)
        uid = str(uuid4())

        x = threading.Thread(target=threaded_transform, args=(input_data, dirname, uid))
        x.start()

        self.finish(
            json.dumps(
                {
                    "message": "processing transformation",
                    "dirname": str(dirname),
                    "uid": uid,
                }
            )
        )
