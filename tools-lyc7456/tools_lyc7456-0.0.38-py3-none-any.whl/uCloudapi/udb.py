import json, requests
import time, datetime
from tools_lyc7456.uCloudapi.signature import verify_ac

# Write by lyc at 2021-12-27


class UDB():
    '''优刻得UDB封装'''
    def __init__(self, key):
        self.PublicKey = key['PublicKey']           # 公钥
        self.PrivateKey = key['PrivateKey']         # 私钥
        self.api_url = key['api_url']               # api接口url
        self.project_id = key['project_id']         # 项目id
        self.region = key['region']                 # 地域
        

    def describeUDBInstance(self, class_type='SQL'):
        """[获取云数据库信息 - DescribeUDBInstance]https://docs.ucloud.cn/api/udb-api/describe_udb_instance
        主要用于获取udb实例id

        Args:
            class_type (str, optional): [DB种类]. 其取值如下：mysql: SQL；mongo: NOSQL；postgresql: postgresql.

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeUDBInstance',            # 接口名称
                'Region': self.region,              # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'ClassType': class_type,
                'Limit': 100,
                'Offset': 0,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeUDBBackup(self, db_id, backup_type='Auto', begin_day=-1):
        """[获取备份列表 - DescribeUDBBackup]https://docs.ucloud.cn/api/udb-api/describe_udb_backup
        主要用于获取指定udb的备份id

        Args:
            db_id (string, require): [DB实例Id]
            backup_type (string, optional): [备份类型] 默认值'Auto'，可选值 Manual 手动 Auto 自动。
            begin_day (int, optional): [过滤条件，查询n天前的备份列表] 取值为整型负数。默认值-1，表示昨天，即获取过去的24小时内的备份列表。

        Returns:
            [str]: [response]
        """
        try:
            backup_type_int = 0 if backup_type == 'Auto' else 1         # 类型转换（string->int）backup_type='Auto' -> 0  或  backup_type='Manual' -> 1
            now = datetime.datetime.now()
            begin_time = now + datetime.timedelta(days=begin_day)
            params = {
                'Action': 'DescribeUDBBackup',          # 接口名称
                'Region': self.region,                  # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'Limit': 100,
                'Offset': 0,
                'BackupType': backup_type_int,          # backup_type_int [备份类型]. 默认值为0。可选值为0或1，0表示自动，1表示手动。
                'BeginTime': int(time.mktime(begin_time.timetuple())),          # 过滤条件:起始时间(Unix时间戳)
                'EndTime': int(time.mktime(now.timetuple())),                   # 过滤条件:结束时间(Unix时间戳)
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeUDBInstanceBackupURL(self, db_id, backup_id):
        """[获取UDB备份下载地址 - DescribeUDBInstanceBackupURL]https://docs.ucloud.cn/api/udb-api/describe_udb_instance_backup_url

        Args:
            db_id (string, require): [DB实例Id]
            backup_id (string, require): [DB实例备份ID]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeUDBInstanceBackupURL',          # 接口名称
                'Region': self.region,                  # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'BackupId': backup_id,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeURedisGroup(self):
        """[查询主备Redis - DescribeURedisGroup]https://docs.ucloud.cn/api/umem-api/describe_uredis_group
        主要用于获取主备版Redis实例id

        Args:

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeURedisGroup',          # 接口名称
                'Region': self.region,                  # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'Limit': 100,
                'Offset': 0,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeURedisBackup(self, group_id, backup_type='Auto', begin_day=-1):
        """[查询主备redis备份 - DescribeURedisBackup]https://docs.ucloud.cn/api/umem-api/describe_uredis_backup
        主要用于获取主备版Redis实例id对应的备份id

        Args:
            group_id (string, require): [组的ID（Redis实例id）]
            backup_type (string, optional): [备份类型] 默认值'Auto'，可选值 Manual 手动 Auto 自动。
            begin_day (int, optional): [过滤条件，查询n天前的备份列表] 取值为整型负数。默认值-1，表示昨天，即获取过去的24小时内的备份列表。

        Returns:
            [str]: [response]
        """
        try:
            now = datetime.datetime.now()
            begin_time = now + datetime.timedelta(days=begin_day)
            now_timestamp = int(time.mktime(now.timetuple()))
            begin_time_timestamp = int(time.mktime(begin_time.timetuple()))
            params = {
                'Action': 'DescribeURedisBackup',       # 接口名称
                'Region': self.region,                  # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'GroupId': group_id,
                'Limit': 100,
                'Offset': 0,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')
            response_dict = json.loads(resp_string)

            # 以时间区间、备份类型为维度缩小查询范围
            response_dict_new = {
                'RetCode': response_dict['RetCode'],
                'Action': response_dict['Action'],
                'DataSet': [],
            }
            if response_dict['RetCode'] == 0:
                for item in response_dict['DataSet']:
                    if begin_time_timestamp < item['BackupTime'] < now_timestamp and item['BackupType'] == backup_type:
                        response_dict_new['DataSet'].append(item)
            
            response_dict_new['TotalCount'] = len(response_dict_new['DataSet'])
            return json.dumps(response_dict_new)

        except Exception as err:
            # print(err)
            return err



    def describeURedisBackupURL(self, backup_id, zone):
        """[获取主备Redis备份下载链接 - DescribeURedisBackupURL]https://docs.ucloud.cn/api/umem-api/describe_uredis_backup_url

        Args:
            backup_id (string, require): [备份ID]
            zone (string, require): [可用区]

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeURedisBackupURL',          # 接口名称
                'Region': self.region,                  # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'Zone': zone,
                'BackupId': backup_id,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def backupUDBInstanceSlowLog(self, db_id, begin_time, end_time, backup_name):
        """[备份UDB指定时间段的slowlog分析结果 - BackupUDBInstanceSlowLog]https://docs.ucloud.cn/api/udb-api/backup_udb_instance_slow_log

        Args:
            db_id (string, require): DB实例Id,该值可以通过DescribeUDBInstance获取
            begin_time (int, require): 过滤条件:起始时间(时间戳)
            end_time (int, require): 过滤条件:结束时间(时间戳)
            backup_name (string, require): 备份文件名称

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'BackupUDBInstanceSlowLog',            # 接口名称
                'Region': self.region,              # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'BeginTime': begin_time,
                'EndTime': end_time,
                'BackupName': backup_name,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeUDBLogPackage(self, db_id, log_package_type=3, begin_day=-1):
        """[列表UDB实例日志备份信息 - DescribeUDBLogPackage]https://docs.ucloud.cn/api/udb-api/describe_udb_log_package
        列表UDB实例binlog或slowlog或errorlog备份信息
        
        Args:
            db_id (string, require): DB实例Id,该值可以通过DescribeUDBInstance获取
            log_package_type(int, optional): 需要列出的备份文件类型，每种文件的值如下：
                                            2 : BINLOG_BACKUP 
                                            3 : SLOW_QUERY_BACKUP 
                                            4 : ERRORLOG_BACKUP
            begin_day (int, optional): [过滤条件，查询n天前的备份列表] 取值为整型负数。默认值-1，表示昨天，即获取过去的24小时内的备份列表。

        Returns:
            [str]: [response]
        """
        try:
            now = datetime.datetime.now()
            begin_time = now + datetime.timedelta(days=begin_day)
            params = {
                'Action': 'DescribeUDBLogPackage',            # 接口名称
                'Region': self.region,              # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'Type': log_package_type,
                'Limit': 100,
                'Offset': 0,
                'BeginTime': int(time.mktime(begin_time.timetuple())),          # 过滤条件:起始时间(Unix时间戳)
                'EndTime': int(time.mktime(now.timetuple())),                   # 过滤条件:结束时间(Unix时间戳)
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeUDBLogBackupURL(self, db_id, backup_id):
        """[获取UDB的slowlog备份地址 - DescribeUDBLogBackupURL]https://docs.ucloud.cn/api/udb-api/describe_udb_log_backup_url

        2022-5-23 UDB NVMe机型下载链接无法下载，请替换为 describeUDBBinlogBackupURL 接口来使用。

        Args:
            db_id (string, require): DB实例Id,该值可以通过DescribeUDBInstance获取
            backup_id (int, require): DB实例binlog备份ID，可以从DescribeUDBLogPackage结果当中获得

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeUDBLogBackupURL',            # 接口名称
                'Region': self.region,              # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'BackupId': backup_id,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err



    def describeUDBBinlogBackupURL(self, db_id, backup_id):
        """[获取UDB的Binlog备份地址 - DescribeUDBBinlogBackupURL]https://docs.ucloud.cn/api/udb-api/describe_udb_binlog_backup_url

        Args:
            db_id (string, require): DB实例Id,该值可以通过DescribeUDBInstance获取
            backup_id (int, require): DB实例binlog备份ID，可以从DescribeUDBLogPackage结果当中获得

        Returns:
            [str]: [response]
        """
        try:
            params = {
                'Action': 'DescribeUDBBinlogBackupURL',            # 接口名称
                'Region': self.region,              # 地区
                'ProjectId': self.project_id,
                'PublicKey': self.PublicKey,
                'DBId': db_id,
                'BackupId': backup_id,
            }
            # 签名
            signature = verify_ac(self.PublicKey, self.PrivateKey, params)
            params['Signature'] = signature

            # POST请求接口
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url=self.api_url, headers=headers, data=json.dumps(params))
            resp_string = response.content.decode('utf-8')

            return resp_string

        except Exception as err:
            # print(err)
            return err