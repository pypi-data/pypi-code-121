#!/usr/bin/python3+

import os, sys, json

from com.interface.mdc_gateway_base_define import ErrorInfo, SortType, Play_Back_Type, QueryType, QueryServerConfig

sys.path.insert(1, "./model")
sys.path.insert(2, "./interface")
sys.path.insert(3, "./libs")

from com.interface import mdc_recvdata_interface as recvdata
# from log_handle import PyLog
import time
from multiprocessing import Lock
from com.interface.mdc_gateway_head import mdc_gateway_client

global notifys  # 全局变量，不能做临时变量，需要全局使用,注意生存周期
notifys = recvdata.PyNotify()
notifys.thisown = 0


class GatewayInterface():
    ineffective_size = 9999999999
    max_query_size = 104857600
    min_synchronous_data_len = 10
    service_value = 0
    query_exit = False
    reconnect = False
    login_success = False
    no_connections = False
    reconnect_count = 0
    mutex = Lock()
    task_id_status = {}

    def __init__(self):
        self.service_value = 0
        self.query_exit = False
        self.reconnect = False
        self.login_success = False
        self.no_connections = False
        self.reconnect_count = 0
        self.open_file_log = False
        self.open_cout_log = False
        self.open_trace = True

    def get_service_value(self):
        return self.service_value

    def set_service_value(self, i):
        self.service_value = i

    def get_query_exit(self):
        return self.query_exit

    def set_query_exit(self, value):
        self.query_exit = value

    def get_reconnect(self):
        return self.reconnect

    def set_reconnect(self, value):
        self.reconnect = value

    def get_login_flag(self):
        return self.login_success

    def get_no_connections(self):
        return self.no_connections

    def set_no_connections(self, value):
        self.no_connections = value

    def get_reconnect_count(self):
        return self.reconnect_count

    def set_reconnect_count(self, value):
        self.reconnect_count = value

    def get_version(self):
        ver = str(mdc_gateway_client.python_get_version())
        return ver;

    def get_error_code_value(self, code):
        value = ErrorInfo.get_error_code_value(code)

        return value

    def add_ip_map(self, original_ip, map_ip):
        mdc_gateway_client.python_add_ip_map(original_ip.encode(encoding="utf-8"), map_ip.encode(encoding="utf-8"))

    def delete_ip_map(self, original_ip):
        mdc_gateway_client.python_delete_ip_map(original_ip.encode(encoding="utf-8"))

    def add_ip_port(self, original_port, map_port):
        mdc_gateway_client.python_add_port_map(original_port, map_port)

    def delete_ip_map(self, original_port):
        mdc_gateway_client.python_delete_port_map(original_port)

    def is_trace(self):
        return mdc_gateway_client.python_is_trace();

    def is_compress(self):
        return mdc_gateway_client.python_is_compress();

    def is_responseCallback(self):
        return mdc_gateway_client.python_is_response_callback();

    def init(self, open_trace, open_file_log, open_cout_log):
        mdc_gateway_client.python_init_env()
        mdc_gateway_client.python_open_response_callback()
        self.open_trace = open_trace
        self.open_file_log = open_file_log
        self.open_cout_log = open_cout_log

    def __init_log__(self):
        if self.open_file_log:
            mdc_gateway_client.python_open_file_log()
        else:
            mdc_gateway_client.python_close_file_log()
        if self.open_cout_log:
            mdc_gateway_client.python_open_cout_log()
        else:
            mdc_gateway_client.python_close_cout_log()
        if self.open_trace:
            mdc_gateway_client.python_open_trace()
        else:
            mdc_gateway_client.python_close_trace()

    def open_compress(self, torf):
        if torf:
            mdc_gateway_client.python_open_compress()
        else:
            mdc_gateway_client.python_close_compress()

    def fini(self):
        mdc_gateway_client.python_logout()
        mdc_gateway_client.python_fini_env()

    # 订阅-全订阅 param:marketDataTypeList 为 EMarketDataType 枚举值集合
    def subscribebytype(self, datatype, marketdatatypes):
        if self.get_login_flag():
            subscribejson = {"DataType": datatype}
            subscribejson["MarketdataTypes"] = marketdatatypes
            subscribestr = json.dumps(subscribejson)

            ret = mdc_gateway_client.python_subscribe(subscribestr, len(subscribestr))
            if ret < 0:
                print("subscribeAll failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
        else:
            print("Unsuccessful login")

    def subscribebyid(self, datatype, htscSecurityids):
        if self.get_login_flag():
            subscribejson = {"DataType": datatype}
            subscribejson["HTSCSecurityIDs"] = htscSecurityids
            subscribestr = json.dumps(subscribejson)

            ret = mdc_gateway_client.python_subscribe(subscribestr, len(subscribestr))
            if ret < 0:
                print("subscribeAll failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
        else:
            print("Unsuccessful login")

    # 回放  params:securityIdList 为标的 str值集合;marketDataType 为 EMarketDataType 枚举值集合;exrightsType 为EPlaybackExrightsType枚举值,startTime str类型;stopTime str类型
    def playCallback(self, id_list, marketDataType, exrightsType, startTime, stopTime ,isMdtime =True):
        if self.get_login_flag():
            for id in id_list:
                playbackjson = {}
                playbackjson["TaskID"] = mdc_gateway_client.python_get_task_id()
                self.mutex.acquire()
                self.task_id_status[playbackjson["TaskID"]] = 0
                self.mutex.release()

                htscSecurityIDs = []

                htscSecurityID = {}
                htscSecurityID["HTSCSecurityID"] = id
                htscSecurityID["EMarketDataType"] = marketDataType
                htscSecurityIDs.append(htscSecurityID)

                playbackjson["HTSCSecurityIDs"] = htscSecurityIDs
                playbackjson["ExrightsType"] = exrightsType
                playbackjson["StartTime"] = startTime
                playbackjson["EndTime"] = stopTime

                if isMdtime:
                    playbackjson["Sort"] = SortType.Sort_MDTime
                else:
                    playbackjson["Sort"] = SortType.Sort_RecivedTime

                playbackjson["DataType"] = Play_Back_Type.Play_Back

                playback_info = json.dumps(playbackjson)
                while (self.task_id_status.__len__() >= 5):
                    time.sleep(1)

                ret = mdc_gateway_client.python_request_playback(playback_info, len(playback_info))
                if ret < 0:
                    print(self.get_error_code_value(ret))
                    print("playCallback failed!!!")
                    exit(-1)

            while (self.task_id_status.__len__() > 0):
                time.sleep(1)
        else:
            print("Unsuccessful login")

    # 回放  params:securityIdList 为标的 str值集合;marketDataType 为 EMarketDataType 枚举值集合;exrightsType 为EPlaybackExrightsType枚举值,startTime str类型;stopTime str类型
    def playSortCallback(self, id_list, startTime, stopTime, marketDataType, exrightsType, sort):
        if self.get_login_flag():
            for id in id_list:
                playbackjson = {}
                playbackjson["TaskID"] = mdc_gateway_client.python_get_task_id()
                self.mutex.acquire()
                self.task_id_status[playbackjson["TaskID"]] = 0
                self.mutex.release()

                htscSecurityIDs = []

                htscSecurityID = {}
                htscSecurityID["HTSCSecurityID"] = id
                htscSecurityID["EMarketDataType"] = marketDataType
                htscSecurityIDs.append(htscSecurityID)

                playbackjson["HTSCSecurityIDs"] = htscSecurityIDs
                playbackjson["ExrightsType"] = exrightsType
                playbackjson["StartTime"] = startTime
                playbackjson["EndTime"] = stopTime

                playbackjson["Sort"] = sort
                playbackjson["DataType"] = Play_Back_Type.Play_Back

                playback_info = json.dumps(playbackjson)
                while (self.task_id_status.__len__() >= 5):
                    time.sleep(1)

                ret = mdc_gateway_client.python_request_playback(playback_info, len(playback_info))
                if ret < 0:
                    print(self.get_error_code_value(ret))
                    print("playCallback failed!!!")
                    exit(-1)
                self.set_service_value(0)
            while (1):
                value = self.get_service_value()
                if value == 16 or value == 17 or value == 18:
                    break;
                else:
                    time.sleep(1)
        else:
            print("Unsuccessful login")

    def queryfininfo(self, querytype, params, synchronousflag=False, securityIDSourceAndTypes=[], securityIdList=[]):

        if synchronousflag:  # 同步
            self.queryfininfosynchronous(querytype, params, securityIDSourceAndTypes, securityIdList)
        else:  # 异步
            self.queryfininfoasynchronous(querytype, params, securityIDSourceAndTypes, securityIdList)

    def queryfininfosynchronous(self, querytype, params, securityIDSourceAndTypes=[], securityIdList=[]):

        request = {"DataType": querytype}
        request["Params"] = params
        securitySourceTypes = []
        securityIds = []

        for securityIDSourceAndType in iter(securityIDSourceAndTypes):
            securitySourceTypes.append(securityIDSourceAndType)
        if len(securitySourceTypes) > 0:
            request["MarketdataTypes"] = securitySourceTypes
        for id in securityIdList:
            securityIds.append(id)
        if len(securityIds) > 0:
            request["HTSCSecurityIDs"] = securityIds
        print(request)
        request_info = json.dumps(request)

        rettempdata = mdc_gateway_client.python_request_fin_info_query_sync(request_info, len(request_info))
        retdatalenstr = mdc_gateway_client.cdata(rettempdata, self.min_synchronous_data_len)
        retdatalen = int(retdatalenstr)
        if retdatalen == self.ineffective_size:
           return "invalid request"
        else:
            if self.min_synchronous_data_len < retdatalen < self.max_query_size:
                retdatastr = mdc_gateway_client.cdata(rettempdata, retdatalen)
                result = json.loads(retdatastr[self.min_synchronous_data_len:retdatalen])
                return result
            else:
                return "invalid data"


    def queryfininfoasynchronous(self, querytype, params, securityIDSourceAndTypes=[], securityIdList=[]):

        request = {"DataType": querytype}
        request["Params"] = params
        securitySourceTypes = []
        securityIds = []

        for securityIDSourceAndType in iter(securityIDSourceAndTypes):
            securitySourceTypes.append(securityIDSourceAndType)
        if len(securitySourceTypes) > 0:
            request["MarketdataTypes"] = securitySourceTypes
        for id in securityIdList:
            securityIds.append(id)
        if len(securityIds) > 0:
            request["HTSCSecurityIDs"] = securityIds
        print(request)
        request_info = json.dumps(request)

        ret = mdc_gateway_client.python_request_fin_info_query_async(request_info, len(request_info))
        if ret < 0:
            print("queryfininfo failed!!! reason:%s" % (self.get_error_code_value(ret)))
            exit(-1)

    def queryMdContantCallback(self, securityIDSourceAndTypes, securityIdList, synchronousflag=False):
        self.queryCallback(QueryType.QUERY_CONSTANT, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryLastMdContantCallback(self, securityIDSourceAndTypes, securityIdList ,synchronousflag=False):
        self.queryCallback(QueryType.QUERY_CONSTANT_TODAY, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryETFInfoCallback(self, securityIDSourceAndTypes, securityIdList ,synchronousflag=False):
        self.queryCallback(QueryType.QUERY_ETFBASICINFO, securityIDSourceAndTypes, securityIdList, synchronousflag)

    def queryLastMdTickCallback(self, securityIDSourceAndTypes, securityIdList ,synchronousflag=False):
        self.queryCallback(QueryType.QUERY_TICK, securityIDSourceAndTypes, securityIdList, synchronousflag)

    # 查询  params:queryType 为int值;securityIdSource 为市场ESecurityIDSource 枚举值;securityType 为 ESecurityIDSource枚举值集合
    def queryCallback(self, queryType, securityIDSourceAndTypes, securityIdList ,synchronousflag=False):
        if self.get_login_flag():
            request = {"DataType": queryType}
            securitySourceTypes = []
            securityIds = []

            for securityIDSourceAndType in iter(securityIDSourceAndTypes):
                securitySourceTypes.append(securityIDSourceAndType)
            request["MarketdataTypes"] = securitySourceTypes
            for id in securityIdList:
                securityIds.append(id)
            request["HTSCSecurityIDs"] = securityIds
            print(request)
            request_info = json.dumps(request)
            ret = mdc_gateway_client.python_request_mdquery(request_info, len(request_info))
            if ret < 0:
                print("queryCallback failed!!! reason:%s" % (self.get_error_code_value(ret)))
                exit(-1)
            self.set_query_exit(False)
            while True:
                exit = self.get_query_exit()
                if exit:
                    break;
                else:
                    time.sleep(1)
        else:
            print("Unsuccessful login")

    def login(self, ip, port, username, pwd, istoken, certlog, backuplist,
              queryaddress=QueryServerConfig.QUERY_ADDRESS,
              querycert=QueryServerConfig.QUERY_CERT,
              thread_count=1):
        self.__init_log__()
        # 必须存在的回调注册，若不存在，则不会产生回调
        mdc_gateway_client.Notify_Regist(notifys)
        loginjson = {}
        loginjson["UserName"] = username
        loginjson["Password"] = pwd
        loginjson["IsToken"] = istoken
        loginjson["MainServerIP"] = ip
        loginjson["MainServerPort"] = port
        loginjson["BackServer"] = backuplist
        loginjson["QueryAddress"] = queryaddress
        loginjson["QueryCert"] = querycert
        loginjson["QuerySSL"] = QueryServerConfig.QUERY_IS_SSL



        loginstr = json.dumps(loginjson)


        ret = mdc_gateway_client.python_login(loginstr, len(loginstr))
        return ret


    def setCallBack(self, callback):
        recvdata.PyNotify_Regist(callback)

    # def own_deal_log(self,use_init,open_trace = True):
    #     if not use_init:
    #         self.open_trace = open_trace
    #         self.open_file_log = False
    #         self.open_cout_log = False
    #     log = PyLog()
    #     recvdata.PyLog_Regist(log)


class Element():
    def __init__(self, source, type, list):
        self.source = source
        self.type = type
        self.list = list


class SecurityIDSourceAndType():
    def __init__(self, source, type):
        self.source = source
        self.type = type


class SubscribeByIdElement():
    def __init__(self, id, typeList):
        self.id = id
        self.securityIDSourceAndTypeList = typeList


class QueryElement():
    def __init__(self, idList, type):
        self.idList = idList
        self.securityIDSourceAndType = type


class BackupList():
    def __init__(self):
        self.list = mdc_gateway_client.StrIntMap()

    def Add(self, key, value):
        self.list[key.encode(encoding="utf-8")] = value


class StrList():
    def __init__(self):
        self.list = mdc_gateway_client.StrList()

    def Add(self, value):
        self.list.push_back(value.encode(encoding="utf-8"))
