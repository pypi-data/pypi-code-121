# -*- coding: utf-8 -*-
# Segun RG 2485 – Proyecto FE v2.8 - 12/09/2016

from zeep import Client, helpers

from .error import AfipError
from l10n_ar_api.afip_webservices import config
from .invoice import ElectronicInvoiceValidator


class WsfeInvoiceDetails(object):
    """
    Se encarga de asignar los detalles de una invoice en
    los factories de WSFE.

    :param client: Cliente / Webservice.
    :param invoice: Objeto ElectronicInvoice para tomar los detalles.
    :param last_invoice_number: Ultimo numero de comprobante.
    """

    def __init__(self, client, invoice, last_invoice_number):
        self.client = client
        self.invoice = invoice
        self.last_invoice_number = last_invoice_number
        self.detail = None

    def get_details(self):
        """ Devuelve los detalles completos para esa factura """

        self._set_details()

        return self.detail

    def _set_details(self):
        """ Completa los detalles a enviar segun los datos del documento """

        self.detail = self._get_detail()
        self.detail.Concepto = self.invoice.concept
        self.detail.DocTipo = self.invoice.customer_document_type
        self.detail.DocNro = self.invoice.customer_document_number
        self.detail.CbteDesde = self.last_invoice_number+1
        self.detail.CbteHasta = self.last_invoice_number+1
        self.detail.CbteFch = self.invoice.document_date
        self.detail.ImpTotal = round(self.invoice.get_total_amount(), 2)
        self.detail.ImpTotConc = round(self.invoice.untaxed_amount, 2)
        self.detail.ImpNeto = round(self.invoice.taxed_amount, 2)
        self.detail.ImpOpEx = round(self.invoice.exempt_amount, 2)
        self.detail.ImpIVA = round(self.invoice.get_total_iva(), 2)
        self.detail.ImpTrib = round(self.invoice.get_total_tributes(), 2)
        if self.invoice.concept not in [2, 3]:
            self.detail.FchServDesde = ''
            self.detail.FchServHasta = ''
            # Si es factura de crédito hay que informar siempre fecha de vencimiento
            self.detail.FchVtoPago = '' if self.invoice.document_code not in [201, 206, 211] else self.invoice.payment_due_date
        else:
            self.detail.FchServDesde = self.invoice.service_from
            self.detail.FchServHasta = self.invoice.service_to
            # Para notas de crédito / débito FCE no hay que informar fecha de vencimiento de pago.
            self.detail.FchVtoPago = self.invoice.payment_due_date if self.invoice.document_code not in [202, 203, 207, 208, 212, 213] \
                else None
        self.detail.MonId = self.invoice.mon_id
        self.detail.MonCotiz = round(self.invoice.mon_cotiz, 6)
        self._set_iva()
        self._set_tributes()
        self._set_optionals()
        self._set_associated_documents()
        self._set_period()

    def _serialize_period(self, period_from, period_to):
        return self._get_period()(
            FchDesde=period_from,
            FchHasta=period_to
        )

    def _set_period(self):
        """ Agrega al detalle el periodo asociado """
        if self.invoice.period_from and self.invoice.period_to:
            self.detail.PeriodoAsoc = self._serialize_period(self.invoice.period_from, self.invoice.period_to)

    def _serialize_tribute(self, tribute):
        return self._get_tribute()(
            Id=tribute.document_code,
            BaseImp=round(tribute.taxable_base, 2),
            Alic=tribute.aliquot,
            Importe=round(tribute.amount, 2),
            Desc='Impuesto codigo {}'.format(tribute.document_code),
        )

    def _set_tributes(self):
        """ Agrega al detalle el array de tributos del documento """

        if self.invoice.array_tributes:
            self.detail.Tributos = self._get_tribute_array()([
                self._serialize_tribute(tribute) for tribute in self.invoice.array_tributes
            ])

    def _serialize_iva(self, iva):
        return self._get_iva()(
            Id=iva.document_code,
            BaseImp=round(iva.taxable_base, 2),
            Importe=round(iva.amount, 2)
        )

    def _serialize_optional(self, optional):
        return self._get_optional()(
            Id=optional.optional_id,
            Valor=optional.value,
        )

    def _serialize_associated_document(self, associated_document):
        return self._get_associated_document()(
            Tipo=associated_document.document_type,
            PtoVta=associated_document.point_of_sale,
            Nro=associated_document.number,
            Cuit=associated_document.cuit,
            CbteFch=associated_document.document_date
        )

    def _set_iva(self):
        """ Agrega al detalle el array de iva del documento """

        if self.invoice.array_iva:
            self.detail.Iva = self._get_iva_array()([
                self._serialize_iva(iva) for iva in self.invoice.array_iva
            ])

    def _set_associated_documents(self):
        if self.invoice.associated_documents:
            self.detail.CbtesAsoc = self._get_associated_document_array()([
                self._serialize_associated_document(associated) for associated in self.invoice.associated_documents
            ])

    def _set_optionals(self):
        if self.invoice.array_optionals:
            self.detail.Opcionales = self._get_optional_array()([
                self._serialize_optional(optional) for optional in self.invoice.array_optionals
            ])

    def _get_detail(self):
        return self.client.type_factory('ns0').FECAEDetRequest()

    def _get_associated_document_array(self):
        return self.client.get_type('ns0:ArrayOfCbteAsoc')

    def _get_optional_array(self):
        return self.client.get_type('ns0:ArrayOfOpcional')

    def _get_associated_document(self):
        return self.client.get_type('ns0:CbteAsoc')

    def _get_optional(self):
        return self.client.get_type('ns0:Opcional')

    def _get_iva(self):
        return self.client.get_type('ns0:AlicIva')

    def _get_iva_array(self):
        return self.client.get_type('ns0:ArrayOfAlicIva')

    def _get_tribute(self):
        return self.client.get_type('ns0:Tributo')

    def _get_tribute_array(self):
        return self.client.get_type('ns0:ArrayOfTributo')

    def _get_period(self):
        return self.client.get_type('ns0:Periodo')


