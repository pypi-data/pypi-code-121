# -*- coding: utf-8 -*-
import argparse
import datetime
import multiprocessing
import os
import re
import time
import math
import subprocess
from io import StringIO
from threading import Timer
from functools import reduce
from .adbTool import Adb
import logging
import threading

DATA_TITLE = "TimeStamp,app CPU Load(%),Total CPU(%),Memory(MB),Native(MB),Dalvik(MB),totalTraffic(Kb/s),trafficUp,trafficDown,GPU Load [%],Threads,virtual Mem(MB),Activities,FPS,wakeups"
APPEND_MEM_INFO = r"Stack, Ashmen, OtherDev, SoMmap, ApkMmap, TtfMmap, DexMmap, OatMmap, ArtMmap, OtherMmap, GlMtrack, Unknow"
HEAP_PROFILE = True
AndroidVersion = 0
argvmap = {}
ErrorCode = {'Normal': 0, "Not_Exist": 1}


class BaseProfiler(threading.Thread):
    def __init__(self, adb, image=False):
        threading.Thread.__init__(self)
        self.adb = adb
        self.androidversion = self.getAndroidVersion()
        self.image = image
        self.bStop = False

    def stop(self):
        self.bStop = True

    def getAndroidVersion(self):
        output = self.adb.cmd("shell", "getprop", "ro.build.version.sdk").communicate()[0].decode("utf-8").strip()
        if output.isdigit():
            return output
        else:
            return 0


class CpuProfiler(BaseProfiler):
    def __init__(self, pid, adb,outpath):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.processcpuRatioList = []
        self.cpuRatioList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.titile = ["应用占用CPU(%)", "总占用CPU(%)"]
        self.processname = ''
        self.rpid = ''
        self.thread_cpu_filepath = open(outpath.replace('.csv', '_cpu_by_thread.log'), mode="w+")
        self.support_m = self.support_m_param()
        self.appcpu = -1
        self.totalcpu = -1

    def init(self):
        processCpu, retcode = self.getprocessCpuStat()
        idleCpu, totalCpu = self.getTotalCpuStat()
        self.lastRecord["processCpu"] = processCpu if not retcode else 0
        self.lastRecord["idleCpu"] = idleCpu
        self.lastRecord["totalCpu"] = totalCpu
        self.lastTime = datetime.datetime.now()
        self.androidversion = self.getAndroidVersion()

    def setprocessname(self, pname):
        self.processname = pname

    def getprocessname(self):
        return self.processname

    def settpid(self, rpid):
        self.rpid = rpid

    def gettpid(self):
        return self.rpid

    '''
    参考：
    http://blog.sina.com.cn/s/blog_aed19c1f0102wcun.html
    http://www.blogjava.net/fjzag/articles/317773.html
    '''

    def getprocessCpuStat(self):
        if self.gettpid():
            #get threads cpu%
            stringBuffer = self.adb.cmd("shell", "cat", "/proc/" +str(self.appPid) + "/task/" + str(self.gettpid()) + "/stat").communicate()[0].decode(
                "utf-8").strip()
        else:
            stringBuffer = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/stat").communicate()[0].decode(
            "utf-8").strip()
        r = re.compile("\\s+")
        if r'No such file or directory' in stringBuffer:
            logging.warning("process %s Not exist!" % self.appPid)
            return 0, ErrorCode['Not_Exist']
        toks = r.split(stringBuffer)
        if len(toks) > 14:
            processCpu = float(int(toks[13]) + int(toks[14]))
            #print("self.getfpid",self.getfpid(), "toks[13]",toks[13],"toks[14]",toks[14])
        else:
            processCpu = 0
        return processCpu, ErrorCode['Normal']

    def getTotalCpuStat(self):
        child_out = self.adb.cmd("shell", "cat", "/proc/stat").communicate()[0].decode("utf-8").strip().split("\r\r\n")[
            0]
        if int(self.androidversion) >= 19:
            child_out = self.adb.cmd("shell", "cat", "/proc/stat", "|grep ^cpu\ ").communicate()[0].decode(
                "utf-8").strip()
            if " grep: not found" in child_out:
                child_out = \
                    self.adb.cmd("shell", "cat", "/proc/stat").communicate()[0].decode("utf-8").strip().split("\r\r\n")[
                        0]
        r = re.compile(r'(?<!cpu)\d+')
        # cpu user nice system idle iowait irq softirq stealstolen guest
        toks = r.findall(child_out)
        idleCpu = float(toks[3])
        totalCpu = float(reduce(lambda x, y: int(x) + int(y), toks));
        return idleCpu, totalCpu

    def profile(self):
        return self.appcpu,self.totalcpu

    def run(self):
        self.init()
        while self.bStop is False:
            try:
                processCpu, retcode = self.getprocessCpuStat()
                idleCpu, totalCpu = self.getTotalCpuStat()
                currentTime = datetime.datetime.now()
                diffTime = currentTime - self.lastTime

                retry = False
                processcpuRatio = 100 * (processCpu - self.lastRecord["processCpu"]) / (totalCpu - self.lastRecord["totalCpu"])
                cpuRatio = 100 * ((totalCpu - idleCpu) - (self.lastRecord["totalCpu"] - self.lastRecord["idleCpu"])) / (
                        totalCpu - self.lastRecord["totalCpu"])
                # if (diffTime.seconds * 1000 + diffTime.microseconds / 1000) < abs(totalCpu - self.lastRecord["totalCpu"]):
                # 	logging.info("cpu data abnormal, do again!")
                # 	retry = True

                self.lastTime = currentTime
                self.lastRecord["processCpu"] = processCpu
                self.lastRecord["idleCpu"] = idleCpu
                self.lastRecord["totalCpu"] = totalCpu

                try:
                    now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
                    self.thread_cpu_filepath.write("\n\n" + "=" * 40 + "获取时间：%s " % (now_time) + "=" * 40 + "\n")
                    if self.support_m:
                        output = self.adb.cmd("shell", "top","-m","400", "-H", "-n", "1", "-p", str(self.appPid)).communicate(timeout=3)[0].decode("utf-8")
                    else:
                        output = self.adb.cmd("shell", "top", "-H","-n","1","-p", str(self.appPid)).communicate(timeout=3)[0].decode("utf-8")
                    self.thread_cpu_filepath.write(output)
                except Exception as e:
                    logging.error(str(e))
                if self.image:
                    # 保存画图数据
                    self.processcpuRatioList.append(round(float(processcpuRatio), 2))
                    self.cpuRatioList.append(round(float(cpuRatio), 2))
                self.appcpu = round(float(processcpuRatio), 2)
                self.totalcpu = round(float(cpuRatio), 2)
            except Exception as e:
                logging.error(str(e))

    def support_m_param(self):
        try:
            #-m	Maximum number of tasks to show
            output = self.adb.cmd("shell", "top", "--help").communicate(timeout=3)[0].decode("utf-8")
            if "Maximum number of tasks to show" in output:
                return True
            return False
        except:
            return False

