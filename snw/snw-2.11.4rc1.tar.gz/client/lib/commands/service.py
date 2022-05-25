import json
import logging
import math
import os
import sys
from datetime import datetime

import requests

import client.launcher as launcher
from lib import utils
from prettytable import PrettyTable

launcher.LOGGER = logging.getLogger()


class Service:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def config(self, serviceList):
        if not (self.options.action == 'list' or
                self.options.action == 'set' or self.options.action == 'get' or
                self.options.action == 'del' or self.options.action == 'select'):
            raise ValueError('action should be list, get, set, del, select')
        params = None
        if self.options.service not in serviceList:
            raise ValueError('unknown service: %s' % self.options.service)
        if self.options.action == 'list' or self.options.action == 'get':
            r = requests.get(os.path.join(self.options.url, "service/listconfig",
                                          self.options.service),
                             auth=self.auth, params=params)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'service/listconfig\' '
                                   'service: %s' % r.text)
            result = r.json()
            if self.options.action == 'list' and not self.is_json:
                res = PrettyTable(["Name", "Last Modified", "Current"])
                for r in result["configurations"]:
                    mtime = result["configurations"][r][0]
                    mdate = datetime.fromtimestamp(math.ceil(float(mtime))).isoformat()
                    res.add_row([r, mdate, r == result["current"] and "yes" or "no"])
            elif self.options.action == 'get':
                if self.options.configname is None:
                    self.options.configname = result["current"]
                if self.options.configname not in result["configurations"]:
                    raise ValueError('unknown configuration: %s' % self.options.configname)
                res = result["configurations"][self.options.configname][1]
            else:
                res = result
        else:
            if self.options.configname is None:
                raise ValueError('argument -cn/--configname is required')
            if self.options.action == "set" and self.options.config is None:
                raise ValueError('argument -c/--config is required for `setconfig`')
            if self.options.action == "set":
                config = self.options.config
                try:
                    if config.startswith("@"):
                        with open(config[1:], "rt") as f:
                            config = f.read()
                    jconfig = json.loads(config)
                    if jconfig.get("name") != self.options.service:
                        raise ValueError('config name should be corresponding to service')
                except Exception as err:
                    raise ValueError(str(err))
                r = requests.post(os.path.join(self.options.url, "service",
                                               self.options.action + "config",
                                               self.options.service, self.options.configname),
                                  data={'config': config}, auth=self.auth)
            else:
                r = requests.get(os.path.join(self.options.url, "service",
                                              self.options.action + "config",
                                              self.options.service, self.options.configname),
                                 auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'service/%s\' '
                                   'service: %s' % (self.options.service, r.text))
            res = r.json()
        return res

    def enable_disable(self, serviceList):
        if self.options.service not in serviceList:
            raise ValueError('unknown service: %s' % self.options.service)
        params = {}
        service = serviceList[self.options.service]
        if self.options.subcmd == "disable" and self.options.message:
            params = {'message': self.options.message}
        r = requests.get(os.path.join(self.options.url, "service", self.options.subcmd,
                                      self.options.service, self.options.resource),
                         auth=self.auth, params=params)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'service/%s\' '
                               'service: %s' % (self.options.subcmd, r.text))
        res = r.json()
        return res

    def stop_restart(self, serviceList):
        if self.options.service not in serviceList:
            raise ValueError('unknown service: %s' % self.options.service)
        r = requests.get(os.path.join(self.options.url, "service",
                                      self.options.subcmd, self.options.service), auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'service/%s\' '
                               'service: %s' % (self.options.subcmd, r.text))
        res = r.json()
        return res

    def execute_command(self):
        result = None
        status, serviceList = utils.get_services(url=self.options.url, user_auth=self.auth)
        if status is False:
            launcher.LOGGER.error('incorrect result from \'service/list\' service: %s',
                                  serviceList[1])
            sys.exit(1)
        if self.options.subcmd == "config":
            result = self.config(serviceList)
        if self.options.subcmd == "stop" or self.options.subcmd == "restart":
            result = self.stop_restart(serviceList)
        if self.options.subcmd == "disable" or self.options.subcmd == "enable":
            result = self.enable_disable(serviceList)
        return result