class WsfeOptional(object):

    def __init__(self, optional_id, value):
        self.optional_id = optional_id
        self.value = value


class WsfeAssociatedDocument(object):

    def __init__(self, document_type, point_of_sale, number, cuit, document_date):
        self.document_type = document_type
        self.point_of_sale = point_of_sale
        self.number = number
        self.cuit = cuit
        self._document_date = None
        self.document_date = document_date

    def _parse_date(self, value):
        return value.strftime('%Y%m%d')

    @property
    def document_date(self):
        return self._document_date

    @document_date.setter
    def document_date(self, value):
        self._document_date = self._parse_date(value)


class Wsfe(object):
    """
    Factura electronica.

    :param access_token: AccessToken - Token de acceso
    :param cuit: Cuit de la empresa
    :param homologation: Homologacion si es True
    :param url: Url de servicios para Wsfe
    """

    def __init__(self, access_token, cuit, homologation=True, url=None):
        if not url:
            self.url = config.service_urls.get('wsfev1_homologation') if homologation\
                else config.service_urls.get('wsfev1_production')
        else:
            self.url = url

        self.accessToken = access_token
        self.cuit = cuit
        self.auth_request = self._create_auth_request()

    def check_webservice_status(self):
        """ Consulta el estado de los webservices de AFIP."""

        res = Client(self.url).service.FEDummy()

        if hasattr(res, 'Errors'):
            raise AfipError.parse_error(res)
        if res.AppServer != 'OK':
            raise Exception('El servidor de aplicaciones no se encuentra disponible. Intente mas tarde.')
        if res.DbServer != 'OK':
            raise Exception('El servidor de base de datos no se encuentra disponible. Intente mas tarde.')
        if res.AuthServer != 'OK':
            raise Exception('El servidor de auntenticacion no se encuentra disponible. Intente mas tarde.')

    def get_cae(self, invoices, pos):
        """
        :param invoices: Conjunto de Objetos ElectronicInvoice, documentos a enviar a AFIP.
        :param pos: Numero de punto de venta.
        :returns str: Respuesta de AFIP sobre la validacion del documento.
        """

        self._validate_invoices(invoices)
        FECAERequest = self._set_FECAERequest(invoices, pos)
        # FECAESolicitar(Auth: ns0:FEAuthRequest, FeCAEReq: ns0:FECAERequest) ->
        # FECAESolicitarResult: ns0:FECAEResponse
        return Client(self.url).service.FECAESolicitar(
            Auth=self.auth_request,
            FeCAEReq=FECAERequest
        ), FECAERequest

    def get_cotization(self, currency):
        """
        :param currency: Id de la moneda consultar
        :return: Cotización de la moneda para el día de hoy.
        """
        cotiz_response = Client(self.url).service.FEParamGetCotizacion(
            Auth=self.auth_request,
            MonId=currency,
        )
        if cotiz_response.Errors:
            raise AfipError().parse_error(cotiz_response)

        return cotiz_response.ResultGet.MonCotiz

    def show_error(self, response):
        if response.Errors:
            raise AfipError.parse_error(response)

    def get_last_number(self, pos_number, document_type_number):
        """
        :param pos_number: Numero de punto de venta
        :param document_type_number: Numero del tipo de documento segun AFIP a consultar
        :return: Numero de ultimo comprobante autorizado para ese tipo
        """

        # FECompUltimoAutorizado(Auth: ns0:FEAuthRequest, PtoVta: xsd:int, CbteTipo: xsd:int) ->
        # FECompUltimoAutorizadoResult: ns0:FERecuperaLastCbteResponse

        last_number_response = Client(self.url).service.FECompUltimoAutorizado(
            Auth=self.auth_request,
            PtoVta=pos_number,
            CbteTipo=document_type_number,
        )
        if last_number_response.Errors:
            raise AfipError().parse_error(last_number_response)

        return last_number_response.CbteNro

    def _validate_invoices(self, invoices):
        """
        Valida que los campos de la factura electronica sean validos

        :param invoices: Lista de Objetos Invoice, documentos a validar.
        """

        invoiceValidator = ElectronicInvoiceValidator()
        for invoice in invoices:
            invoiceValidator.validate_invoice(invoice)

    def _get_header(self):
        return Client(self.url).get_type('ns0:FECAECabRequest')

    def _get_cae_request(self):
        return Client(self.url).get_type('ns0:FECAERequest')

    def _get_array_cae_request(self):
        return Client(self.url).get_type('ns0:ArrayOfFECAEDetRequest')

    def _get_document_type(self, invoices):
        document_types = set([invoice.document_code for invoice in invoices])
        if len(document_types) > 1:
            raise AttributeError("Los documentos a enviar deben ser del mismo tipo")

        return next(iter(document_types))

    def _set_FECAERequest(self, invoices, pos):
        """
        :param invoices: Conjunto de objetos ElectronicInvoice.
        :param pos: Numero de punto de venta.
        :returns: FECAERequest / Envio de documentos para recibir el CAE.
        """

        header = self._set_header(invoices, pos)
        array_cae_request = self._get_array_cae_request()

        details = []
        last_invoice = self.get_last_number(header.PtoVta, header.CbteTipo)

        for invoice in invoices:
            details.append(WsfeInvoiceDetails(Client(self.url), invoice, last_invoice).get_details())
            last_invoice += 1

        cae_request = self._get_cae_request()

        # ns0:FECAERequest(FeCabReq: ns0:FECAECabRequest, FeDetReq: ns0:ArrayOfFECAEDetRequest)
        FECAERequest = cae_request(
            FeCabReq=header,
            FeDetReq=array_cae_request(details)
        )

        return FECAERequest

    def _set_header(self, invoices, pos):
        """
        :param invoices: Conjunto de Objetos ElectronicInvoice.
        :param pos: Numero de punto de venta.
        :returns: FeCabReq / cabecera de envio de documentos completo.
        """

        header_request = self._get_header()
        # ns0:FECAECabRequest(CantReg: xsd:int, PtoVta: xsd:int, CbteTipo: xsd:int)
        header = header_request(
            CantReg=len(invoices),
            PtoVta=pos,
            CbteTipo=self._get_document_type(invoices)
        )

        return header

    def _create_auth_request(self):
        """ Setea el FEAuthRequest, necesario para utilizar el resto de los metodos """

        FEAuthRequest = Client(self.url).get_type('ns0:FEAuthRequest')
        # ns0:FEAuthRequest(Token: xsd:string, Sign: xsd:string, Cuit: xsd:long)
        auth_request = FEAuthRequest(
            Token=self.accessToken.token,
            Sign=self.accessToken.sign,
            Cuit=self.cuit
        )
        return auth_request

    def retrieve_cae(self, document_type_number, inv_number, pos_number):
        """
        :param document_type_number: Numero del tipo de documento segun AFIP a consultar
        :param inv_number: nro de factura con cae a retraer
        :param pos_number: Numero de punto de venta
        :return: FECompConsultar / Detalles de la
        """
        FeCompConsReq = Client(self.url).get_type('ns0:FECompConsultaReq')
        _FeCompConsReq = FeCompConsReq(
            CbteTipo=document_type_number,
            CbteNro=inv_number,
            PtoVta=pos_number
        )

        cae_details = Client(self.url).service.FECompConsultar(
            Auth=self.auth_request,
            FeCompConsReq=_FeCompConsReq
        )
        #if cae_details.Errors:
        #    raise AfipError().parse_error(cae_details)

        res = helpers.serialize_object(cae_details)
        req = helpers.serialize_object(_FeCompConsReq)
        return res, req

