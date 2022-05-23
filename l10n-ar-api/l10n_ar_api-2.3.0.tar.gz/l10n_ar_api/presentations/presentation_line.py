# -*- coding: utf-8 -*-
import sys
import unidecode


class PresentationLine(object):
    __slots__ = []

    @staticmethod
    def factory(presentation, line_name):
        """
        :param presentation: Tipo de presentacion
        :param line_name: Nombre de la linea a completar para la presentacion
        """

        if presentation == "libroIVADigital":

            if line_name == 'ventasCbte': return LibroIvaDigitalVentasCbteLine()
            if line_name == 'ventasAlicuotas': return LibroIvaDigitalVentasAlicuotasLine()
            if line_name == "comprasCbte": return LibroIvaDigitalComprasCbteLine()
            if line_name == "comprasAlicuotas": return LibroIvaDigitalComprasAlicuotasLine()
            if line_name == "comprasImportaciones": return LibroIvaDigitalComprasImportacionesLine()
            if line_name == "creditoFiscalImportacionServ": return LibroIvaDigitalImportacionServicioCreditoFiscalLine()

        if presentation == "ventasCompras":

            if line_name == "cabecera": return PurchaseSalesPresentationCabeceraLine()
            if line_name == "ventasCbte": return PurchaseSalesPresentationVentasCbteLine()
            if line_name == "ventasAlicuotas": return PurchaseSalesPresentationVentasAlicuotasLine()
            if line_name == "comprasCbte": return PurchaseSalesPresentationComprasCbteLine()
            if line_name == "comprasAlicuotas": return PurchaseSalesPresentationComprasAlicuotasLine()
            if line_name == "comprasImportaciones": return PurchaseSalesPresentationComprasImportacionesLine()
            if line_name == "creditoFiscalImportacionServ": return PurchaseSalesPresentationCreditoFiscalImportacionServLine()

        if presentation == "sifere":

            if line_name == "retenciones": return SifereRetentionLine()
            if line_name == "percepciones": return SiferePerceptionLine()

        if presentation == "sicore":

            if line_name == "retenciones": return SicoreRetentionLine()

        if presentation == "cot":

            if line_name == "header": return StockPickingCotHeaderLine()
            if line_name == "line": return StockPickingCotLine()
            if line_name == "product": return StockPickingCotProductLine()
            if line_name == "footer": return StockPickingCotFooterLine()

        if presentation == "arba":

            if line_name == 'retenciones': return ArbaRetentionLine()
            if line_name == 'percepciones': return ArbaPerceptionLine()
            if line_name == 'percepciones2': return ArbaPerceptionLine2()

        if presentation == "padron_tucuman":

            if line_name == 'datos': return PadronTucumanDatosLine()
            if line_name == 'retper': return PadronTucumanRetPerLine()

        if presentation == "agip":

            if line_name == 'retenciones' or line_name == 'percepciones': return AgipLine()
            if line_name == 'percepciones_NC': return AgipRefundLine()

        if presentation == "sircar":

            if line_name == 'percepciones': return PerceptionSircarLine()

        if presentation == "misiones":

            if line_name == "retenciones": return RetentionMisionesLine()
            if line_name == "percepciones": return PerceptionMisionesLine()

        assert 0, "No existe la presentacion: " + presentation + ", o el tipo: " + line_name

    def _fill_and_validate_len(self, attribute, variable, length, numeric=True):
        """
        :param attribute: Atributo a validar la longitud
        :param length: Longitud que deberia tener
        """

        attribute = self._convert_to_string(attribute, variable)
        attribute = attribute.zfill(length) if numeric else (
            unidecode.unidecode(attribute).ljust(length)[:length] if sys.version_info.major >= 3 else
            unidecode.unidecode(attribute.decode('utf-8')).ljust(length)[:length]
        )

        criteria = len(attribute) > length
        if criteria:
            raise ValueError(('El valor {variable} contiene mas digitos de '
                              'los pre-establecidos').format(variable=variable))

        return attribute
    
    def _fill_or_set_to_highest(self, attribute, variable, length):
        """
        Si el atributo es más largo de lo permitido, tomo el máximo valor permitido posible (ej.: si la base de la
        retención permite hasta 11 caracteres y tengo un número con 12 -ej.: 100000000,00-, tomo 99999999,99).
        Caso contrario, relleno con ceros normalmente.
        :param attribute: Atributo a rellenar
        :param length: Longitud que deberia tener
        """
        attribute = self._convert_to_string(attribute, variable)
        if len(attribute) <= length:
            return self._fill_and_validate_len(attribute, variable, length)
        integer_part = ''.join('9' for i in range(length-3))
        fractional_part = '99'
        return ','.join([integer_part, fractional_part])

    def _convert_to_string(self, attribute, variable):
        """
        :param attribute: Atributo para pasar a str
        """
        try:
            attribute = str(attribute)
        except ValueError:
            raise ValueError('Valor {variable} erroneo o incompleto'.format(variable=variable))

        return attribute

    def get_line_string(self):

        try:
            line_string = ''.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string

    def get_values(self):
        raise NotImplementedError("Funcion get_values no implementada para esta clase")


class PurchaseSalesPresentationCabeceraLine(PresentationLine):
    __slots__ = ['_cuit', '_periodo', '_secuencia', '_sinMovimiento',
                 '_prorratearCFC', '_cFCGlobal', '_importeCFCG', '_importeCFCAD',
                 '_importeCFCP', '_importeCFnCG', '_cFCSSyOC', '_cFCCSSyOC']

    def __init__(self):
        self._cuit = None
        self._periodo = None
        self._secuencia = None
        self._sinMovimiento = None
        self._prorratearCFC = None
        self._cFCGlobal = None
        self._importeCFCG = None
        self._importeCFCAD = None
        self._importeCFCP = None
        self._importeCFnCG = None
        self._cFCSSyOC = None
        self._cFCCSSyOC = None

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 11)

    @property
    def periodo(self):
        return self._periodo

    @periodo.setter
    def periodo(self, periodo):
        self._periodo = self._fill_and_validate_len(periodo, 'periodo', 6)

    @property
    def secuencia(self):
        return self._secuencia

    @secuencia.setter
    def secuencia(self, secuencia):
        self._secuencia = self._fill_and_validate_len(secuencia, 'secuencia', 2)

    @property
    def sinMovimiento(self):
        return self._sinMovimiento

    @sinMovimiento.setter
    def sinMovimiento(self, sinMovimiento):
        self._sinMovimiento = self._fill_and_validate_len(sinMovimiento, 'sinMovimiento', 1, numeric=False)

    @property
    def prorratearCFC(self):
        return self._prorratearCFC

    @prorratearCFC.setter
    def prorratearCFC(self, prorratearCFC):
        self._prorratearCFC = self._fill_and_validate_len(prorratearCFC, 'prorratearCFC', 1, numeric=False)

    @property
    def cFCGlobal(self):
        return self._cFCGlobal

    @cFCGlobal.setter
    def cFCGlobal(self, cFCGlobal):
        self._cFCGlobal = self._fill_and_validate_len(cFCGlobal, 'cFCGlobal', 1, numeric=False)

    @property
    def importeCFCG(self):
        return self._importeCFCG

    @importeCFCG.setter
    def importeCFCG(self, importeCFCG):
        self._importeCFCG = self._fill_and_validate_len(importeCFCG, 'importeCFCG', 15)

    @property
    def importeCFCAD(self):
        return self._importeCFCAD

    @importeCFCAD.setter
    def importeCFCAD(self, importeCFCAD):
        self._importeCFCAD = self._fill_and_validate_len(importeCFCAD, 'importeCFCAD', 15)

    @property
    def importeCFCP(self):
        return self._importeCFCP

    @importeCFCP.setter
    def importeCFCP(self, importeCFCP):
        self._importeCFCP = self._fill_and_validate_len(importeCFCP, 'importeCFCP', 15)

    @property
    def importeCFnCG(self):
        return self._importeCFnCG

    @importeCFnCG.setter
    def importeCFnCG(self, importeCFnCG):
        self._importeCFnCG = self._fill_and_validate_len(importeCFnCG, 'importeCFnCG', 15)

    @property
    def cFCSSyOC(self):
        return self._cFCSSyOC

    @cFCSSyOC.setter
    def cFCSSyOC(self, cFCSSyOC):
        self._cFCSSyOC = self._fill_and_validate_len(cFCSSyOC, 'cFCSSyOC', 15)

    @property
    def cFCCSSyOC(self):
        return self._cFCCSSyOC

    @cFCCSSyOC.setter
    def cFCCSSyOC(self, cFCCSSyOC):
        self._cFCCSSyOC = self._fill_and_validate_len(cFCCSSyOC, 'cFCCSSyOC', 15)

    def get_values(self):
        values = [self.cuit, self.periodo, self.secuencia, self.sinMovimiento,
                  self.prorratearCFC, self.cFCGlobal, self.importeCFCG,
                  self.importeCFCAD, self.importeCFCP, self.importeCFnCG,
                  self.cFCSSyOC, self.cFCCSSyOC]

        return values


class PurchaseSalesPresentationVentasCbteLine(PresentationLine):
    __slots__ = ['_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante', '_numeroHasta',
                 '_codigoDocumento', '_numeroComprador', '_denominacionComprador',
                 '_importeTotal', '_importeTotalNG', '_percepcionNC', '_importeExentos',
                 '_importePercepciones', '_importePerIIBB', '_importePerIM',
                 '_importeImpInt', '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva',
                 '_codigoOperacion', '_otrosTributos', '_fechaVtoPago']

    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._numeroHasta = None
        self._codigoDocumento = None
        self._numeroComprador = None
        self._denominacionComprador = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._percepcionNC = None
        self._importeExentos = None
        self._importePercepciones = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._otrosTributos = None
        self._fechaVtoPago = None

    def get_values(self):
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.numeroHasta, self.codigoDocumento, self.numeroComprador,
                  self.denominacionComprador, self.importeTotal, self.importeTotalNG,
                  self.percepcionNC, self.importeExentos, self.importePercepciones,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.otrosTributos, self.fechaVtoPago]

        return values

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def numeroHasta(self):
        return self._numeroHasta

    @numeroHasta.setter
    def numeroHasta(self, numeroHasta):
        self._numeroHasta = self._fill_and_validate_len(numeroHasta, 'numeroHasta', 20)

    @property
    def codigoDocumento(self):
        return self._codigoDocumento

    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)

    @property
    def numeroComprador(self):
        return self._numeroComprador

    @numeroComprador.setter
    def numeroComprador(self, numeroComprador):
        self._numeroComprador = self._fill_and_validate_len(numeroComprador, 'numeroComprador', 20)

    @property
    def denominacionComprador(self):
        return self._denominacionComprador

    @denominacionComprador.setter
    def denominacionComprador(self, denominacionComprador):
        self._denominacionComprador = self._fill_and_validate_len(denominacionComprador, 'denominacionComprador', 30,
                                                                  numeric=False)

    @property
    def importeTotal(self):
        return self._importeTotal

    @importeTotal.setter
    def importeTotal(self, importeTotal):
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)

    @property
    def importeTotalNG(self):
        return self._importeTotalNG

    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)

    @property
    def percepcionNC(self):
        return self._percepcionNC

    @percepcionNC.setter
    def percepcionNC(self, percepcionNC):
        self._percepcionNC = self._fill_and_validate_len(percepcionNC, 'percepcionNC', 15)

    @property
    def importeExentos(self):
        return self._importeExentos

    @importeExentos.setter
    def importeExentos(self, importeExentos):
        self._importeExentos = self._fill_and_validate_len(importeExentos, 'importeExentos', 15)

    @property
    def importePercepciones(self):
        return self._importePercepciones

    @importePercepciones.setter
    def importePercepciones(self, importePercepciones):
        self._importePercepciones = self._fill_and_validate_len(importePercepciones, 'importePercepciones', 15)

    @property
    def importePerIIBB(self):
        return self._importePerIIBB

    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)

    @property
    def importePerIM(self):
        return self._importePerIM

    @importePerIM.setter
    def importePerIM(self, importePerIM):
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)

    @property
    def importeImpInt(self):
        return self._importeImpInt

    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva

    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)

    @property
    def codigoOperacion(self):
        return self._codigoOperacion

    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)

    @property
    def otrosTributos(self):
        return self._otrosTributos

    @otrosTributos.setter
    def otrosTributos(self, otrosTributos):
        self._otrosTributos = self._fill_and_validate_len(otrosTributos, 'otrosTributos', 15)

    @property
    def fechaVtoPago(self):
        return self._fechaVtoPago

    @fechaVtoPago.setter
    def fechaVtoPago(self, fechaVtoPago):
        self._fechaVtoPago = self._fill_and_validate_len(fechaVtoPago, 'fechaVtoPago', 8)


