# -*- coding: utf-8 -*-
from psutil import long
from zeep import Client, xsd
import base64
import os
from zeep.transports import Transport
from abc import abstractmethod, ABCMeta

from .exceptions import ServiceFacturaException
from ..generator.generator33 import GeneratorXmlThreeDotThree


class AbstractService(object):
    __metaclass__ = ABCMeta

    def __init__(self, data):
        self.__dir_xml = os.path.dirname(os.path.abspath(__file__))
        self.data = data
        self.generator = None
        # ----------------Datos del
        # Proveedor---------------------------------------------------------------------------#
        self.noCertificado = data.get('no_certificado')
        self.provider = ''
        self.username = ''
        self.password = ''
        self.csdPassword = ''
        self.urlTimbrar = ''
        self.urlsTimbrar = {}
        self.urlUtilerias = ''
        self.urlCancelar = ''
        self.urlVerificar = ''
        # ----------------Datos de Verificación------------------------------------------------------------------------#
        self.verificado = False
        self.idComprobanteVerificacion = ''
        # ----------------Datos de Cancelación-------------------------------------------------------------------------#
        self.cancelado = False
        self.acuseSat = None
        # ----------------Datos de Facturación-------------------------------------------------------------------------#
        self.versionXml = ''
        self.xmlSinTimbrar = ''
        self.xmlTimbrado = ''
        self.timbrado = False
        self.datosXml = None
        # ----------------Datos Generales------------------------------------------------------------------------------#
        self.estatus = 0
        self.mensaje = ''

    def setDatosProveedor(self, provider):
        datos_facturacion = self.data.get('datos_facturacion')
        datos = datos_facturacion.get(provider)
        self.provider = provider
        datos_acceso = datos.get('datos_acceso').get(self.noCertificado)
        self.username = datos_acceso.get('username')
        self.password = datos_acceso.get('password')
        self.csdPassword = datos_acceso.get('csd_password')
        self.urlsTimbrar = datos.get('url_timbrar')
        self.urlUtilerias = datos['url_utilerias']
        self.urlCancelar = datos['url_cancelar']
        self.urlVerificar = datos['url_verificar']

    @abstractmethod
    def timbrar(self, xmlString):
        pass

    @abstractmethod
    def cancelar(self, rfc, uuid):
        pass

    def cancelarTest(self, rfc, uuid):
        self.acuseSat = None
        if uuid == "00000000-0000-0000-0000-000000000000":
            self.cancelado = 'Requested'
        elif uuid == "FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF":
            self.cancelado = True

    @abstractmethod
    def verificar(self, rfc, xmlString):
        pass

    # ---------------------Datos de
    # Verificación------------------------------------------------------------------------#
    def get_resultado_verificacion(self):
        return self.verificado

    def get_id_comprobante_verificacion(self):
        return self.idComprobanteVerificacion

    # ---------------------Datos de
    # Cancelación-------------------------------------------------------------------------#
    def get_resultado_cancelacion(self):
        return self.cancelado

    def get_acuse_sat(self):
        return self.acuseSat.decode('utf-8')

    def get_acuse_sat_base64(self):
        return base64.b64encode(self.acuseSat).decode('utf8')

    # ---------------------Datos de
    # Facturación-------------------------------------------------------------------------#
    def get_resultado_timbrado(self):
        return self.timbrado

    def get_xml_sin_timbrar(self):
        return self.xmlSinTimbrar

    def get_xml_timbrado(self):
        return self.xmlTimbrado

    def get_datos_xml(self):
        return self.datosXml

    def get_version_xml(self):
        return self.versionXml

    # ---------------------Datos
    # Generales------------------------------------------------------------------------------#
    def get_estatus(self):
        return self.estatus

    def get_mensaje(self):
        return self.mensaje

    def get_provider(self):
        return self.provider

    def get_url_timbrar(self):
        return self.urlTimbrar

    def get_url_utilerias(self):
        return self.urlUtilerias

    def get_url_cancelar(self):
        return self.urlCancelar

    def get_url_verificar(self):
        return self.urlVerificar

    def generate_xml(self):
        try:
            if self.data.get('version') == '3.3':
                self.generator = GeneratorXmlThreeDotThree(self.data)
                self.__set_data_to_generator()
        except Exception as e:
            raise Exception(e)

    def __set_data_to_generator(self):
        self.generator.generate_xml()


