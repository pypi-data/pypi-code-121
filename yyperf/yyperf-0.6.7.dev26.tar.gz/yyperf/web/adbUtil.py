#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys

import re
import logging
import time
import subprocess
import uiautomator2 as u2

logging = logging.getLogger("main_log")


def GetConnectedDevice():
    try:
        out = os.popen('adb devices').read()
        res = re.findall('(\S*)\\s+device', out)
        if len(res) > 1:
            return res[1:]
        else:
            return []
    except Exception as e:
        logging.error(str(e))
        return []


def IsOnline(deviceName):
    out = os.popen('adb devices').read()
    if len(out) < 5:
        return False
    res = re.search('%s\\s+device' % deviceName, out)
    if res is None:
        return False
    return True

def GetPowerState(deviceName):
    """
    获取屏幕状态True-开屏，False-黑屏
    """
    try:
        outStr = os.popen("adb -s %s shell \" dumpsys power | grep 'Display Power:'\"" % (deviceName)).read()
        if outStr.find('Display Power: state=ON') != -1:
            return True
        else:
            return False
    except Exception as e:
        logging.error(str(e))
        return False


def GetBatteryInfo(deviceName, filter):
    """
    获取电池信息
    """
    info = '0'
    try:
        outStr = os.popen("adb -s %s shell \" dumpsys battery | grep '%s'\"" % (deviceName, filter)).read()
        # logging.info(outStr)
        outlist = outStr.split('\n')
        for line in outlist:
            if line.find(filter + ':') != -1:
                if filter == 'powered':
                    info += line.strip() + ';'
                else:
                    info = line.split(':')[1].strip()
                    break
    except Exception as e:
        logging.error(str(e))
    return info


def waitBattery(*args):
    deviceName, filter, value = args[0]
    dict = {'level': '电量', 'temperature': '温度'}
    val = GetBatteryInfo(deviceName, filter)
    logging.info("当前%s为：%s，目标值为：%s" % (dict[filter], val, value))
    if (filter == 'temperature' and int(val) <= int(value)) or (filter == 'level' and int(val) == int(value)):
        return True
    time.sleep(60)
    return False

def GetPid(device, packageName):
    try:
        cmd = "adb -s %s shell \"ps -ef|grep %s\"" % (device, packageName + "$")
        outputs = os.popen(cmd).read()
        logging.info('GetPid outputs===' + outputs)
        pattern = r'^\w+\s+(\d+)\s+.*\s+%s$' % packageName.strip()
        m = re.search(pattern, outputs.strip())
        if m:
            return m.group(1)
        else:
            logging.info("app still not get up")
        cmd = "adb -s %s shell \"ps |grep %s\"" % (device, packageName + "$")
        outputs = os.popen(cmd).read()
        logging.info('GetPid outputs===' + outputs)
        pattern = r'^\w+\s+(\d+)\s+.*\s+%s' % packageName.strip()
        m = re.search(pattern, outputs)
        if m:
            return m.group(1)
        else:
            logging.info("No process named %s found!" % packageName)
            return -1
    except Exception as e:
        logging.error(str(e))
        return -1

def GetDeviceInfo(device):
    try:
        cmd = "adb -s %s shell getprop " % device + "%s"
        verPattern = "ro.build.version.release"
        modelPattern = "ro.product.model"
        brandPattern = "ro.product.brand"
        brand = os.popen(cmd % brandPattern).read()
        brand = brand.strip("\n").strip()
        model = os.popen(cmd % modelPattern).read()
        model = model.strip("\n").strip()
        version = os.popen(cmd % verPattern).read()
        version = version.strip("\n").strip()
        return "%s|%s|%s|%s" % (device, brand, model, version)
    except Exception as e:
        logging.error(str(e))
        return device


def LogcatMonitorLog(device, filename, key=None):
    try:
        # os.popen("adb -s %s shell logcat -c" % device)
        cmd = "adb -s %s shell logcat" % (device)
        if key is not None:
            cmd = "adb -s %s shell \" logcat | grep %s\"" % (device, key)
        logging.info(cmd)
        logcat_file = open(filename, mode='w')
        return subprocess.Popen(cmd, stdout=logcat_file, stderr=logcat_file, shell=True), logcat_file
        # logFile = open(filename, 'w+',encoding='utf-8')
        # pro = subprocess.Popen(cmd, stdout=logFile, stderr=logFile, shell=True)
        # while pro.poll() is None :
        #    time.sleep(5)
        # logging.info(u"logcat已退出")
        # logFile.close()
    except Exception as e:
        logging.error(str(e))
        return None


