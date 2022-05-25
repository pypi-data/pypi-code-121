import json
import os
import time

import jwt
from servicefoundry.cli.util import json_default_encoder

from servicefoundry.internal.const import SESSION_FILE

class ServiceFoundrySession:
    def __init__(
        self,
        client_id,
        access_token,
        refresh_token,
        session_file_location=SESSION_FILE,
        refresher=None,
        cluster=None,
        workspace=None,
    ):
        self.client_id = client_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session_file_location = session_file_location
        self.refresher = refresher
        self.cluster = cluster
        self.workspace = workspace

    def save_session(self):
        with open(self.session_file_location, "w") as file:
            json.dump(
                {
                    "client_id": self.client_id,
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "cluster": self.cluster,
                    "workspace": self.workspace,
                },
                file,
                default=json_default_encoder
            )
            # Ensure it is written to disk
            file.flush()
            os.fsync(file.fileno())

    def refresh_access_token(self):
        self.access_token, self.refresh_token = self.refresher(self)
        self.save_session()

    def get_expiry(self):
        return self.decode()["exp"]

    def get_ttl(self):
        return self.get_expiry() - time.time()

    def get_user_details(self):
        decoded = self.decode()
        return {"username": decoded["preferred_username"], "email": decoded["email"]}

    def decode(self):
        return jwt.decode(self.access_token, options={"verify_signature": False})

    def set_cluster(self, cluster):
        self.cluster = cluster
        return cluster

    def get_cluster(self):
        return self.cluster

    def set_workspace(self, workspace):
        self.workspace = workspace
        return workspace

    def get_workspace(self):
        return self.workspace