class ThreadCount(BaseProfiler):
    def __init__(self, pid, appName, adb,outpath):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.appName = appName
        self.title = ["线程数"]
        self.threadcount = []
        self.thread_filepath = open(outpath.replace('.csv','_thread.log'),mode="w+")
        self.vmsize_filepath = open(outpath.replace('.csv', '_虚拟内存使用信息.log'), mode="w+")
        self.count = 1
        self.thread_cnt = -1
        self.vmsize = -1

    def getThreadCount(self):
        sendCmd = self.adb.cmd("shell", "top", "-d 2 -n 1 ", "|grep %s" % self.appPid).communicate()[0].decode(
            "utf-8").strip()
        if self.appName not in sendCmd:
            return 0
        items = list(filter(lambda x: x != '', sendCmd.split(' ')))
        # Android 7.0 以上top： PID USER     PR  NI CPU% S  #THR     VSS     RSS PCY Name
        # Android 7.0 以下top:  PID PR CPU% S  #THR     VSS     RSS PCY UID      Name
        threadcount = 0
        if items and len(items) > 4:
            if int(self.getAndroidVersion()) < 24:
                threadcount = items[4]
            else:  # 7.0 以上
                threadcount = items[6]
            self.threadcount.append(threadcount)
            return threadcount
        else:
            logging.warning("Error passing thread count with pid %s" % self.appPid)
        return 0

    def getThreadCountByStatus(self):
        return self.thread_cnt,self.vmsize

    def run(self) -> None:
        while self.bStop is False:
            try:
                outputs = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/status", "|grep Threads").communicate()[
                    0].decode("utf-8").strip()
                if outputs:
                    self.thread_cnt = int(outputs.split('\t')[1].strip())
                now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
                self.thread_filepath.write("\n\n" + "=" * 40 + "%s -- 第%d次获取,线程总数为：%d" % (now_time,self.count,self.thread_cnt) + "=" * 40 + "\n")
                output = self.adb.cmd("shell", "ps", "-AT", str(self.appPid)).communicate()[0].decode("utf-8")
                self.thread_filepath.write(output)
                vmsizes = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/status", "|grep VmSize").communicate()[
                    0].decode("utf-8").strip()
                if vmsizes:
                    self.vmsize = float(vmsizes.split('\t')[1].replace("kB","").strip())/1024
                now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
                self.vmsize_filepath.write(
                    "\n\n" + "=" * 40 + "%s -- 第%d次获取,虚拟内存大小为：%d" % (now_time, self.count, self.vmsize) + "=" * 40 + "\n")
                output = self.adb.cmd("shell", "run-as", self.appName,"showmap", str(self.appPid)).communicate()[0].decode("utf-8")
                self.vmsize_filepath.write(output)
                self.count += 1
            except Exception as e:
                logging.error(str(e))

