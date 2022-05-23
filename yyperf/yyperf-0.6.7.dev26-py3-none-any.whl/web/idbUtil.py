#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import json
import logging
import os
import sys
import traceback
from typing import Optional
from collections import defaultdict

from tidevice._device import Device
from tidevice._proto import MODELS, PROGRAM_NAME
from tidevice._usbmux import Usbmux
from tidevice.exceptions import MuxError, ServiceError

um = Usbmux()  # Usbmux
logger = logging.getLogger(PROGRAM_NAME)


def _complete_udid(udid: Optional[str] = None) -> str:
    infos = um.device_list()
    if not udid:
        if len(infos) >= 2:
            sys.exit("More than 2 devices detected")
        if len(infos) == 0:
            sys.exit("No device detected")
        return infos[0].udid

    # Find udid exactly match
    for info in infos:
        if info.udid == udid:
            return udid

    # Find udid starts-with
    _udids = [
        info.udid for info in infos
        if info.udid.startswith(udid)
    ]

    if len(_udids) == 1:
        return _udids[0]

    raise RuntimeError("No matched device", udid)


def _udid2device(udid: Optional[str] = None) -> Device:
    _udid = _complete_udid(udid)
    if _udid != udid:
        logger.debug("AutoComplete udid %s", _udid)
    del (udid)
    return Device(_udid, um)


def _print_json(value):
    def _bytes_hook(obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode()
        else:
            return str(obj)

    print(json.dumps(value, indent=4, ensure_ascii=False, default=_bytes_hook))


def GetConnectedDevice():
    print("List of apple devices attached")
    ret_result = []
    result = []
    try:
        for dinfo in um.device_list():
            udid, conn_type = dinfo.udid, dinfo.conn_type
            ret_result.append(udid)
            try:
                _d = Device(udid, um)
                name = _d.name
                print(udid, name, conn_type)
            except MuxError:
                name = ""
            result.append(dict(udid=udid, name=name, conn_type=conn_type))
    except:
        return ret_result
    # _print_json(result)
    return ret_result


def GetDeviceInfo(udid):
    d = _udid2device(udid)
    value = d.get_value()
    # _print_json(value)
    # print("{:17s} {}".format("MarketName:",
    #                          MODELS.get(value['ProductType'])))
    ret_result = '%s|%s|iOS %s' % (udid, MODELS.get(value['ProductType']), value.get('ProductVersion'))
    # for attr in ('DeviceName', 'ProductVersion', 'ProductType',
    #          'ModelNumber', 'SerialNumber', 'PhoneNumber',
    #          'CPUArchitecture', 'ProductName', 'ProtocolVersion',
    #          'RegionInfo', 'TimeIntervalSince1970', 'TimeZone',
    #          'UniqueDeviceID', 'WiFiAddress', 'BluetoothAddress',
    #          'BasebandVersion'):
    #     print("{:17s} {}".format(attr + ":", value.get(attr)))
    return ret_result


def get_app_list(udid):
    d = _udid2device(udid)
    applist = []
    for info in d.installation.iter_installed():
        # bundle_path = info['BundlePath']
        bundle_id = info['CFBundleIdentifier']
        try:
            display_name = info['CFBundleDisplayName']
            # major.minor.patch
            version = info.get('CFBundleShortVersionString', '')
            #print(bundle_id, display_name, version)
            package = f"{display_name} {version}--{bundle_id}"
            applist.append(package)
        except BrokenPipeError:
            break
    return applist


def start_app(udid, bundle_id):
    d = _udid2device(udid)
    try:
        pid = d.instruments.app_launch(bundle_id)
        print("PID:", pid)
        return pid
    except ServiceError as e:
        logger.error(traceback.format_exc())
        return -1

def getapp_pid(udid, bundle_id):
    d = _udid2device(udid)
    app_infos = list(d.installation.iter_installed(app_type=None))
    ps = list(d.instruments.app_process_list(app_infos))
    pid = -1
    pro_name = ""
    # keys = ['pid', 'name', 'bundle_id', 'display_name']
    for p in ps:
        if p['bundle_id']==bundle_id:
            pid = p['pid']
            pro_name = p['name']
    return pid,pro_name

def screen_shot(device, filepath):
    # os.popen('tidevice -u %s screenshot %s' % (device, filepath)).read()
    d = _udid2device(device)
    filename = filepath or "screenshot.jpg"
    print("Screenshot saved to", filename)
    d.screenshot().convert("RGB").save(filename)


def DownloadLogs(device, bundleId, remotePath, localPath):
    cmd = 'ios-deploy --id %s --bundle_id %s --download=%s --to %s' % (device, bundleId, remotePath, localPath)
    logging.info('下载日志文件。。。')
    logging.info(cmd)
    outstr = os.popen(cmd).read()
    logging.info('日志下载完成' + outstr)


def removeLogs(device, bundleId, remotePath):
    cmd = 'ios-deploy --id %s --bundle_id %s --list=%s ' % (device, bundleId, remotePath)
    outLines = os.popen(cmd).readlines()
    for line in outLines:
        if line.startswith(remotePath):
            rmcmd = 'ios-deploy --id %s --bundle_id %s --rm %s' % (device, bundleId, line.strip())
            logging.info(rmcmd)
            os.popen(rmcmd)


def dowloadApp(url, path):
    print(('dowloading app to %s from %s ' % (path, url)))
    cmd = 'curl -o %s %s' % (path, url)
    outStr = os.popen(cmd).read()
    # print outStr
    strList = outStr.split('\n')
    for line in strList:
        if line.find('100 ') != -1:
            return True
    return False


def installApp(path, udid):
    if os.path.exists(path) is False:
        return False
    logging.info('installing the app from %s ' % path)
    d = _udid2device(udid)
    bundle_id = d.app_install(path)
    logger.info(bundle_id)


def unInstallApp(appid, udid):
    print(('uninstall the app %s from %s' % (appid, udid)))
    d = _udid2device(udid)
    ok = d.app_uninstall(appid)
    return ok


# 根据进程唯一名找到进程ID，并杀掉进程
def killProcess(processKey, deviceid=''):
    if deviceid != '':
        outStr = os.popen('ps -A | grep \'%s\' | grep \'%s\'' % (processKey, deviceid)).read()
    else:
        outStr = os.popen('ps -A | grep \'%s\'' % processKey).read()
    pid = ''
    strList = outStr.split('\n')
    for line in strList:
        if line.find(processKey) != -1 and line.find('ps -A | grep \'%s\'' % processKey) == -1:
            logging.info(line)
            pid = line.strip().split(' ')[0]
            logging.info(pid)
            break
    if pid != '':
        os.popen('kill ' + pid).read()


if __name__ == "__main__":
    print(getapp_pid("00008110-0010699A3C79801E","com.yy.enterprise.yyvoice"))
