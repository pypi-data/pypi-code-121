class CliConfig:
    __conf = {"logs": False, "json": False}

    @staticmethod
    def get(name):
        return CliConfig.__conf[name]

    @staticmethod
    def set(name, value):
        CliConfig.__conf[name] = value