class MemProfiler(BaseProfiler):
    def __init__(self, pid, adb,outpath):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        # self.adb = adb
        self.PSSList = []
        self.NativeHeapList = []
        self.DalvikHeapList = []
        self.ActivityList = []
        # more info
        self.StackList = []
        self.AshmemList = []
        self.OtherDevList = []
        self.SoMmapList = []
        self.ApkMmapList = []
        self.TtfMmapList = []
        self.DexMmapList = []
        self.OatMmapList = []
        self.ArtMmapList = []
        self.OtherMmapList = []
        self.GlMtrackList = []
        self.UnknowList = []

        self.lastRecord = {}
        self.titile = ["总内存(MB)", "NativeHeap(MB)", "DalvikHeap(MB)"]
        self.titleplus = ["Stack", "Ashmen", "OtherDev", "SoMmap", "ApkMmap", "TtfMmap", "DexMmap", "OatMmap",
                          "ArtMmap", "OtherMmap", "GlMtrack", "Unknow"]
        self.meminfo_file = open(outpath.replace('.csv', '_meminfo.log'), mode="w+")
        self.pss = -1
        self.native = -1
        self.dalvik = -1
        self.activity = -1

    def init(self):
        self.androidversion = self.getAndroidVersion()

    def timeout(self, p):
        if p.poll() is None:
            logging.info('appmonitor Error: process taking too long to complete--terminating')
            p.kill()

    def getProcessMem(self):
        if HEAP_PROFILE == False:
            return 0, 0, 0

        cmdProcess = self.adb.cmd("shell", "dumpsys", "meminfo", self.appPid)
        output = ""
        #my_timer = Timer(30, self.timeout, [cmdProcess])
        try:
            #my_timer.start()
            output = cmdProcess.communicate()[0].decode("utf-8").strip()
            self.meminfo_file.write(output)
            self.meminfo_file.flush()
        except ValueError as err:
            logging.info(err.args)
        finally:
            pass
            #my_timer.cancel()

        m = re.search(r'TOTAL\s*(\d+)', output)
        native = r'Native Heap\s*(\d+)'
        dalvik = r'Dalvik Heap\s*(\d+)'
        activities = r' Activities:\s*(\d+)'
        if int(self.androidversion) < 19:
            native = r'Native \s*(\d+)'
            dalvik = r'Dalvik \s*(\d+)'
        m1 = re.search(native, output)
        m2 = re.search(dalvik, output)
        m3 = re.search(activities, output)
        PSS = float(m.group(1)) if m is not None else -1024
        NativeHeap = float(m1.group(1)) if m1 is not None else -1024
        DalvikHeap = float(m2.group(1)) if m2 is not None else -1024
        Activities = float(m3.group(1)) if m3 is not None else -1
        # more info
        stack = r'Stack\s*(\d+)'
        ashmem = r'Ashmem\s*(\d+)'
        other_dev = r'Other dev\s*(\d+)'
        so_mmap = r'\.so mmap\s*(\d+)'
        apk_mmap = r'\.apk mmap\s*(\d+)'
        ttf_mmap = r'\.ttf mmap\s*(\d+)'
        dex_mmap = r'\.dex mmap\s*(\d+)'
        oat_mmap = r'\.oat mmap\s*(\d+)'
        art_mmap = r'\.art mmap\s*(\d+)'
        other_mmap = r'Other mmap\s*(\d+)'
        gl_mtrack = r'GL mtrack\s*(\d+)'
        unknow = r'Unknown\s*(\d+)'
        Stack = float(re.search(stack, output).group(1)) if re.search(stack, output) is not None else -1
        Ashmen = float(re.search(ashmem, output).group(1)) if re.search(ashmem, output) is not None else -1
        OtherDev = float(re.search(other_dev, output).group(1)) if re.search(other_dev, output) is not None else -1
        SoMmap = float(re.search(so_mmap, output).group(1)) if re.search(so_mmap, output) is not None else -1
        ApkMmap = float(re.search(apk_mmap, output).group(1)) if re.search(apk_mmap, output) is not None else -1
        TtfMmap = float(re.search(ttf_mmap, output).group(1)) if re.search(ttf_mmap, output) is not None else -1
        DexMmap = float(re.search(dex_mmap, output).group(1)) if re.search(dex_mmap, output) is not None else -1
        OatMmap = float(re.search(oat_mmap, output).group(1)) if re.search(oat_mmap, output) is not None else -1
        ArtMmap = float(re.search(art_mmap, output).group(1)) if re.search(art_mmap, output) is not None else -1
        OtherMmap = float(re.search(other_mmap, output).group(1)) if re.search(other_mmap, output) is not None else -1
        GlMtrack = float(re.search(gl_mtrack, output).group(1)) if re.search(gl_mtrack, output) is not None else -1
        Unknown = float(re.search(unknow, output).group(1)) if re.search(unknow, output) is not None else -1
        return PSS, NativeHeap, DalvikHeap, Stack, Ashmen, OtherDev, SoMmap, ApkMmap, TtfMmap, DexMmap, OatMmap, ArtMmap, OtherMmap, GlMtrack, Unknown, Activities

    def profile(self):
        return self.pss,self.native,self.dalvik,self.activity

    def run(self):
        self.init()
        while self.bStop is False:
            try:
                PSS, NativeHeap, DalvikHeap, Stack, Ashmen, OtherDev, SoMmap, ApkMmap, TtfMmap, DexMmap, OatMmap, ArtMmap, OtherMmap, GlMtrack, Unknow, Activities = self.getProcessMem()
                if self.image:
                    self.PSSList.append(round(PSS / 1024, 2))
                    self.NativeHeapList.append(round(NativeHeap / 1024, 2))
                    self.DalvikHeapList.append(round(DalvikHeap / 1024, 2))
                    self.ActivityList.append(Activities)
                self.pss = round(PSS / 1024, 2)
                self.native = round(NativeHeap / 1024, 2)
                self.dalvik = round(DalvikHeap / 1024,2)
                self.activity = Activities
            except Exception as e:
                logging.error(str(e))