class PurchaseSalesPresentationVentasAlicuotasLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_importeNetoGravado', '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.importeNetoGravado, self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class PurchaseSalesPresentationComprasCbteLine(PresentationLine):
    __slots__ = ['_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante',
                 '_despachoImportacion', '_codigoDocumento', '_numeroVendedor',
                 '_denominacionVendedor', '_importeTotal', '_importeTotalNG',
                 '_importeOpExentas', '_importePerOIva', '_importePerOtrosImp',
                 '_importePerIIBB', '_importePerIM', '_importeImpInt',
                 '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva',
                 '_codigoOperacion', '_credFiscComp', '_otrosTrib',
                 '_cuitEmisor', '_denominacionEmisor', '_ivaComision']

    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._despachoImportacion = None
        self._codigoDocumento = None
        self._numeroVendedor = None
        self._denominacionVendedor = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._importeOpExentas = None
        self._importePerOIva = None
        self._importePerOtrosImp = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._credFiscComp = None
        self._otrosTrib = None
        self._cuitEmisor = None
        self._denominacionEmisor = None
        self._ivaComision = None

    def get_values(self):
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.despachoImportacion, self.codigoDocumento, self.numeroVendedor,
                  self.denominacionVendedor, self.importeTotal, self.importeTotalNG,
                  self.importeOpExentas, self.importePerOIva, self.importePerOtrosImp,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.credFiscComp, self.otrosTrib,
                  self.cuitEmisor, self.denominacionEmisor, self.ivaComision]

        return values

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def despachoImportacion(self):
        return self._despachoImportacion

    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16,
                                                                numeric=False)

    @property
    def codigoDocumento(self):
        return self._codigoDocumento

    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)

    @property
    def numeroVendedor(self):
        return self._numeroVendedor

    @numeroVendedor.setter
    def numeroVendedor(self, numeroVendedor):
        self._numeroVendedor = self._fill_and_validate_len(numeroVendedor, 'numeroVendedor', 20)

    @property
    def denominacionVendedor(self):
        return self._denominacionVendedor

    @denominacionVendedor.setter
    def denominacionVendedor(self, denominacionVendedor):
        self._denominacionVendedor = self._fill_and_validate_len(denominacionVendedor, 'denominacionVendedor', 30,
                                                                 numeric=False)

    @property
    def importeTotal(self):
        return self._importeTotal

    @importeTotal.setter
    def importeTotal(self, importeTotal):
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)

    @property
    def importeTotalNG(self):
        return self._importeTotalNG

    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)

    @property
    def importeOpExentas(self):
        return self._importeOpExentas

    @importeOpExentas.setter
    def importeOpExentas(self, importeOpExentas):
        self._importeOpExentas = self._fill_and_validate_len(importeOpExentas, 'importeOpExentas', 15)

    @property
    def importePerOIva(self):
        return self._importePerOIva

    @importePerOIva.setter
    def importePerOIva(self, importePerOIva):
        self._importePerOIva = self._fill_and_validate_len(importePerOIva, 'importePerOIva', 15)

    @property
    def importePerOtrosImp(self):
        return self._importePerOtrosImp

    @importePerOtrosImp.setter
    def importePerOtrosImp(self, importePerOtrosImp):
        self._importePerOtrosImp = self._fill_and_validate_len(importePerOtrosImp, 'importePerOtrosImp', 15)

    @property
    def importePerIIBB(self):
        return self._importePerIIBB

    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)

    @property
    def importePerIM(self):
        return self._importePerIM

    @importePerIM.setter
    def importePerIM(self, importePerIM):
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)

    @property
    def importeImpInt(self):
        return self._importeImpInt

    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva

    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)

    @property
    def codigoOperacion(self):
        return self._codigoOperacion

    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)

    @property
    def credFiscComp(self):
        return self._credFiscComp

    @credFiscComp.setter
    def credFiscComp(self, credFiscComp):
        self._credFiscComp = self._fill_and_validate_len(credFiscComp, 'credFiscComp', 15)

    @property
    def otrosTrib(self):
        return self._otrosTrib

    @otrosTrib.setter
    def otrosTrib(self, otrosTrib):
        self._otrosTrib = self._fill_and_validate_len(otrosTrib, 'otrosTrib', 15)

    @property
    def cuitEmisor(self):
        return self._cuitEmisor

    @cuitEmisor.setter
    def cuitEmisor(self, cuitEmisor):
        self._cuitEmisor = self._fill_and_validate_len(cuitEmisor, 'cuitEmisor', 11)

    @property
    def denominacionEmisor(self):
        return self._denominacionEmisor

    @denominacionEmisor.setter
    def denominacionEmisor(self, denominacionEmisor):
        self._denominacionEmisor = self._fill_and_validate_len(denominacionEmisor, 'denominacionEmisor', 30,
                                                               numeric=False)

    @property
    def ivaComision(self):
        return self._ivaComision

    @ivaComision.setter
    def ivaComision(self, ivaComision):
        self._ivaComision = self._fill_and_validate_len(ivaComision, 'ivaComision', 15)


class PurchaseSalesPresentationComprasAlicuotasLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_codigoDocVend', '_numeroIdVend', '_importeNetoGravado',
                 '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._codigoDocVend = None
        self._numeroIdVend = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.codigoDocVend, self.numeroIdVend, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def codigoDocVend(self):
        return self._codigoDocVend

    @codigoDocVend.setter
    def codigoDocVend(self, codigoDocVend):
        self._codigoDocVend = self._fill_and_validate_len(codigoDocVend, 'codigoDocVend', 2)

    @property
    def numeroIdVend(self):
        return self._numeroIdVend

    @numeroIdVend.setter
    def numeroIdVend(self, numeroIdVend):
        self._numeroIdVend = self._fill_and_validate_len(numeroIdVend, 'numeroIdVend', 20)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class PurchaseSalesPresentationComprasImportacionesLine(PresentationLine):
    __slots__ = ['_despachoImportacion', '_importeNetoGravado',
                 '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._despachoImportacion = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.despachoImportacion, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def despachoImportacion(self):
        return self._despachoImportacion

    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16,
                                                                numeric=False)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class PurchaseSalesPresentationCreditoFiscalImportacionServLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_descripcion', '_identificacionComprobante',
                 '_fechaOperacion', '_montoMonedaOriginal', '_codigoMoneda',
                 '_tipoCambio', '_cuitPrestador', '_nifPrestador', '_nombrePrestador',
                 '_alicuotaAplicable', '_fechaIngresoImpuesto', '_montoImpuesto',
                 '_impuestoComputable', '_idPago', '_cuitEntidadPago']

    def __init__(self):
        self._tipoComprobante = None
        self._descripcion = None
        self._identificacionComprobante = None
        self._fechaOperacion = None
        self._montoMonedaOriginal = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cuitPrestador = None
        self._nifPrestador = None
        self._nombrePrestador = None
        self._alicuotaAplicable = None
        self._fechaIngresoImpuesto = None
        self._montoImpuesto = None
        self._impuestoComputable = None
        self._idPago = None
        self._cuitEntidadPago = None

    def get_values(self):
        values = [self.tipoComprobante, self.descripcion, self.identificacionComprobante,
                  self.fechaOperacion, self.montoMonedaOriginal, self.codigoMoneda,
                  self.tipoCambio, self.cuitPrestador, self.nifPrestador, self.nombrePrestador,
                  self.alicuotaAplicable, self.fechaIngresoImpuesto, self.montoImpuesto,
                  self.impuestoComputable, self.idPago, self.cuitEntidadPago]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 1)

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, descripcion):
        self._descripcion = self._fill_and_validate_len(descripcion, 'descripcion', 20, numeric=False)

    @property
    def identificacionComprobante(self):
        return self._identificacionComprobante

    @identificacionComprobante.setter
    def identificacionComprobante(self, identificacionComprobante):
        self._identificacionComprobante = self._fill_and_validate_len(identificacionComprobante,
                                                                      'identificacionComprobante', 20, numeric=False)

    @property
    def fechaOperacion(self):
        return self._fechaOperacion

    @fechaOperacion.setter
    def fechaOperacion(self, fechaOperacion):
        self._fechaOperacion = self._fill_and_validate_len(fechaOperacion, 'fechaOperacion', 8)

    @property
    def montoMonedaOriginal(self):
        return self._montoMonedaOriginal

    @montoMonedaOriginal.setter
    def montoMonedaOriginal(self, montoMonedaOriginal):
        self._montoMonedaOriginal = self._fill_and_validate_len(montoMonedaOriginal, 'montoMonedaOriginal', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cuitPrestador(self):
        return self._cuitPrestador

    @cuitPrestador.setter
    def cuitPrestador(self, cuitPrestador):
        self._cuitPrestador = self._fill_and_validate_len(cuitPrestador, 'cuitPrestador', 11)

    @property
    def nifPrestador(self):
        return self._nifPrestador

    @nifPrestador.setter
    def nifPrestador(self, nifPrestador):
        self._nifPrestador = self._fill_and_validate_len(nifPrestador, 'nifPrestador', 20, numeric=False)

    @property
    def nombrePrestador(self):
        return self._nombrePrestador

    @nombrePrestador.setter
    def nombrePrestador(self, nombrePrestador):
        self._nombrePrestador = self._fill_and_validate_len(nombrePrestador, 'nombrePrestador', 30, numeric=False)

    @property
    def alicuotaAplicable(self):
        return self._alicuotaAplicable

    @alicuotaAplicable.setter
    def alicuotaAplicable(self, alicuotaAplicable):
        self._alicuotaAplicable = self._fill_and_validate_len(alicuotaAplicable, 'alicuotaAplicable', 4)

    @property
    def fechaIngresoImpuesto(self):
        return self._fechaIngresoImpuesto

    @fechaIngresoImpuesto.setter
    def fechaIngresoImpuesto(self, fechaIngresoImpuesto):
        self._fechaIngresoImpuesto = self._fill_and_validate_len(fechaIngresoImpuesto, 'fechaIngresoImpuesto', 8)

    @property
    def montoImpuesto(self):
        return self._montoImpuesto

    @montoImpuesto.setter
    def montoImpuesto(self, montoImpuesto):
        self._montoImpuesto = self._fill_and_validate_len(montoImpuesto, 'montoImpuesto', 15)

    @property
    def impuestoComputable(self):
        return self._impuestoComputable

    @impuestoComputable.setter
    def impuestoComputable(self, impuestoComputable):
        self._impuestoComputable = self._fill_and_validate_len(impuestoComputable, 'impuestoComputable', 15)

    @property
    def idPago(self):
        return self._idPago

    @idPago.setter
    def idPago(self, idPago):
        self._idPago = self._fill_and_validate_len(idPago, 'idPago', 20, numeric=False)

    @property
    def cuitEntidadPago(self):
        return self._cuitEntidadPago

    @cuitEntidadPago.setter
    def cuitEntidadPago(self, cuitEntidadPago):
        self._cuitEntidadPago = self._fill_and_validate_len(cuitEntidadPago, 'cuitEntidadPago', 11)


class LibroIvaDigitalVentasCbteLine(PresentationLine):
    __slots__ = ['_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante', '_numeroHasta',
                 '_codigoDocumento', '_numeroComprador', '_denominacionComprador',
                 '_importeTotal', '_importeTotalNG', '_percepcionNC', '_importeExentos',
                 '_importePercepciones', '_importePerIIBB', '_importePerIM',
                 '_importeImpInt', '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva',
                 '_codigoOperacion', '_otrosTributos', '_fechaVtoPago']

    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._numeroHasta = None
        self._codigoDocumento = None
        self._numeroComprador = None
        self._denominacionComprador = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._percepcionNC = None
        self._importeExentos = None
        self._importePercepciones = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._otrosTributos = None
        self._fechaVtoPago = None

    def get_values(self):
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.numeroHasta, self.codigoDocumento, self.numeroComprador,
                  self.denominacionComprador, self.importeTotal, self.importeTotalNG,
                  self.percepcionNC, self.importeExentos, self.importePercepciones,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.otrosTributos, self.fechaVtoPago]

        return values

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def numeroHasta(self):
        return self._numeroHasta

    @numeroHasta.setter
    def numeroHasta(self, numeroHasta):
        self._numeroHasta = self._fill_and_validate_len(numeroHasta, 'numeroHasta', 20)

    @property
    def codigoDocumento(self):
        return self._codigoDocumento

    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)

    @property
    def numeroComprador(self):
        return self._numeroComprador

    @numeroComprador.setter
    def numeroComprador(self, numeroComprador):
        self._numeroComprador = self._fill_and_validate_len(numeroComprador, 'numeroComprador', 20)

    @property
    def denominacionComprador(self):
        return self._denominacionComprador

    @denominacionComprador.setter
    def denominacionComprador(self, denominacionComprador):
        self._denominacionComprador = self._fill_and_validate_len(denominacionComprador, 'denominacionComprador', 30,
                                                                  numeric=False)

    @property
    def importeTotal(self):
        return self._importeTotal

    @importeTotal.setter
    def importeTotal(self, importeTotal):
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)

    @property
    def importeTotalNG(self):
        return self._importeTotalNG

    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)

    @property
    def percepcionNC(self):
        return self._percepcionNC

    @percepcionNC.setter
    def percepcionNC(self, percepcionNC):
        self._percepcionNC = self._fill_and_validate_len(percepcionNC, 'percepcionNC', 15)

    @property
    def importeExentos(self):
        return self._importeExentos

    @importeExentos.setter
    def importeExentos(self, importeExentos):
        self._importeExentos = self._fill_and_validate_len(importeExentos, 'importeExentos', 15)

    @property
    def importePercepciones(self):
        return self._importePercepciones

    @importePercepciones.setter
    def importePercepciones(self, importePercepciones):
        self._importePercepciones = self._fill_and_validate_len(importePercepciones, 'importePercepciones', 15)

    @property
    def importePerIIBB(self):
        return self._importePerIIBB

    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)

    @property
    def importePerIM(self):
        return self._importePerIM

    @importePerIM.setter
    def importePerIM(self, importePerIM):
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)

    @property
    def importeImpInt(self):
        return self._importeImpInt

    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva

    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)

    @property
    def codigoOperacion(self):
        return self._codigoOperacion

    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)

    @property
    def otrosTributos(self):
        return self._otrosTributos

    @otrosTributos.setter
    def otrosTributos(self, otrosTributos):
        self._otrosTributos = self._fill_and_validate_len(otrosTributos, 'otrosTributos', 15)

    @property
    def fechaVtoPago(self):
        return self._fechaVtoPago

    @fechaVtoPago.setter
    def fechaVtoPago(self, fechaVtoPago):
        self._fechaVtoPago = self._fill_and_validate_len(fechaVtoPago, 'fechaVtoPago', 8)


class LibroIvaDigitalVentasAlicuotasLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_importeNetoGravado', '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.importeNetoGravado, self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class LibroIvaDigitalComprasCbteLine(PresentationLine):
    __slots__ = ['_fecha', '_tipo', '_puntoDeVenta', '_numeroComprobante',
                 '_despachoImportacion', '_codigoDocumento', '_numeroVendedor',
                 '_denominacionVendedor', '_importeTotal', '_importeTotalNG',
                 '_importeOpExentas', '_importePerOIva', '_importePerOtrosImp',
                 '_importePerIIBB', '_importePerIM', '_importeImpInt',
                 '_codigoMoneda', '_tipoCambio', '_cantidadAlicIva',
                 '_codigoOperacion', '_credFiscComp', '_otrosTrib',
                 '_cuitEmisor', '_denominacionEmisor', '_ivaComision']

    def __init__(self):
        self._fecha = None
        self._tipo = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._despachoImportacion = None
        self._codigoDocumento = None
        self._numeroVendedor = None
        self._denominacionVendedor = None
        self._importeTotal = None
        self._importeTotalNG = None
        self._importeOpExentas = None
        self._importePerOIva = None
        self._importePerOtrosImp = None
        self._importePerIIBB = None
        self._importePerIM = None
        self._importeImpInt = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cantidadAlicIva = None
        self._codigoOperacion = None
        self._credFiscComp = None
        self._otrosTrib = None
        self._cuitEmisor = None
        self._denominacionEmisor = None
        self._ivaComision = None

    def get_values(self):
        values = [self.fecha, self.tipo, self.puntoDeVenta, self.numeroComprobante,
                  self.despachoImportacion, self.codigoDocumento, self.numeroVendedor,
                  self.denominacionVendedor, self.importeTotal, self.importeTotalNG,
                  self.importeOpExentas, self.importePerOIva, self.importePerOtrosImp,
                  self.importePerIIBB, self.importePerIM, self.importeImpInt,
                  self.codigoMoneda, self.tipoCambio, self.cantidadAlicIva,
                  self.codigoOperacion, self.credFiscComp, self.otrosTrib,
                  self.cuitEmisor, self.denominacionEmisor, self.ivaComision]

        return values

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def despachoImportacion(self):
        return self._despachoImportacion

    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16,
                                                                numeric=False)

    @property
    def codigoDocumento(self):
        return self._codigoDocumento

    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)

    @property
    def numeroVendedor(self):
        return self._numeroVendedor

    @numeroVendedor.setter
    def numeroVendedor(self, numeroVendedor):
        self._numeroVendedor = self._fill_and_validate_len(numeroVendedor, 'numeroVendedor', 20)

    @property
    def denominacionVendedor(self):
        return self._denominacionVendedor

    @denominacionVendedor.setter
    def denominacionVendedor(self, denominacionVendedor):
        self._denominacionVendedor = self._fill_and_validate_len(denominacionVendedor, 'denominacionVendedor', 30,
                                                                 numeric=False)

    @property
    def importeTotal(self):
        return self._importeTotal

    @importeTotal.setter
    def importeTotal(self, importeTotal):
        self._importeTotal = self._fill_and_validate_len(importeTotal, 'importeTotal', 15)

    @property
    def importeTotalNG(self):
        return self._importeTotalNG

    @importeTotalNG.setter
    def importeTotalNG(self, importeTotalNG):
        self._importeTotalNG = self._fill_and_validate_len(importeTotalNG, 'importeTotalNG', 15)

    @property
    def importeOpExentas(self):
        return self._importeOpExentas

    @importeOpExentas.setter
    def importeOpExentas(self, importeOpExentas):
        self._importeOpExentas = self._fill_and_validate_len(importeOpExentas, 'importeOpExentas', 15)

    @property
    def importePerOIva(self):
        return self._importePerOIva

    @importePerOIva.setter
    def importePerOIva(self, importePerOIva):
        self._importePerOIva = self._fill_and_validate_len(importePerOIva, 'importePerOIva', 15)

    @property
    def importePerOtrosImp(self):
        return self._importePerOtrosImp

    @importePerOtrosImp.setter
    def importePerOtrosImp(self, importePerOtrosImp):
        self._importePerOtrosImp = self._fill_and_validate_len(importePerOtrosImp, 'importePerOtrosImp', 15)

    @property
    def importePerIIBB(self):
        return self._importePerIIBB

    @importePerIIBB.setter
    def importePerIIBB(self, importePerIIBB):
        self._importePerIIBB = self._fill_and_validate_len(importePerIIBB, 'importePerIIBB', 15)

    @property
    def importePerIM(self):
        return self._importePerIM

    @importePerIM.setter
    def importePerIM(self, importePerIM):
        self._importePerIM = self._fill_and_validate_len(importePerIM, 'importePerIM', 15)

    @property
    def importeImpInt(self):
        return self._importeImpInt

    @importeImpInt.setter
    def importeImpInt(self, importeImpInt):
        self._importeImpInt = self._fill_and_validate_len(importeImpInt, 'importeImpInt', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cantidadAlicIva(self):
        return self._cantidadAlicIva

    @cantidadAlicIva.setter
    def cantidadAlicIva(self, cantidadAlicIva):
        self._cantidadAlicIva = self._fill_and_validate_len(cantidadAlicIva, 'cantidadAlicIva', 1)

    @property
    def codigoOperacion(self):
        return self._codigoOperacion

    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1, numeric=False)

    @property
    def credFiscComp(self):
        return self._credFiscComp

    @credFiscComp.setter
    def credFiscComp(self, credFiscComp):
        self._credFiscComp = self._fill_and_validate_len(credFiscComp, 'credFiscComp', 15)

    @property
    def otrosTrib(self):
        return self._otrosTrib

    @otrosTrib.setter
    def otrosTrib(self, otrosTrib):
        self._otrosTrib = self._fill_and_validate_len(otrosTrib, 'otrosTrib', 15)

    @property
    def cuitEmisor(self):
        return self._cuitEmisor

    @cuitEmisor.setter
    def cuitEmisor(self, cuitEmisor):
        self._cuitEmisor = self._fill_and_validate_len(cuitEmisor, 'cuitEmisor', 11)

    @property
    def denominacionEmisor(self):
        return self._denominacionEmisor

    @denominacionEmisor.setter
    def denominacionEmisor(self, denominacionEmisor):
        self._denominacionEmisor = self._fill_and_validate_len(denominacionEmisor, 'denominacionEmisor', 30,
                                                               numeric=False)

    @property
    def ivaComision(self):
        return self._ivaComision

    @ivaComision.setter
    def ivaComision(self, ivaComision):
        self._ivaComision = self._fill_and_validate_len(ivaComision, 'ivaComision', 15)


class LibroIvaDigitalComprasAlicuotasLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_puntoDeVenta', '_numeroComprobante',
                 '_codigoDocVend', '_numeroIdVend', '_importeNetoGravado',
                 '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._tipoComprobante = None
        self._puntoDeVenta = None
        self._numeroComprobante = None
        self._codigoDocVend = None
        self._numeroIdVend = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.tipoComprobante, self.puntoDeVenta, self.numeroComprobante,
                  self.codigoDocVend, self.numeroIdVend, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 5)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 20)

    @property
    def codigoDocVend(self):
        return self._codigoDocVend

    @codigoDocVend.setter
    def codigoDocVend(self, codigoDocVend):
        self._codigoDocVend = self._fill_and_validate_len(codigoDocVend, 'codigoDocVend', 2)

    @property
    def numeroIdVend(self):
        return self._numeroIdVend

    @numeroIdVend.setter
    def numeroIdVend(self, numeroIdVend):
        self._numeroIdVend = self._fill_and_validate_len(numeroIdVend, 'numeroIdVend', 20)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class LibroIvaDigitalComprasImportacionesLine(PresentationLine):
    __slots__ = ['_despachoImportacion', '_importeNetoGravado',
                 '_alicuotaIva', '_impuestoLiquidado']

    def __init__(self):
        self._despachoImportacion = None
        self._importeNetoGravado = None
        self._alicuotaIva = None
        self._impuestoLiquidado = None

    def get_values(self):
        values = [self.despachoImportacion, self.importeNetoGravado,
                  self.alicuotaIva, self.impuestoLiquidado]

        return values

    @property
    def despachoImportacion(self):
        return self._despachoImportacion

    @despachoImportacion.setter
    def despachoImportacion(self, despachoImportacion):
        self._despachoImportacion = self._fill_and_validate_len(despachoImportacion, 'despachoImportacion', 16,
                                                                numeric=False)

    @property
    def importeNetoGravado(self):
        return self._importeNetoGravado

    @importeNetoGravado.setter
    def importeNetoGravado(self, importeNetoGravado):
        self._importeNetoGravado = self._fill_and_validate_len(importeNetoGravado, 'importeNetoGravado', 15)

    @property
    def alicuotaIva(self):
        return self._alicuotaIva

    @alicuotaIva.setter
    def alicuotaIva(self, alicuotaIva):
        self._alicuotaIva = self._fill_and_validate_len(alicuotaIva, 'alicuotaIva', 4)

    @property
    def impuestoLiquidado(self):
        return self._impuestoLiquidado

    @impuestoLiquidado.setter
    def impuestoLiquidado(self, impuestoLiquidado):
        self._impuestoLiquidado = self._fill_and_validate_len(impuestoLiquidado, 'impuestoLiquidado', 15)


