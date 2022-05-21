import time
from copy import deepcopy

import requests


class api(object):
    ''' API '''

    ''' Zabbix API URL, User Login Result '''
    url, auth = None, None

    '''
    https://www.zabbix.com/documentation/current/en/manual/api#performing-requests
    The request must have the Content-Type header set to one of these values:
        application/json-rpc, application/json or application/jsonrequest.
    '''
    header = {'Content-Type': 'application/json-rpc'}

    def __init__(self, url, user, password):
        ''' Initiation '''
        self.url = url
        user_info = self.request("user.login", {
            "username": user,
            "password": password
        })
        self.auth = user_info['result']

    def request(self, method, params=None):
        ''' Request '''

        '''
        Request Data
        https://www.zabbix.com/documentation/current/en/manual/api#authentication
        id - an arbitrary identifier of the request
        id - 请求标识符, 这里使用UNIX时间戳作为唯一标示
        '''
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": self.auth,
            "id": int(time.time())
        }

        # Request
        response = requests.post(self.url, headers=self.header, json=data)

        # Return JSON
        return response.json()

    def logout(self):
        ''' User Logout '''
        return self.request('user.logout', [])

    def logout_exit(self, str='Error'):
        ''' Logout and Exit '''
        print(str)
        try:
            self.logout()
        except:
            exit(1)
        exit(1)

    def get_hosts_by_template_name(self, name='', output='extend'):
        '''
        Get hosts by template name
        name: string/array
        example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']
        如果 name 为 '' (空), 返回所有 host
        '''

        # Get Templates
        response = self.request('template.get', {'output': ['templateid'], 'filter': {'host': name}})

        # Get Host
        try:
            if response.get('result') and len(response['result']) > 0:
                ids = [i['templateid'] for i in response['result']]
                hosts = self.request('host.get', {'output': output, 'templateids': ids})
                return hosts['result']
            else:
                return []
        except Exception as e:
            print(e)
            return []

    def get_ids_by_template_name(self, name=''):
        '''
        Get ids by template name
        name: string/array
        example: 'Linux by Zabbix agent' / ['Linux by Zabbix agent', 'Linux by Zabbix agent active']
        如果 name 为 '' (空), 返回所有 template id
        '''

        response = self.request('template.get', {'output': 'templateid', 'filter': {'name': name}})

        try:
            if response.get('result') and len(response['result']) > 0:
                ids = [i['templateid'] for i in response['result']]
                return ids
            else:
                return []
        except Exception as e:
            print(e)
            return []

    def get_ids_by_hostgroup_name(self, name=''):
        '''
        Get ids by hostgroup name
        name: string/array
        example: 'Linux servers' / ['Linux servers', 'Discovered hosts']
        如果 name 为 '' (空), 返回所有 hostgroup id
        '''

        response = self.request('hostgroup.get', {'output': 'groupid', 'filter': {'name': name}})

        try:
            if response.get('result') and len(response['result']) > 0:
                ids = [i['groupid'] for i in response['result']]
                return ids
            else:
                return []
        except Exception as e:
            print(e)
            return []

    def get_hosts_by_hostgroup_name(self, name='', output='extend'):
        '''
        Get hosts by hostgroup name
        name: string/array
        example: 'Linux servers' / ['Linux servers', 'Discovered hosts']
        如果 name 为 '' (空), 返回所有 hosts
        '''

        ids = self.get_ids_by_hostgroup_name(name)
        if ids == []:
            return []

        hosts = self.request('host.get', {'output': output, 'groupids': ids})

        try:
            if hosts.get('result'):
                return hosts['result']
            else:
                return []
        except Exception as e:
            print(e)
            return []

    def get_history_by_item_key(self, hosts=[], time_from='', time_till='', item_key='', data_type=3):
        '''
        https://www.zabbix.com/documentation/6.0/en/manual/api/reference/history/get
        hosts: Host List
        time_from: Datetime From
        time_till: Datetime Till
        item_key: Item Key
        data_type: Data Type
        '''

        # Deep Copy (拷贝数据为局部变量)
        # 父函数中有 hosts 变量, 而此函数对 hosts 的值进行了修改, 所以会导致父函数中 hosts 的值改变
        # 使用 deepcopy 拷贝一份数据, 就不会改变父函数中 hosts 的值
        __hosts = deepcopy(hosts)

        # ----------------------------------------------------------------------------------------------------

        # Item Get
        hostids = [i['hostid'] for i in __hosts]
        item_params = {
            'output': ['name', 'itemid', 'hostid'],
            'hostids': hostids,
            'filter': {'key_': item_key}
        }
        items = self.request('item.get', item_params)

        # ----------------------------------------------------------------------------------------------------

        # Put Item ID to Hosts
        # 这一步目的是因为 history 获取的顺序是乱的, 为了使输出和 Host 列表顺序一致, 将 Item ID 追加到 Host, 然后遍历 Host 列表输出
        if items.get('result') and len(items['result']) > 0:
            for host in __hosts:
                item = next((item for item in items['result'] if host['hostid'] == item['hostid']), '')
                host['itemkey'] = item_key
                host['itemid'] = item['itemid']
        else:
            for host in __hosts:
                host['itemkey'] = item_key
                host['itemid'] = ''

        # ----------------------------------------------------------------------------------------------------

        # History Get
        itemids = [i['itemid'] for i in items['result']]
        history_params = {
            'output': 'extend',
            'history': data_type,
            'itemids': itemids,
            'time_from': time_from,
            'time_till': time_till
        }
        history = self.request('history.get', history_params)

        # ----------------------------------------------------------------------------------------------------

        # Put history to hosts
        if history.get('result') and len(history['result']) > 0:
            for host in __hosts:
                data = [data for data in history['result'] if host['itemid'] == data['itemid']]
                host['history'] = data
        else:
            for host in __hosts:
                host['history'] = []

        # ----------------------------------------------------------------------------------------------------

        # Return Result
        return __hosts

    def get_interface_by_host_id(self, hostid='', output='extend'):
        '''
        Get interface by host id
        hostids: string/array
        example: '10792' / ['10792', '10793']
        如果 name 为 '' (空), 则返回 []
        '''

        response = self.request('hostinterface.get', {'output': output, 'hostids': hostid})

        try:
            if response.get('result'):
                return response['result']
            else:
                return []
        except Exception as e:
            print(e)
            return []