class FlowProfiler(BaseProfiler):
    def __init__(self, pid, adb):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.adb = adb
        self.flowList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.titile = ["流量(Kb/s)", "上行流量(Kb/s)", "下行流量(Kb/s)"]
        self.total_flow = -1
        self.up_flow = -1
        self.down_flow = -1

    def init(self):
        sendNum, recNum = self.getFlow()
        self.lastRecord["sendNum"] = sendNum
        self.lastRecord["recNum"] = recNum
        self.lastTime = datetime.datetime.now()

    def getFlow(self):
        output = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/net/dev", "|grep wlan0").communicate()[
            0].decode("utf-8").strip()
        m = re.search(r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', output)
        if m:
            recNum = float(m.group(1))
            sendNum = float(m.group(2))
        else:
            logging.info("Couldn't get rx and tx data from: %s!" % output)
            recNum = 0.0
            sendNum = 0.0
        return sendNum, recNum

    def profile(self):
        return self.total_flow,self.up_flow,self.down_flow

    def run(self) -> None:
        self.init()
        while self.bStop is False:
            try:
                sendNum, recNum = self.getFlow()
                currentTime = datetime.datetime.now()
                diffTime = currentTime - self.lastTime

                seconds = diffTime.seconds + float(diffTime.microseconds) / 1000000
                flow = (((sendNum - self.lastRecord["sendNum"]) + (recNum - self.lastRecord["recNum"])) / 1024) / seconds
                flow = round(flow, 2)
                upflow = (sendNum - self.lastRecord["sendNum"]) / 1024 / seconds
                downflow = (recNum - self.lastRecord["recNum"]) / 1024 / seconds
                upflow = round(upflow, 2)
                downflow = round(downflow, 2)

                self.lastTime = currentTime
                self.lastRecord["sendNum"] = sendNum
                self.lastRecord["recNum"] = recNum

                if flow > 0:
                    self.flowList.append(flow)
                self.total_flow = flow
                self.up_flow = upflow
                self.down_flow = downflow
            except Exception as e:
                logging.error(str(e))

class GpuProfiler(BaseProfiler):
    gpuReachable = True

    def __init__(self, pid, adb):
        BaseProfiler.__init__(self, adb)
        self.bStop = False
        self.appPid = pid
        self.adb = adb
        self.titile = ["GPU(%)"]
        self.gpu = -1

    def stop(self):
        self.bStop = True

    def getGpuInfo(self):
        return self.gpu

    def run(self) -> None:
        while self.bStop is False:
            try:
                # cmd = "adb -s %s shell cat /sys/class/kgsl/kgsl-3d0/gpubusy" % self.adb.device_serial()
                # pipe = os.popen(cmd)
                # text = pipe.read()
                # sts = pipe.close()
                # if sts is None: sts = 0
                self.gpu = -1
                if not self.gpuReachable:
                    return
                text = self.adb.cmd("shell", "cat", "/sys/class/kgsl/kgsl-3d0/gpubusy").communicate()[0].decode("utf-8").strip()
                # 某些手机没有权限,如三星s7edge金色
                if text == '':
                    # 进一步确认
                    status, output = subprocess.getstatusoutput(
                        'adb -s %s shell cat /sys/class/kgsl/kgsl-3d0/gpubusy' % self.adb.device_serial())
                    if status == 256:
                        self.gpuReachable = False
                        return
                if text[-1:] == '\n':  text = text[:-1]
                if "No such file or directory" in text or "Permission denied" in text:
                    self.gpuReachable = False
                    return
                # return sts, text
                m = re.search(r'\s*(\d+)\s*(\d+)', text)
                if m:
                    utilization_arg_1 = m.group(1)
                    utilization_arg_2 = m.group(2)
                else:
                    # print("Couldn't get utilization data from: %s!" % text)
                    self.gpuReachable = False
                    return
                if float(utilization_arg_2) != 0:
                    self.gpu = str(round((float(utilization_arg_1) / float(utilization_arg_2)) * 100, 2))
            except Exception as e:
                logging.error(str(e))

class FpsProfiler(BaseProfiler):

    def __init__(self, pid, adb):
        super(FpsProfiler, self).__init__(adb)
        self.appPid = pid
        self.titile = ["FPS"]
        self.is_first = True
        self.last_frames = 0
        self.last_realtime = 0
        self.fps = -1
        flag = -1
        if self.getAndroidVersion() == 23:
            flag = self.get_fps_info_surfaceview()
        if flag != -1:
            self.get_method = self.get_fps_info_surfaceview
            logging.info("Android6.0，使用get_fps_info_surfaceview获取fps")
        else:
            flag = self.get_fps_info_histogram()
            if flag == -1:
                logging.info("get_fps_info_histogram数据匹配失败，使用get_fps_info_framestats获取fps")
                self.get_method = self.get_fps_info_framestats
            else:
                logging.info("使用get_fps_info_histogram获取fps")
                self.get_method = self.get_fps_info_histogram

    def get_fps_info(self):
        """
        使用gfxinfo 的 (total_frames_rendered差值 / realtime差值) 进行统计
        当在静止页面停留时间越长，fps越不准确
        """
        # 获取对应包的gfxinfo
        if self.is_first:
            cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid)
            output = cmd_process.communicate()[0].decode("utf-8").strip()
            result = re.findall(r'Realtime: (\d*)|Total frames rendered: (\d*)', output)
            self.last_realtime = int(result[0][0])
            self.last_frames = int(result[1][1])
            self.is_first = False
        cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid)
        output = cmd_process.communicate()[0].decode("utf-8").strip()
        result = re.findall(r'Realtime: (\d*)|Total frames rendered: (\d*)', output)
        # 帧率 = 相差帧数/时间间隔
        realtime1 = int(result[0][0])
        frames1 = int(result[1][1])
        frames = frames1 - self.last_frames
        times = realtime1 - self.last_realtime
        self.last_frames, self.last_realtime = frames1, realtime1
        fps = round(frames / (times / 1000), 2)
        # print('frames: %.2f' % (frames))
        # print('times: %.2f' % (times))
        # print('FPS: %.2f' % (self.fps))
        # print('----')
        return fps

    def get_fps_info_framestats(self):
        """
        使用gfxinfo 的 framestats 进行统计
        获取帧的渲染时间来计算fps： count(frames) / (sum(FrameCompleted) - sum(IntendedVsync))

        实测荣耀10只打印了最近10帧的信息，但小米note3能打印120帧
        """
        frames = 0
        frames_time = 0.0
        # 拿到framestats中的所有有帧统计的activity的帧时间
        cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid, "framestats")
        output = cmd_process.communicate()[0].decode("utf-8").strip()
        results = re.findall(r'---PROFILEDATA---([\w\s,]*)-?', output)
        # 清空已获取的帧信息
        cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid, "reset")
        _ = cmd_process.communicate()[0].decode("utf-8").strip()
        for result in results:
            result = result.strip()
            result_lines = result.split("\n")
            if len(result_lines) > 1:
                for line in result_lines[1:]:
                    values = line.strip().split(",")
                    if values[0] == "0":
                        frames += 1
                        frames_time += round((int(values[13]) - int(values[1])) / 1000000000, 5)  # 纳秒 -> 秒
            else:
                continue
        if frames_time:
            fps = round(frames / frames_time, 2)
        else:
            fps = frames
        # print('frames: %.2f'%(frames))
        # print('times: %.5f'%(frames_time))
        # print('FPS: %.2f'%(fps))
        # print('----')
        return fps

    def get_fps_info_histogram(self):
        """
        使用gfxinfo 的 HISTOGRAM 进行统计: <=16.67ms的记为normal_frame，>的计算同步时间

        fps = int(normal_frame * 60 / (normal_frame + vsync_overtime))
        """
        cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid)
        output = cmd_process.communicate()[0].decode("utf-8").strip()
        cmd_process = self.adb.cmd("shell", "dumpsys", "gfxinfo", self.appPid, "reset")
        _ = cmd_process.communicate()[0].decode("utf-8").strip()

        m = re.search(r'HISTOGRAM:(.*)', output)
        if m is None:
            return -1
        items = m.group(1)
        frames = {}
        for item in items.strip().split():
            cost, count = item.strip().split('=')
            if int(count) > 0:
                frames[int(cost[:-2])] = int(count)

        if not frames:
            return -1

        renderd_frames = sum(count for _, count in frames.items())

        def jank(cost, count) -> int:
            if cost <= 16.67:
                return 0
            else:
                return count * int(math.ceil(cost / 16.67)) - 1

        jank_frames = sum(jank(float(cost), count) for cost, count in frames.items())
        fps = int(60 * renderd_frames / (renderd_frames + jank_frames))
        # print(f"rendered: {renderd_frames}")
        # print(f"jank: {jank_frames}")
        # print(f'fps: {int(60 * renderd_frames / (renderd_frames + jank_frames))}')
        return fps

    def get_fps_info_surfaceview(self):
        # 获取Fps 通过SurfaceFlinger方式（Android8.0以上不支持）

        """
        命令: adb shell dumpsys SurfaceFlinger --latency  LayerName
        这个命令能获取游戏/视频应用的fps数据
        其中LayerName在各个不同系统中获取的命令是不一样的
        在Android 6系统直接就是SurfaceView
        在Android 7系统中可以通过 dumpsys window windows | grep mSurface | grep SurfaceView 然后通过数据截取到
        在Android 8系统中可以通过 dumpsys SurfaceFlinger | grep android包名获取到

        :return:
        """
        cmd_process = self.adb.cmd("shell", "dumpsys", "SurfaceFlinger", "--latency", "SurfaceView")
        context = cmd_process.communicate()
        fpsinfo = context[0].decode("utf-8").strip().split("\r\n")

        if len(fpsinfo) > 128:
            fpsinfo = fpsinfo[:128]

        # print(fpsinfo)

        times = []
        try:
            for line in fpsinfo:
                flist = line.split()
                if len(flist) == 0:
                    continue
                times.append(flist)
            start_time = int(times[-122][0])
            end_time = int(times[-2][0])
            # print(start_time)
            # print(end_time)
            fps = 127 / ((end_time - start_time) / 1000000000.0)
            return round(fps, 2)
        except:
            return -1

    def profile(self):
        return self.fps

    def run(self) -> None:
        while self.bStop is False:
            try:
                self.fps = self.get_method()
            except Exception as e:
                logging.error(str(e))