class LibroIvaDigitalImportacionServicioCreditoFiscalLine(PresentationLine):
    __slots__ = ['_tipoComprobante', '_descripcion', '_identificacionComprobante',
                 '_fechaOperacion', '_montoMonedaOriginal', '_codigoMoneda',
                 '_tipoCambio', '_cuitPrestador', '_nifPrestador', '_nombrePrestador',
                 '_alicuotaAplicable', '_fechaIngresoImpuesto', '_montoImpuesto',
                 '_impuestoComputable', '_idPago', '_cuitEntidadPago']

    def __init__(self):
        self._tipoComprobante = None
        self._descripcion = None
        self._identificacionComprobante = None
        self._fechaOperacion = None
        self._montoMonedaOriginal = None
        self._codigoMoneda = None
        self._tipoCambio = None
        self._cuitPrestador = None
        self._nifPrestador = None
        self._nombrePrestador = None
        self._alicuotaAplicable = None
        self._fechaIngresoImpuesto = None
        self._montoImpuesto = None
        self._impuestoComputable = None
        self._idPago = None
        self._cuitEntidadPago = None

    def get_values(self):
        values = [self.tipoComprobante, self.descripcion, self.identificacionComprobante,
                  self.fechaOperacion, self.montoMonedaOriginal, self.codigoMoneda,
                  self.tipoCambio, self.cuitPrestador, self.nifPrestador, self.nombrePrestador,
                  self.alicuotaAplicable, self.fechaIngresoImpuesto, self.montoImpuesto,
                  self.impuestoComputable, self.idPago, self.cuitEntidadPago]

        return values

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 1)

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, descripcion):
        self._descripcion = self._fill_and_validate_len(descripcion, 'descripcion', 20, numeric=False)

    @property
    def identificacionComprobante(self):
        return self._identificacionComprobante

    @identificacionComprobante.setter
    def identificacionComprobante(self, identificacionComprobante):
        self._identificacionComprobante = self._fill_and_validate_len(identificacionComprobante,
                                                                      'identificacionComprobante', 20, numeric=False)

    @property
    def fechaOperacion(self):
        return self._fechaOperacion

    @fechaOperacion.setter
    def fechaOperacion(self, fechaOperacion):
        self._fechaOperacion = self._fill_and_validate_len(fechaOperacion, 'fechaOperacion', 8)

    @property
    def montoMonedaOriginal(self):
        return self._montoMonedaOriginal

    @montoMonedaOriginal.setter
    def montoMonedaOriginal(self, montoMonedaOriginal):
        self._montoMonedaOriginal = self._fill_and_validate_len(montoMonedaOriginal, 'montoMonedaOriginal', 15)

    @property
    def codigoMoneda(self):
        return self._codigoMoneda

    @codigoMoneda.setter
    def codigoMoneda(self, codigoMoneda):
        self._codigoMoneda = self._fill_and_validate_len(codigoMoneda, 'codigoMoneda', 3, numeric=False)

    @property
    def tipoCambio(self):
        return self._tipoCambio

    @tipoCambio.setter
    def tipoCambio(self, tipoCambio):
        self._tipoCambio = self._fill_and_validate_len(tipoCambio, 'tipoCambio', 10)

    @property
    def cuitPrestador(self):
        return self._cuitPrestador

    @cuitPrestador.setter
    def cuitPrestador(self, cuitPrestador):
        self._cuitPrestador = self._fill_and_validate_len(cuitPrestador, 'cuitPrestador', 11)

    @property
    def nifPrestador(self):
        return self._nifPrestador

    @nifPrestador.setter
    def nifPrestador(self, nifPrestador):
        self._nifPrestador = self._fill_and_validate_len(nifPrestador, 'nifPrestador', 20, numeric=False)

    @property
    def nombrePrestador(self):
        return self._nombrePrestador

    @nombrePrestador.setter
    def nombrePrestador(self, nombrePrestador):
        self._nombrePrestador = self._fill_and_validate_len(nombrePrestador, 'nombrePrestador', 30, numeric=False)

    @property
    def alicuotaAplicable(self):
        return self._alicuotaAplicable

    @alicuotaAplicable.setter
    def alicuotaAplicable(self, alicuotaAplicable):
        self._alicuotaAplicable = self._fill_and_validate_len(alicuotaAplicable, 'alicuotaAplicable', 4)

    @property
    def fechaIngresoImpuesto(self):
        return self._fechaIngresoImpuesto

    @fechaIngresoImpuesto.setter
    def fechaIngresoImpuesto(self, fechaIngresoImpuesto):
        self._fechaIngresoImpuesto = self._fill_and_validate_len(fechaIngresoImpuesto, 'fechaIngresoImpuesto', 8)

    @property
    def montoImpuesto(self):
        return self._montoImpuesto

    @montoImpuesto.setter
    def montoImpuesto(self, montoImpuesto):
        self._montoImpuesto = self._fill_and_validate_len(montoImpuesto, 'montoImpuesto', 15)

    @property
    def impuestoComputable(self):
        return self._impuestoComputable

    @impuestoComputable.setter
    def impuestoComputable(self, impuestoComputable):
        self._impuestoComputable = self._fill_and_validate_len(impuestoComputable, 'impuestoComputable', 15)

    @property
    def idPago(self):
        return self._idPago

    @idPago.setter
    def idPago(self, idPago):
        self._idPago = self._fill_and_validate_len(idPago, 'idPago', 20, numeric=False)

    @property
    def cuitEntidadPago(self):
        return self._cuitEntidadPago

    @cuitEntidadPago.setter
    def cuitEntidadPago(self, cuitEntidadPago):
        self._cuitEntidadPago = self._fill_and_validate_len(cuitEntidadPago, 'cuitEntidadPago', 11)


class SifereLine(PresentationLine):
    __slots__ = ['_jurisdiccion', '_cuit', '_fecha',
                 '_puntoDeVenta', '_tipo', '_letra',
                 '_importe']

    def __init__(self):
        self._jurisdiccion = None
        self._cuit = None
        self._fecha = None
        self._puntoDeVenta = None
        self._tipo = None
        self._letra = None
        self._importe = None

    @property
    def jurisdiccion(self):
        return self._jurisdiccion

    @jurisdiccion.setter
    def jurisdiccion(self, jurisdiccion):
        self._jurisdiccion = self._fill_and_validate_len(jurisdiccion, 'jurisdiccion', 3)

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10)

    @property
    def puntoDeVenta(self):
        return self._puntoDeVenta

    @puntoDeVenta.setter
    def puntoDeVenta(self, puntoDeVenta):
        self._puntoDeVenta = self._fill_and_validate_len(puntoDeVenta, 'puntoDeVenta', 4)

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, tipo):
        self._tipo = self._fill_and_validate_len(tipo, 'tipo', 1)

    @property
    def letra(self):
        return self._letra

    @letra.setter
    def letra(self, letra):
        self._letra = self._fill_and_validate_len(letra, 'letra', 1)

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = self._fill_and_validate_len(importe, 'importe', 11)


class SifereRetentionLine(SifereLine):
    __slots__ = ['_numeroBase', '_numeroComprobante']

    def __init__(self):
        super(SifereRetentionLine, self).__init__()
        self._numeroBase = None
        self._numeroComprobante = None

    @property
    def numeroBase(self):
        return self._numeroBase

    @numeroBase.setter
    def numeroBase(self, numeroBase):
        self._numeroBase = self._fill_and_validate_len(numeroBase, 'numeroBase', 20)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 16)

    def get_values(self):
        values = [self._jurisdiccion, self._cuit, self._fecha, self._puntoDeVenta,
                  self._numeroComprobante, self._tipo, self._letra, self._numeroBase,
                  self._importe]

        return values


class SiferePerceptionLine(SifereLine):
    __slots__ = ['_numeroComprobante']

    def __init__(self):
        super(SiferePerceptionLine, self).__init__()
        self._numeroComprobante = None

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 8)

    def get_values(self):
        values = [self._jurisdiccion, self._cuit, self._fecha, self._puntoDeVenta,
                  self._numeroComprobante, self._tipo, self._letra, self._importe]

        return values


class SicoreLine(PresentationLine):
    __slots__ = []


class SicoreRetentionLine(SicoreLine):
    __slots__ = ['_codigoComprobante', '_fechaDocumento', '_referenciaDocumento',
                 '_importeDocumento', '_codigoImpuesto', '_codigoRegimen',
                 '_codigoOperacion', '_base', '_fecha', '_codigoCondicion',
                 '_retencionPracticadaSS', '_importe', '_porcentaje', '_fechaEmision',
                 '_codigoDocumento', '_cuit', '_numeroCertificado']

    def __init__(self):
        super(SicoreRetentionLine, self).__init__()
        self._codigoComprobante = None
        self._fechaDocumento = None
        self._referenciaDocumento = None
        self._importeDocumento = None
        self._codigoImpuesto = None
        self._codigoRegimen = None
        self._codigoOperacion = None
        self._base = None
        self._fecha = None
        self._codigoCondicion = None
        self._retencionPracticadaSS = None
        self._importe = None
        self._porcentaje = None
        self._fechaEmision = None
        self._codigoDocumento = None
        self._cuit = None
        self._numeroCertificado = None

    @property
    def codigoComprobante(self):
        return self._codigoComprobante

    @codigoComprobante.setter
    def codigoComprobante(self, codigoComprobante):
        self._codigoComprobante = self._fill_and_validate_len(codigoComprobante, 'codigoComprobante', 2)

    @property
    def fechaDocumento(self):
        return self._fechaDocumento

    @fechaDocumento.setter
    def fechaDocumento(self, fechaDocumento):
        self._fechaDocumento = self._fill_and_validate_len(fechaDocumento, 'fechaDocumento', 10)

    @property
    def referenciaDocumento(self):
        return self._referenciaDocumento

    @referenciaDocumento.setter
    def referenciaDocumento(self, referenciaDocumento):
        self._referenciaDocumento = self._fill_and_validate_len(referenciaDocumento, 'referenciaDocumento', 16)

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = self._fill_and_validate_len(importe, 'importe', 14)

    @property
    def codigoImpuesto(self):
        return self._codigoImpuesto

    @codigoImpuesto.setter
    def codigoImpuesto(self, codigoImpuesto):
        self._codigoImpuesto = self._fill_and_validate_len(codigoImpuesto, 'codigoImpuesto', 4)

    @property
    def codigoRegimen(self):
        return self._codigoRegimen

    @codigoRegimen.setter
    def codigoRegimen(self, codigoRegimen):
        self._codigoRegimen = self._fill_and_validate_len(codigoRegimen, 'codigoRegimen', 3)

    @property
    def codigoOperacion(self):
        return self._codigoOperacion

    @codigoOperacion.setter
    def codigoOperacion(self, codigoOperacion):
        self._codigoOperacion = self._fill_and_validate_len(codigoOperacion, 'codigoOperacion', 1)

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, base):
        self._base = self._fill_and_validate_len(base, 'base', 14)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10)

    @property
    def codigoCondicion(self):
        return self._codigoCondicion

    @codigoCondicion.setter
    def codigoCondicion(self, codigoCondicion):
        self._codigoCondicion = self._fill_and_validate_len(codigoCondicion, 'codigoCondicion', 2)

    @property
    def retencionPracticadaSS(self):
        return self._retencionPracticadaSS

    @retencionPracticadaSS.setter
    def retencionPracticadaSS(self, retencionPracticadaSS):
        self._retencionPracticadaSS = self._fill_and_validate_len(retencionPracticadaSS, 'retencionPracticadaSS', 1)

    @property
    def importeDocumento(self):
        return self._importeDocumento

    @importeDocumento.setter
    def importeDocumento(self, importeDocumento):
        self._importeDocumento = self._fill_and_validate_len(importeDocumento, 'importeDocumento', 16)

    @property
    def porcentaje(self):
        return self._porcentaje

    @porcentaje.setter
    def porcentaje(self, porcentaje):
        self._porcentaje = self._fill_and_validate_len(porcentaje, 'porcentaje', 6)

    @property
    def fechaEmision(self):
        return self._fechaEmision

    @fechaEmision.setter
    def fechaEmision(self, fechaEmision):
        self._fechaEmision = self._fill_and_validate_len(fechaEmision, 'fechaEmision', 10)

    @property
    def codigoDocumento(self):
        return self._codigoDocumento

    @codigoDocumento.setter
    def codigoDocumento(self, codigoDocumento):
        self._codigoDocumento = self._fill_and_validate_len(codigoDocumento, 'codigoDocumento', 2)

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 20)

    @property
    def numeroCertificado(self):
        return self._numeroCertificado

    @numeroCertificado.setter
    def numeroCertificado(self, numeroCertificado):
        self._numeroCertificado = self._fill_and_validate_len(numeroCertificado, 'numeroCertificado', 14)

    def get_values(self):
        values = [self._codigoComprobante,
                  self._fechaDocumento,
                  self._referenciaDocumento,
                  self._importeDocumento,
                  self._codigoImpuesto,
                  self._codigoRegimen,
                  self._codigoOperacion,
                  self._base,
                  self._fecha,
                  self._codigoCondicion,
                  self._retencionPracticadaSS,
                  self._importe,
                  self._porcentaje,
                  self._fechaEmision,
                  self._codigoDocumento,
                  self._cuit,
                  self._numeroCertificado, ]

        return values