class ServiceSF(AbstractService):

    def __init__(self, data):
        super(self.__class__, self).__init__(data)
        self.setDatosProveedor(data.get('provider'))

    def timbrar(self, xmlString):
        self.versionXml = self.data.get('version')
        self.xmlSinTimbrar = xmlString
        self.xmlTimbrado = ''
        self.timbrado = False
        self.urlTimbrar = self.urlsTimbrar[self.data.get('version')]
        try:
            isZipFile = False
            client = Client(self.urlTimbrar, transport = Transport(timeout = 240))
            timbrado = client.service.timbrar(self.username, self.password, xmlString, isZipFile)
            if timbrado.status == 200:
                resultados = timbrado.resultados[0]
                if resultados.status == 200:
                    self.mensaje = resultados.mensaje
                    self.estatus = resultados.status
                    self.xmlTimbrado = resultados.cfdiTimbrado
                    self.timbrado = True
                else:
                    raise ServiceFacturaException(None, self.provider, 'ValidaciónTimbrado',
                                                  status = resultados.status,
                                                  message = resultados.mensaje, typeError = 'TimbrarServiceException')
            else:
                raise ServiceFacturaException(None, self.provider, 'Timbrado', status = timbrado.status,
                                              message = timbrado.mensaje, typeError = 'TimbrarServiceException')
        except Exception as e:
            print(str(e))
            raise ServiceFacturaException(e, self.provider, 'Timbrar')

    def cancelar(self, rfc, uuid):
        self.acuseSat = None
        self.cancelado = False
        try:
            cerRead = base64.b64decode(self.data.get('certificado_base64'))
            keyRead = base64.b64decode(self.data.get('key_base64'))
            cliente = Client(self.urlCancelar, transport = Transport(timeout = 240))
            estatus = cliente.service.getStatusCancelacionAsincrona(
                usuario = self.username,
                password = self.password,
                transactionId = uuid
            )
            status = estatus.status
            mensaje = estatus.mensaje
            if status == 211:
                self.cancelado = 'InProcess'
                self.mensaje = estatus.mensaje
                self.estatus = estatus
            elif status == 200 and estatus.acuseSat:
                self.acuseSat = estatus.acuseSat
                self.cancelado = True
                self.mensaje = estatus.acuseSat
                self.estatus = estatus
            elif status == 702:
                cancelacion = cliente.service.cancelarAsincrono(
                    usuario = self.username,
                    password = self.password,
                    uuid = uuid,
                    rfcEmisor = rfc,
                    emailNotifica = '',
                    csdCer = cerRead,
                    csdKey = keyRead,
                    csdPassword = self.csdPassword
                )
                status = cancelacion.status
                mensaje = cancelacion.mensaje
                if status == 211:
                    self.cancelado = 'InProcess'
                    self.mensaje = mensaje
                    self.estatus = status
                elif status == 200 and mensaje == uuid.lower():
                    self.cancelado = 'Requested'
                    self.mensaje = mensaje
                    self.estatus = status
                elif status == 701:
                    cliente = Client(self.urlUtilerias, transport = Transport(timeout = 240))
                    buscar = cliente.service.buscar(
                        usuario = self.username,
                        password = self.password,
                        parametros = {
                            'uuid': uuid
                        }
                    )
                    if buscar.status == 200 and len(buscar.cfdis) > 0:
                        cfdi = buscar.cfdis[0]
                        if cfdi.cancelado:
                            self.cancelado = True
                            self.estatus = buscar
                        else:
                            self.cancelado = 'InProcess'
                            self.mensaje = buscar.mensaje
                            self.estatus = buscar.status
                    else:
                        raise ServiceFacturaException(
                            None,
                            self.provider,
                            'Estatus CFDI',
                            status = buscar.status,
                            message = buscar.mensaje,
                            typeError = 'ServiceFacturaException'
                        )
                else:
                    raise ServiceFacturaException(None, self.provider, 'Cancelacion', status = status,
                                                  message = mensaje, typeError = 'ServiceFacturaException')
            else:
                raise ServiceFacturaException(None, self.provider, 'EstatusCancelacion', status = status,
                                              message = mensaje, typeError = 'ServiceFacturaException')
        except Exception as e:
            raise ServiceFacturaException(e, self.provider, 'Cancelar')

    def verificar(self, rfc, xmlString):
        self.idComprobanteVerificacion = ''
        self.verificado = False
        try:
            header = xsd.ComplexType([
                xsd.Element(
                    '{http://ws.recepcion.cfdi.solucionfactible.com/}rfcReceptor',
                    xsd.String()),
                xsd.Element(
                    '{http://ws.recepcion.cfdi.solucionfactible.com/}password',
                    xsd.String()),
                xsd.Element(
                    '{http://ws.recepcion.cfdi.solucionfactible.com/}usuario',
                    xsd.String())
            ])
            header_value = header(
                rfcReceptor = rfc,
                password = self.password,
                usuario = self.username
            )
            cliente = Client(self.urlVerificar, transport = Transport(timeout = 240))
            validacion = cliente.service.valida(
                comprobante = xmlString,
                configuraciones = [{
                    'tipo': 'ValidarAddendasSinNamespacePropio',
                    'valor': False
                }, {
                    'tipo': 'ValidarAddendasConNamespacePropio',
                    'valor': False
                }],
                _soapheaders = [header_value]
            )
            estatus = long(str(validacion.estatus).replace('V', '').replace('E', ''))
            self.mensaje = validacion.mensaje
            if estatus == 200:
                self.idComprobanteVerificacion = validacion.idComprobante
                self.verificado = True
                self.mensaje = ''
                self.estatus = estatus
            else:
                mensaje = validacion.mensaje
                if len(validacion.detalleMensajes) > 0:
                    mensaje += ' ' + validacion.detalleMensajes[0]
                if 'V' in validacion.estatus:
                    raise ServiceFacturaException(None, self.provider, 'Verificado', status = estatus,
                                                  message = mensaje, typeError = 'ServiceFacturaException')
                else:
                    raise ServiceFacturaException(None, self.provider, 'Verificación', status = estatus,
                                                  message = mensaje, typeError = 'ServiceFacturaException')
        except Exception as e:
            raise ServiceFacturaException(e, self.provider, 'Verificar')

    def search_invoice(self, **kwargs):
        try:
            client = Client(self.urlUtilerias, transport = Transport(timeout = 240))
            response = client.service.buscar(
                self.username,
                self.password,
                parametros=kwargs
            )
            return response
        except Exception as e:
            raise ServiceFacturaException(e, self.provider, 'Timbrar')

    def get_status_cancelacion(self, uuid):
        try:
            cliente = Client(self.urlCancelar, transport=Transport(timeout=240))
            response = cliente.service.getStatusCancelacionAsincrona(
                usuario=self.username,
                password=self.password,
                transactionId=uuid
            )
            return response
        except Exception as e:
            raise ServiceFacturaException(e, self.provider, 'Estatuc cancelacion')