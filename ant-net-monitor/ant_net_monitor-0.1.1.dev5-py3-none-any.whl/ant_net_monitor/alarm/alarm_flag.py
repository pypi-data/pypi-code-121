class AlarmFlag:
    alarm_dict: dict
    alarm_flag: dict
    alarm_counter: dict

    @classmethod
    def init_flag(cls, all_alarm_items):
        cls.alarm_dict = {item.name: item.alarm_value for item in all_alarm_items}
        cls.alarm_flag = {item.name: False for item in all_alarm_items}
        cls.alarm_counter = {item.name: 0 for item in all_alarm_items}

    @classmethod
    def set_flag(cls, name, flag):
        cls.alarm_flag[name] = flag

    @classmethod
    def get_all_flag(cls):
        return cls.alarm_flag

    @classmethod
    def check_cpu_alarm(cls, cpu_usage, cpu_iowait, cpu_steal):
        if cpu_usage > cls.alarm_dict["cpu_usage"]:
            cls.alarm_counter["cpu_usage"] += 1
        else:
            cls.alarm_counter["cpu_usage"] -= 1
        if cpu_iowait > cls.alarm_dict["cpu_iowait"]:
            cls.alarm_counter["cpu_iowait"] += 1
        else:
            cls.alarm_counter["cpu_iowait"] -= 1
        if cpu_steal > cls.alarm_dict["cpu_steal"]:
            cls.alarm_counter["cpu_steal"] += 1
        else:
            cls.alarm_counter["cpu_steal"] -= 1

        if cls.alarm_counter["cpu_usage"] >= 10:
            cls.set_flag("cpu_usage", True)
            cls.alarm_counter["cpu_usage"] = 10
        elif cls.alarm_counter["cpu_usage"] <= 0:
            cls.set_flag("cpu_usage", False)
            cls.alarm_counter["cpu_usage"] = 0

        if cls.alarm_counter["cpu_iowait"] >= 10:
            cls.set_flag("cpu_iowait", True)
            cls.alarm_counter["cpu_iowait"] = 10
        elif cls.alarm_counter["cpu_iowait"] <= 0:
            cls.set_flag("cpu_iowait", False)
            cls.alarm_counter["cpu_iowait"] = 0

        if cls.alarm_counter["cpu_steal"] >= 10:
            cls.set_flag("cpu_steal", True)
            cls.alarm_counter["cpu_steal"] = 10
        elif cls.alarm_counter["cpu_steal"] <= 0:
            cls.set_flag("cpu_steal", False)
            cls.alarm_counter["cpu_steal"] = 0
