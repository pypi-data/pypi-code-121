import argparse
import os
import time

import threading

import logging

from ios_device import py_ios_device
from ios_device.py_ios_device import PyiOSDevice
logging = logging.getLogger("yyperf")

app_cpu = -1
total_cpu = -1
memory = -1
native = -1
dalvik = -1
gpu = -1
threads = -1
virtual_memory = -1
fps = -1
activities = -1
media_cpu = -1
wakeups = -1
pre_wakeups = -1

perf_file_name = None
fps_file_handler = None
gpu_file_handler = None
memory_file_handler = None

process_attr = None
pid = -1
media_pid = -1
cpuCount = 4

GET_TIME_OUT = 10
gpu_get_time = fps_get_time = system_get_time = -1

class app_monitor(threading.Thread):
    DATA_TITLE = "TimeStamp,app CPU Load(%),Total CPU(%),Memory(MB),Native(MB),Dalvik(MB)," \
                 "totalTraffic(Kb/s),trafficUp,trafficDown,GPU Load [%],Threads,virtual Mem(MB),Activities,FPS,mediasvrd CPU(%),wakeups"
    def __init__(self,device_id,bundle_id,process,timeout=30,filename=None,interval=1):
        threading.Thread.__init__(self)
        self.device_id = device_id
        self.bundle_id = bundle_id
        self.process_name = process
        self.file_name = filename
        self.timeout = timeout
        self.interval = interval
        self.bstop = False
        self.pid = -1
        self.total_traffic = -1
        self.traffic_up = -1
        self.traffic_down = -1
        self.ios_version = 14

    def get_pid_cmd(self):
        try:
            cmd = f"tidevice -u {self.device_id} ps |grep {self.bundle_id}"
            outstr = os.popen(cmd).read().strip('\n').strip()
            pid = int(outstr.split(' ')[0])
            return pid
        except Exception as e:
            logging.info(str(e))
            return -1

    def get_pid(self, process_name, retry=2):
        try:
            if retry < 0:
                return self.get_pid_cmd()
            process_list = py_ios_device.get_processes(device_id=self.device_id)
            process_list = list(filter(lambda pro: pro['name'] == process_name, process_list))
            if len(process_list) > 1:
                logging.info(f"获取到{len(process_list)}个进程名为{process_name}的进程")
                for process in process_list:
                    if 'foregroundRunning' in process and process['foregroundRunning']:
                        return process['pid']
            elif len(process_list) == 1:
                return process_list[0]['pid']
            time.sleep(1)
            return self.get_pid(process_name, retry=retry - 1)
        except Exception as e:
            logging.info(str(e))
            time.sleep(1)
            return self.get_pid(process_name, retry=retry - 1)

    def get_traffic(self):
        pre_total_traffic = -1
        pre_traffic_up = -1
        pre_traffic_down = -1
        pre_total = 0
        pre_up = 0
        pre_down = 0
        pre_time = time.time()
        fail_count = 0
        traffic_channel = PyiOSDevice(device_id=self.device_id)
        while self.bstop is False and self.timeout>0:
            try:
                data = traffic_channel.get_netstat(self.pid)
                cur_time = time.time()
                if self.pid in data:
                    traffic_info = data[self.pid]
                    cur_total_traffic = traffic_info['net.bytes']
                    cur_traffic_up = traffic_info['net.tx.bytes']
                    cur_traffic_down = traffic_info['net.rx.bytes']
                    diff = cur_time-pre_time
                    if pre_total_traffic != -1:
                        self.total_traffic = (cur_total_traffic - pre_total_traffic) / diff / 1024.0
                        self.traffic_up = (cur_traffic_up - pre_traffic_up) / diff / 1024.0
                        self.traffic_down = (cur_traffic_down - pre_traffic_down) / diff / 1024.0
                    pre_total_traffic = cur_total_traffic
                    pre_traffic_up = cur_traffic_up
                    pre_traffic_down = cur_traffic_down
                else:
                    fail_count += 1
                    self.total_traffic = pre_total
                    self.traffic_up = pre_up
                    self.traffic_down = pre_down
                if self.total_traffic<0 or self.traffic_down<0 or self.traffic_up<0 or self.traffic_up>100000 or self.traffic_down>100000:
                    #流量数据为负数时，取上一次的数据
                    self.total_traffic = pre_total
                    self.traffic_up = pre_up
                    self.traffic_down = pre_down
                pre_time = cur_time
                pre_total = self.total_traffic
                pre_up = self.traffic_up
                pre_down = self.traffic_down
                time.sleep(self.interval)
                if fail_count>5:
                    logging.info("超过5次获取失败，重启流量数据获取服务")
                    try:
                        traffic_channel.stop()
                    except Exception as e:
                        logging.info(str(e))
                    traffic_channel = PyiOSDevice(device_id=self.device_id)
                    fail_count = 0
            except Exception as e:
                logging.error(str(e))
                try:
                    traffic_channel.stop()
                except Exception as e:
                    logging.info(str(e))
                traffic_channel = PyiOSDevice(device_id=self.device_id)
        traffic_channel.stop()

    def get_gpu(self):
        global gpu_get_time
        def gpu_callback(res):
            try:
                global gpu_file_handler, gpu,fps, perf_file_name,gpu_get_time
                gpu_get_time = time.time()
                if gpu_file_handler is None and perf_file_name:
                    gpu_file_handler = open(perf_file_name.replace('.csv', "_gpu_detail.csv"), mode='w+',
                                            encoding='utf-8')
                    gpu_file_handler.write(",".join(res['header'].keys()) + "\n")
                gpu = res['header']['Device Utilization %']
                fps = res['header']['CoreAnimationFramesPerSecond']
                data = ",".join([str(v) for v in res['header'].values()]) + "\n"
                gpu_file_handler.write(data)
                gpu_file_handler.flush()
            except Exception as e:
                logging.error(str(e))
        count = 0
        while count < 5:
            try:
                channel = py_ios_device.start_get_gpu(device_id=self.device_id, callback=gpu_callback)
                break
            except Exception:
                count += 1
        if count>=5:
            logging.info("gpu数据服务启动失败")
            self.bstop = True
        gpu_get_time = time.time()
        while self.bstop is False and self.timeout>0:
            try:
                if gpu_get_time!=-1 and time.time()-gpu_get_time>GET_TIME_OUT:
                    logging.info("大于10秒没有返回gpu数据，重启gpu获取服务")
                    try:
                        py_ios_device.stop_get_gpu(channel)
                        channel.stop()
                    except Exception as e:
                        logging.info(str(e))
                    channel = py_ios_device.start_get_gpu(device_id=self.device_id, callback=gpu_callback)
                time.sleep(1)
            except Exception as e:
                logging.error(str(e))
        py_ios_device.stop_get_gpu(channel)
        channel.stop()

    def get_fps(self):
        global fps_get_time
        def fps_callback(res):
            try:
                global fps_file_handler, fps, perf_file_name,fps_get_time
                fps_get_time = time.time()
                if fps_file_handler is None and perf_file_name:
                    fps_file_handler = open(perf_file_name.replace('.csv', "_fps_detail.csv"), mode='w+',
                                            encoding='utf-8')
                    fps_file_handler.write(",".join(res.keys()) + "\n")
                data = ",".join([str(v) for v in res.values()]) + "\n"
                fps_file_handler.write(data)
                fps_file_handler.flush()
            except Exception as e:
                logging.error(str(e))
        channel = py_ios_device.start_get_fps(device_id=self.device_id, callback=fps_callback)
        fps_get_time = time.time()
        while self.bstop is False and self.timeout>0:
            try:
                if fps_get_time!=-1 and time.time()-fps_get_time>GET_TIME_OUT:
                    logging.info("大于10秒没有返回fps数据，重启fps获取服务")
                    try:
                        py_ios_device.stop_get_fps(channel)
                        channel.stop()
                    except Exception as e:
                        logging.info(str(e))
                    channel = py_ios_device.start_get_fps(device_id=self.device_id, callback=fps_callback)
                time.sleep(1)
            except Exception as e:
                logging.error(str(e))
        py_ios_device.stop_get_fps(channel)
        channel.stop()

    def get_system(self):
        global system_get_time
        def memory_callback(res):
            try:
                global process_attr, pid, media_pid, memory_file_handler, perf_file_name, virtual_memory, \
                    cpuCount, total_cpu, app_cpu, threads, media_cpu, memory, dalvik, native, wakeups, pre_wakeups,system_get_time
                system_get_time = time.time()
                for item in res:
                    if 'ProcessesAttributes' in item:
                        process_attr = item['ProcessesAttributes']
                        if memory_file_handler is None and perf_file_name:
                            memory_file_handler = open(perf_file_name.replace('.csv', "_perf_detail.csv"), mode='w+',
                                                       encoding='utf-8')
                            memory_file_handler.write(",".join(process_attr) + "\n")
                    if 'CPUCount' in item:
                        cpuCount = item['CPUCount']
                    if 'Processes' in item:
                        total = 0
                        for p, data in item['Processes'].items():
                            if p == pid:
                                virtual_memory = data[process_attr.index('memVirtualSize')] / 1024 / 1024.0
                                if data[process_attr.index('cpuUsage')]:
                                    app_cpu = data[process_attr.index('cpuUsage')] / cpuCount
                                threads = data[process_attr.index('threadCount')]
                                memory = data[process_attr.index('physFootprint')] / 1024 / 1024.0
                                dalvik = data[process_attr.index('memRPrvt')] / 1024 / 1024.0
                                native = data[process_attr.index('memResidentSize')] / 1024 / 1024.0
                                ups = data[process_attr.index('intWakeups')]
                                if pre_wakeups != -1:
                                    wakeups = ups - pre_wakeups
                                pre_wakeups = ups
                                if memory_file_handler:
                                    memory_file_handler.write(",".join([str(v) for v in data]) + "\n")
                                    memory_file_handler.flush()
                            elif p == media_pid and data[process_attr.index('cpuUsage')]:
                                media_cpu = data[process_attr.index('cpuUsage')] / cpuCount
                            if data[process_attr.index('cpuUsage')]:
                                total += data[process_attr.index('cpuUsage')]
                        total_cpu = total / cpuCount
            except Exception as e:
                logging.error(str(e))

        count = 0
        while count<5:
            try:
                channel =  py_ios_device.start_get_system(device_id=self.device_id, callback=memory_callback)
                try:
                    self.ios_version = float(channel.lockdown.ios_version.vstring)
                except Exception as e:
                    logging.info(str(e))
                    self.ios_version = 14
                break
            except Exception:
                count += 1
        if count >= 5:
            logging.info("memory数据服务启动失败")
            self.bstop = True
        system_get_time = time.time()
        while self.bstop is False and self.timeout>0:
            try:
                if system_get_time!=-1 and time.time()-system_get_time>GET_TIME_OUT:
                    logging.info("大于10秒没有返回系统数据，重启系统数据获取服务")
                    try:
                        py_ios_device.stop_get_system(channel)
                        channel.stop()
                    except Exception as e:
                        logging.info(str(e))
                    channel = py_ios_device.start_get_system(device_id=self.device_id, callback=memory_callback)
                time.sleep(1)
            except Exception as e:
                logging.error(str(e))
        py_ios_device.stop_get_system(channel)
        channel.stop()

    def run(self) -> None:
        global pid, media_pid,perf_file_name, virtual_memory,fps,gpu, \
            cpuCount, total_cpu, app_cpu, threads, media_cpu, memory, dalvik, native,wakeups
        perf_file_name = self.file_name
        pid = self.pid = self.get_pid(self.process_name)
        media_pid =self.get_pid("mediaserverd")
        if pid==-1:
            logging.error("获取pid失败")
            return None
        sys_thd = threading.Thread(target=self.get_system)
        sys_thd.setDaemon(True)
        sys_thd.start()
        traffic_thd = threading.Thread(target=self.get_traffic)
        traffic_thd.setDaemon(True)
        traffic_thd.start()
        gpu_thd = threading.Thread(target=self.get_gpu)
        gpu_thd.setDaemon(True)
        gpu_thd.start()
        fps_thd = threading.Thread(target=self.get_fps)
        fps_thd.setDaemon(True)
        fps_thd.start()
        #等待线程启动
        time.sleep(5)
        perffile = open(self.file_name,mode='w+',encoding='utf-8')
        perffile.write(self.DATA_TITLE+"\n")
        while self.bstop is False and self.timeout>0:
            try:
                str_now_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))
                if app_cpu==-1 or total_cpu==-1 or memory==-1:
                    #为-1时还没获取到数据，不写入
                    continue
                cpu = app_cpu
                m_cpu = media_cpu
                t_cpu = total_cpu
                if self.ios_version < 14:
                    cpu = app_cpu*100
                    m_cpu = media_cpu*100
                    t_cpu = total_cpu*100
                line = f'{str_now_time},{cpu:.2f},{t_cpu:.2f},{memory:.2f},{native:.2f},{dalvik:.2f},{self.total_traffic:.2f},' \
                       f'{self.traffic_up:.2f},{self.traffic_down:.2f},{gpu:.2f},{threads},{virtual_memory:.2f},{activities},' \
                       f'{fps:.2f},{m_cpu:.2f},{wakeups}\n'
                print(line)
                perffile.write(line)
                perffile.flush()
                time.sleep(self.interval)
                self.timeout -= self.interval
                print(f"剩余时间{self.timeout}")
            except Exception as e:
                logging.error(str(e))
        perffile.close()
        self.close()

    def close(self):
        global memory_file_handler,gpu_file_handler,fps_file_handler
        if memory_file_handler:
            memory_file_handler.close()
        if gpu_file_handler:
            gpu_file_handler.close()
        if fps_file_handler:
            fps_file_handler.close()

    def stop(self):
        self.bstop = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ios perf data monitor")
    parser.add_argument('-filename', type=str, default='73_YY.csv',
                        help='csv file name (end with .csv)')
    parser.add_argument('-time', type=float, default=30.0, help='trace time (second)')
    parser.add_argument('-process', type=str, default="YYMobile", help='process name')
    parser.add_argument('-bundle_id', type=str, default=None, help='bundle_id')
    parser.add_argument('-udid', type=str, default="00008030-001479841407802E", help='device udid')
    args = parser.parse_args()
    monitor = app_monitor(device_id=args.udid,bundle_id=args.bundle_id,process=args.process,
                          filename=args.filename,timeout=args.time)
    monitor.start()
    monitor.join(args.time+10)