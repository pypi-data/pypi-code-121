# Most of the collecting code was picked from other places
from __future__ import absolute_import

import logging
from typing import Any, Dict, Optional

from mlfoundry.background import utils as bg_utils
from mlfoundry.background.interface import Interface
from mlfoundry.vendor.pynvml import pynvml

logger = logging.getLogger(__name__)

try:
    import psutil
except ImportError:
    logger.warning(
        f"`psutil` is not installed. System metrics will not be reported. Install with `pip install psutil`"
    )
    psutil = None

# TODO (chiragjn): Add cgroup reading mode for Linux/Docker and TPU support
MEGABYTE = float(1024 * 1024)


def gpu_in_use_by_this_process(gpu_handle) -> bool:
    if not psutil:
        return False
    base_process = psutil.Process().parent() or psutil.Process()
    our_processes = base_process.children(recursive=True)
    our_processes.append(base_process)
    our_pids = {process.pid for process in our_processes}
    compute_pids = {
        process.pid
        for process in pynvml.nvmlDeviceGetComputeRunningProcesses(gpu_handle)
    }
    graphics_pids = {
        process.pid
        for process in pynvml.nvmlDeviceGetGraphicsRunningProcesses(gpu_handle)
    }
    pids_using_device = compute_pids | graphics_pids
    return len(pids_using_device & our_pids) > 0


# TODO (chiragjn): Separate stats collecting functionality into another module for unit testing
class SystemMetricsJob(bg_utils.BackgroundJob):
    """
    Collect system resources (cpu, memory, disk, network, gpu) metrics and log them with the run

    Attributes:
        num_samples_to_aggregate: number of samples to aggregate before logging them
        gpu_count: number of GPUs detected
        _pid: process PID to monitor and collect stats for
        _interface: `background.interface.Interface` instance to publish collected stats with
        _sampled: dict holding metric name to list of samples for that metric
        _sample_count: how many samples out of `num_samples_to_aggregate`  have been collected
        _network_init: number of bytes sent and received before we start measuring for our run
    """

    name_prefix = "MLFSystemMetricsThread"

    def __init__(
        self,
        pid: int,
        interface: Interface,
        num_samples_to_aggregate: int = 15,
        interval: float = 2.0,
    ) -> None:
        """
        Args:
            pid: process PID to monitor and collect stats for
            interface: `background.interface.Interface` instance to publish collected stats with
            num_samples_to_aggregate: number of samples to aggregate before logging them, defaults to 15
            interval: time in seconds to sleep between consecutive stats collecting, defaults to 2 seconds
        """
        super().__init__(
            name=f"{SystemMetricsJob.name_prefix}:{interface.run_id}", interval=interval
        )
        self.num_samples_to_aggregate = num_samples_to_aggregate
        try:
            pynvml.nvmlInit()
            self.gpu_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError:
            self.gpu_count = 0
        self._pid = pid
        self._interface: Optional[Interface] = interface
        self._sampled = {}
        self._sample_count = 0
        if psutil:
            net = psutil.net_io_counters()
            self._network_init = {"sent": net.bytes_sent, "recv": net.bytes_recv}
        else:
            self._network_init = {"sent": 0, "recv": 0}
            logger.warning(
                "`psutil` not installed, only GPU stats will be reported. Install with `pip install psutil`"
            )

    def _collect_gpu_stats(self, stats: Dict[str, Any]) -> None:
        """
        Collect GPU specific stats in given `stats` dict

        Args:
            stats: dict to collect stats into
        """
        for i in range(0, self.gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            try:
                utilz = pynvml.nvmlDeviceGetUtilizationRates(handle)
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                temp = pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU
                )
                in_use_by_current_process = gpu_in_use_by_this_process(handle)

                stats[f"gpu.{i}.gpu"] = utilz.gpu
                stats[f"gpu.{i}.memory"] = utilz.memory
                stats[f"gpu.{i}.memory_allocated.percent"] = (
                    memory.used / float(memory.total)
                ) * 100
                stats[f"gpu.{i}.temperature"] = temp

                if in_use_by_current_process:
                    stats[f"gpu.process.{i}.gpu"] = utilz.gpu
                    stats[f"gpu.process.{i}.memory"] = utilz.memory
                    stats[f"gpu.process.{i}.memory_allocated.percent"] = (
                        memory.used / float(memory.total)
                    ) * 100
                    stats[f"gpu.process.{i}.temperature"] = temp

                try:
                    power_watts = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                    power_capacity_watts = (
                        pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
                    )
                    power_usage = (power_watts / power_capacity_watts) * 100
                    stats[f"gpu.{i}.power.watts"] = power_watts
                    stats[f"gpu.{i}.power.percent"] = power_usage

                    if in_use_by_current_process:
                        stats[f"gpu.process.{i}.power.watts"] = power_watts
                        stats[f"gpu.process.{i}.power.percent"] = power_usage

                except pynvml.NVMLError:
                    pass
            except pynvml.NVMLError:
                pass

    def _collect_system_stats(self, stats: Dict[str, Any]):
        """
        Collect CPU, memory, disk and network related stats given `stats` dict

        Args:
            stats: dict to collect stats into
        """
        if psutil:
            net = psutil.net_io_counters()
            sysmem = psutil.virtual_memory()
            stats["cpu.percent"] = psutil.cpu_percent()
            stats["memory.percent"] = sysmem.percent
            stats["network.sent.bytes"] = net.bytes_sent - self._network_init["sent"]
            stats["network.recv.bytes"] = net.bytes_recv - self._network_init["recv"]
            stats["disk.percent"] = psutil.disk_usage("/").percent
            stats["proc.memory.available.mb"] = sysmem.available / MEGABYTE
            try:
                proc = psutil.Process(pid=self._pid)
                stats["proc.memory.rss.mb"] = proc.memory_info().rss / MEGABYTE
                stats["proc.memory.percent"] = proc.memory_percent()
                stats["proc.cpu.threads"] = proc.num_threads()
            except psutil.NoSuchProcess:
                pass

    def collect_stats(self) -> Dict[str, float]:
        """
        Collect gpu and system stats

        Returns:
            Dict[str, float]: dict mapping metric name to value for that metric
        """
        stats = {}
        self._collect_gpu_stats(stats)
        self._collect_system_stats(stats)
        return stats

    def _flush(self) -> None:
        """
        Aggregate (mean, max) and log collected stats so far and reset sampling state
        """
        if not self._sampled:
            return
        stats = self.collect_stats()
        metric_dict = {}
        for stat, value in stats.items():
            if isinstance(value, (float, int)):
                samples = list(self._sampled.get(stat, [value]))
                if samples:
                    metric_dict[f"mlf.system_metrics.{stat}.max"] = round(
                        max(samples), 2
                    )
                    metric_dict[f"mlf.system_metrics.{stat}.avg"] = round(
                        sum(samples) / len(samples), 2
                    )
        if self._interface:
            self._interface.log_metrics(metric_dict=metric_dict)
        self._sample_count = 0
        self._sampled = {}

    def _loop(self) -> None:
        """
        Collect stats and add them to samples. Flush if we have collected the max number of samples allowed
        """
        stats = self.collect_stats()
        for stat, value in stats.items():
            if isinstance(value, (int, float)):
                self._sampled[stat] = self._sampled.get(stat, [])
                self._sampled[stat].append(value)
        self._sample_count += 1
        if self._sample_count >= self.num_samples_to_aggregate:
            self._flush()

    def _finish(self) -> None:
        """
        Flush any remaining collected stats samples
        """
        self._flush()
        self._interface = None
