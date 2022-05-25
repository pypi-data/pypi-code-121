import importlib

from . import (
    basic_status,
    cpu_status,
    disk_status,
    interrupt_status,
    load_status,
    network_status,
    ram_status,
    snmp_agent,
    swap_status,
    system_info,
)

Alarm = importlib.import_module("ant_net_monitor.alarm").Alarm

class SnmpStatus:
    def __init__(self, agent):
        self.agent = agent
        self.CPUStatus = cpu_status.CPUStatus(agent)
        self.RAMStatus = ram_status.RAMStatus(agent)
        self.DiskStatus = disk_status.DiskStatus(agent)
        self.NetworkStatus = network_status.NetworkStatus(agent)
        self.LoadStatus = load_status.LoadStatus(agent)
        self.SwapStatus = swap_status.SwapStatus(agent)
        self.InterruptStatus = interrupt_status.InterruptStatus(agent)
        self.System = system_info.System(agent)

    def save_all(self):
        self.CPUStatus.save()
        self.RAMStatus.save()
        self.DiskStatus.save()
        self.NetworkStatus.save()
        self.LoadStatus.save()
        self.SwapStatus.save()
        self.InterruptStatus.save()
        #! 不需要在线程循环里保存系统信息

        self.check_alarm()

    def check_alarm(self):
        cpu_status_info = cpu_status.CPUStatusInfo.get_last(self.agent)
        ram_status_info = ram_status.RAMStatusInfo.get_last(self.agent)
        swap_status_info = swap_status.SwapStatusInfo.get_last(self.agent)

        Alarm.check_snmp_cpu_alarm(cpu_status_info.used_percent)
        Alarm.check_snmp_ram_alarm(ram_status_info.used_percent)
        Alarm.check_snmp_swap_alarm(swap_status_info.used_percent)

    def init_system_status(self):
        self.System.save()

    @classmethod
    def init_agent(cls, app, host, community):
        snmp_agent.SnmpAgent.init_agent(app, host, community)

    @classmethod
    def get_agent_list(cls, app):
        with app.app_context():
            return [cls(agent) for agent in snmp_agent.SnmpAgent.get_all()]

    @classmethod
    def get_basic_status(cls):
        agent = snmp_agent.SnmpAgent.query.first()
        return basic_status.BasicStatus.get_last(agent)

    @classmethod
    def get_cpu_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return cpu_status.CPUStatusInfo.get_batch(agent)
        elif type == "update":
            return cpu_status.CPUStatusInfo.get_last(agent)
        elif type == "day":
            return cpu_status.CPUStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_ram_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return ram_status.RAMStatusInfo.get_batch(agent)
        elif type == "update":
            return ram_status.RAMStatusInfo.get_last(agent)
        elif type == "day":
            return ram_status.RAMStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_disk_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return disk_status.DiskStatusInfo.get_batch(agent)
        elif type == "update":
            return disk_status.DiskStatusInfo.get_last(agent)
        elif type == "day":
            return disk_status.DiskStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_network_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return network_status.NetworkStatusInfo.get_batch(agent)
        elif type == "update":
            return network_status.NetworkStatusInfo.get_last(agent)
        elif type == "day":
            return network_status.NetworkStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_load_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return load_status.LoadStatusInfo.get_batch(agent)
        elif type == "update":
            return load_status.LoadStatusInfo.get_last(agent)
        elif type == "day":
            return load_status.LoadStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_swap_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return swap_status.SwapStatusInfo.get_batch(agent)
        elif type == "update":
            return swap_status.SwapStatusInfo.get_last(agent)
        elif type == "day":
            return swap_status.SwapStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_interrupt_status(cls, type):
        agent = snmp_agent.SnmpAgent.query.first()
        if type == "init":
            return interrupt_status.InterruptStatusInfo.get_batch(agent)
        elif type == "update":
            return interrupt_status.InterruptStatusInfo.get_last(agent)
        elif type == "day":
            return interrupt_status.InterruptStatusInfo.get_in_one_day(agent)

    @classmethod
    def get_system_info(cls):
        agent = snmp_agent.SnmpAgent.query.first()
        return system_info.SystemInfo.get_last(agent)
