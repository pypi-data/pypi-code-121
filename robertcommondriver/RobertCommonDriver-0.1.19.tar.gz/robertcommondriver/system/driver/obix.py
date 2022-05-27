
import logging
import requests
from typing import Any, Dict
import xml.etree.ElementTree as Etree
from xml.dom.minidom import parseString
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .base import BasePoint, BaseDriver, PointTableDict

# Disable security request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

'''
    pip install requests==2.26.0
'''


# ObixPoint
class ObixPoint(BasePoint):
    def __init__(self, point_writable: bool, point_name: str, point_url: str, point_type: str, point_description: str = '', point_sample_value: Any = None):
        super().__init__('obix', point_writable, point_name, point_description, point_sample_value)

        self.point_url = point_url
        self.point_type = point_type

    @property
    def get_point_url(self):
        return self.point_url

    @property
    def get_point_type(self):
        return self.point_type


def enum_value_handler(v):
    try:
        return int(v)
    except Exception:
        return str(v)


# Obix Driver
class ObixDriver(BaseDriver):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        super().__init__(dict_config, dict_point)
        ##########
        self.obix_user = ''  # Obix user
        self.obix_psw = ''  # ObixPsw
        self.obix_url = ''  # Obix Url
        self.obix_timeout = 10  # Obix timeout
        self.enable = True
        self.obix_types = {
            'int': int,
            'bool': lambda x: x.lower() == "true",
            'real': float,
            'enum': enum_value_handler,
        }
        self.obix_point_dict = {}  # point_name:BEOPBaseEngine
        self.obix_point_url_name = {}  # url:name

        self.obix_auth_content = None
        self.obix_watch_url = ''
        ##########

        self.configure()

    def __del__(self):
        super().__del__()
        self._del_watch()

    def reset(self):
        self.obix_point_dict = {}
        self.obix_point_url_name = {}  # url:name
        self._del_watch()  #

    def configure(self):
        # config
        self.obix_user = str(self.dict_config.get("username"))
        self.obix_psw = str(self.dict_config.get("password"))
        self.obix_url = str(self.dict_config.get("url", ""))
        self.obix_timeout = int(str(self.dict_config.get("timeout", "10")))
        self.enable = str(self.dict_config.get("enabled", "true")).lower() == 'true'

        if not self.obix_url.startswith('http'):
            self.obix_url = f'http://{self.obix_url}'

        self.obix_auth_content = HTTPBasicAuth(self.obix_user, self.obix_psw)

        #
        self.reset()

        # csv
        for point_name in self.dict_point.keys():
            point_url = str(self.dict_point[point_name]['point_url'])
            if not point_url.endswith('/'):
                point_url = f'{point_url}/'
            if not point_url.endswith('/out/'):
                point_url = f"{point_url}out/"
            self.obix_point_dict[point_name] = ObixPoint(bool(self.dict_point[point_name]['point_writable']),
                                                             str(self.dict_point[point_name]['point_name']), point_url,
                                                             str(self.dict_point[point_name]['point_type']),
                                                             str(self.dict_point[point_name]['point_description']))

    def exit(self):
        self._del_watch()

    def ping_target(self) -> bool:
        try:
            rt = requests.get(f'{self.obix_url}/obix', auth=self.obix_auth_content, timeout=self.obix_timeout, verify=False)
            if rt.status_code == 200:
                return True
        except Exception as e:
            logging.error(f"ping fail({e.__str__()})")
        return False

    def parse_result(self, point, result):
        try:
            result.raise_for_status()
            document = parseString(result.text)
            root = document.documentElement
            return str(root.getAttribute("val")) if point.get_point_type != 'bool' else str(int(self.obix_types[point.get_point_type](root.getAttribute("val"))))
        except Exception as e:
            logging.error(f"parse value({point.get_point_name}) fail({e.__str__()})")
        return ''

    def get_points(self, dict_point: dict = {}) -> dict:
        if len(dict_point) == 0:
            return self._scrap_points()
        else:
            return self._get_points(dict_point)

    def _get_points(self, dict_point: dict) -> dict:
        result_dict = {}
        point_list = []
        for point_name in dict_point.keys():
            if point_name in self.obix_point_dict.keys():
                point = self.obix_point_dict[point_name]
                point_list.append(point)

        async_results = point_list

        for point, result in zip(point_list, async_results):
            result_dict[point.get_point_name] = self.parse_result(point, result)

        return result_dict

    def _scrap_points(self) -> dict:
        result_dict = {}
        try:
            if self._add_watch_and_point() != '':
                result_dict = self._pool_refresh(self.obix_watch_url)
        except Exception as e:
            logging.error(f'scrap points fail {e.__str__()}')
        return result_dict

    def set_points(self, dict_point: dict) -> dict:
        set_result_dict = {}
        async_requests = []
        point_list = []
        for point_name in dict_point.keys():
            point_value = dict_point[point_name]
            if point_name in self.obix_point_dict.keys():
                point = self.obix_point_dict[point_name]
                point_list.append(point)
                data = f'<{self.obix_types[point.get_point_type]} val="{str(point_value).lower()}" />'
                # async_requests.append(grequests.post('%s%sset' % (self.obix_url, point.get_point_url), data=data,
                #                                      auth=self.obix_auth_content))
        return set_result_dict

    def reset_config(self, dict_config: dict):
        super().reset_config(dict_config)
        self.configure()

    def reset_point(self, dict_point: dict):
        super().reset_point(dict_point)
        self.configure()

    def search_points(self, call_back_func=None) -> Dict[str, Dict[str, Any]]:
        search_point = {}
        obix_driver_url = f'{self.obix_url}/obix/config/'
        rt = requests.get(obix_driver_url, auth=self.obix_auth_content, verify=False)
        if rt.status_code == 200:
            xml_str = rt.text
            root = Etree.fromstring(xml_str)
            if root is not None:
                for node in root:
                    if node.tag.startswith('{http://obix.org/ns/schema/1.0}ref'):
                        if node.attrib is not None:             #schedule search
                            network_url = f"{obix_driver_url}{node.attrib['href']}"
                            self._search_obix_network(network_url, network_url, search_point, call_back_func)
        return search_point

    def _search_obix_network(self, network_url: str, search_url: str, search_point: dict, call_back_func=None):
        rt = requests.get(search_url, auth=self.obix_auth_content, verify=False)
        if rt.status_code != 200:
            return
        xml_str = rt.text
        root = Etree.fromstring(xml_str)
        if root is None:
            return
        for node in root:
            if not node.tag.startswith('{http://obix.org/ns/schema/1.0}ref'):
                continue
            if node.attrib is None:
                continue
            if "is" not in node.attrib.keys():
                continue
            is_param = node.attrib['is']
            if is_param.find('obix:Point') >= 0 or is_param.find('/obix/def/schedule') >= 0:
                self._get_obix_point_property(network_url, search_url + node.attrib['href'], search_point)

                if call_back_func:
                    call_back_func(search_point)
            else:
                search_url_next = search_url + node.attrib['href']
                self._search_obix_network(network_url, search_url_next, search_point, call_back_func)

    def _get_obix_point_property(self, network_url: str, point_address_url: str, search_point: dict):
        _point_address_url = f'{point_address_url}out' if not point_address_url.endswith('out') else point_address_url
        rt = requests.get(_point_address_url, auth=self.obix_auth_content, verify=False)
        if rt.status_code == 200:
            point_name = self._format_obix_point_name(network_url, point_address_url)
            obix_doc = parseString(rt.text)
            obix_element = obix_doc.documentElement
            search_point[point_name] = dict(
                point_name=point_name,
                point_writable=True,
                point_url=point_address_url.replace(self.obix_url, ''),
                point_type=obix_element.tagName,
                point_description=obix_element.getAttribute("display"),
                point_sample_value=obix_element.getAttribute("val"))

    def _format_obix_point_name(self, network_url: str, point_address_url: str) -> str:
        return point_address_url.replace(network_url, "").replace("/points/", "_").replace("$", "_")[:-1].replace("/", "_")

    # Add subscription (need to re-add when the number of failures reaches 2 or the subscription expires)
    def _add_watch_and_point(self) -> str:
        if self.obix_watch_url == '':
            self.obix_watch_url = self._add_watch(f'{self.obix_url}/obix/watchService/make/')
            if self.obix_watch_url != '':
                if self._add_point(self.obix_watch_url) == False:
                    self._del_watch()
        return self.obix_watch_url

    def _add_watch(self, watch_url: str) -> str:
        rt = requests.post(watch_url, data='', auth=self.obix_auth_content, timeout=self.obix_timeout, verify=False)
        if rt.status_code == 200:
            xml_str = rt.text
            root = Etree.fromstring(xml_str)
            if root != None and root.attrib != None:
                return root.attrib['href']
            raise Exception(f'obix Add Watch Fail({rt.text})')
        else:
            raise Exception(f'obix Add Watch Fail({rt.status_code})')

    def _del_watch(self):
        if self.obix_watch_url != '':
            rt = requests.post(f'{self.obix_watch_url}delete/', data='', auth=self.obix_auth_content,timeout=self.obix_timeout, verify=False)
            if rt.status_code == 200:
                xml_str = rt.text
                root = Etree.fromstring(xml_str)
            self.obix_watch_url = ''

    def _add_point(self, watch_url: str) -> bool:
        request_body = '<obj is="obix:WatchIn"><list names="hrefs">'
        for point_name in self.obix_point_dict.keys():
            point_url = self.obix_point_dict[point_name].get_point_url
            self.obix_point_url_name[point_url] = self.obix_point_dict[point_name]
            point_uri = '<uri val="%s" />' % point_url
            request_body = request_body + point_uri
        request_body = request_body + '</list></obj>'

        rt = requests.post('%sadd/' % watch_url, data=request_body, auth=self.obix_auth_content, timeout=self.obix_timeout, verify=False)
        if rt.status_code == 200:
            xml_str = rt.text
            root = Etree.fromstring(xml_str)
            if root != None and root.attrib != None:
                isParam = root.attrib['is']
                if isParam.find('obix:WatchOut') >= 0:
                    for node in root:
                        if node.tag == '{http://obix.org/ns/schema/1.0}list':
                            for point in node:
                                if point.tag == '{http://obix.org/ns/schema/1.0}err':
                                    logging.error(f"obix Add Point Fail({point.attrib['href']})")
                return True
            logging.error(f'obix Add Point Fail({rt.text})')
        else:
            logging.error(f'obix Add Point Fail({rt.status_code})')
        return False

    def _pool_refresh(self, watch_url: str) -> dict:
        result_dict = {}
        rt = requests.post(f'{watch_url}pollRefresh/', data='', auth=self.obix_auth_content,timeout=self.obix_timeout, verify=False)
        if rt.status_code == 200:
            xml_str = rt.text
            root = Etree.fromstring(xml_str)
            if root != None and root.attrib != None:
                is_param = root.attrib['is']
                if is_param.find('obix:WatchOut') >= 0:
                    for node in root:
                        if node.tag.startswith('{http://obix.org/ns/schema/1.0}list'):
                            if node.attrib != None:
                                if node.attrib['name'] == 'values':
                                    for value in node:
                                        self._format_obix_point_value(value.attrib['href'], value.attrib['val'],result_dict)
                elif is_param.find('obix:BadUriErr') >= 0:
                    self._del_watch()
        else:
            raise Exception(f'obix poolRefresh Fail({rt.status_code})')
        return result_dict

    def _format_obix_point_value(self, point_url, point_value, result_dict):
        if point_url in self.obix_point_url_name.keys():
            point = self.obix_point_url_name[point_url]
            point_name = point.get_point_name
            point_type = point.get_point_type
            converter = self.obix_types.get(point_type, str)
            point_value = str(point_value) if point_type != 'bool' else str(int(converter(point_value)))
            result_dict[point_name] = point_value