def StopLogcatMonitor(device):
    try:
        pid = -1
        outLines = os.popen("adb -s %s shell \"ps | grep logcat\"" % device).readlines()
        for line in outLines:
            if line.startswith("shell") and line.find('logcat') != -1:
                pid = int(line.strip().split()[1])
        if pid != -1:
            logging.info("logcat pid:%s" % pid)
            os.popen("adb -s %s shell kill %s" % (device, pid))
        logging.info("logcat已退出")
    except Exception as e:
        logging.error(str(e))


def stopAPP(device, package):
    os.popen("adb -s %s shell am force-stop %s" % (device, package))


def removeFile(device, filename):
    cmd = "adb -s %s shell rm %s" % (device, filename)
    os.popen(cmd).read()


def isAppInstalled(device, package):
    cmd = "adb -s %s shell \"pm list packages | grep %s\"" % (device, package)
    outStr = os.popen(cmd).read().strip()
    return outStr.startswith("package:%s" % package)


def getAppVersion(device, package):
    try:
        verName = ""
        verCode = ""
        cmd = "adb -s %s shell \"dumpsys package %s | grep version\"" % (device, package)
        outLines = os.popen(cmd).readlines()
        for line in outLines:
            line = line.strip()
            if line.startswith("versionCode"):
                verCode = line.split(' ')[0].split('=')[1]
            elif line.startswith("versionName"):
                verName = line.split('=')[1]
        return "%s#%s" % (verName, verCode)
    except Exception as e:
        logging.error(str(e))
        return ""


def getApkPackage(apkPath):
    packageName = ""
    activityName = ""
    try:
        cmd = "aapt dump badging %s|grep package" % apkPath
        output = os.popen(cmd).read()
        pat = re.compile("name=\'(.*?)\'")
        res = pat.findall(output)
        if res:
            packageName = res[0]
        cmd = "aapt dump badging %s|grep launchable-activity" % apkPath
        output = os.popen(cmd).read()
        pat = re.compile('name=\'(.*?)\'')
        res = pat.findall(output)
        if res:
            activityName = res[0]
    except Exception as e:
        logging.error(str(e))
    return packageName, activityName


def get_default_input_method(device):
    output = os.popen('adb -s %s shell settings get secure default_input_method' % device).read()
    return output.strip('\n')


def set_default_input_method(device, method):
    os.popen('adb -s %s  shell settings put secure default_input_method %s' % (device, method)).read()


def get_input_method_list(device):
    methods = []
    try:
        output = os.popen('adb -s %s shell ime list -s' % device).read()
        methods = output.strip().split('\n')
    except Exception as e:
        logging.error(str(e))
    return methods


def screen_shot(device, filepath):
    os.popen("adb -s %s shell screencap /sdcard/test.png" % device).read()
    os.popen("adb -s %s pull /sdcard/test.png %s" % (device, filepath)).read()
    os.popen("adb -s %s shell rm /sdcard/test.png" % device).read()


def check_install_app_is_64bit(device, package):
    try:
        out = os.popen('adb -s %s shell \"ps | grep zygote64\"' % device).read()
        outlist = re.split('\\s+', out)
        pid = outlist[1]
        out = os.popen('adb -s %s shell \"ps |grep %s\"' % (device, pid)).read()
        res = re.search(package, out)
        if res is None:
            return False
        return True
    except Exception as e:
        logging.info(e)
        return None

def get_app_list(device):
    cmd = f"adb -s {device} shell pm list package -3"
    outputs = os.popen(cmd).readlines()
    app_list = []
    d = None
    try:
        d = u2.connect(device)
    except Exception as e:
        logging.error(str(e))
    for line in outputs:
        line = line.strip()
        package = line.split(':')[-1]
        if d :
            try:
                appinfo = d.app_info(package)
                package = f"{appinfo['label']} {appinfo['versionName']}#{appinfo['versionCode']}--{package}"
            except Exception as e:
                logging.error(str(e))
        app_list.append(package)
    return app_list

def start_app(device,package):
    try:
        d = u2.connect(device)
        d.app_start(package)
    except Exception as e:
        logging.error(str(e))

if __name__ == "__main__":
    GetPid("", "com.duowan.kiwi")
