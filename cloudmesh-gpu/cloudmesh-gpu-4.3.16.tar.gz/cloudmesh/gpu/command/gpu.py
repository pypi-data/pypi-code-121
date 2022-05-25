import json

from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.gpu.gpu import Gpu
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


class GpuCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_gpu(self, args, arguments):
        """
        ::

          Usage:
                gpu watch [--gpu=GPU] [--delay=SECONDS] [--logfile=LOGFILE] [--count=COUNT] [--dense]
                gpu --json [--gpu=GPU] [--pretty] [FILE]
                gpu --xml
                gpu --yaml
                gpu processes [--gpu=GPU] [--format=FORMAT] [--detail]
                gpu system
                gpu status
                gpu count
                gpu kill
                gpu

          This command returns some information about NVIDIA GPUs if your
          system has them. Please use the cms command in the commandline with
          `cms gpu`

          Options:
              --json              returns the information in json
              --xml               returns the information in xml
              --yaml              returns the information in xml
              --logfile=LOGFILE   the logfile
              --count=COUNT       how many times the watch is run [default: -1]
              --dense             do not print any spaces [default: False]
              --detail            short process names [default: False]
              --format=FORMAT     table, json, yaml [default: table]
              --gpu=GPUS

          Description:

            Although some GPU information tools exist, we did not find all information
            that we needed. Also the output format was not convenient enough for later
            analysis. The program we developed can obtain information at specified
            intervals. Note that at this time the tool is restricted to NVIDIA GPU's.

                cms gpu kill
                    In case you run the gpu command in the background you can kill it with the
                    `kill command`

                cms gpu count
                    Returns the number of GPUS.

                gpu watch [--gpu=GPU] [--delay=SECONDS] [--logfile=LOGFILE] [--count=COUNT] [--dense]
                    This command allows to print environmental variables in a continious fashion.
                    If count is used the command is executed that number of times. If it is ommitted
                    it runs continiously. The delay specifies how many seconds between invocations are
                    dealyed. The `logfile` specifies an output file in which the events are written.
                    By default spaces are included so the output has a table like format. The spaces
                    can be eliminated with dense so that less space is used in the log file.
                    In case multiple GPUs are present one can select specific GPUs fr which the
                    monitoring entries are generated.
                    The watch command output is proceeded by a header that is adapted based on the
                    gpus specified. This makes it possible to read in the file as dataframe and apply
                    easily plotting tools.

                    An example output looks like (the newline in this example in the header was
                    introduced to increase readability of this documentation. In an execution it is
                    one line.

                    # ####################################################################################
                    # time, 0 id, 0 gpu_util %, 0 memory_util %, 0 encoder_util %, 0 decoder_util %,
                    # ... 0 gpu_temp C, 0 power_draw W
                    2022-03-18 11:26:40.877006,   0,  11,  16,   0,   0,    49,    47.47
                    2022-03-18 11:26:40.983229,   0,  17,  17,   0,   0,    49,    47.59
                    2022-03-18 11:26:41.093406,   0,  17,  17,   0,   0,    49,    47.88

                gpu --json [--gpu=GPU] [--pretty] [FILE]
                    Prints out the information in json format. We have eliminated some of the attributes
                    that are not important to us at this time. with the `pretty` flag the json is printed
                    in indented pretty format.
                    The FILE parameter is used to read in a saved instance from nvidid-smi.

                gpu --xml
                    Prints out the information in xml format. This is the format that is retrieved from
                    nvidia-smi. The gpu selection flag is not enabled for this format. If you want to
                    implement it, create a pull request.

                gpu --yaml
                    Prints out the information in yaml format. The gpu selection flag is not enabled
                    for this format. If you want to implement it, create a pull request.

                gpu processes [--gpu=GPU] [--format=FORMAT] [--detail]
                    Prints out the processes running on the GPU in the specified format for the selected GPUs.
                    The process name is shortened based on removing the path of the command. If the full path
                    is needed one can use the `detail` flag. Allowed formats are table, csv, json, and yaml.

                    A sample output for a table looks similar to

                +-----+-----+-----+------+-------------+---------------------+-----------------+--------------+
                | job | gpu | pid | type | used_memory | compute_instance_id | gpu_instance_id | process_name |
                +-----+-----+-----+------+-------------+---------------------+-----------------+--------------+
                | 1   | 0   | 173 | G    | 198 MiB     | N/A                 | N/A             | Xorg         |
                | 2   | 0   | 260 | G    | 610 MiB     | N/A                 | N/A             | Xorg         |
                | 3   | 0   | 274 | G    | 49 MiB      | N/A                 | N/A             | gnome-shell  |
                | 4   | 0   | 436 | G    | 27 MiB      | N/A                 | N/A             | zoom         |
                | 5   | 0   | 321 | G    | 100 MiB     | N/A                 | N/A             | slack        |
                | 6   | 0   | 591 | G    | 11 MiB      | N/A                 | N/A             | firefox      |
                +-----+-----+-----+------+-------------+---------------------+-----------------+--------------+


                gpu system
                    Returns information about the GPU card

                        [
                          {
                            "product_name": "NVIDIA GeForce RTX 3090",
                            "product_brand": "GeForce",
                            "product_architecture": "Ampere",
                            "vbios_version": "94.02.42.00.A9",
                            "inforom_version": {
                              "img_version": "G001.0000.03.03",
                              "oem_object": "2.0",
                              "ecc_object": "N/A",
                              "pwr_object": "N/A"
                            },
                            "accounted_processes": null,
                            "vendor": "ASUSTeK Computer Inc. Device [abcd:1234]"
                          }
                        ]


                gpu status
                    Returns elementary status information such as environmental sensors

                        [
                          {
                            "fan_speed": "0 %",
                            "utilization": {
                              "gpu_util": "18 %",
                              "memory_util": "18 %",
                              "encoder_util": "0 %",
                              "decoder_util": "0 %"
                            },
                            "temperature": {
                              "gpu_temp": "48 C",
                              "gpu_temp_max_threshold": "98 C",
                              "gpu_temp_slow_threshold": "95 C",
                              "gpu_temp_max_gpu_threshold": "93 C",
                              "gpu_target_temperature": "83 C",
                              "memory_temp": "N/A",
                              "gpu_temp_max_mem_threshold": "N/A"
                            },
                            "supported_gpu_target_temp": {
                              "gpu_target_temp_min": "65 C",
                              "gpu_target_temp_max": "91 C"
                            },
                            "power_readings": {
                              "power_state": "P8",
                              "power_management": "Supported",
                              "power_draw": "47.28 W",
                              "power_limit": "390.00 W",
                              "default_power_limit": "390.00 W",
                              "enforced_power_limit": "390.00 W",
                              "min_power_limit": "100.00 W",
                              "max_power_limit": "480.00 W"
                            },
                            "clocks": {
                              "graphics_clock": "210 MHz",
                              "sm_clock": "210 MHz",
                              "mem_clock": "405 MHz",
                              "video_clock": "555 MHz"
                            },
                            "voltage": {
                              "graphics_volt": "737.500 mV"
                            },
                            "accounted_processes": null
                          }
                        ]



        """

        map_parameters(arguments,
                       "json",
                       "xml",
                       "yaml",
                       "pretty",
                       "delay",
                       "logfile",
                       "table",
                       "detail",
                       "output"
                       )
        arguments.format = arguments["--format"]
        arguments.gpu = Parameter.expand(arguments["--gpu"])
        # VERBOSE(arguments)

        def _select(d, what):
            try:
                selected = []
                data = dict(gpu.smi(output="json"))["nvidia_smi_log"]['gpu']
                selection = [int(i) for i in what]
                # selected = [data[i] for i in selection]
                # this way we can pass numbers which do not exist
                selected = []
                for i in selection:
                    try:
                        selected.append(data[i])
                    except:
                        pass
                d["nvidia_smi_log"]['gpu'] = selected
            except Exception as e:
                print(e)
            return d

        try:
            gpu = Gpu()
            if arguments.gpu is None:
                arguments.gpu = [str(i) for i in range(gpu.count)]

            if arguments.watch:

                gpu.watch(logfile=arguments.logfile,
                          delay=arguments.delay,
                          repeated=int(arguments["--count"]),
                          dense=arguments["--dense"],
                          gpu=arguments.gpu)

                return ""

            elif arguments.kill:

                r = Shell.run('ps -ax | fgrep "cms gpu watch"').splitlines()
                for entry in r:
                    if "python" in entry:
                        pid = entry.strip().split()[0]
                        Shell.kill_pid(pid)

                return ""

            elif arguments.xml:
                try:
                    result = gpu.smi(output="xml")
                except:
                    Console.error("nvidia-smi must be installed on the system")
                    return ""

            elif arguments.json and arguments.pertty:
                filename = arguments.FILE
                result = gpu.smi(output="json", filename=filename)
                result = _select(result, arguments.gpu)

            elif arguments.json:
                filename = arguments.FILE
                result = gpu.smi(output="json", filename=filename)
                result = _select(result, arguments.gpu)

            elif arguments.yaml:
                result = gpu.smi(output="yaml")

            elif arguments.processes:

                arguments.pretty = True
                result = gpu.processes()
                d = []
                counter = 0
                for i in result.keys():
                    if str(i) in arguments.gpu:
                        for p in result[i]:
                            counter = counter + 1
                            p["gpu"] = i
                            p["job"] = counter
                            p = dict(p)
                            if not arguments.detail:
                                p["process_name"] = p["process_name"].split()[0].strip()
                                try:
                                    p["process_name"] = p["process_name"].split("/")[-1]
                                except:
                                    pass
                            d.append(p)
                    print(Printer.write(d,
                                        output=arguments.format,
                                        order=["job", "gpu", "pid", "type", "used_memory", "compute_instance_id",
                                               "gpu_instance_id", "process_name"]))
                return ""

            elif arguments.system:
                arguments.pretty = True
                result = gpu.system()
                # result  = _select(result, arguments.gpu)

            elif arguments.status:
                arguments.pretty = True
                result = gpu.status()
                # result  = _select(result, arguments.gpu)

            elif arguments.count:
                arguments.pretty = True
                result = gpu.count

            else:
                result = gpu.smi()
                # result  = _select(result, arguments.gpu)

            try:
                if arguments.pretty:
                    # result = _select(result, arguments.gpu)
                    result = json.dumps(result, indent=2)
            except:
                result = None
        except:
            result = None

        print(result)

        return ""
