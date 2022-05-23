# coding: utf-8
from future.utils import bytes_to_native_str as n


class TelecomCompany:
    TELECOM_COMPANIES = {
        'internet': {
            'Euskaltel': 'Euskaltel',
            'Jazztel': 'Jazztel',
            'MasMovil': 'Más Móvil',
            'Movistar': 'Movistar',
            'Aire / Nubip': 'Nubip',
            'Ono': 'Ono',
            'Orange': 'Orange',
            'Parlem': 'Parlem',
            'PepePhone': 'PepePhone',
            'Som Connexió': 'SomConnexio',
            'Vodafone': 'Vodafone',
            'Vodafone-Ono': 'VodafoneOno',
            'Yoigo': 'Yoigo'
        },
        'mobile': {
            'Aire / Nubip': 'AireNubip',
            'Amena': 'Amena',
            'BT': 'BT',
            'Cable Móvil': 'CableMovil',
            'Carref': 'Carrefour',
            'DIGI Spain Telecom': 'DIGI',
            ' E-Plus España (KPN-Bankinter)': 'EPLUS',
            'Eroski': 'Eroski',
            'Euskaltel (Europa)': 'Euskaltel',
            'Fonyou': 'Fonyou',
            'GT Mobile': 'GTMobil',
            'Happy Móvil': 'HappyMovil',
            'Hits': 'Hits',
            'IOS -Pinger-Alow-Vozelia-KNET-SUOAireNubipP': 'IOS',
            'Ibercom': 'Ibercom',
            'Icatel': 'Icatel',
            'Infotelecom': 'Infotelecom',
            'Jazztel': 'Jazztel',
            'Least Cost Routing Telecom': 'LeastCostRoutingTelecom',
            'Lebara': 'Lebara',
            'Llamaya': 'Llamaya',
            'Lowi (Vodafone Enabler)': 'Lowi',
            'Lycamobile': 'Lycamobile',
            'Más Móvil': 'MasMovil',
            'More Minutes': 'MoreMinutes',
            'movistar': 'Movistar',
            'Neo Sky': 'NeoSky',
            'Oceane': 'Oceane',
            'Ono': 'Ono',
            'Orange': 'Orange',
            'Orbitel': 'Orbitel',
            'Parlem': 'Parlem',
            'Pepephone 4G': 'Pepephone4G',
            'Procono PTV Telecom': 'Procono',
            'RACC': 'RACC',
            'R Cable y Telecomunicaciones': 'RCable',
            'República Móvil': 'RepublicaMovil',
            'Sarnet': 'Sarnet',
            'Simyo': 'Simyo',
            'Som Connexió': 'SomConnexio',
            'Suop (IO S)': 'Suop',
            'Telecable Móvil': 'TelecableMovil',
            'The Phone House': 'ThePhoneHouse',
            'Tuenti': 'Tuenti',
            'Viva Mobile': 'VivaMobile',
            'Vivazzi': 'Vivazzi',
            'Vodafone-Ono': 'VodafoneOno',
            'Voz Telecom': 'VozTelecom',
            'Xphera Móviles': 'XpheraMoviles',
            'Yoigo': 'Yoigo',
            'You Mobile': 'YouMobil',
        }
    }

    def __init__(self, type, company):
        self.type = type
        self.company = company

        if not self.company:
            self.name = 'None'
        else:
            telecom_companies_by_type = self.TELECOM_COMPANIES.get(self.type, {})
            erp_name = n(self.company.name.encode('utf8'))
            self.name = telecom_companies_by_type.get(erp_name, "Other")

    def __str__(self):
        return self.name
