class ServiceMappingMobileMinutes():
    SERVICES = {
        '0min': '0',
        '100min': '100',
        '200min': '200',
        'unlim': 'unlimited',
    }

    @classmethod
    def minutes(cls, otrs_service):
        return cls.SERVICES[otrs_service]