class StockPickingCotLine(PresentationLine):
    __slots__ = ['_tipoRegistro', '_fechaEmision', '_codigoUnico',
                 '_fechaSalidaTransporte', '_horaSalidaTransporte', '_sujetoGenerador',
                 '_destinatarioConsumidorFinal', '_destinatarioTipoDocumento', '_destinatarioDocumento',
                 '_codigoCondicion',
                 '_destinatarioCuit', '_destinatarioRazonSocial', '_destinatarioTenedor', '_destinoDomicilioCalle',
                 '_destinoDomicilioNumero', '_destinoDomicilioComple', '_destinoDomicilioPiso', '_destinoDomicilioDto',
                 '_destinoDomicilioBarrio', '_destinoDomicilioCodigoPostal', '_destinoDomicilioLocalidad',
                 '_destinoDomicilioProvincia', '_propioDestinoDomicilioCodigo', '_entregaDomicilioOrigen',
                 '_origenCuit', '_origenRazonSocial', '_emisorTenedor', '_origenDomicilioCalle',
                 '_origenDomicilioNumero', '_origenDomicilioComple', '_origenDomicilioPiso', '_origenDomicilioDto',
                 '_origenDomicilioBarrio', '_origenDomicilioCodigoPostal', '_origenDomicilioLocalidad',
                 '_origenDomicilioProvincia', '_transportistaCuit', '_tipoRecorrido',
                 '_recorridoLocalidad', '_recorridoCalle', '_recorridoRuta', '_patenteVehiculo', '_patenteAcoplado',
                 '_productoNoTermDev', '_importe']

    def __init__(self):
        super(StockPickingCotLine, self).__init__()
        self._tipoRegistro = None
        self._fechaEmision = None
        self._codigoUnico = None
        self._fechaSalidaTransporte = None
        self._horaSalidaTransporte = None
        self._sujetoGenerador = None
        self._destinatarioConsumidorFinal = None
        self._destinatarioTipoDocumento = None
        self._destinatarioDocumento = None
        self._destinatarioCuit = None
        self._destinatarioRazonSocial = None
        self._destinatarioTenedor = None
        self._destinoDomicilioCalle = None
        self._destinoDomicilioNumero = None
        self._destinoDomicilioComple = None
        self._destinoDomicilioPiso = None
        self._destinoDomicilioDto = None
        self._destinoDomicilioBarrio = None
        self._destinoDomicilioCodigoPostal = None
        self._destinoDomicilioLocalidad = None
        self._destinoDomicilioProvincia = None
        self._propioDestinoDomicilioCodigo = None
        self._entregaDomicilioOrigen = None
        self._origenCuit = None
        self._origenRazonSocial = None
        self._emisorTenedor = None
        self._origenDomicilioCalle = None
        self._origenDomicilioNumero = None
        self._origenDomicilioComple = None
        self._origenDomicilioPiso = None
        self._origenDomicilioDto = None
        self._origenDomicilioBarrio = None
        self._origenDomicilioCodigoPostal = None
        self._origenDomicilioLocalidad = None
        self._origenDomicilioProvincia = None
        self._transportistaCuit = None
        self._tipoRecorrido = None
        self._recorridoLocalidad = None
        self._recorridoCalle = None
        self._recorridoRuta = None
        self._patenteVehiculo = None
        self._patenteAcoplado = None
        self._productoNoTermDev = None
        self._importe = None

    @property
    def tipoRegistro(self):
        return self._tipoRegistro

    @tipoRegistro.setter
    def tipoRegistro(self, tipoRegistro):
        self._tipoRegistro = self._fill_and_validate_len(tipoRegistro,
                                                         'tipoRegistro', 2, False)

    @property
    def fechaEmision(self):
        return self._fechaEmision

    @fechaEmision.setter
    def fechaEmision(self, fechaEmision):
        self._fechaEmision = self._fill_and_validate_len(fechaEmision,
                                                         'fechaEmision', 8, False)

    @property
    def codigoUnico(self):
        return self._codigoUnico

    @codigoUnico.setter
    def codigoUnico(self, codigoUnico):
        self._codigoUnico = self._fill_and_validate_len(codigoUnico,
                                                        'codigoUnico', 16, False)

    @property
    def fechaSalidaTransporte(self):
        return self._fechaSalidaTransporte

    @fechaSalidaTransporte.setter
    def fechaSalidaTransporte(self, fechaSalidaTransporte):
        self._fechaSalidaTransporte = self._fill_and_validate_len(fechaSalidaTransporte,
                                                                  'fechaSalidaTransporte', 8, False)

    @property
    def horaSalidaTransporte(self):
        return self._horaSalidaTransporte

    @horaSalidaTransporte.setter
    def horaSalidaTransporte(self, horaSalidaTransporte):
        self._horaSalidaTransporte = self._fill_and_validate_len(horaSalidaTransporte,
                                                                 'horaSalidaTransporte', 4, False)

    @property
    def sujetoGenerador(self):
        return self._sujetoGenerador

    @sujetoGenerador.setter
    def sujetoGenerador(self, sujetoGenerador):
        self._sujetoGenerador = self._fill_and_validate_len(sujetoGenerador,
                                                            'sujetoGenerador', 1, False)

    @property
    def destinatarioConsumidorFinal(self):
        return self._destinatarioConsumidorFinal

    @destinatarioConsumidorFinal.setter
    def destinatarioConsumidorFinal(self, destinatarioConsumidorFinal):
        self._destinatarioConsumidorFinal = self._fill_and_validate_len(destinatarioConsumidorFinal,
                                                                         'destinatarioConsumidorFinal', 1, False)

    @property
    def destinatarioTipoDocumento(self):
        return self._destinatarioTipoDocumento

    @destinatarioTipoDocumento.setter
    def destinatarioTipoDocumento(self, destinatarioTipoDocumento):
        self._destinatarioTipoDocumento = self._fill_and_validate_len(destinatarioTipoDocumento,
                                                                    'destinatarioTipoDocumento', 3, False)

    @property
    def destinatarioDocumento(self):
        return self._destinatarioDocumento

    @destinatarioDocumento.setter
    def destinatarioDocumento(self, destinatarioDocumento):
        self._destinatarioDocumento = self._fill_and_validate_len(destinatarioDocumento,
                                                                  'destinatarioDocumento', 11, False)

    @property
    def destinatarioCuit(self):
        return self._destinatarioCuit

    @destinatarioCuit.setter
    def destinatarioCuit(self, destinatarioCuit):
        self._destinatarioCuit = self._fill_and_validate_len(destinatarioCuit,
                                                             'destinatarioCuit', 11, False)

    @property
    def destinatarioRazonSocial(self):
        return self._destinatarioRazonSocial

    @destinatarioRazonSocial.setter
    def destinatarioRazonSocial(self, destinatarioRazonSocial):
        self._destinatarioRazonSocial = self._fill_and_validate_len(destinatarioRazonSocial,
                                                                    'destinatarioRazonSocial', 50, False)

    @property
    def destinatarioTenedor(self):
        return self._destinatarioTenedor

    @destinatarioTenedor.setter
    def destinatarioTenedor(self, destinatarioTenedor):
        self._destinatarioTenedor = self._fill_and_validate_len(destinatarioTenedor,
                                                                'destinatarioTenedor', 1, False)

    @property
    def destinoDomicilioCalle(self):
        return self._destinoDomicilioCalle

    @destinoDomicilioCalle.setter
    def destinoDomicilioCalle(self, destinoDomicilioCalle):
        self._destinoDomicilioCalle = self._fill_and_validate_len(destinoDomicilioCalle,
                                                                  'destinoDomicilioCalle', 40, False)

    @property
    def destinoDomicilioNumero(self):
        return self._destinoDomicilioNumero

    @destinoDomicilioNumero.setter
    def destinoDomicilioNumero(self, destinoDomicilioNumero):
        self._destinoDomicilioNumero = self._fill_and_validate_len(destinoDomicilioNumero,
                                                                  'destinoDomicilioNumero', 5, False)

    @property
    def destinoDomicilioComple(self):
        return self._destinoDomicilioComple

    @destinoDomicilioComple.setter
    def destinoDomicilioComple(self, destinoDomicilioComple):
        self._destinoDomicilioComple = self._fill_and_validate_len(destinoDomicilioComple,
                                                                   'destinoDomicilioComple', 5, False)

    @property
    def destinoDomicilioPiso(self):
        return self._destinoDomicilioPiso

    @destinoDomicilioPiso.setter
    def destinoDomicilioPiso(self, destinoDomicilioPiso):
        self._destinoDomicilioPiso = self._fill_and_validate_len(destinoDomicilioPiso,
                                                                 'destinoDomicilioPiso', 3, False)

    @property
    def destinoDomicilioDto(self):
        return self._destinoDomicilioDto

    @destinoDomicilioDto.setter
    def destinoDomicilioDto(self, destinoDomicilioDto):
        self._destinoDomicilioDto = self._fill_and_validate_len(destinoDomicilioDto,
                                                                'destinoDomicilioDto', 4, False)

    @property
    def destinoDomicilioBarrio(self):
        return self._destinoDomicilioBarrio

    @destinoDomicilioBarrio.setter
    def destinoDomicilioBarrio(self, destinoDomicilioBarrio):
        self._destinoDomicilioBarrio = self._fill_and_validate_len(destinoDomicilioBarrio,
                                                                   'destinoDomicilioBarrio', 30, False)

    @property
    def destinoDomicilioCodigoPostal(self):
        return self._destinoDomicilioCodigoPostal

    @destinoDomicilioCodigoPostal.setter
    def destinoDomicilioCodigoPostal(self, destinoDomicilioCodigoPostal):
        self._destinoDomicilioCodigoPostal = self._fill_and_validate_len(destinoDomicilioCodigoPostal,
                                                                         'destinoDomicilioCodigoPostal', 8, False)

    @property
    def destinoDomicilioLocalidad(self):
        return self._destinoDomicilioLocalidad

    @destinoDomicilioLocalidad.setter
    def destinoDomicilioLocalidad(self, destinoDomicilioLocalidad):
        self._destinoDomicilioLocalidad = self._fill_and_validate_len(destinoDomicilioLocalidad,
                                                                      'destinoDomicilioLocalidad', 50, False)

    @property
    def destinoDomicilioProvincia(self):
        return self._destinoDomicilioProvincia

    @destinoDomicilioProvincia.setter
    def destinoDomicilioProvincia(self, destinoDomicilioProvincia):
        self._destinoDomicilioProvincia = self._fill_and_validate_len(destinoDomicilioProvincia,
                                                                      'destinoDomicilioProvincia', 1, False)

    @property
    def propioDestinoDomicilioCodigo(self):
        return self._propioDestinoDomicilioCodigo

    @propioDestinoDomicilioCodigo.setter
    def propioDestinoDomicilioCodigo(self, propioDestinoDomicilioCodigo):
        self._propioDestinoDomicilioCodigo = self._fill_and_validate_len(propioDestinoDomicilioCodigo,
                                                                         'propioDestinoDomicilioCodigo', 20, False)

    @property
    def entregaDomicilioOrigen(self):
        return self._entregaDomicilioOrigen

    @entregaDomicilioOrigen.setter
    def entregaDomicilioOrigen(self, entregaDomicilioOrigen):
        self._entregaDomicilioOrigen = self._fill_and_validate_len(entregaDomicilioOrigen,
                                                                   'entregaDomicilioOrigen', 20, False)

    @property
    def origenCuit(self):
        return self._origenCuit

    @origenCuit.setter
    def origenCuit(self, origenCuit):
        self._origenCuit = self._fill_and_validate_len(origenCuit,
                                                       'origenCuit', 11, False)

    @property
    def origenRazonSocial(self):
        return self._origenRazonSocial

    @origenRazonSocial.setter
    def origenRazonSocial(self, origenRazonSocial):
        self._origenRazonSocial = self._fill_and_validate_len(origenRazonSocial,
                                                              'origenRazonSocial', 50, False)

    @property
    def emisorTenedor(self):
        return self._emisorTenedor

    @emisorTenedor.setter
    def emisorTenedor(self, emisorTenedor):
        self._emisorTenedor = self._fill_and_validate_len(emisorTenedor,
                                                          'emisorTenedor', 1, False)

    @property
    def origenDomicilioCalle(self):
        return self._origenDomicilioCalle

    @origenDomicilioCalle.setter
    def origenDomicilioCalle(self, origenDomicilioCalle):
        self._origenDomicilioCalle = self._fill_and_validate_len(origenDomicilioCalle,
                                                                 'origenDomicilioCalle', 40, False)

    @property
    def origenDomicilioNumero(self):
        return self._origenDomicilioNumero

    @origenDomicilioNumero.setter
    def origenDomicilioNumero(self, origenDomicilioNumero):
        self._origenDomicilioNumero = self._fill_and_validate_len(origenDomicilioNumero,
                                                                  'origenDomicilioNumero', 5, False)

    @property
    def origenDomicilioComple(self):
        return self._origenDomicilioComple

    @origenDomicilioComple.setter
    def origenDomicilioComple(self, origenDomicilioComple):
        self._origenDomicilioComple = self._fill_and_validate_len(origenDomicilioComple,
                                                                  'origenDomicilioComple', 5, False)

    @property
    def origenDomicilioPiso(self):
        return self._origenDomicilioPiso

    @origenDomicilioPiso.setter
    def origenDomicilioPiso(self, origenDomicilioPiso):
        self._origenDomicilioPiso = self._fill_and_validate_len(origenDomicilioPiso,
                                                                'origenDomicilioPiso', 3, False)

    @property
    def origenDomicilioDto(self):
        return self._origenDomicilioDto

    @origenDomicilioDto.setter
    def origenDomicilioDto(self, origenDomicilioDto):
        self._origenDomicilioDto = self._fill_and_validate_len(origenDomicilioDto,
                                                               'origenDomicilioDto', 4, False)
        
    @property
    def origenDomicilioBarrio(self):
        return self._origenDomicilioBarrio

    @origenDomicilioBarrio.setter
    def origenDomicilioBarrio(self, origenDomicilioBarrio):
        self._origenDomicilioBarrio = self._fill_and_validate_len(origenDomicilioBarrio,
                                                                  'origenDomicilioBarrio', 30, False)
        
    @property
    def origenDomicilioCodigoPostal(self):
        return self._origenDomicilioCodigoPostal

    @origenDomicilioCodigoPostal.setter
    def origenDomicilioCodigoPostal(self, origenDomicilioCodigoPostal):
        self._origenDomicilioCodigoPostal = self._fill_and_validate_len(origenDomicilioCodigoPostal,
                                                                        'origenDomicilioCodigoPostal', 8, False)
    
    @property
    def origenDomicilioLocalidad(self):
        return self._origenDomicilioLocalidad

    @origenDomicilioLocalidad.setter
    def origenDomicilioLocalidad(self, origenDomicilioLocalidad):
        self._origenDomicilioLocalidad = self._fill_and_validate_len(origenDomicilioLocalidad,
                                                                     'origenDomicilioLocalidad', 50, False)
    
    @property
    def origenDomicilioProvincia(self):
        return self._origenDomicilioProvincia

    @origenDomicilioProvincia.setter
    def origenDomicilioProvincia(self, origenDomicilioProvincia):
        self._origenDomicilioProvincia = self._fill_and_validate_len(origenDomicilioProvincia,
                                                                     'origenDomicilioProvincia', 1)

    @property
    def transportistaCuit(self):
        return self._transportistaCuit

    @transportistaCuit.setter
    def transportistaCuit(self, transportistaCuit):
        self._transportistaCuit = self._fill_and_validate_len(transportistaCuit,
                                                              'transportistaCuit', 11, False)

    @property
    def tipoRecorrido(self):
        return self._tipoRecorrido

    @tipoRecorrido.setter
    def tipoRecorrido(self, tipoRecorrido):
        self._tipoRecorrido = self._fill_and_validate_len(tipoRecorrido,
                                                          'tipoRecorrido', 1, False)

    @property
    def recorridoLocalidad(self):
        return self._recorridoLocalidad

    @recorridoLocalidad.setter
    def recorridoLocalidad(self, recorridoLocalidad):
        self._recorridoLocalidad = self._fill_and_validate_len(recorridoLocalidad,
                                                               'recorridoLocalidad', 50, False)

    @property
    def recorridoCalle(self):
        return self._recorridoCalle

    @recorridoCalle.setter
    def recorridoCalle(self, recorridoCalle):
        self._recorridoCalle = self._fill_and_validate_len(recorridoCalle,
                                                           'recorridoCalle', 40, False)

    @property
    def recorridoRuta(self):
        return self._recorridoRuta

    @recorridoRuta.setter
    def recorridoRuta(self, recorridoRuta):
        self._recorridoRuta = self._fill_and_validate_len(recorridoRuta,
                                                          'recorridoRuta', 40, False)

    @property
    def patenteVehiculo(self):
        return self._patenteVehiculo

    @patenteVehiculo.setter
    def patenteVehiculo(self, patenteVehiculo):
        self._patenteVehiculo = self._fill_and_validate_len(patenteVehiculo,
                                                            'patenteVehiculo', 7, False)

    @property
    def patenteAcoplado(self):
        return self._patenteAcoplado

    @patenteAcoplado.setter
    def patenteAcoplado(self, patenteAcoplado):
        self._patenteAcoplado = self._fill_and_validate_len(patenteAcoplado,
                                                            'patenteAcoplado', 7, False)

    @property
    def productoNoTermDev(self):
        return self._productoNoTermDev

    @productoNoTermDev.setter
    def productoNoTermDev(self, productoNoTermDev):
        self._productoNoTermDev = self._fill_and_validate_len(productoNoTermDev,
                                                              'productoNoTermDev', 1, False)

    @property
    def importe(self):
        return self._importe

    @importe.setter
    def importe(self, importe):
        self._importe = self._fill_and_validate_len(importe,
                                                    'importe', 10)

    def get_values(self):
        values = [
            self._tipoRegistro,
            self._fechaEmision,
            self._codigoUnico,
            self._fechaSalidaTransporte,
            self._horaSalidaTransporte,
            self._sujetoGenerador,
            self._destinatarioConsumidorFinal,
            self._destinatarioTipoDocumento,
            self._destinatarioDocumento,
            self._destinatarioCuit,
            self._destinatarioRazonSocial,
            self._destinatarioTenedor,
            self._destinoDomicilioCalle,
            self._destinoDomicilioNumero,
            self._destinoDomicilioComple,
            self._destinoDomicilioPiso,
            self._destinoDomicilioDto,
            self._destinoDomicilioBarrio,
            self._destinoDomicilioCodigoPostal,
            self._destinoDomicilioLocalidad,
            self._destinoDomicilioProvincia,
            self._propioDestinoDomicilioCodigo,
            self._entregaDomicilioOrigen,
            self._origenCuit,
            self._origenRazonSocial,
            self._emisorTenedor,
            self._origenDomicilioCalle,
            self._origenDomicilioNumero,
            self._origenDomicilioComple,
            self._origenDomicilioPiso,
            self._origenDomicilioDto,
            self._origenDomicilioBarrio,
            self._origenDomicilioCodigoPostal,
            self._origenDomicilioLocalidad,
            self._origenDomicilioProvincia,
            self._transportistaCuit,
            self._tipoRecorrido,
            self._recorridoLocalidad,
            self._recorridoCalle,
            self._recorridoRuta,
            self._patenteVehiculo,
            self._patenteAcoplado,
            self._productoNoTermDev,
            self._importe
        ]

        return values

    def get_line_string(self):

        try:
            line_string = '|'.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class StockPickingCotHeaderLine(PresentationLine):
    __slots__ = [
        '_tipoRegistro', '_cuitEmpresa'
    ]

    def __init__(self):
        super(StockPickingCotHeaderLine, self).__init__()
        self._tipoRegistro = None
        self._cuitEmpresa = None

    @property
    def tipoRegistro(self):
        return self._tipoRegistro

    @tipoRegistro.setter
    def tipoRegistro(self, tipoRegistro):
        self._tipoRegistro = self._fill_and_validate_len(tipoRegistro, 'tipoRegistro', 2, False)

    @property
    def cuitEmpresa(self):
        return self._cuitEmpresa

    @cuitEmpresa.setter
    def cuitEmpresa(self, cuitEmpresa):
        self._cuitEmpresa = self._fill_and_validate_len(cuitEmpresa, 'cuitEmpresa', 11, False)

    def get_values(self):
        values = [
            self._tipoRegistro,
            self._cuitEmpresa,
        ]

        return values

    def get_line_string(self):

        try:
            line_string = '|'.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class StockPickingCotFooterLine(PresentationLine):
    __slots__ = [
        '_tipoRegistro', '_cantidadTotalRemitos'
    ]

    def __init__(self):
        super(StockPickingCotFooterLine, self).__init__()
        self._tipoRegistro = None
        self._cantidadTotalRemitos = None

    @property
    def tipoRegistro(self):
        return self._tipoRegistro

    @tipoRegistro.setter
    def tipoRegistro(self, tipoRegistro):
        self._tipoRegistro = self._fill_and_validate_len(tipoRegistro,
                                                         'tipoRegistro', 2, False)

    @property
    def cantidadTotalRemitos(self):
        return self._cantidadTotalRemitos

    @cantidadTotalRemitos.setter
    def cantidadTotalRemitos(self, cantidadTotalRemitos):
        self._cantidadTotalRemitos = self._fill_and_validate_len(cantidadTotalRemitos,
                                                                 'cantidadTotalRemitos', 10, False)

    def get_values(self):
        values = [
            self._tipoRegistro,
            self._cantidadTotalRemitos,
        ]

        return values

    def get_line_string(self):

        try:
            line_string = '|'.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class StockPickingCotProductLine(PresentationLine):
    __slots__ = [
        '_tipoRegistro', '_codigoUnicoProducto', '_rentasCodigoUnidadMedida',
        '_cantidad', '_propioCodigoProducto', '_propioDescripcionProducto',
        '_propioDescripcionUnidadMedida', '_cantidadAjustada'
    ]

    def __init__(self):
        super(StockPickingCotProductLine, self).__init__()
        self._tipoRegistro = None
        self._codigoUnicoProducto = None
        self._rentasCodigoUnidadMedida = None
        self._cantidad = None
        self._propioCodigoProducto = None
        self._propioDescripcionProducto = None
        self._propioDescripcionUnidadMedida = None
        self._cantidadAjustada = None

    @property
    def tipoRegistro(self):
        return self._tipoRegistro

    @tipoRegistro.setter
    def tipoRegistro(self, tipoRegistro):
        self._tipoRegistro = self._fill_and_validate_len(tipoRegistro,
                                                         'tipoRegistro', 2, False)

    @property
    def codigoUnicoProducto(self):
        return self._codigoUnicoProducto

    @codigoUnicoProducto.setter
    def codigoUnicoProducto(self, codigoUnicoProducto):
        self._codigoUnicoProducto = self._fill_and_validate_len(codigoUnicoProducto,
                                                                'codigoUnicoProducto', 6, False)

    @property
    def rentasCodigoUnidadMedida(self):
        return self._rentasCodigoUnidadMedida

    @rentasCodigoUnidadMedida.setter
    def rentasCodigoUnidadMedida(self, rentasCodigoUnidadMedida):
        self._rentasCodigoUnidadMedida = self._fill_and_validate_len(rentasCodigoUnidadMedida,
                                                                     'rentasCodigoUnidadMedida', 1, False)

    @property
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, cantidad):
        self._cantidad = self._fill_and_validate_len(cantidad,
                                                     'cantidad', 15)

    @property
    def propioCodigoProducto(self):
        return self._propioCodigoProducto

    @propioCodigoProducto.setter
    def propioCodigoProducto(self, propioCodigoProducto):
        self._propioCodigoProducto = self._fill_and_validate_len(propioCodigoProducto,
                                                                 'propioCodigoProducto', 25, False)
        
    @property
    def propioDescripcionProducto(self):
        return self._propioDescripcionProducto

    @propioDescripcionProducto.setter
    def propioDescripcionProducto(self, propioDescripcionProducto):
        self._propioDescripcionProducto = self._fill_and_validate_len(propioDescripcionProducto,
                                                                      'propioDescripcionProducto', 40, False)

    @property
    def propioDescripcionUnidadMedida(self):
        return self._propioDescripcionUnidadMedida

    @propioDescripcionUnidadMedida.setter
    def propioDescripcionUnidadMedida(self, propioDescripcionUnidadMedida):
        self._propioDescripcionUnidadMedida = self._fill_and_validate_len(propioDescripcionUnidadMedida,
                                                                          'propioDescripcionUnidadMedida', 20, False)

    @property
    def cantidadAjustada(self):
        return self._cantidadAjustada

    @cantidadAjustada.setter
    def cantidadAjustada(self, cantidadAjustada):
        self._cantidadAjustada = self._fill_and_validate_len(cantidadAjustada,
                                                             'cantidadAjustada', 15)

    def get_values(self):
        values = [
            self._tipoRegistro,
            self._codigoUnicoProducto,
            self._rentasCodigoUnidadMedida,
            self._cantidad,
            self._propioCodigoProducto,
            self._propioDescripcionProducto,
            self._propioDescripcionUnidadMedida,
            self._cantidadAjustada,
        ]

        return values

    def get_line_string(self):

        try:
            line_string = '|'.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class ArbaRetentionLine(PresentationLine):

    # http://www.arba.gov.ar/Archivos/Publicaciones/dise%C3%B1o_registro_ar_web.pdf, 1.7 RETENCIONES
    __slots__ = ['_cuit', '_fechaRetencion', '_numeroSucursal',
                 '_numeroEmision', '_importeRetencion', '_tipoOperacion']

    def __init__(self):
        super(ArbaRetentionLine, self).__init__()
        self._cuit = None
        self._fechaRetencion = None
        self._numeroSucursal = None
        self._numeroEmision = None
        self._importeRetencion = None
        self._tipoOperacion = None

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13, numeric=False)

    @property
    def fechaRetencion(self):
        return self._fechaRetencion

    @fechaRetencion.setter
    def fechaRetencion(self, fechaRetencion):
        self._fechaRetencion = self._fill_and_validate_len(fechaRetencion, 'fechaRetencion', 10, numeric=False)

    @property
    def numeroSucursal(self):
        return self._numeroSucursal

    @numeroSucursal.setter
    def numeroSucursal(self, numeroSucursal):
        self._numeroSucursal = self._fill_and_validate_len(numeroSucursal, 'numeroSucursal', 4)

    @property
    def numeroEmision(self):
        return self._numeroEmision

    @numeroEmision.setter
    def numeroEmision(self, numeroEmision):
        self._numeroEmision = self._fill_and_validate_len(numeroEmision, 'numeroEmision', 8)

    @property
    def importeRetencion(self):
        return self._importeRetencion

    @importeRetencion.setter
    def importeRetencion(self, importeRetencion):
        self._importeRetencion = self._fill_and_validate_len(importeRetencion, 'importeRetencion', 11)
    
    @property
    def tipoOperacion(self):
        return self._tipoOperacion

    @tipoOperacion.setter
    def tipoOperacion(self, tipoOperacion):
        self._tipoOperacion = self._fill_and_validate_len(tipoOperacion, 'tipoOperacion', 1, numeric=False)
    
    def get_values(self):
        values = [
            self._cuit,
            self._fechaRetencion,
            self._numeroSucursal,
            self._numeroEmision,
            self._importeRetencion,
            self._tipoOperacion,
        ]

        return values