class AppTrafficProfiler(BaseProfiler):
    def __init__(self, pid, adb):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.adb = adb
        self.flowList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.uid = 0
        # iface：网络性质［wlan0－wifi流量 lo－本地流量 rmnet0－4g/3g/2g流量 ...］
        self.networktype = 'wlan0'
        self.titile = ["流量(Kb/s)", "上行流量(Kb/s)", "下行流量(Kb/s)"]
        self.defaultMethod = True
        self.total_flow = -1
        self.up_flow = -1
        self.down_flow = -1

    def init(self):
        self.uid = self.getuid()
        self.lastRecord["recNum"], self.lastRecord["sendNum"] = self.getTrafficData()
        self.lastTime = datetime.datetime.now()

    def getuid(self):
        uid = 0
        uids = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/status", "|grep Uid").communicate()[
            0].decode("utf-8").strip()
        if uids:
            uid = uids.split('\t')[1]
        return uid

    def getFlow(self):
        output = self.adb.cmd("shell", "cat", "/proc/" + str(self.appPid) + "/net/dev",
                              "|grep {0}".format(self.networktype)).communicate()[0].decode("utf-8").strip()
        m = re.search(r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', output)
        if m:
            recNum = float(m.group(1))
            sendNum = float(m.group(2))
        else:
            logging.info("Couldn't get rx and tx data from: %s!" % output)
            recNum = 0.0
            sendNum = 0.0
        return recNum, sendNum

    # http://www.voidcn.com/article/p-tolukrhb-vz.html
    # http://www.dreamingfish123.info/?p=1154
    def getTrafficData(self):
        if not self.uid:
            return 0, 0
        # /proc/net/xt_qtaguid/stats各列代表意义
        # idx iface acct_tag_hex uid_tag_int cnt_set rx_bytes rx_packets tx_bytes tx_packets
        # rx_tcp_bytes rx_tcp_packets rx_udp_bytes rx_udp_packets rx_other_bytes rx_other_packets
        # tx_tcp_bytes tx_tcp_packets tx_udp_bytes tx_udp_packets tx_other_bytes tx_other_packets
        # iface：网络性质［wlan0－wifi流量 lo－本地流量 rmnet0－3g/2g流量 ...］
        if self.defaultMethod:
            output = self.adb.cmd("shell", "cat", "/proc/net/xt_qtaguid/stats", "|grep {0}".format(str(self.uid)),
                                  "|grep {0}".format(self.networktype)).communicate()[0].decode("utf-8").strip()
            rx_list = []
            tx_list = []
            totalrx = 0.0
            totaltx = 0.0
            if output:
                lines = output.splitlines()
                validlines = filter(lambda x: len(x) > 1, lines)
                for item in validlines:
                    # 前后台流量都算上
                    if len(item.strip().split()) < 8:  # 保证第6／8项存在
                        logging.warning(
                            r'wrong format in data: split len=' + str(len(item.split())) + r'content: ' + str(item))
                        continue
                    rx_bytes = item.split()[5]
                    tx_bytes = item.split()[7]
                    rx_list.append(int(rx_bytes))
                    tx_list.append(int(tx_bytes))
                totalrx = float(sum(rx_list))
                totaltx = float(sum(tx_list))
            else:
                # 无效或没有使用网络
                logging.warning(
                    "Couldn't get rx and tx data from: /proc/net/xt_qtaguid/stats! maybe this uid doesnot connetc to net")
                self.defaultMethod = False
                return self.getFlow()
            return totalrx, totaltx
        else:
            return self.getFlow()

    def profile(self):
        return self.total_flow, self.up_flow, self.down_flow

    def run(self) -> None:
        self.init()
        while self.bStop is False:
            try:
                recNum, sendNum = self.getTrafficData()
                currentTime = datetime.datetime.now()
                diffTime = currentTime - self.lastTime

                seconds = diffTime.seconds + float(diffTime.microseconds) / 1000000
                upflow = (sendNum - self.lastRecord["sendNum"]) / 1024 / seconds
                downflow = (recNum - self.lastRecord["recNum"]) / 1024 / seconds
                upflow = round(upflow, 2) if sendNum > 0 else -0.0
                downflow = round(downflow, 2) if recNum > 0 else -0.0
                flow = round(upflow + downflow, 2)

                self.lastTime = currentTime
                self.lastRecord["sendNum"] = sendNum
                self.lastRecord["recNum"] = recNum

                if self.image and flow > 0:
                    self.flowList.append(flow)
                self.total_flow = flow
                self.up_flow = upflow
                self.down_flow = downflow
            except Exception as e:
                logging.error(str(e))

class WakeupsProfiler(BaseProfiler):
    def __init__(self, appName, adb,outpath):
        BaseProfiler.__init__(self, adb)
        self.appName = appName
        self.alarm_filepath = open(outpath.replace('.csv','_dumpsys_alarm.log'),mode="w+")
        self.count = 1
        self.wakeups = 0

    def getWakeups(self):
        return self.wakeups

    def run(self) -> None:
        while self.bStop is False:
            try:
                outputs = self.adb.cmd("shell", "dumpsys", "alarm").communicate()[0].decode("utf-8").strip()
                if outputs:
                    match_str = '%s.*running,\s*(\d+)\s*wakeups:' % (self.appName)
                    mat = re.search(match_str,outputs)
                    if mat:
                        self.wakeups = int(mat.group(1))
                now_time = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time()))
                self.alarm_filepath.write("\n\n" + "=" * 40 + "%s -- 第%d次获取,wakeups总数为：%d" % (now_time,self.count,self.wakeups) + "=" * 40 + "\n")
                self.alarm_filepath.write(outputs)
                self.count += 1
            except Exception as e:
                logging.error(str(e))

