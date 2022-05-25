import os
# from cloudmesh.common.Printer import Printer
import pprint
import sys
from datetime import date
from datetime import datetime
from signal import signal, SIGINT

import xmltodict
import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import readfile


class Gpu:

    def __init__(self):

        self.running = True
        try:
            self._smi = dict(self.smi(output="json"))['nvidia_smi_log']['gpu']
            if not isinstance(self._smi, list):
                self._smi = [self._smi]
        except KeyError:
            raise RuntimeError("nvidia-smi not installed.")
        self.gpus = 0

    def exit_handler(self, signal_received, frame):
        """
        Kube manager has a build in Benchmark framework. In case you
        press CTRL-C, this handler assures that the benchmarks will be printed.

        :param signal_received:
        :type signal_received:
        :param frame:
        :type frame:
        :return:
        :rtype:
        """
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        self.running = False

    @property
    def count(self):
        if self.gpus == 0:
            try:
                self.gpus = int(Shell.run("nvidia-smi --list-gpus | wc -l").strip())
            except:
                self.gpus = 0
        return self.gpus

    def vendor(self):
        if os.name != "nt":
            try:
                r = Shell.run("lspci -vnn | grep VGA -A 12 | fgrep Subsystem:").strip()
                result = r.split("Subsystem:")[1].strip()
            except:
                result = None
        else:
            try:
                r = Shell.run("wmic path win32_VideoController get AdapterCompatibility").strip()
                result = [x.strip() for x in r.split("\r\r\n")[1:]]
            except Exception:
                results = None
        return result

    def processes(self):
        result = {}
        try:
            # We want to call this each time, as we want the current processes
            data = dict(self.smi(output="json"))["nvidia_smi_log"]['gpu']
            for i in range(self.count):
                information = data[i]["processes"]["process_info"]
                result[i] = information
        except Exception as e:
            print(e)
        return result

    def system(self):
        result = self._smi
        for gpu_instance in range(len(self._smi)):
            for attribute in [
                '@id',
                # 'product_name',
                # 'product_brand',
                # 'product_architecture',
                'display_mode',
                'display_active',
                'persistence_mode',
                'mig_mode',
                'mig_devices',
                'accounting_mode',
                'accounting_mode_buffer_size',
                'driver_model',
                'serial',
                'uuid',
                'minor_number',
                # 'vbios_version',
                'multigpu_board',
                'board_id',
                'gpu_part_number',
                'gpu_module_id',
                # 'inforom_version',
                'gpu_operation_mode',
                'gsp_firmware_version',
                'gpu_virtualization_mode',
                'ibmnpu',
                'pci',
                'fan_speed',
                'performance_state',
                'clocks_throttle_reasons',
                'fb_memory_usage',
                'bar1_memory_usage',
                'compute_mode',
                'utilization',
                'encoder_stats',
                'fbc_stats',
                'ecc_mode',
                'ecc_errors',
                'retired_pages',
                'remapped_rows',
                'temperature',
                'supported_gpu_target_temp',
                'power_readings',
                'clocks',
                'applications_clocks',
                'default_applications_clocks',
                'max_clocks',
                'max_customer_boost_clocks',
                'clock_policy',
                'voltage',
                'supported_clocks',
                'processes'
            ]:
                try:
                    del result[gpu_instance][attribute]
                    result[gpu_instance]["vendor"] = self.vendor()
                except KeyError:
                    pass
        return result

    def status(self):
        result = self._smi
        for gpu_instance in range(len(self._smi)):
            for attribute in [
                '@id',
                'product_name',
                'product_brand',
                'product_architecture',
                'display_mode',
                'display_active',
                'persistence_mode',
                'mig_mode',
                'mig_devices',
                'accounting_mode',
                'accounting_mode_buffer_size',
                'driver_model',
                'serial',
                'uuid',
                'minor_number',
                'vbios_version',
                'multigpu_board',
                'board_id',
                'gpu_part_number',
                'gpu_module_id',
                'inforom_version',
                'gpu_operation_mode',
                'gsp_firmware_version',
                'gpu_virtualization_mode',
                'ibmnpu',
                'pci',
                # 'fan_speed',
                'performance_state',
                'clocks_throttle_reasons',
                'fb_memory_usage',
                'bar1_memory_usage',
                'compute_mode',
                # 'utilization',
                'encoder_stats',
                'fbc_stats',
                'ecc_mode',
                'ecc_errors',
                'retired_pages',
                'remapped_rows',
                # 'temperature',
                # 'supported_gpu_target_temp',
                # 'power_readings',
                # 'clocks',
                'applications_clocks',
                'default_applications_clocks',
                'max_clocks',
                'max_customer_boost_clocks',
                'clock_policy',
                # 'voltage',
                'supported_clocks',
                'processes'
            ]:
                try:
                    del result[gpu_instance][attribute]
                except KeyError:
                    pass
        return result

    def smi(self, output=None, filename=None):
        # None = text
        # json
        # yaml
        try:
            if filename is None and output is None:
                result = Shell.run("nvidia-smi").replace("\r", "")
                return result

            if filename is not None:
                r = readfile(filename)
            else:
                r = Shell.run("nvidia-smi -q -x")
            if output == "xml":
                result = r
            elif output == "json":
                result = xmltodict.parse(r)

                if int(result["nvidia_smi_log"]["attached_gpus"]) == 1:
                    data = result["nvidia_smi_log"]["gpu"]
                    result["nvidia_smi_log"]["gpu"] = [data]

            elif output == "yaml":
                result = yaml.dump(xmltodict.parse(r))
        except Exception as e:
            print(e)
            result = None
        return result

    def watch(self, logfile=None, delay=1.0, repeated=None, dense=False, gpu=None):

        if repeated is None:
            repeated = -1
        else:
            repeated = int(repeated)

        try:
            delay = float(delay)
        except Exception as e:
            delay = 1.0

        signal(SIGINT, self.exit_handler)

        stream = sys.stdout
        if logfile is None:
            stream = sys.stdout
        else:
            stream = open(logfile, "w")

        print("# ####################################################################################")
        print("# time, ", end="")
        for i in range(self.count):
            print(
                f"{i} id, "
                f"{i} gpu_util %, "
                f"{i} memory_util %, "
                f"{i} encoder_util %, "
                f"{i} decoder_util %, "
                f"{i} gpu_temp C, "
                f"{i} power_draw W",
                end="")
        print()

        counter = repeated

        if gpu is not None:
            selected = [int(i) for i in gpu]
        else:
            selected = list(range(self.count))
        while self.running:
            try:
                if counter > 0:
                    counter = counter - 1
                    self.running = self.running and counter > 0
                today = date.today()
                now = datetime.now().time()  # time object
                data = self.smi(output="json")

                result = [f"{today}:{now}"]

                for gpu in range(self.count):
                    if gpu in selected:
                        utilization = dotdict(data["nvidia_smi_log"]["gpu"][gpu]["utilization"])
                        temperature = dotdict(data["nvidia_smi_log"]["gpu"][gpu]["temperature"])
                        power = dotdict(data["nvidia_smi_log"]["gpu"][gpu]["power_readings"])
                        line = \
                            f"{gpu:>3}, " \
                            f"{utilization.gpu_util[:-2]: >3}, " \
                            f"{utilization.memory_util[:-2]: >3}, " \
                            f"{utilization.encoder_util[:-2]: >3}, " \
                            f"{utilization.decoder_util[:-2]: >3}, " \
                            f"{temperature.gpu_temp[:-2]: >5}, " \
                            f"{power.power_draw[:-2]: >8}"
                        result.append(line)

                result = ", ".join(result)
                if dense:
                    result = result.replace(" ", "")
                print(result, file=stream)

            except Exception as e:
                print(e)

    def __str__(self):
        return pprint.pformat(self._smi, indent=2)
