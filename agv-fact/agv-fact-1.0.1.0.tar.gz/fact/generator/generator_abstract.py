# -*- encoding: utf-8 -*-

from abc import abstractmethod, ABCMeta
from base64 import b64encode, b64decode

from xml.dom.minidom import parse
from xml.etree import ElementTree
from lxml import etree
from lxml.etree import XSLTParseError

from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

import os
import logging


class AbstractGeneratorXml(object):
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.global_data = data
        self.data = data.get('data')
        self.dir_xml = os.path.dirname(os.path.abspath(__file__))
        self.dom = parse(self.dir_xml + '/comprobante.xml')
        self.algoritmoSha = None
        self.tipo_objeto = self.data.get('tipo') # I, E, P, T
        self.complemento = self.data.get('complemento', '') # Pago, CartaPorte
        self.tipo_transporte = self.data.get('tipo_transporte', '')
        self.version = ''
        self.__cadena_original = ''
        self.cadena_original_value = ''

    @abstractmethod
    def generate_xml(self):
        pass

    def create_xml(self, certificado_file_cer64, certificado_file_pem64):
        self.generate_xml()
        if self.global_data.get('provider') == 'solucion_factible':
            self.set_certificado(certificado_file_cer64)
            self.set_sello(certificado_file_pem64)

    def get_version(self):
        """
        Obtiene la version del xml
        :return:
        """
        return self.data.get('version')

    def reset_dom(self):
        """
        Resetear el dom a 0 elementos
        :return:
        """
        self.dom = parse(self.dir_xml + '/comprobante.xml')

    def get_xml(self):
        """
        Retorna el xml en utf8
        :return:
        """
        return self.dom.toxml(encoding='UTF-8')

    def get_xml_str(self):
        """
        Retorna el xml en formato string en utf8
        :return:
        """
        return self.dom.toxml(encoding='UTF-8').decode('utf8')

    def set_certificado(self, certificado64):
        """
        Recibe el certificado abierto como archivo
        :param certificado_file:
        :return:
        """
        try:
            logging.info('OBTENIENDO EL CERTIFICADO DEL XML')
            logging.info('CERTIFICADO DEL XML DEL INGRESO_ID')
            certificadoA = [certificado64[i:i + 76] for i in range(0, len(certificado64), 76)]
            certificadoF = ''
            for val in certificadoA:
                if certificadoF != '':
                    certificadoF += ' '
                certificadoF += val.decode("utf-8")
            self.dom.setAttribute('Certificado', certificadoF)
            logging.info('SETEO DEL CERTIFICADO EN EL XML')
        except Exception as e:
            logging.error('Error al generar el certificado. Error: ' + str(e))
            raise Exception(e)

    def set_sello(self, certificado_file_pem64):
        """
        Genera el el sello y lo agrega al xml
        :param certificado_file_pem64:
        :return:
        """
        try:
            logging.info('OBTENIENDO EL SELLO DEL XML')
            certificado_file_pem_bytes = b64decode(certificado_file_pem64)
            key = RSA.importKey(certificado_file_pem_bytes)
            logging.info('OBTENIENDO LA CADENA ORIGINAL DEL XML')
            self.cadena_original_value = self.get_cadena_original(self.get_xml())
            logging.info('LA CADENA ORIGINAL DEL XML')
            digest = self.algoritmoSha.new()
            digest.update(bytes(self.cadena_original_value))
            signer = PKCS1_v1_5.new(key)
            sign = signer.sign(digest)
            sello = b64encode(sign)
            self.dom.setAttribute('Sello', sello.decode("utf-8"))
        except Exception as e:
            logging.error('Error generar el sello. Error: ' + str(e))
            raise Exception(e)

    def get_cadena_original(self, xml):
        """
        Genera la cadena original y la retorna
        :param xml:
        :return: cadena_original
        """
        try:
            if type(xml) == str:
                xml = xml.encode('utf-8')
            xml = etree.fromstring(xml)
            logging.info('PARSE DE LA CADENA ORIGINAL DEL XML')
            logging.info(self.dir_xml)
            if self.data.get('version') == '3.3':
                xslt = etree.parse(self.dir_xml + '/cadenaoriginal_3_3_local/cadenaoriginal_3_3.xslt')
            if self.data.get('version') == '4.0':
                xslt = etree.parse(self.dir_xml + '/cadenaoriginal_3_3_local/cadenaoriginal_4_0.xslt')
            logging.info('XSLT CADENA ORIGINAL DEL XML')
            parser = etree.XSLT(xslt)
            logging.info('XSLT CADENA ORIGINAL DEL XML 2')
            cadena_original = parser(xml)
            logging.info('XSLT CADENA ORIGINAL DEL XML 3')
            return cadena_original
        except XSLTParseError as e:
            logging.error(u"Hubo un error al generar la cadena original, por favor intente mas tarde: " + str(e))
            raise Exception(u"Hubo un error al generar la cadena original, por favor intente mas tarde: " + str(e))
        except Exception as e:
            logging.error('Error al leer el archivo: cadenaoriginal_' + self.data.get('version') + '.xslt:' + str(e))
            raise Exception(e)

    @property
    def cadena_original(self) -> str:
        """
        Retorna la cadena original en string
        :return: cadena_original_value
        """
        return self.cadena_original_value

    def get_datos(self, xml):
        self.__cadena_original = self.get_cadena_original(xml)
        xml_info = self.get_xml_info(xml)
        return {
            'cadena_original': str(self.__cadena_original),
            'serie': xml_info['documento'].attrib['Serie'],
            'fecha_emision': xml_info['documento'].attrib['Fecha'],
            'no_certificado': xml_info['documento'].attrib['NoCertificado'],
            'folio': xml_info['documento'].attrib['Folio'],
            'uuid': xml_info['complemento'].attrib['UUID'],
            'fecha_timbrado': xml_info['complemento'].attrib['FechaTimbrado'],
            'sello_emisor': xml_info['complemento'].attrib['SelloCFD'],
            'sello_sat': xml_info['complemento'].attrib['SelloSAT'],
            'no_certificado_sat': xml_info['complemento'].attrib['NoCertificadoSAT'],
        }

    def get_xml_info(self, xml):
        if type(xml) == str:
            xml = xml.encode('utf-8')
        root = ElementTree.fromstring(xml)
        xmlinfo = {}
        xmlinfo['xml'] = xml
        xmlinfo['documento'] = root
        indice = 0
        for doc in root:
            if doc.tag == '{http://www.sat.gob.mx/cfd/3}Complemento':
                break
            else:
                indice += 1
        for complemento_data in root[indice]:
            xmlinfo['complemento'] = complemento_data
        return xmlinfo