class app_monitor(threading.Thread):
    timeout_in_seconds = 120

    def __init__(self, period, fileName, appName, serial=None, image=False, duration=0):
        threading.Thread.__init__(self)
        #multiprocessing.Process.__init__(self)
        self.adb = Adb(serial=serial)
        self.appPid = 0
        self.appName = appName
        self.period = period
        self.fileName = fileName
        self.pigName = fileName + ".png"
        # self.getappPid()
        self.running = True
        self.lastRecord = {}
        self.image = image
        self.duration = duration
        self.processes = ''
        self.getMemDetails = False

    # self.is_alive = False
    def setProcess(self, processlist):
        if processlist:
            self.processes = processlist

    def setMemDetails(self, toOpen=False):
        if toOpen:
            self.getMemDetails = toOpen

    def stop(self):
        self.running = False

    def getAppPid(self, pname=''):
        if not pname:
            # outputs = self.adb.cmd("shell", "top", "-n", "1").communicate()[0].decode("utf-8").strip()
            # print("shabi--->%s" % self.appName[:14])
            # #18657 u0_a164       6 -14 2.4G 361M 162M R  7.3   6.3   1:09.12 com.duowan.mobi+
            # # 这个正则有问题，可能匹配到后半部分1:09.12 com.duowan.mobi+，此时拿到的pid=1
            # r = "(\\d+).*\\s+%s[^:]" % self.appName[:14]
            # m = re.search(r, outputs)
            # # print(outputs)
            # if m:
            #     return m.group(1)
            # else:
            cmd = "adb -s %s shell \"ps -ef|grep %s\""%(self.adb.device_serial(),self.appName+ "$")
            outputs = os.popen(cmd).read()
            logging.info('outputs==='+outputs)
            #outputs,ret = self.adb.cmd("shell", "ps", "-ef", "|grep", self.appName + "$").communicate()
            pattern = r'^\w+\s+(\d+)\s+.*\s+%s$' % self.appName.strip()
            m = re.search(pattern, outputs.strip())
            if m:
                return m.group(1)
            else:
                logging.info("app still not get up")
        #else:
        # TODO: may be different between models/android-versions
        # USER     PID   PPID  VSIZE  RSS     WCHAN    PC        NAME
        cmd = "adb -s %s shell \"ps |grep %s\"" % (self.adb.device_serial(), self.appName + "$")
        outputs = os.popen(cmd).read()
        logging.info('outputs==='+ outputs)
        pattern = r'^\w+\s+(\d+)\s+.*\s+%s' % pname.strip()
        m = re.search(pattern, outputs)
        if m:
            return m.group(1)
        else:
            logging.info("No process named %s found!" % pname)
            return 0

    def getThreadPid(self, threadname):
        #return process,thread
        outputs = self.adb.cmd("shell", "top", "-t -n 1", "|grep ", self.appName, "|grep",
                         "\'" + threadname +"\'").communicate()[
                0].decode("utf-8").strip()
        r = "(\\d+)\s(\d+).*"
        m = re.search(r, outputs)
        if m:
            print(threadname, m.group(2))
            return m.group(2)
        else:
            outputs = self.adb.cmd('shell', 'ls', '/proc/{0}/task'.format(self.appPid)).communicate()[0].decode("utf-8").strip()
            tasks = outputs.split('\n')
            taskpid = 0
            for task in tasks:
                task.strip()
                cmd = 'cat /proc/{0}/task/{1}/stat'.format(self.appPid, task)
                taskoutput = self.adb.cmd('shell', cmd).communicate()[0].decode(
                    "utf-8").strip()
                r = "(\\d+)\s\({0}\)\s.*".format(threadname)
                m = re.search(r, taskoutput)
                if m:
                    taskpid = m.group(1)
                    print(threadname, taskpid)
                    break
            return taskpid

    def waitForAppReady(self):
        start_time = int(time.time())
        while self.appPid == 0:
            elapsed = int(time.time()) - start_time
            # 做完一部分任务后,判断是否超时
            if elapsed >= app_monitor.timeout_in_seconds:
                logging.info("获取app pid超时，退出")
                self.running = False
                break

            logging.info("appPid == 0")
            self.appPid = self.getAppPid()

        logging.info("appPid == %s"%str(self.appPid))

    def pic(self, processcpuRatioList, cpuRatioList, PSSList, NativeHeapList, DalvikHeapList, flowList):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mtick
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        # 设置右侧Y轴显示百分数
        fmt = '%.2f%%'
        yticks = mtick.FormatStrFormatter(fmt)

        def minY(listData):
            return round(min(listData) * 0.8, 2)

        def maxY(listData):
            return round(max(listData) * 1.2, 2)

        def drawSubplot(pos, x, y, xlabels, ylabels):
            plt.subplot(pos)
            plt.plot(x, y, label=ylabels)
            plt.xlabel(xlabels)
            plt.ylabel(ylabels)
            plt.ylim(minY(y), maxY(y))
            # plt.title(u'应用CPU')
            plt.legend()

        plt.figure(figsize=(20, 10))
        import platform
        systemtype = platform.system()
        winFlag = False
        if 'Darwin' in systemtype or 'Linux' in systemtype:
            xcoordinate = 'time(s)'
        elif 'Windows' in systemtype:
            xcoordinate = u'时间(秒)'
            winFlag = True
        else:
            # 默认
            xcoordinate = 'time(s)'

        timeList = [x * 2 for x in range(len(processcpuRatioList))]
        drawSubplot(321, timeList, processcpuRatioList, xcoordinate, u'应用CPU(%)' if winFlag else 'app-cpu(%)')
        plt.gca().yaxis.set_major_formatter(yticks)

        timeList = [x * 2 for x in range(len(cpuRatioList))]
        drawSubplot(322, timeList, cpuRatioList, xcoordinate, u"总cpu(%)" if winFlag else 'cpu(%)')
        plt.gca().yaxis.set_major_formatter(yticks)

        timeList = [x * 2 for x in range(len(PSSList))]
        drawSubplot(323, timeList, PSSList, xcoordinate, u"总内存(MB)" if winFlag else 'PSS(M)')

        timeList = [x * 2 for x in range(len(NativeHeapList))]
        drawSubplot(324, timeList, NativeHeapList, xcoordinate, u"Native内存(MB)" if winFlag else 'Native(M)')

        timeList = [x * 2 for x in range(len(DalvikHeapList))]
        drawSubplot(325, timeList, DalvikHeapList, xcoordinate, u"Dalvik内存(MB)" if winFlag else 'Dalvik(M)')

        timeList = [x * 2 for x in range(len(flowList))]
        drawSubplot(326, timeList, flowList, xcoordinate, u"流量(kb/s)" if winFlag else 'Traffic(Kbps)')

        # plt.gca().yaxis.set_minor_formatter(yticks)
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.55, wspace=0.25)

        # plt.show()
        print(self.pigName)
        plt.savefig(self.pigName)

    def run(self):
        # 根据应用的包名称 获取CPU以及内存占用
        #logging.info("app_monitor run")
        # self.is_alive = True

        # 等待获取到被监控app的pid后才开始采集数据
        #logging.info("waitForAppReady begin")
        self.waitForAppReady()
        #logging.info("Tracing pid = %s"%str(self.appPid))
        #logging.info("waitForAppReady end")

        profile_list = []
        #flowProfile = FlowProfiler(self.appPid, self.adb)
        #flowProfile.setDaemon(True)
        # flowProfile.start()
        cpuProfile = CpuProfiler(self.appPid, self.adb,self.fileName)
        profile_list.append(cpuProfile)
        memProfile = MemProfiler(self.appPid, self.adb,self.fileName)
        profile_list.append(memProfile)
        gpuProfile = GpuProfiler(self.appPid, self.adb)
        profile_list.append(gpuProfile)
        threadcountProfile = ThreadCount(self.appPid, self.appName, self.adb,self.fileName)
        profile_list.append(threadcountProfile)
        fps_profile = FpsProfiler(self.appPid, self.adb)
        profile_list.append(fps_profile)
        wakeups_profile = WakeupsProfiler(self.appName,self.adb,self.fileName)
        profile_list.append(wakeups_profile)
        trafficProfile = AppTrafficProfiler(self.appPid, self.adb)
        profile_list.append(trafficProfile)
        for profile in profile_list:
            profile.setDaemon(True)
            profile.start()

        # 附加进程
        plist = []
        appendprocesses = ','
        if self.processes:
            for processname in self.processes.split(','):
                processname = processname.strip()

                if processname:
                    appendprocesses += processname + ","
                    if isinstance(processname, int):
                        tpid = int(processname)
                    else:
                        tpid = self.getThreadPid(str(processname))
                    proc = CpuProfiler(self.appPid, self.adb,self.fileName)
                    proc.setprocessname(processname)
                    proc.settpid(tpid)
                    proc.init()
                    plist.append(proc)

        f = open(self.fileName, "w+", encoding='utf-8')
        #f.write('\xEF\xBB\xBF')
        title = DATA_TITLE
        if len(self.processes) > 0:
            title += appendprocesses
        if self.getMemDetails:
            title += APPEND_MEM_INFO
        title += "\n"
        f.write(title)

        firstRun = True
        errorTimes = 0
        #print(DATA_TITLE.replace(",", "     "))
        starttime = datetime.datetime.now()
        pre_data = {}
        while self.running:
            try:
                nowtime = datetime.datetime.now()
                if self.duration != 0 and ((nowtime - starttime).total_seconds() - self.period - 1) >= self.duration:
                    self.running = False
                    break
                str_now_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))
                processcpuRatio, cpuRatio = cpuProfile.profile()
                if float(processcpuRatio)<0:
                    continue
                PSS, NativeHeap, DalvikHeap, Activities = memProfile.profile()
                if float(PSS)<0:
                    continue
                # flow, upflow, downflow = flowProfile.profile()
                flow, upflow, downflow = trafficProfile.profile()
                gpu = gpuProfile.getGpuInfo()
                fps = fps_profile.profile()
                wakeups = wakeups_profile.getWakeups()
                threadcount,vmsize = threadcountProfile.getThreadCountByStatus()
                datalist = {'appcpu':processcpuRatio,'totalcpu':cpuRatio,'PSS':PSS,'NativeHeap':NativeHeap,'DalvikHeap':DalvikHeap,
                            'Activities':Activities,'flow':flow, 'upflow':upflow, 'downflow':downflow,
                            'gpu':gpu,'fps':fps,'threadcount':threadcount,'vmsize':vmsize,'wakeups':wakeups}
                for key,value in datalist.items():
                    #获取数据异常时，使用前一次获取的数据
                    if (float(value)<0 or (key in ['upflow','downflow','flow'] and value>100000)) and key in list(pre_data.keys()):
                        datalist[key] = pre_data[key]
                    else:
                        pre_data[key] = value
                write_str = "%s,%5s,%5s,%6s,%6s,%6s,%6s,%6s,%6s,%5s,%5s,%.2f,%5s,%.2f,%s" % (
                    str(str_now_time), str(datalist['appcpu']), str(datalist['totalcpu']), str(datalist['PSS']), str(datalist['NativeHeap']),
                    str(datalist['DalvikHeap']),str(datalist['flow']), str(datalist['upflow']), str(datalist['downflow']),
                    str(datalist['gpu']), str(datalist['threadcount']), datalist['vmsize'], str(datalist['Activities']),
                    datalist['fps'],str(datalist['wakeups']))
                # 将数据写入文件
                #print(write_str)
                f.write(write_str + "\n")
                f.flush()

            except Exception as e:
                errorTimes += 1
                if (errorTimes > 5):  # 本来想尝试通过看app是否还在来判断，但是发现用例结束后，app仍然在后台运行
                    logging.info("monitor app end or process exception: %s" % e)
                    break
                else:
                    logging.info("monitor app get data failed: %s" % e)
                    pid = self.getAppPid()
                    if pid==0 or pid!=self.appPid:
                        logging.info("maybe the app is crash or is restart")
                    self.waitForAppReady()
                    continue
            # 中低端机型采集数据命令需要约3秒，高端机型如P9／小米6等采集命令时间较短
            collectiontime = (datetime.datetime.now() - nowtime).total_seconds()
            if float(self.period) > float(collectiontime):
                time.sleep(float(self.period - collectiontime))

        for profile in profile_list:
            profile.stop()

        f.close()

        # if self.image:
        #     print(u"开始绘图了")
        #     self.pic(cpuProfile.processcpuRatioList, cpuProfile.cpuRatioList, memProfile.PSSList,
        #              memProfile.NativeHeapList, memProfile.DalvikHeapList, trafficProfile.flowList)
        #     print(u"绘图结束了")

        # self.running = False