class ArbaPerceptionLine(PresentationLine):
    # http://www.arba.gov.ar/Archivos/Publicaciones/dise%C3%B1o_registro_ar_web.pdf
    # 1.1. Percepciones ( excepto actividad 29, 7 quincenal y 17 de Bancos)
    __slots__ = ['_cuit', '_fechaPercepcion', '_tipoComprobante',
                 '_letraComprobante', '_numeroSucursal', '_numeroEmision',
                 '_basePercepcion', '_importePercepcion',
                 '_tipoOperacion', '_sign']

    def __init__(self):
        super(ArbaPerceptionLine, self).__init__()
        self._cuit = None
        self._fechaPercepcion = None
        self._tipoComprobante = None
        self._letraComprobante = None
        self._numeroSucursal = None
        self._numeroEmision = None
        self._sign = None
        self._basePercepcion = None
        self._importePercepcion = None
        self._tipoOperacion = None

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13, numeric=False)

    @property
    def sign(self):
        return self._sign

    @sign.setter
    def sign(self, sign):
        self._sign = self._fill_and_validate_len(sign, 'sign', 1)

    @property
    def fechaPercepcion(self):
        return self._fechaPercepcion

    @fechaPercepcion.setter
    def fechaPercepcion(self, fechaPercepcion):
        self._fechaPercepcion = self._fill_and_validate_len(fechaPercepcion, 'fechaPercepcion', 10, numeric=False)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 1, numeric=False)

    @property
    def letraComprobante(self):
        return self._letraComprobante

    @letraComprobante.setter
    def letraComprobante(self, letraComprobante):
        self._letraComprobante = self._fill_and_validate_len(letraComprobante, 'letraComprobante', 1, numeric=False)

    @property
    def numeroSucursal(self):
        return self._numeroSucursal

    @numeroSucursal.setter
    def numeroSucursal(self, numeroSucursal):
        self._numeroSucursal = self._fill_and_validate_len(numeroSucursal, 'numeroSucursal', 4)

    @property
    def numeroEmision(self):
        return self._numeroEmision

    @numeroEmision.setter
    def numeroEmision(self, numeroEmision):
        self._numeroEmision = self._fill_and_validate_len(numeroEmision, 'numeroEmision', 8)

    @property
    def basePercepcion(self):
        return self._basePercepcion

    @basePercepcion.setter
    def basePercepcion(self, basePercepcion):
        self._basePercepcion = self._fill_or_set_to_highest(basePercepcion, 'basePercepcion', 11)

    @property
    def importePercepcion(self):
        return self._importePercepcion

    @importePercepcion.setter
    def importePercepcion(self, importePercepcion):
        self._importePercepcion = self._fill_or_set_to_highest(importePercepcion, 'importePercepcion', 10)

    @property
    def tipoOperacion(self):
        return self._tipoOperacion

    @tipoOperacion.setter
    def tipoOperacion(self, tipoOperacion):
        self._tipoOperacion = self._fill_and_validate_len(tipoOperacion, 'tipoOperacion', 1, numeric=False)

    def get_values(self):
        values = [
            self._cuit,
            self._fechaPercepcion,
            self._tipoComprobante,
            self._letraComprobante,
            self._numeroSucursal,
            self._numeroEmision,
            self._sign,
            self._basePercepcion,
            self._sign,
            self._importePercepcion,
            self._tipoOperacion,
        ]

        return values


