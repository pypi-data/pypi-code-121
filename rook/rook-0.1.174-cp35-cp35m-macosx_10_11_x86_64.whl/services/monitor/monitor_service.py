import time
import threading

from rook.config import ShutdownConfig

class MonitorService(object):

    class Usage(object):
        def __init__(self, cpu, global_cpu, virtual_memory, start_time, uptime):
            self.cpu = cpu
            self.global_cpu = global_cpu
            self.virtual_memory = virtual_memory
            self.start_time = start_time
            self.uptime = uptime

    NAME = "Monitor"

    def __init__(self):
        self._thread = None
        self._running = False
        self.last_usage = None
        self._psutil = None

    def start(self):
        import psutil
        self._psutil = psutil

        if not self._thread:
            self._thread = threading.Thread(name="rookout-" + type(self).__name__, target=self._collect_data)
            self._thread.daemon = True

            self._running = True
            self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join(1)

    @staticmethod
    def get_last_usage():
        return monitor_instance.last_usage

    @staticmethod
    def get_instance():
        return monitor_instance

    def _collect_data(self):
        process = self._psutil.Process()

        times = process.cpu_times()
        last_user_time = times.user

        cpu_count = self._psutil.cpu_count()

        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(process.create_time()))
        uptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._psutil.boot_time()))

        while self._running:
            try:
                if ShutdownConfig.IS_SHUTTING_DOWN:
                    return

                global_cpu = self._psutil.cpu_percent()

                times = process.cpu_times()
                current_user_time = times.user

                diff = current_user_time - last_user_time
                process_cpu = diff / (500 * cpu_count) * 100000

                last_user_time = current_user_time

                mem_info = process.memory_info()
                virtual_memory = mem_info.vms

                self.last_usage = MonitorService.Usage(process_cpu, global_cpu, virtual_memory, start_time, uptime)

            except:  # we want the loop to always keep going lgtm[py/catch-base-exception]
                pass

            time.sleep(0.5)


monitor_instance = MonitorService()
