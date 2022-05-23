import json
import os
import tornado

from jupyter_server.base.handlers import APIHandler


def check_transformation_exists(dirname: str, uid: str):
    """
    Check if we can find the transformed file
    inside the unique folder we generate from uid.
    """
    path_exist = os.path.join(dirname, "." + uid, "mutableai_transform")
    if os.path.exists(path_exist):
        onlyfiles = [
            f
            for f in os.listdir(path_exist)
            if os.path.isfile(os.path.join(path_exist, f))
        ]
        for file in onlyfiles:
            if "ipynb" in file.split("."):
                return os.path.join(path_exist, file)

    return None


class CheckStatusRouterHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps({"data": "This is /jlab-ext-example/TRANSFORM_NB endpoint!"})
        )

    @tornado.web.authenticated
    def post(self):
        input_data = self.get_json_body()
        dirname = input_data["dirname"]
        uid = input_data["uid"]

        file = check_transformation_exists(dirname, uid)

        if file:
            self.finish({"status": "finished", "file": file})
        else:
            self.finish({"status": "pending", "file": ""})
