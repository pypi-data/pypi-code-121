import logging
from threading import Thread

from kamzik3.devices.deviceWorker import DeviceWorker
from kamzik3.snippets.snippetsYaml import YamlSerializable
from kamzik3.snippets.snippetsZmq import BalancedServer


class DeviceServer(BalancedServer, Thread, YamlSerializable):
    def __init__(self, host, port, workers_count=5, worker_class=DeviceWorker):
        self.logger = logging.getLogger("Console.DeviceServer@{}:{}".format(host, port))
        Thread.__init__(self)
        BalancedServer.__init__(self, host, port, workers_count, worker_class)