class ArbaPerceptionLine2(ArbaPerceptionLine):
    # http://www.arba.gov.ar/Archivos/Publicaciones/dise%C3%B1o_registro_ar_web.pdf
    # 1.2. Percepciones Actividad 7 método Percibido (quincenal/mensual)

    def __init__(self):
        super(ArbaPerceptionLine2, self).__init__()

    def get_values(self):
        values = super(ArbaPerceptionLine2, self).get_values()
        values.insert(10, self._fechaPercepcion)
        return values


class PadronTucumanDatosLine(PresentationLine):
    # PadronTucumanDatos
    __slots__ = ['_fecha', '_tipoDoc', '_documento',  '_tipoComprobante', '_letraComprobante',
                 '_codLugarEmision', '_numero', '_baseCalculo', '_alicuota', '_monto']

    def __init__(self):
        super(PadronTucumanDatosLine, self).__init__()
        self._fecha = None
        self._tipoDoc = None
        self._documento = None
        self._tipoComprobante = None
        self._letraComprobante = None
        self._codLugarEmision = None
        self._numero = None
        self._baseCalculo = None
        self._alicuota = None
        self._monto = None

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 8)

    @property
    def tipoDoc(self):
        return self._tipoDoc

    @tipoDoc.setter
    def tipoDoc(self, tipoDoc):
        self._tipoDoc = self._fill_and_validate_len(tipoDoc, 'tipoDoc', 2)

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, documento):
        self._documento = self._fill_and_validate_len(documento, 'documento', 11)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 2)

    @property
    def letraComprobante(self):
        return self._letraComprobante

    @letraComprobante.setter
    def letraComprobante(self, letraComprobante):
        self._letraComprobante = self._fill_and_validate_len(letraComprobante, 'letraComprobante', 1, numeric=False)

    @property
    def codLugarEmision(self):
        return self._codLugarEmision

    @codLugarEmision.setter
    def codLugarEmision(self, codLugarEmision):
        self._codLugarEmision = self._fill_and_validate_len(codLugarEmision, 'codLugarEmision', 4)

    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, numero):
        self._numero = self._fill_and_validate_len(numero, 'numero', 8)

    @property
    def baseCalculo(self):
        return self._baseCalculo

    @baseCalculo.setter
    def baseCalculo(self, baseCalculo):
        self._baseCalculo = self._fill_and_validate_len(baseCalculo, 'baseCalculo', 15)

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = self._fill_and_validate_len(alicuota, 'alicuota', 6)

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, monto):
        self._monto = self._fill_and_validate_len(monto, 'monto', 15)

    def get_values(self):
        values = [
            self._fecha,
            self._tipoDoc,
            self._documento,
            self._tipoComprobante,
            self._letraComprobante,
            self._codLugarEmision,
            self._numero,
            self._baseCalculo,
            self._alicuota,
            self._monto
        ]

        return values


class PadronTucumanRetPerLine(PresentationLine):
    # PadronTucumanRetPer
    __slots__ = ['_tipoDoc', '_documento',  '_nombre', '_domicilio', '_numero',
                 '_localidad', '_provincia', '_noUsado', '_codPostal']

    def __init__(self):
        super(PadronTucumanRetPerLine, self).__init__()
        self._tipoDoc = None
        self._documento = None
        self._nombre = None
        self._domicilio = None
        self._numero = None
        self._localidad = None
        self._provincia = None
        self._noUsado = None  # Llenado con blancos.
        self._codPostal = None

    @property
    def tipoDoc(self):
        return self._tipoDoc

    @tipoDoc.setter
    def tipoDoc(self, tipoDoc):
        self._tipoDoc = self._fill_and_validate_len(tipoDoc, 'tipoDoc', 2)

    @property
    def documento(self):
        return self._documento

    @documento.setter
    def documento(self, documento):
        self._documento = self._fill_and_validate_len(documento, 'documento', 11)

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        self._nombre = self._fill_and_validate_len(nombre, 'nombre', 40, numeric=False)

    @property
    def domicilio(self):
        return self._domicilio

    @domicilio.setter
    def domicilio(self, domicilio):
        self._domicilio = self._fill_and_validate_len(domicilio, 'domicilio', 40, numeric=False)

    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, numero):
        self._numero = self._fill_and_validate_len(numero, 'numero', 5)

    @property
    def localidad(self):
        return self._localidad

    @localidad.setter
    def localidad(self, localidad):
        self._localidad = self._fill_and_validate_len(localidad, 'localidad', 15, numeric=False)

    @property
    def provincia(self):
        return self._provincia

    @provincia.setter
    def provincia(self, provincia):
        self._provincia = self._fill_and_validate_len(provincia, 'provincia', 15, numeric=False)

    @property
    def noUsado(self):
        return self._noUsado

    @noUsado.setter
    def noUsado(self, noUsado):
        self._noUsado = self._fill_and_validate_len(noUsado, 'noUsado', 11)

    @property
    def codPostal(self):
        return self._codPostal

    @codPostal.setter
    def codPostal(self, codPostal):
        self._codPostal = self._fill_and_validate_len(codPostal, 'codPostal', 8, numeric=False)

    def get_values(self):
        values = [
            self._tipoDoc,
            self._documento,
            self._nombre,
            self._domicilio,
            self._numero,
            self._localidad,
            self._provincia,
            self._noUsado,
            self._codPostal
        ]

        return values


class AgipLine(PresentationLine):
    # https://www.agip.gob.ar/filemanager/source/Agentes/DocTecnicoImpoOperacionesDise%C3%B1odeRegistro.pdf, 2.0 AGIP
    # Diseño de Registro de Importaciones de Retenciones/Percepciones
    __slots__ = ['_tipoOperacion', '_codigoDeNorma', '_fecha', '_tipoComprobante', '_letraComprobante',
                 '_numeroComprobante', '_fechaComprobante', '_montoComprobante', '_numeroCertificado',
                 '_tipoDocRetenido', '_numeroDocRetenido', '_situacionIBRetenido', '_numeroInscripcionIBRetenido',
                 '_situacionIVARetenido', '_razonSocialRetenido', '_importeOtrosConceptos', '_importeIVA',
                 '_montoSujetoRetencion', '_alicuota', '_retencionPracticada', '_montoTotalRetenido']

    def __init__(self):
        super(AgipLine, self).__init__()
        self._tipoOperacion = None
        self._codigoDeNorma = None
        self._fecha = None
        self._tipoComprobante = None
        self._letraComprobante = None
        self._numeroComprobante = None
        self._fechaComprobante = None
        self._montoComprobante = None
        self._numeroCertificado = None
        self._tipoDocRetenido = None
        self._numeroDocRetenido = None
        self._situacionIBRetenido = None
        self._numeroInscripcionIBRetenido = None
        self._situacionIVARetenido = None
        self._razonSocialRetenido = None
        self._importeOtrosConceptos = None
        self._importeIVA = None
        self._montoSujetoRetencion = None
        self._alicuota = None
        self._retencionPracticada = None
        self._montoTotalRetenido = None

    @property
    def tipoOperacion(self):
        return self._tipoOperacion

    @tipoOperacion.setter
    def tipoOperacion(self, tipoOperacion):
        self._tipoOperacion = self._fill_and_validate_len(tipoOperacion, 'tipoOperacion', 1)

    @property
    def codigoDeNorma(self):
        return self._codigoDeNorma

    @codigoDeNorma.setter
    def codigoDeNorma(self, codigoDeNorma):
        self._codigoDeNorma = self._fill_and_validate_len(codigoDeNorma, 'codigoDeNorma', 3)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10, numeric=False)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 2, numeric=False)

    @property
    def letraComprobante(self):
        return self._letraComprobante

    @letraComprobante.setter
    def letraComprobante(self, letraComprobante):
        self._letraComprobante = self._fill_and_validate_len(letraComprobante, 'letraComprobante', 1, numeric=False)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 16)

    @property
    def fechaComprobante(self):
        return self._fechaComprobante

    @fechaComprobante.setter
    def fechaComprobante(self, fechaComprobante):
        self._fechaComprobante = self._fill_and_validate_len(fechaComprobante, 'fechaComprobante', 10, numeric=False)

    @property
    def montoComprobante(self):
        return self._montoComprobante

    @montoComprobante.setter
    def montoComprobante(self, montoComprobante):
        self._montoComprobante = self._fill_and_validate_len(montoComprobante, 'montoComprobante', 16)

    @property
    def numeroCertificado(self):
        return self._numeroCertificado

    @numeroCertificado.setter
    def numeroCertificado(self, numeroCertificado):
        self._numeroCertificado = self._fill_and_validate_len(numeroCertificado, 'numeroCertificado', 16, numeric=False)

    @property
    def tipoDocRetenido(self):
        return self._tipoDocRetenido

    @tipoDocRetenido.setter
    def tipoDocRetenido(self, tipoDocRetenido):
        self._tipoDocRetenido = self._fill_and_validate_len(tipoDocRetenido, 'tipoDocRetenido', 1)

    @property
    def numeroDocRetenido(self):
        return self._numeroDocRetenido

    @numeroDocRetenido.setter
    def numeroDocRetenido(self, numeroDocRetenido):
        self._numeroDocRetenido = self._fill_and_validate_len(numeroDocRetenido, 'numeroDocRetenido', 11)

    @property
    def situacionIBRetenido(self):
        return self._situacionIBRetenido

    @situacionIBRetenido.setter
    def situacionIBRetenido(self, situacionIBRetenido):
        self._situacionIBRetenido = self._fill_and_validate_len(situacionIBRetenido, 'situacionIBRetenido', 1)

    @property
    def numeroInscripcionIBRetenido(self):
        return self._numeroInscripcionIBRetenido

    @numeroInscripcionIBRetenido.setter
    def numeroInscripcionIBRetenido(self, numeroInscripcionIBRetenido):
        self._numeroInscripcionIBRetenido = self._fill_and_validate_len(numeroInscripcionIBRetenido,
                                                                        'numeroInscripcionIBRetenido', 11)

    @property
    def situacionIVARetenido(self):
        return self._situacionIVARetenido

    @situacionIVARetenido.setter
    def situacionIVARetenido(self, situacionIVARetenido):
        self._situacionIVARetenido = self._fill_and_validate_len(situacionIVARetenido, 'situacionIVARetenido', 1)

    @property
    def razonSocialRetenido(self):
        return self._razonSocialRetenido

    @razonSocialRetenido.setter
    def razonSocialRetenido(self, razonSocialRetenido):
        self._razonSocialRetenido = self._fill_and_validate_len(razonSocialRetenido, 'razonSocialRetenido', 30,
                                                                numeric=False)

    @property
    def importeOtrosConceptos(self):
        return self._importeOtrosConceptos

    @importeOtrosConceptos.setter
    def importeOtrosConceptos(self, importeOtrosConceptos):
        self._importeOtrosConceptos = self._fill_and_validate_len(importeOtrosConceptos, 'importeOtrosConceptos', 16)

    @property
    def importeIVA(self):
        return self._importeIVA

    @importeIVA.setter
    def importeIVA(self, importeIVA):
        self._importeIVA = self._fill_and_validate_len(importeIVA, 'importeIVA', 16)

    @property
    def montoSujetoRetencion(self):
        return self._montoSujetoRetencion

    @montoSujetoRetencion.setter
    def montoSujetoRetencion(self, montoSujetoRetencion):
        self._montoSujetoRetencion = self._fill_and_validate_len(montoSujetoRetencion, 'montoSujetoRetencion', 16)

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = self._fill_and_validate_len(alicuota, 'alicuota', 5)

    @property
    def retencionPracticada(self):
        return self._retencionPracticada

    @retencionPracticada.setter
    def retencionPracticada(self, retencionPracticada):
        self._retencionPracticada = self._fill_and_validate_len(retencionPracticada, 'retencionPracticada', 16)

    @property
    def montoTotalRetenido(self):
        return self._montoTotalRetenido

    @montoTotalRetenido.setter
    def montoTotalRetenido(self, montoTotalRetenido):
        self._montoTotalRetenido = self._fill_and_validate_len(montoTotalRetenido, 'montoTotalRetenido', 16)

    def get_values(self):
        values = [
            self._tipoOperacion,
            self._codigoDeNorma,
            self._fecha,
            self._tipoComprobante,
            self._letraComprobante,
            self._numeroComprobante,
            self._fechaComprobante,
            self._montoComprobante,
            self._numeroCertificado,
            self._tipoDocRetenido,
            self._numeroDocRetenido,
            self._situacionIBRetenido,
            self._numeroInscripcionIBRetenido,
            self._situacionIVARetenido,
            self._razonSocialRetenido,
            self._importeOtrosConceptos,
            self._importeIVA,
            self._montoSujetoRetencion,
            self._alicuota,
            self._retencionPracticada,
            self._montoTotalRetenido
        ]

        return values


