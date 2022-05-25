"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

from blackduck.HubRestApi import HubInstance
from blackduck_c_cpp.util import util
from requests.exceptions import ConnectionError


class HubAPI:

    def __init__(self, bd_url, api_token, insecure):
        self.bd_url = bd_url
        self.api_token = api_token
        self.insecure = insecure
        self.hub = None

    def authenticate(self):
        try:
            self.hub = HubInstance(self.bd_url, api_token=self.api_token, insecure=self.insecure,
                                   write_config_flag=False)
        except KeyError:
            util.error_and_exit("Make sure you have the right API key and --insecure flag is set correctly")
        except ConnectionError:
            util.error_and_exit(
                "ConnectionError occurred. Make sure you have the correct url and insecure flag is set correctly")

    def create_or_verify_project_version_exists(self, project_name, version_name, phase='DEVELOPMENT'):
        self.authenticate()
        project = self.hub.get_project_by_name(project_name)
        if project:
            version = self.hub.get_version_by_name(project, version_name)
            if version:
                return
            if not version:
                response = self.hub.create_project_version(project, version_name, parameters={'phase': phase})
        else:
            response = self.hub.create_project(project_name, version_name, parameters={'version_phase': phase})

        if not response.ok:
            util.error_and_exit(
                "Error creating project version -- (Response({}): {})".format(response.status_code, response.text))

    def get_hub_version(self):
        hub_version_dict = {}
        try:
            self.authenticate()
            hub_version_dict = self.hub.version_info
        except:  # in case we don't get version info
            hub_version_dict['version'] = '0.0.0'
        return hub_version_dict['version']
