class ServiceMappingServices():
    SERVICES = {
        'Mobile': 'mobile',
        'Fibra': 'fiber',
        'ADSL': 'adsl',
        'ADSL+100min': 'adsl100',
        'ADSL+1000min': 'adsl1000'
    }

    @classmethod
    def service(cls, otrs_service):
        return cls.SERVICES[otrs_service]
