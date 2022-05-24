class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        key = hash((cls, str(args), str(kwargs)))
        if key not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[key] = instance
        return cls._instances[key]
