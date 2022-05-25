"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import urllib3
import logging
import os
import tqdm

# Disable warnings: InsecureRequestWarning
urllib3.disable_warnings()


def read_in_chunks(file_object_1, chunk_size=1024000000):
    """Generator to read a file in chunks.
    Default chunk size: 1GB."""
    while True:
        data = file_object_1.read(chunk_size)
        if not data:
            break
        yield data


class BDBAApi:
    """
    Class that facilitates an authenticated connection to the hub for uploading binary files to BDBA.
    """

    def __init__(self, hub_api):
        hub_api.authenticate()
        self.hub = hub_api.hub

    def upload_binary_part(self, project_name, version_name, codelocation_name, binary_file, file_chunk):
        """ upload bdba tar file to hub"""
        if not os.path.exists(binary_file):
            logging.warning("Binary file not found. There will be no BDBA results.")
            return

        multipart_encoder = MultipartEncoder(fields={'projectName': project_name,
                                                     'version': version_name,
                                                     'codeLocationName': codelocation_name,
                                                     'fileupload': (binary_file, file_chunk, 'application/octet-stream')
                                                     }
                                             )
        headers = self.hub.get_headers()
        headers.pop('Accept')
        headers.pop('Content-Type')

        with tqdm.tqdm(desc="BDBA Upload",
                       total=multipart_encoder.len,
                       dynamic_ncols=True,
                       unit='B',
                       unit_scale=True,
                       unit_divisor=1024) as bar:
            multipart_monitor = MultipartEncoderMonitor(multipart_encoder,
                                                        lambda monitor: bar.update(monitor.bytes_read - bar.n))
            headers['Content-Type'] = multipart_monitor.content_type
            try:
                response = requests.post('{}/api/uploads'.format(self.hub.config['baseurl']),
                                         headers=headers,
                                         data=multipart_monitor,
                                         verify=not self.hub.config['insecure'], timeout=600)
                if not response.ok:
                    if response.status_code == 402:
                        logging.error("BDBA is not licensed for use with the current Black Duck instance -- will not be used.")
                    else:
                        logging.error(
                            "Problem uploading the file to BDBA -- (Response({}): {})".format(response.status_code,
                                                                                              response.text))
                else:
                    logging.info("Upload completed!")

            except requests.exceptions.ReadTimeout as e:
                logging.error("Timeout error occurred when uploading BDBA file {}".format(e))

    def upload_binary(self, project_name, version_name, codelocation_name, binary_file):
        """send chunk of binary file to upload"""
        if not os.path.exists(binary_file):
            logging.warning("Binary file not found. There will be no BDBA results.")
            return
        bdba_count = 0
        with open(binary_file, 'rb') as file_obj:
            for file_chunk in read_in_chunks(file_obj):
                bdba_count += 1
                logging.info("Uploading bdba tar file part {}".format(bdba_count))
                upd_codelocation_name = codelocation_name + "-" + str(bdba_count) + "-BDBA"
                self.upload_binary_part(project_name, version_name, upd_codelocation_name, binary_file, file_chunk)

    def __call__(self, project_name, version_name, codelocation_name, binary_file):
        try:
            self.upload_binary(project_name, version_name, codelocation_name, binary_file)
        except MemoryError as e:
            logging.error("Please verify if you are using right version of python - 32bit vs 64bit - {}".format(e))
