from fact.services.services import ServiceSF

data2 = {
    'no_certificado': '00001000000407148598',
    'provider': 'solucion_factible',
    'version': '3.3',
    'datos_facturacion': {
        'solucion_factible': {
            'datos_acceso': {
                '00001000000407148598': {
                    'username': 'testing@solucionfactible.com', 'password': 'timbrado.SF.16672',
                    'csd_password': 'Ciag2010'
                },
            },
            'url_timbrar': {
                '3.3': 'https://testing.solucionfactible.com/ws/services/Timbrado?wsdl',
                '3.2': 'https://testing.solucionfactible.com/ws/services/Timbrado?wsdl',
            },
            'url_cancelar': 'https://testing.solucionfactible.com/ws/services/Cancelacion?wsdl',
            'url_verificar': 'https://testing.solucionfactible.com/timbrado/services/ValidacionCFD?wsdl',
            'url_utilerias': 'https://testing.solucionfactible.com/ws/services/Utilerias?wsdl',
        }
    },
    'data': {
        'tipo': 'I',
        'descripcion': '',
        'conceptos': []
    }
}


class FactoryService:

    def __new__(cls, data, *args, **kwargs):
        if data.get('provider') == 'solucion_factible':
            return ServiceSF(data)
        else:
            return None


class FactoryServiceTest:

    def __new__(cls, data, *args, **kwargs):
        if data2.get('provider') == 'solucion_factible':
            return ServiceSF(data2)
        else:
            return None