def start_performance(output_without_ext, device_id, package, time=2, duration=0, image=False):
    logtimename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    argvmap['timeIntervalSec'] = time
    argvmap['result'] = output_without_ext
    argvmap['package'] = package
    argvmap['serial'] = device_id
    argvmap['image'] = image
    argvmap['duration'] = duration

    # for key in argvmap.keys():
    #     print(key, ': ', argvmap[key])
    # print('')

    # period, fileName, appName, loghd, serial，
    appMonitor = app_monitor(argvmap['timeIntervalSec'], argvmap['result'], argvmap['package'],
                            argvmap['serial'], argvmap['image'], argvmap['duration'])
    # performance.setDaemon(True)
    appMonitor.start()
    return appMonitor

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help=u'verbose')
    parser.add_argument('-t', '--time', type=int, default=2, help=u'interval time in second. 时间间隔（秒）')
    parser.add_argument('-d', '--duration', type=int, default=0, help=u'duration in second. 持续时间（秒）')
    parser.add_argument('-s', '--device', help=u'target device serial. 设备ID')
    parser.add_argument('-f', '--file', help=u'the path to store the result file, no ext. 结果存放文件,不带扩展名')
    parser.add_argument('-p', '--package', default="com.duowan.mobile", help=u'target app package name. 包名')
    parser.add_argument('-i', '--image', default=False, help=u'to draw results or not. 是否画图，默认不画: True/False或1/0')
    parser.add_argument('-ap', '--append_process', type=str, help=u'vice processes cpu usage. 次进程cpu使用率, '
                                                                  u'多个进程请用在引号内以逗号分开')
    parser.add_argument('-m', '--meminfo', action="store_true", help=u'print(more memory info. 打印更多内存信息')
    args = parser.parse_args()

    if args.verbose:
        parser.print_help()
        exit(0)
    adbInstance = Adb()
    if not adbInstance:
        raise RuntimeError
    devicedict = adbInstance.devices()
    if len(devicedict.keys()) == 0:
        print(u'没有发现设备')
        raise RuntimeError
    deviceid = list(devicedict.keys())[0]
    if (len(devicedict.keys()) > 1) and not args.device:
        print('multiple devices attached but no one is specified.')
        index = 0
        devicelist = []
        for key in devicedict.keys():
            info = r"%d : %s, %s" % (int(index), key, devicedict[key])
            devicelist.append(key)
            index += 1
            print(info)
        choice = int(input(u'Please input index of devices above to monitor(return to set the first one):'))
        deviceid = devicelist[choice] if (choice < len(devicelist)) else devicelist[0]

    # 默认值
    logtimename = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    argvmap['timeIntervalSec'] = args.time
    argvmap['result'] = os.path.abspath(args.file) if args.file \
        else os.path.join(os.getcwd(), 'log', logtimename)
    argvmap['package'] = args.package
    argvmap['serial'] = args.device if args.device else deviceid
    argvmap['image'] = args.image
    argvmap['duration'] = args.duration

    devicename = argvmap['serial']
    if argvmap['serial'] and not args.file:
        devicename = str(adbInstance.devices()[argvmap['serial']])
        argvmap['result'] += ('_' + devicename)

    for key in argvmap.keys():
        if key == 'serial':
            print('device', ': ', devicedict[argvmap[key]])
        else:
            print(key, ': ', argvmap[key])

    # period, fileName, appName, loghd, serial，
    appMonitor = app_monitor(argvmap['timeIntervalSec'], argvmap['result'], argvmap['package'],
                             argvmap['serial'], argvmap['image'],argvmap['duration'])
    if args.append_process:
        appMonitor.setProcess(args.append_process)
    if args.meminfo:
        appMonitor.setMemDetails(True)
    appMonitor.start()
    appMonitor.join()

    # appMonitor = app_monitor(1, "./111_test", "com.duowan.mobile",
    #                          "84cad46c", True, 900)
    # appMonitor = app_monitor(1, "./111_test", "com.ycloud.squareplayer",
    #                          "84cad46c", True, 900)
    # appMonitor.waitForAppReady()
    # fps_profile = FpsProfiler(appMonitor.appPid, appMonitor.adb)
    # for i in range(100):
    #     # print(fps_profile.get_fps_info_histogram())
    #     # print(fps_profile.get_fps_info())
    #     # print(fps_profile.get_fps_info_framestats())
    #     print(fps_profile.get_fps_info_surfaceview())
    #     print("\n")
    #     time.sleep(1)
