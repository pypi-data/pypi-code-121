import json
import os
import tornado
import shutil

from jupyter_server.base.handlers import APIHandler
from .utils import update_analytics


def clean_up(dirname: str):
    if os.path.exists(dirname) and os.path.isdir(dirname):
        shutil.rmtree(dirname)


def accept_changes(dirname, filename, uid):
    if not uid:
        return False

    # Create base file path
    old_file = os.path.join(dirname, filename)
    # Create transformed file path
    new_file = os.path.join(
        dirname, "." + uid, "mutableai_transform", filename)
    # If we find the transformed file then
    # read from that file and replace the base file
    # after this action we delete that folder.
    if os.path.exists(new_file):
        # Read in the file
        with open(new_file, "r") as file:
            filedata = file.read()
    if os.path.exists(old_file) and filedata:
        # Write the file out again
        with open(old_file, "w") as file:
            file.write(filedata)
        transformed_dirname = os.path.join(dirname, "." + uid)
        clean_up(transformed_dirname)
        return True
    return False


def decline_changes(dirname, uid):
    """
    Delete the unique folder name if declined.
    """
    if not uid:
        return False
    dirpath = os.path.join(dirname, "." + uid)
    clean_up(dirpath)
    return True


class FileActionRouterHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps(
                {"data": "This is /jlab-ext-example/TRANSFORM_NB endpoint!"})
        )

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()

        # base directory name
        dirname = input_data.get("dirname", "")

        # base file name
        file_name = input_data.get("filename", "")

        # uid for the transformed name
        uid = input_data.get("uid", "")

        # File action type

        action = input_data.get("action", "")

        url = "https://" + input_data.get("url", "")

        api_key = input_data.get("api_key", "")
        status = False

        if action == "accept":
            status = accept_changes(dirname, file_name, uid)
            update_analytics(url, api_key, "accepted")
        elif action == "decline":
            status = decline_changes(dirname, uid)
            update_analytics(url, api_key, "declined")

        if status:
            self.finish({"status": "completed"})
        else:
            self.finish({"status": "failed"})
