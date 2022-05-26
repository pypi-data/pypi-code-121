#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json

from com.interface.mdc_gateway_head import mdc_gateway_client

global callback
callback = None

global logs
logs = None


def PyNotify_Regist(notify):
    global callback
    callback = notify


def PyLog_Regist(log):
    global logs
    logs = log
    mdc_gateway_client.Log_Regist(logs)


class PyNotify(mdc_gateway_client.Notify):
    def __init__(self):
        mdc_gateway_client.Notify.__init__(self)
        self.code = b'?$&@'

    def OnMarketData(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnMarketData(json.loads(result))
        except BaseException as e:
            print("Notify OnMarketData error happened!")
            print(buf)
            print(e)

    def OnPlaybackPayload(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnPlaybackPayload(result)
        except BaseException as e:
            print("Notify error happened in OnPlaybackPayload")
            print(buf)
            print(e)

    def OnPlaybackStatus(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnPlaybackStatus(result)

        except BaseException as e:
            print("Notify error happened in OnPlaybackStatus")
            print(buf)
            print(e)

    def OnPlaybackResponse(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnPlaybackResponse(result)
        except BaseException as e:
            print("Notify error happened in OnPlaybackResponse")
            print(buf)
            print(e)

    def OnPlaybackControlResponse(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnPlaybackControlResponse(result)
        except BaseException as e:
            print("Notify error happened in OnPlaybackControlResponse")
            print(buf)
            print(e)

    def OnServiceMessage(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnServiceMessage(result)
        except BaseException as e:
            print("Notify error happened in OnServiceMessage")
            print(buf)
            print(e)

    def OnSubscribeResponse(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnSubscribeResponse(result)
        except BaseException as e:
            print("Notify error happened in OnSubscribeResponse")
            print(buf)
            print(e)

    def OnQueryResponse(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnQueryResponse(result)
        except BaseException as e:
            print("Notify error happened in OnQueryResponse")
            print(buf)
            print(e)

    def OnFinInfoQueryResponse(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnFinInfoQueryResponse(result)
        except BaseException as e:
            print("Notify error happened in OnFinInfoQueryResponse")
            print(buf)
            print(e)

    def OnGeneralError(self, buf, size):
        try:
            result = mdc_gateway_client.cdata(buf, size)
            if callback is not None and (len(result) > 0):
                callback.OnGeneralError(result)
        except BaseException as e:
            print("Notify error happened in OnGeneralError")
            print(buf)
            print(e)

    def OnLoginSuccess(self):
        if callback is not None:
            callback.OnLoginSuccess()

    def OnLoginFailed(self, error_no, message):
        try:
            if callback is not None:
                callback.OnLoginFailed(error_no, message)
        except BaseException as e:
            print("Notify error happened in OnLoginFailed")
            print(e)

    def OnNoConnections(self):
        if callback is not None:
            callback.OnNoConnections()

    def OnReconnect(self):
        if callback is not None:
            callback.OnReconnect()
