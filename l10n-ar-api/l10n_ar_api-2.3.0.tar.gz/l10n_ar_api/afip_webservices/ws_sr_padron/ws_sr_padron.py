# -*- coding: utf-8 -*-
# Segun RG 2485 – Proyecto FE v2.8 - 12/09/2016
import sys
sys.path.append("..")
from zeep import Client
from .. import config


class InvalidIdException(Exception):
    def __init__(self, msg):
        super(Exception, self).__init__(msg)


class WsSrPadron(object):
    """
    Consulta Padron A5.
    
    :param access_token: AccessToken - Token de acceso
    :param cuit: Cuit de la empresa
    :param homologation: Homologacion si es True
    :param url: Url de servicios para WsSrPadron
    """
        
    def __init__(self, access_token, cuit, homologation=True, url=None):
        if not url:
            self.url = config.service_urls.get('ws_sr_padron_a5_homologation') if homologation\
                else config.service_urls.get('ws_sr_padron_a5_production')
        else:
            self.url = url
        
        self.accessToken = access_token
        self.cuit = cuit

    def get_partner_data(self, vat):
        """
        :param vat: Numero de documentos a consultar
        :returns str: Respuesta de AFIP sobre el numero de documento
        """

        try:
            response = Client(self.url).service.getPersona(
                token=self.accessToken.token,
                sign=self.accessToken.sign,
                cuitRepresentada=self.cuit,
                idPersona=vat
            )
        except Exception as e:
            if e.args[0] == 'No existe persona con ese Id':
                raise InvalidIdException("El numero de documento {} es inexistente.".format(vat))
            if e.args[0] == 'El Id de la persona no es valido':
                raise InvalidIdException("El numero de documento {} no es valido.".format(vat))
            raise Exception(e.args[0])
        return response
