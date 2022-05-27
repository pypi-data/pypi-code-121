#!/usr/bin/python3
import io
import json, datetime, time, mmap
import os
from com.interface.mdc_gateway_interface import GatewayInterface
from com.interface.mdc_gateway_base_define import EMarketDataType, EPlaybackTaskStatus

global interface
interface = GatewayInterface()


def get_interface():
    return interface


class OnRecvMarketData:
    def __init__(self):
        pass

    def OnMarketData(self, marketdatajson):
        try:
            if marketdatajson["marketDataType"] == EMarketDataType.MD_TICK:  # .MD_TICK 快照
                if "mdStock" in marketdatajson:  # 股票
                    timestr = json.dumps(marketdatajson["mdStock"]["MDTime"])
                elif "mdIndex" in marketdatajson:  # 指数
                    timestr = json.dumps( marketdatajson["mdIndex"]["MDTime"])
                elif "mdBond" in marketdatajson:  # 债券
                    timestr = json.dumps(marketdatajson["mdBond"]["MDTime"])
                elif "mdFund" in marketdatajson:  # 基金
                    timestr = json.dumps(marketdatajson["mdFund"]["MDTime"])
                elif "mdOption" in marketdatajson:  # 期权
                    timestr = json.dumps(marketdatajson["mdOption"]["MDTime"])
                elif "mdFuture" in marketdatajson:  # 期权
                    timestr = json.dumps(marketdatajson["mdFuture"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_TRANSACTION:  # .MD_TRANSACTION:逐笔成交
                if "mdTransaction" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdTransaction"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_ORDER:  # .MD_ORDER:逐笔委托
                if "mdOrder" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdOrder"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_CONSTANT:  # .MD_CONSTANT:静态信息
                if "mdConstant" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdConstant"]["HTSCSecurityID"])
                # MD_KLINE:实时数据只提供15S和1MIN K线
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_KLINE_15S or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_1MIN or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_5MIN or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_15MIN or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_30MIN or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_60MIN or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_KLINE_1D:
                if "mdKLine" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdKLine"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_TWAP_1S or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_TWAP_1MIN:  # .TWAP:TWAP数据
                if "mdTwap" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdTwap"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_VWAP_1S or marketdatajson[
                "marketDataType"] == EMarketDataType.MD_VWAP_1MIN:  # .VWAP:VWAP数据
                if "mdVwap" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdVwap"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.AD_FUND_FLOW_ANALYSIS:  # .AD_FUND_FLOW_ANALYSIS:
                if "mdFundFlowAnalysis" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdFundFlowAnalysis"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_ETF_BASICINFO:  # .MD_ETF_BASICINFO:ETF成分股信息
                if "mdETFBasicInfo" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdETFBasicInfo"]["MDTime"])
            elif marketdatajson["marketDataType"] == EMarketDataType.MD_SECURITY_LENDING:  # .MD_SECURITY_LENDING
                if "mdSecurityLending" in marketdatajson:
                    timestr = json.dumps(marketdatajson["mdSecurityLending"]["MDTime"])
        except BaseException as e:
            print("onMarketData error happened!" + marketdatajson)
            print(e)

    def OnPlaybackPayload(self, playloadstr):
        try:
            interface.set_service_value(4)
            # print(playloadstr)
            playloadjson = json.loads(playloadstr)
            if "taskId" in playloadjson:
                print("Parse Message id:" + playloadjson["taskId"])
            marketDataStream = playloadjson["marketDataStream"]
            if "isFinished" in marketDataStream:
                print(marketDataStream)
                print("OnPlaybackPayload total number=%d, serial=%d, isfinish=%d" % (
                    marketDataStream["totalNumber"], marketDataStream["serial"], marketDataStream["isFinished"]))
            else:
                print("OnPlaybackPayload total number=%d, serial=%d" % (
                    marketDataStream["totalNumber"], marketDataStream["serial"]))
            marketDataList = marketDataStream["marketDataList"]
            marketDatas = marketDataList["marketDatas"]
            #for data in iter(marketDatas):
                #self.OnMarketData(data)
        except BaseException as e:
            print(e)

    def OnPlaybackStatus(self, statusstr):
        try:
            statusjson = json.loads(statusstr)
            print("OnPlaybackStatus playback status=%d" % (statusjson["taskStatus"]))
            interface.set_service_value(statusjson["taskStatus"])
            if statusjson["taskStatus"] == EPlaybackTaskStatus.CANCELED or statusjson[
                "taskStatus"] == EPlaybackTaskStatus.COMPLETED or statusjson[
                "taskStatus"] == EPlaybackTaskStatus.FAILED:
                interface.mutex.acquire()
                if statusjson["taskId"] in interface.task_id_status:
                    del interface.task_id_status[statusjson["taskId"]]
                interface.mutex.release()
        except BaseException as e:
            print("error happened in OnPlaybackStatus")
            print(e)

    def OnPlaybackResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    print("OnPlaybackResponse Message id:" + responsejson["taskId"])
                else:
                    # print(response.errorContext.errorCode)
                    print("OnPlaybackResponse failed --> %s" % (responsejson["errorContext"]["message"]))
            else:
                print("OnPlaybackResponse :" + responsestr)
        except BaseException as e:
            print("error happened in OnPlaybackResponse")
            print(e)

    def OnPlaybackControlResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    print(responsejson["currentReplayRate"])
                    print("OnPlaybackControlResponse Message id:" + responsejson["taskId"])
                else:
                    print(
                        "OnPlaybackControlResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
            else:
                print("OnPlaybackControlResponse :" + responsestr)
        except BaseException as e:
            print("error happened in OnPlaybackControlResponse")
            print(e)

    def OnServiceMessage(self, marketDataStr):
        try:
            interface.set_service_value(1)
            marketDataJson = json.loads(marketDataStr)
            self.OnMarketData(marketDataJson)
        except BaseException as e:
            print("error happened in OnServiceMessage")
            print(e)

    def OnSubscribeResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            issucess = responsejson["isSuccess"]
            if issucess:
                print("Subscribe Success!!!")
            else:
                # print(gateway.getErrorCodeValue(response.errorContext.errorCode))
                print("Subscribe failed!!! reason ->" + (responsestr))
        except BaseException as e:
            print("error happened in OnServiceMessage")
            print(e)

    def OnFinInfoQueryResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            print(responsejson)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    print("OnFinInfoQueryResponse sucess")
                else:
                    print("OnFinInfoQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                    interface.set_query_exit(True)
            else:
                print("OnFinInfoQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                interface.set_query_exit(True)
        except BaseException as e:
            print("error happened in OnFinInfoQueryResponse")
            print(e)
    def OnQueryResponse(self, responsestr):
        try:
            responsejson = json.loads(responsestr)
            if "isSuccess" in responsejson:
                if responsejson["isSuccess"]:
                    marketDataStream = responsejson["marketDataStream"]
                    print(
                        "query response total number=%d, serial=%d" % (
                            marketDataStream["totalNumber"], marketDataStream["serial"]))
                    marketDataList = marketDataStream["marketDataList"]
                    marketDatas = marketDataList["marketDatas"]
                    print(marketDatas)
                    #for data in iter(marketDatas):
                        #self.OnMarketData(data)
                    if "isFinished" in marketDataStream:
                        interface.set_query_exit(marketDataStream["isFinished"] == 1)
                else:
                    print("OnQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                    interface.set_query_exit(True)
            else:
                print("OnQueryResponse failed!!! reason -> %s" % (responsejson["errorContext"]["message"]))
                interface.set_query_exit(True)
        except BaseException as e:
            print("error happened in OnQueryResponse")
            print(e)

    def OnGeneralError(self, contextstr):
        try:
            contextjson = json.loads(contextstr)
            # print(gateway.getErrorCodeValue(context.errorCode))
            print("OnGeneralError!!! reason -> %s" % (contextjson["message"]))
        except BaseException as e:
            print("error happened in OnGeneralError")
            print(e)

    def OnLoginSuccess(self):
        interface.login_success = True
        print("OnLoginSuccess!!!")

    def OnLoginFailed(self, error_no, message):
        interface.login_success = False
        try:
            print("OnLoginFailed!!! reason -> %s" % message)
        except BaseException as e:
            print("error happened in OnLoginFailed")
            print(e)

    def OnNoConnections(self):
        print("OnNoConnections!!!")
        interface.set_reconnect(True)
        interface.set_no_connections(True)

    def OnReconnect(self):
        print("OnReconnect!!!")
        interface.set_reconnect(True)
        interface.set_reconnect_count(interface.get_reconnect_count() + 1)