class AgipRefundLine(PresentationLine):
    # https://www.agip.gob.ar/filemanager/source/Agentes/DocTecnicoImpoOperacionesDise%C3%B1odeRegistro.pdf, 2.0 AGIP
    # Diseño de Registro de Importaciones de Notas de crédito
    __slots__ = ['_tipoOperacion', '_numeroNC', '_fechaNC', '_montoNC', '_numeroCertificado',
                 '_tipoComprobante', '_letraComprobante', '_numeroComprobante', '_numeroDocRetenido',
                 '_codigoDeNorma', '_fecha', '_percepcionADeducir', '_alicuota']

    def __init__(self):
        super(AgipRefundLine, self).__init__()
        self._tipoOperacion = None
        self._numeroNC = None
        self._fechaNC = None
        self._montoNC = None
        self._numeroCertificado = None
        self._tipoComprobante = None
        self._letraComprobante = None
        self._numeroComprobante = None
        self._numeroDocRetenido = None
        self._codigoDeNorma = None
        self._fecha = None
        self._percepcionADeducir = None
        self._alicuota = None

    @property
    def tipoOperacion(self):
        return self._tipoOperacion

    @tipoOperacion.setter
    def tipoOperacion(self, tipoOperacion):
        self._tipoOperacion = self._fill_and_validate_len(tipoOperacion, 'tipoOperacion', 1)

    @property
    def numeroNC(self):
        return self._numeroNC

    @numeroNC.setter
    def numeroNC(self, numeroNC):
        self._numeroNC = self._fill_and_validate_len(numeroNC, 'numeroNC', 12)

    @property
    def fechaNC(self):
        return self._fechaNC

    @fechaNC.setter
    def fechaNC(self, fechaNC):
        self._fechaNC = self._fill_and_validate_len(fechaNC, 'fechaNC', 10, numeric=False)

    @property
    def montoNC(self):
        return self._montoNC

    @montoNC.setter
    def montoNC(self, montoNC):
        self._montoNC = self._fill_and_validate_len(montoNC, 'montoNC', 16)

    @property
    def numeroCertificado(self):
        return self._numeroCertificado

    @numeroCertificado.setter
    def numeroCertificado(self, numeroCertificado):
        self._numeroCertificado = self._fill_and_validate_len(numeroCertificado, 'numeroCertificado', 16, numeric=False)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 2, numeric=False)

    @property
    def letraComprobante(self):
        return self._letraComprobante

    @letraComprobante.setter
    def letraComprobante(self, letraComprobante):
        self._letraComprobante = self._fill_and_validate_len(letraComprobante, 'letraComprobante', 1, numeric=False)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 16)

    @property
    def numeroDocRetenido(self):
        return self._numeroDocRetenido

    @numeroDocRetenido.setter
    def numeroDocRetenido(self, numeroDocRetenido):
        self._numeroDocRetenido = self._fill_and_validate_len(numeroDocRetenido, 'numeroDocRetenido', 11)

    @property
    def codigoDeNorma(self):
        return self._codigoDeNorma

    @codigoDeNorma.setter
    def codigoDeNorma(self, codigoDeNorma):
        self._codigoDeNorma = self._fill_and_validate_len(codigoDeNorma, 'codigoDeNorma', 3)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10, numeric=False)

    @property
    def percepcionADeducir(self):
        return self._percepcionADeducir

    @percepcionADeducir.setter
    def percepcionADeducir(self, percepcionADeducir):
        self._percepcionADeducir = self._fill_and_validate_len(percepcionADeducir, 'percepcionADeducir', 16)

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = self._fill_and_validate_len(alicuota, 'alicuota', 5)

    def get_values(self):
        values = [
            self._tipoOperacion,
            self._numeroNC,
            self._fechaNC,
            self._montoNC,
            self._numeroCertificado,
            self._tipoComprobante,
            self._letraComprobante,
            self._numeroComprobante,
            self._numeroDocRetenido,
            self._codigoDeNorma,
            self._fecha,
            self._percepcionADeducir,
            self._alicuota,
        ]

        return values


class PerceptionSircarLine(PresentationLine):
    # https://www.ca.gov.ar/descargar/sircar/Anexo_Registros.pdf
    # Diseño 1 de Registros Retenciones/Percepciones SIRCAR

    __slots__ = ['_nroLinea', '_tipoComprobante', '_letraComprobante',
                '_numeroComprobante', '_cuit', '_fecha', '_monto',
                '_alicuota', '_montoPercibido', '_tipoRegimenPercepcion', '_jurisdiccion']

    def __init__(self):
        super(PerceptionSircarLine, self).__init__()
        self._nroLinea = None
        self._tipoComprobante = None
        self._letraComprobante = None
        self._numeroComprobante = None
        self._cuit = None
        self._fecha = None
        self._monto = None
        self._alicuota = None
        self._montoPercibido = None
        self._tipoRegimenPercepcion = None
        self._jurisdiccion = None

    @property
    def nroLinea(self):
        return self._nroLinea

    @nroLinea.setter
    def nroLinea(self, nroLinea):
        self._nroLinea = self._fill_and_validate_len(nroLinea, 'nroLinea', 5)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = self._fill_and_validate_len(tipoComprobante, 'tipoComprobante', 3)

    @property
    def letraComprobante(self):
        return self._letraComprobante

    @letraComprobante.setter
    def letraComprobante(self, letraComprobante):
        self._letraComprobante = self._fill_and_validate_len(letraComprobante, 'letraComprobante', 1, numeric=False)

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = self._fill_and_validate_len(numeroComprobante, 'numeroComprobante', 12)

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 11)

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10, numeric=False)

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, monto):
        self._monto = monto

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = alicuota

    @property
    def montoPercibido(self):
        return self._montoPercibido

    @montoPercibido.setter
    def montoPercibido(self, montoPercibido):
        self._montoPercibido = montoPercibido

    @property
    def tipoRegimenPercepcion(self):
        return self._tipoRegimenPercepcion

    @tipoRegimenPercepcion.setter
    def tipoRegimenPercepcion(self, tipoRegimenPercepcion):
        self._tipoRegimenPercepcion = self._fill_and_validate_len(tipoRegimenPercepcion, 'tipoRegimenPercepcion', 3)

    @property
    def jurisdiccion(self):
        return self._jurisdiccion

    @jurisdiccion.setter
    def jurisdiccion(self, jurisdiccion):
        self._jurisdiccion = self._fill_and_validate_len(jurisdiccion, 'jurisdiccion', 3)

    def get_values(self):
        values = [
            self._nroLinea,
            self._tipoComprobante,
            self._letraComprobante,
            self._numeroComprobante,
            self._cuit,
            self._fecha,
            self._monto,
            self._alicuota,
            self._montoPercibido,
            self._tipoRegimenPercepcion,
            self._jurisdiccion,
        ]
        return values

    def get_line_string(self):

        try:
            line_string = ','.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class PerceptionMisionesLine(PresentationLine):
    # https://www.atm.misiones.gob.ar/index.php/guia-de-tramites/instructivos/category/53-agentes?download=276:presentacion-ddjj-mensual-de-agente-de-percepcion-de-iibb
    # Diseño de Registro Percepciones Misiones

    __slots__ = ['_fecha', '_tipoComprobante','_numeroComprobante',
                '_razonSocial', '_cuit', '_monto', '_alicuota']

    def __init__(self):
        super(PerceptionMisionesLine, self).__init__()
        self._fecha = None
        self._tipoComprobante = None
        self._numeroComprobante = None
        self._razonSocial = None
        self._cuit = None
        self._monto = None
        self._alicuota = None

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10, numeric=False)

    @property
    def tipoComprobante(self):
        return self._tipoComprobante

    @tipoComprobante.setter
    def tipoComprobante(self, tipoComprobante):
        self._tipoComprobante = tipoComprobante

    @property
    def numeroComprobante(self):
        return self._numeroComprobante

    @numeroComprobante.setter
    def numeroComprobante(self, numeroComprobante):
        self._numeroComprobante = numeroComprobante

    @property
    def razonSocial(self):
        return self._razonSocial

    @razonSocial.setter
    def razonSocial(self, razonSocial):
        self._razonSocial = razonSocial

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13, numeric=False)

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, monto):
        self._monto = monto

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = alicuota

    def get_values(self):
        values = [
            self._fecha,
            self._tipoComprobante,
            self._numeroComprobante,
            self._razonSocial,
            self._cuit,
            self._monto,
            self._alicuota
        ]
        return values

    def get_line_string(self):

        try:
            line_string = ','.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string


class RetentionMisionesLine(PresentationLine):
    # https://www.atm.misiones.gob.ar/index.php/guia-de-tramites/instructivos/category/53-agentes?download=275:presentacion-ddjj-mensual-de-agente-de-retencion-de-iibb
    # Diseño de Registro Retenciones Misiones

    __slots__ = ['_fecha', '_constancia', '_razonSocial',
                '_domicilio', '_cuit', '_monto', '_alicuota']

    def __init__(self):
        super(RetentionMisionesLine, self).__init__()
        self._fecha = None
        self._constancia = None
        self._razonSocial = None
        self._domicilio = None
        self._cuit = None
        self._monto = None
        self._alicuota = None

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, fecha):
        self._fecha = self._fill_and_validate_len(fecha, 'fecha', 10, numeric=False)

    @property
    def constancia(self):
        return self._constancia

    @constancia.setter
    def constancia(self, constancia):
        self._constancia = constancia

    @property
    def razonSocial(self):
        return self._razonSocial

    @razonSocial.setter
    def razonSocial(self, razonSocial):
        self._razonSocial = razonSocial

    @property
    def domicilio(self):
        return self._domicilio

    @domicilio.setter
    def domicilio(self, domicilio):
        self._domicilio = domicilio

    @property
    def cuit(self):
        return self._cuit

    @cuit.setter
    def cuit(self, cuit):
        self._cuit = self._fill_and_validate_len(cuit, 'cuit', 13, numeric=False)

    @property
    def monto(self):
        return self._monto

    @monto.setter
    def monto(self, monto):
        self._monto = monto

    @property
    def alicuota(self):
        return self._alicuota

    @alicuota.setter
    def alicuota(self, alicuota):
        self._alicuota = alicuota

    def get_values(self):
        values = [
            self._fecha,
            self._constancia,
            self._razonSocial,
            self._domicilio,
            self._cuit,
            self._monto,
            self._alicuota
        ]
        return values

    def get_line_string(self):

        try:
            line_string = ','.join(self.get_values())
        except TypeError:
            raise TypeError("La linea esta incompleta o es erronea")

        return line_string

