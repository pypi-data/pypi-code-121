import random
import re
import os
import numpy as np
from typing import Tuple
from addict import Dict
import string
import requests
import ast
from matplotlib import pyplot as plt
import csv


class Generator:

    @staticmethod
    def unique_matchId_generator(letter_count: int = 12, digit_count: int = 8) -> str:
        str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))
        str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))

        sam_list = list(str1)  # it converts the string to list.
        random.shuffle(sam_list)  # It uses a random.shuffle() function to shuffle the string.
        final_string = ''.join(sam_list)
        return final_string

    @staticmethod
    def path_url_creator(**kwargs) -> Tuple[str, str]:
        """

        :param params.gui:
        :param params.cfg:
        :param params.splitData:
        :param params.index:
        :param params.directory:
        :return:
        """
        params = Dict(kwargs)
        i = params.index
        host = params.cfgImage.ip_remote if params.cfgImage.Remote else params.cfgImage.ip_local
        if params.gui:
            ip_path = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
            ip_check = bool(ip_path.match(params.directory))
            if ip_check:
                path = os.path.join(
                    "http://" + host + ":" + params.cfgImage.port + "/" + params.cfgImage.Directory + ":",
                    str(params.splitData[i]["dirname"]), params.splitData[i]["filename"], params.splitData[i]["imgname"])
            else:
                path = os.path.join(params.directory, str(params.splitData[i]["dirname"]),
                                    params.splitData[i]["filename"],
                                    params.splitData[i]["imgname"])
        else:
            # TODO will be dynamic connection for now test phase
            if params.cfgImage.device == "google":
                #     H:\IMAGERY\mapilio_dev\organization\arnavutkoy
                #     https://image.mapilio.com/h:/IMAGERY/mapilio_dev/organization/arnavutkoy/TqbHYpgLXzU7vHKWQDRVjQ.jpeg
                path = os.path.join("https://" + "cdn.mapilio.com", "h:", "IMAGERY", 'mapilio_dev', 'organization',
                                    'arnavutkoy', params.splitData[i]["imgname"])
            if params.cfgImage.device == 'ladybug':
                path = os.path.join(
                    "http://" + "cdn.mapilio.com/" + str(params.cfgImage.directory) + ":",
                    str(params.splitData[i]["dirname"]), params.splitData[i]["filename"], params.splitData[i]["imgname"])

        return host, path

    @staticmethod
    def data_separation(data: list, dividing_percentage: int) -> list:
        """
         Segmenting incoming data

        :param data: data to be processed
        :param dividing_percentage: percentage of data fragmented
        :return: predicted masks
        """
        percentage = int(len(data) / 100 * dividing_percentage)

        for i in range(0, len(data), percentage):
            # Create an index range for l of n items:
            yield data[i:i + percentage]

    @staticmethod
    def take_objects(matchedObjects: list, take: int = 2):

        for i in range(0, len(matchedObjects), take):
            if len(matchedObjects[i:i + take]) % take == 0:
                yield matchedObjects[i:i + take]

    @staticmethod
    def get_exif_information(img_info):
        """
        :param img_info: exif object
        :return: (lat, lon), orientation, (Height, Width), FocalLength, Altitude,
        """
        information = {}
        data = img_info.extract_exif()
        try:
            information["model"] = data["model"]
            information["coordx"] = data["gps"]["latitude"]
            information["coordy"] = data["gps"]["longitude"]
            information["width"] = data["width"]
            information["height"] = data["height"]

            # Focal Length
            fLen_obj = data["gps"]["FocalLength"]
            fLen_str = f"{fLen_obj}"
            fLen_arr = fLen_str.split("/")
            fLen = float(int(fLen_arr[0]) / int(fLen_arr[1]))
            information["FocalLength"] = fLen

            hor_width = data["height"] if data["orientation"] == 1 else data["width"]
            information["orientation"] = hor_width
            # Angle of View
            aFov = np.arctan(hor_width / (2 * fLen)) * (180 / np.pi)
            information["FoV"] = aFov
        except:
            raise Exception(f"Check the image Exif Data some missing values")

        for k, v in information.items():
            if information[k] is None:
                raise Exception(f"{k} is None")
            else:
                pass

        return information

    @staticmethod
    def get_config_response(configUrl: str) -> Dict:
        response = str(Dict(requests.get(configUrl).json()).config)
        pure_response = response.replace("\'", "\"")
        fix_dict = Dict(ast.literal_eval(pure_response))
        return fix_dict

    @staticmethod
    def get_random_hex_color():
        import random
        random_number = random.randint(0, 16777215)
        hex_number = str(hex(random_number))
        color = '#' + hex_number[2:]
        return color

    @staticmethod
    def plt_create_detected_unique_points(
            file_id,
            **points,
            ):
        """
        Creating detected unquie points figure
        Args:
            points : detected_unique_points: classnames and count
                    detected_single_points: single classnames and count
            file_id: where will be saving

        Returns:

        """

        headers = ['Name', 'Count']

        for key, value in points.items():
            for name, detected_points in value.items():
                unique, counts = np.unique(detected_points, return_counts=True)
                detected_points_counts_dict = dict(zip(unique, counts))

                with open(os.path.join('Exports', file_id, f'{name}.csv'), 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    for key_, value_ in detected_points_counts_dict.items():
                        writer.writerow([key_, value_])

                y_pos = np.arange(len(unique))

                plt.figure(figsize=(44, 22))
                plt.barh(y_pos, counts, align='center', alpha=0.5)
                plt.yticks(y_pos, unique)
                plt.xlabel('Counts')
                plt.title(f"{name}")
                plt.savefig(os.path.join('Exports', file_id, f'{name}.png'))  # noqa
                plt.clf()
