from requests import get, post
from zlib import crc32
from hashlib import sha256, sha384, sha512, md5
from mmh3 import hash, hash128
from math import ceil
import json
import os
import threading


class Updater:
    def __init__(self):
        self.config = {}
        self.exit_required = False
        self.config['host'] = 'smartapp.netcad.com'
        self.config['port'] = ''
        self.config['chunk_size'] = 0
        self.config['token'] = 'testtoken'
        thread = threading.Thread(target=self.run)
        thread.start()
        self.FW_CHECKSUM_ATTR = "fw_checksum"
        self.FW_CHECKSUM_ALG_ATTR = "fw_checksum_algorithm"
        self.FW_SIZE_ATTR = "fw_size"
        self.FW_TITLE_ATTR = "fw_title"
        self.FW_VERSION_ATTR = "fw_version"

        self.FW_STATE_ATTR = "fw_state"

        self.REQUIRED_SHARED_KEYS = [self.FW_CHECKSUM_ATTR, self.FW_CHECKSUM_ALG_ATTR, self.FW_SIZE_ATTR,
                                     self.FW_TITLE_ATTR, self.FW_VERSION_ATTR]

    def get_firmware_info(self):
        response = get(f"http://{self.config['host']}:{self.config['port']}/api/v1/{self.config['token']}/attributes",
                       params={"sharedKeys": self.REQUIRED_SHARED_KEYS}).json()
        return response.get("shared", {})

    def send_telemetry(self, telemetry):
        print(f"Sending current info: {telemetry}")
        post(f"http://{self.config['host']}:{self.config['port']}/api/v1/{self.config['token']}/telemetry",
             json=telemetry)

    def dummy_upgrade(self, version_from, version_to):
        print(f"Updating from {version_from} to {version_to}:")
        print(f"Firmware is updated!\n Current firmware version is: {version_to}")

    def verify_checksum(self, firmware_data, checksum_alg, checksum):
        if firmware_data is None:
            print("Firmware wasn't received!")
            return False
        if checksum is None:
            print("Checksum was't provided!")
            return False
        checksum_of_received_firmware = None
        print(f"Checksum algorithm is: {checksum_alg}")
        if checksum_alg.lower() == "sha256":
            checksum_of_received_firmware = sha256(firmware_data).digest().hex()
        elif checksum_alg.lower() == "sha384":
            checksum_of_received_firmware = sha384(firmware_data).digest().hex()
        elif checksum_alg.lower() == "sha512":
            checksum_of_received_firmware = sha512(firmware_data).digest().hex()
        elif checksum_alg.lower() == "md5":
            checksum_of_received_firmware = md5(firmware_data).digest().hex()
        elif checksum_alg.lower() == "murmur3_32":
            reversed_checksum = f'{hash(firmware_data, signed=False):0>2X}'
            if len(reversed_checksum) % 2 != 0:
                reversed_checksum = '0' + reversed_checksum
            checksum_of_received_firmware = "".join(
                reversed([reversed_checksum[i:i + 2] for i in range(0, len(reversed_checksum), 2)])).lower()
        elif checksum_alg.lower() == "murmur3_128":
            reversed_checksum = f'{hash128(firmware_data, signed=False):0>2X}'
            if len(reversed_checksum) % 2 != 0:
                reversed_checksum = '0' + reversed_checksum
            checksum_of_received_firmware = "".join(
                reversed([reversed_checksum[i:i + 2] for i in range(0, len(reversed_checksum), 2)])).lower()
        elif checksum_alg.lower() == "crc32":
            reversed_checksum = f'{crc32(firmware_data) & 0xffffffff:0>2X}'
            if len(reversed_checksum) % 2 != 0:
                reversed_checksum = '0' + reversed_checksum
            checksum_of_received_firmware = "".join(
                reversed([reversed_checksum[i:i + 2] for i in range(0, len(reversed_checksum), 2)])).lower()
        else:
            print("Client error. Unsupported checksum algorithm.")
        print(checksum_of_received_firmware)
        '''
        random_value = random.randint(0, 5)
        if random_value > 3:
            print("Dummy fail! Do not panic, just restart and try again the chance of this fail is ~20%")
            return False
        '''
        return checksum_of_received_firmware == checksum

    def get_firmware(self, fw_info):
        chunk_count = ceil(fw_info.get(self.FW_SIZE_ATTR, 0) / self.config["chunk_size"]) if self.config[
                                                                                                 "chunk_size"] > 0 else 0
        firmware_data = b''
        for chunk_number in range(chunk_count + 1):
            params = {"title": fw_info.get(self.FW_TITLE_ATTR),
                      "version": fw_info.get(self.FW_VERSION_ATTR),
                      "size": self.config["chunk_size"] if self.config["chunk_size"] < fw_info.get(self.FW_SIZE_ATTR,
                                                                                                   0) else fw_info.get(
                          self.FW_SIZE_ATTR, 0),
                      "chunk": chunk_number
                      }
            print(params)
            print(
                f'Getting chunk with number: {chunk_number + 1}. Chunk size is : {self.config["chunk_size"]} byte(s).')
            if 'fw_url' in fw_info:
                print(fw_info['fw_url'])
            else:
                print(
                    f"http{'s' if self.config['port'] == 443 else ''}://{self.config['host']}:{self.config['port']}/api/v1/{self.config['token']}/firmware",
                    params)
                response = get(
                    f"http{'s' if self.config['port'] == 443 else ''}://{self.config['host']}:{self.config['port']}/api/v1/{self.config['token']}/firmware",
                    params=params)
                if response.status_code != 200:
                    print("Received error:")
                    response.raise_for_status()
                    return
                firmware_data = firmware_data + response.content
            return firmware_data

    def save_firmware_info(self, firmware_info, file_dir):
        with open(os.path.join(file_dir, 'firmwareinfo.json'), 'w') as f:
            json.dump(firmware_info, f)

    def load_firmware_info(self, file_dir):
        with open(os.path.join(file_dir, 'firmwareinfo.json'), 'r') as jsonFile:
            jsonObj = json.load(jsonFile)
            jsonFile.close()
        return jsonObj

    def run(self):
        file_dir = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists(os.path.join(file_dir, 'firmwareinfo.json')):
            current_firmware_info = self.load_firmware_info(file_dir)
        else:
            current_firmware_info = {
                "current_fw_title": None,
                "current_fw_version": None
            }
        self.send_telemetry(current_firmware_info)

        while True:
            firmware_info = self.get_firmware_info()
            if (firmware_info.get(self.FW_VERSION_ATTR) is not None and firmware_info.get(
                    self.FW_VERSION_ATTR) != current_firmware_info.get("current_" + self.FW_VERSION_ATTR)) \
                    or (firmware_info.get(self.FW_TITLE_ATTR) is not None and firmware_info.get(
                self.FW_TITLE_ATTR) != current_firmware_info.get("current_" + self.FW_TITLE_ATTR)):
                print("New firmware available!")

                current_firmware_info[self.FW_STATE_ATTR] = "DOWNLOADING"

                self.send_telemetry(current_firmware_info)

                firmware_data = self.get_firmware(firmware_info)

                current_firmware_info[self.FW_STATE_ATTR] = "DOWNLOADED"

                self.send_telemetry(current_firmware_info)

                verification_result = self.verify_checksum(firmware_data, firmware_info.get(self.FW_CHECKSUM_ALG_ATTR),
                                                           firmware_info.get(self.FW_CHECKSUM_ATTR))

                if verification_result:
                    print("Checksum verified!")
                    current_firmware_info[self.FW_STATE_ATTR] = "VERIFIED"

                    self.send_telemetry(current_firmware_info)
                else:
                    print("Checksum verification failed!")
                    current_firmware_info[self.FW_STATE_ATTR] = "FAILED"

                    self.send_telemetry(current_firmware_info)
                    firmware_data = self.get_firmware(firmware_info)
                    continue

                current_firmware_info[self.FW_STATE_ATTR] = "UPDATING"

                self.send_telemetry(current_firmware_info)
                with open(os.path.join(file_dir, 'ndu_gate_update.exe'), "wb") as firmware_file:
                    firmware_file.write(firmware_data)
                self.dummy_upgrade(current_firmware_info["current_" + self.FW_VERSION_ATTR],
                                   firmware_info.get(self.FW_VERSION_ATTR))

                current_firmware_info = {
                    "current_" + self.FW_TITLE_ATTR: firmware_info.get(self.FW_TITLE_ATTR),
                    "current_" + self.FW_VERSION_ATTR: firmware_info.get(self.FW_VERSION_ATTR),
                    self.FW_STATE_ATTR: "UPDATED"
                }

                self.save_firmware_info(current_firmware_info, file_dir)
                self.send_telemetry(current_firmware_info)
                self.exit_required = True
                break
