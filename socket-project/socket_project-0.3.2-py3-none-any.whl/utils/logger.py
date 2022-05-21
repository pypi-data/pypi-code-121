class Logger:
    @staticmethod
    def info(*args, **kwargs):
        print("INFO:", *args, **kwargs)

    @staticmethod
    def debug(*args, **kwargs):
        print("DEBUG:", *args, **kwargs)

    @staticmethod
    def exception(*args, **kwargs):
        print("EXCEPTION:", *args, **kwargs)

    @staticmethod
    def warning(*args, **kwargs):
        print("WARNING:", *args, **kwargs)

    @staticmethod
    def message(*args, **kwargs):
        print("MESSAGE:", *args, **kwargs)

