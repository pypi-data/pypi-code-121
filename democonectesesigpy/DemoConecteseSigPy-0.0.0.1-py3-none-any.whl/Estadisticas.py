# -*- coding: utf-8 -*-
from DemoConecteseSigPy.Utiles import TimeUtil, ToolboxLogger

class Estadisticas:

    def __init__(self) :
        self.estadisticas = []
        self.tablasEstadisticas = []
        self.encuestas = []
        self.valores = {"E": 3, "C": 2, "U": 1, "NU" : 0}
        self.timer = TimeUtil()
    
    def agregarEncuesta(self, idEncuesta):
        encuesta = {}
        encuesta["idEncuesta"] = idEncuesta
        self.encuestas.append(encuesta)

        return encuesta

    def actualizarEncuesta(self, idEncuesta, estados) :
        encuestas = [x for x in self.encuestas if x["idEncuesta"] == idEncuesta]
        encuesta = encuestas[0] if len(encuestas) > 0 else None
        if encuesta:
            for llave in estados:
                encuesta[llave] = estados[llave]
            ToolboxLogger.debug("encuesta {}".format(encuesta))

    def totalEstadoEncuesta(self, llave_estado, valor_estado) :
        cuenta = 0
        for encuesta in self.encuestas :
            if llave_estado in encuesta :
                cuenta = cuenta + 1 if encuesta[llave_estado] == valor_estado else cuenta
        return cuenta

    def agregarEstadistica(self) :
        estadistica = {}
        self.estadisticas.append(estadistica)

        return estadistica

    def _obtenerEstadisticaActual(self):
        indice = len(self.estadisticas) - 1
        if indice >= 0:
            return self.estadisticas[indice]
        else :
            return None

    def _obtenerValor(self, tipo) :
        return self.valores[tipo] if tipo in self.valores else -1

    def actualizarEstadistica(self, nombreTabla, tipo, guid = "{}"):
        valor = self._obtenerValor(tipo)
        estadistica = self._obtenerEstadisticaActual()

        if estadistica != None :
            if not nombreTabla in self.tablasEstadisticas :
                self.tablasEstadisticas.append(nombreTabla)

            if not nombreTabla in estadistica:
                estadistica[nombreTabla] = {"guids": {}, "total" : 0}
                
            if valor > -1 :
                if not guid in estadistica[nombreTabla]["guids"] or valor > estadistica[nombreTabla]["guids"][guid]:
                    estadistica[nombreTabla]["guids"][guid] = valor 

                ToolboxLogger.debug("tabla: '{}' tipo: '{}' guid: {}".format(nombreTabla, tipo, guid))
                estadistica[nombreTabla]["total"] += 1

    def obtenerEstadisticas(self, indice, tipo) :
        cuenta = 0
        valor = self._obtenerValor(tipo)

        estadistica = self.estadisticas[indice]
        for tabla in estadistica:
            for guid in estadistica[tabla]["guids"] :
                if estadistica[tabla]["guids"][guid]  == valor :
                    cuenta += 1

        return cuenta

    def obtenerRegistros(self, indice) :
        cuenta = 0

        estadistica = self.estadisticas[indice]
        for tabla in estadistica:
            for guid in estadistica[tabla]["guids"] :
                cuenta += 1

        return cuenta

    def obtenerOperaciones(self, indice) :
        cuenta = 0

        estadistica = self.estadisticas[indice]
        for tabla in estadistica:
            cuenta = cuenta + estadistica[tabla]["total"] 

        return cuenta

    def obtenerEstadisticasActual(self, tipo) :
        cuenta = 0
        valor = self._obtenerValor(tipo)

        estadistica = self._obtenerEstadisticaActual()
        for tabla in estadistica:
            for guid in estadistica[tabla]["guids"] :
                if estadistica[tabla]["guids"][guid]  == valor :
                    cuenta += 1

        return cuenta

    def obtenerRegistrosActual(self) :
        cuenta = 0
        estadistica = self._obtenerEstadisticaActual()
        for tabla in estadistica:
            for guid in estadistica[tabla]["guids"] :
                cuenta += 1

        return cuenta

    def obtenerOperacionesActual(self) :
        cuenta = 0

        estadistica = self._obtenerEstadisticaActual()
        for tabla in estadistica:
            cuenta = cuenta + estadistica[tabla]["total"] 

        return cuenta
    
    def obtenerTotalEstadisticas(self, tipo) :
        cuenta = 0
        valor = self._obtenerValor(tipo)

        for estadistica in self.estadisticas:
            for tabla in estadistica:
                for guid in estadistica[tabla]["guids"] :
                    if estadistica[tabla]["guids"][guid]  == valor :
                        cuenta += 1

        return cuenta

    def obtenerTotalRegistros(self) :
        cuenta = 0
        for estadistica in self.estadisticas:
            for tabla in estadistica:
                for guid in estadistica[tabla]["guids"] :
                    cuenta += 1

        return cuenta

    def obtenerTotalOperaciones(self) :
        cuenta = 0
        for estadistica in self.estadisticas:
            for tabla in estadistica:
                cuenta = cuenta + estadistica[tabla]["total"] 

        return cuenta

    def obtenerTotalEstadisticasTabla(self, tabla, tipo) :
        cuenta = 0
        valor = self._obtenerValor(tipo)

        for estadistica in self.estadisticas:
            if tabla in estadistica :
                for guid in estadistica[tabla]["guids"] :
                    if estadistica[tabla]["guids"][guid]  == valor :
                        cuenta += 1
        return cuenta

    def obtenerTotalRegistrosTabla(self, tabla) :
        cuenta = 0
        for estadistica in self.estadisticas:
            if tabla in estadistica :
                for guid in estadistica[tabla]["guids"] :
                    cuenta += 1

        return cuenta

    def obtenerTotalOperacionesTabla(self, tabla) :
        cuenta = 0
        for estadistica in self.estadisticas:
            if tabla in estadistica :
                cuenta = cuenta + estadistica[tabla]["total"] 

        return cuenta
    
    def obtenerTotalTablas(self) :
        return len(self.tablasEstadisticas)

    def obtenerNumeroEstadisticas(self) :
        return len(self.estadisticas)

    def duracionPorEstadistica(self) :
        return self.timer.timeSpan / self.obtenerNumeroEstadisticas()
    
    def duracionPorRegistro(self) :
        return self.timer.timeSpan / self.obtenerTotalRegistros()

    def duracionPorOperacion(self) :
        return self.timer.timeSpan / self.obtenerTotalOperaciones()

    def minutosPorEstadistica(self) :
        return 1 / self.estadisticasPorMinuto() if self.estadisticasPorMinuto() != 0 else 0

    def minutosPorRegistro(self) :
        return 1 / self.registrosPorMinuto() if self.registrosPorMinuto() != 0 else 0
    
    def minutosPorOperacion(self) :
        return 1 / self.operacionesPorMinuto() if self.operacionesPorMinuto() != 0 else 0

    def estadisticasPorMinuto(self) :
        return self.obtenerNumeroEstadisticas() / self.timer.timeSpan.total_seconds() * 60 if self.timer.timeSpan.total_seconds() != 0 else 0

    def registrosPorMinuto(self) :
        return self.obtenerTotalRegistros() / self.timer.timeSpan.total_seconds() * 60 if self.timer.timeSpan.total_seconds() != 0 else 0

    def operacionesPorMinuto(self) :
        return self.obtenerTotalOperaciones() / self.timer.timeSpan.total_seconds() * 60 if self.timer.timeSpan.total_seconds() != 0 else 0