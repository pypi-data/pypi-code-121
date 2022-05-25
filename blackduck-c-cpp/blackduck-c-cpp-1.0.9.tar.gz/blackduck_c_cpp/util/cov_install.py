"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
from google.cloud import storage
from google.oauth2 import service_account
import hashlib
import shutil
import logging
import json
from blackduck_c_cpp.util import util
import os
import stat
import tempfile
from blackduck_c_cpp.util import global_settings


class CoverityInstall:
    """Class to download latest coverity package for different OS """
    def __init__(self, cov_home, hub_api, platform, force, blackduck_c_cpp_version):
        hub_api.authenticate()
        self.hub_api = hub_api
        self.hub = hub_api.hub
        self.cov_home = cov_home
        self.platform = platform
        if self.platform == global_settings.darwin_pltfrm:
            self.platform = global_settings.macos_pltfrm
            platform = global_settings.macos_pltfrm
        self.force = force
        self.cov_zippath = 'cov-latest' + '-' + platform + '.zip'
        self.cov_filepath = os.path.join(self.cov_home, self.cov_zippath)
        self.tool_token_response = None
        self.tool_token_json = None
        self.gcp_filepath = None
        self.blackduck_c_cpp_version = blackduck_c_cpp_version
        self.min_cov_year_for_api = 2021
        self.min_cov_vers_for_api = 10
        try:
            self.run()
        except Exception as e:
            logging.error("Exception occurred: {}".format(e))

    def hub_api_tool_token(self):
        """
        get token from hub tool-token api
        """
        data = json.dumps({"clientName": "blackduck-c-cpp", "clientVersion": self.blackduck_c_cpp_version})
        self.tool_token_response = self.hub.execute_post('{}/api/tool-token'.format(self.hub.config['baseurl']), data)
        if not self.tool_token_response.ok:
            logging.error(
                "Problem connecting to /api/tool-token -- (Response({}): {})".format(
                    self.tool_token_response.status_code,
                    self.tool_token_response.text))
        self.tool_token_json = self.tool_token_response.json()

    def find_any_coverity_version(self):
        """check if any version of coverity is present"""
        if os.path.exists(self.cov_filepath):
            logging.debug(
                "Using older coverity version already present on the system from {}".format(
                    self.cov_filepath))
        else:
            util.error_and_exit("No coverity version is present on the system. Please contact Synopsys Support")

    def gcp_download(self):
        """
        Download mini coverity package from gcp if credentials are correct
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tempfile_path = os.path.join(tmpdir, self.cov_zippath)
            try:
                storage_credentials = service_account.Credentials.from_service_account_info(
                    self.tool_token_json['jsonWebToken'])
                client = storage.Client(credentials=storage_credentials)
                gcp_path_split = self.gcp_filepath.split("/")
                object_name = gcp_path_split[-1]
                bucket_name = gcp_path_split[-2]
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(object_name)
                logging.info("Downloading coverity latest version from gcp to {}".format(tempfile_path))
                blob.download_to_filename(tempfile_path)
            except Exception as e:
                logging.warning("unable to connect to gcp - {}".format(e))
                self.find_any_coverity_version()
                return
            if not self.gcp_checksum == hashlib.sha256(open(tempfile_path, 'rb').read()).hexdigest():
                if not self.force:
                    logging.error(
                        "There's a mismatch between api tool token and gcp checksums, If you want to continue with previous version of coverity, please set force to True in yaml file and retry")
                    util.error_and_exit(
                        "PLEASE CONTACT SYNOPSYS SUPPORT IMMEDIATELY: Mismatch between GCP Bucket and Tool Token Sha2.")
                else:
                    self.find_any_coverity_version()
            else:
                if os.path.exists(self.cov_filepath):
                    os.remove(self.cov_filepath)
                dest = shutil.move(tempfile_path, self.cov_filepath)
                logging.debug("moving coverity files from {} to {}".format(tempfile_path, dest))
                self.unzip_downloaded()

    def unzip_downloaded(self):
        """
        unzip coverity package
        """
        logging.debug("Unzipping coverity latest version zip to location {}".format(self.cov_home))
        shutil.unpack_archive(self.cov_filepath, self.cov_home)

    def verify_checksum_match(self):
        """
        download coverity only if checksum doesn't match
        """
        self.gcp_checksum, self.gcp_filepath = self.tool_token_json['checksum'][self.platform].split(",")
        logging.debug("checksum of latest coverity file in gcp is {}".format(self.gcp_checksum))
        if os.path.exists(self.cov_filepath):
            sha2_filepath = hashlib.sha256(open(self.cov_filepath, 'rb').read()).hexdigest()
            if self.gcp_checksum == sha2_filepath:
                logging.info("Skipping downloading latest version of coverity as it already exists")
                return True
            else:
                logging.info("Downloading latest coverity package as it is not present on disk")
                return False
        else:
            return False

    def set_permissions(self):
        """ set executable permissions for coverity files"""
        logging.debug("setting executable permissions for coverity files")
        st = os.stat(self.cov_home)
        os.chmod(self.cov_home, st.st_mode | stat.S_IEXEC)
        for root, dirs, files in os.walk(self.cov_home):
            for d in dirs:
                st = os.stat(os.path.join(root, d))
                os.chmod(os.path.join(root, d), st.st_mode | stat.S_IEXEC)
            for f in files:
                st = os.stat(os.path.join(root, f))
                os.chmod(os.path.join(root, f), st.st_mode | stat.S_IEXEC)

    def run(self):
        """
        run coverity install
        """
        hub_version = self.hub_api.get_hub_version()
        vers_result = hub_version.split(".")
        if ((int(vers_result[0]) >= self.min_cov_year_for_api and int(vers_result[1]) >= self.min_cov_vers_for_api) or int(
                vers_result[0]) >= self.min_cov_year_for_api + 1):
            self.hub_api_tool_token()
            match_result = self.verify_checksum_match()
            if not match_result:
                self.gcp_download()
            else:
                logging.debug("Latest version is already present on the system at {}".format(self.cov_home))
            self.set_permissions()
        else:
            util.error_and_exit(
                "Automatic update of coverity not supported in Black Duck version {}. please provide coverity_root in yaml file".format(
                    hub_version))
