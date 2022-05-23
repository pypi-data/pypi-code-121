PACS = {
    "PRUEBA": 0,
    "PRODIGIA": 1,
    "FINKOK": 2,
    "STOCONSULTING": 3,
    "DFACTURE": 4,
}

CHOICES_PACS = []
for nombre,valor in PACS.items():
	CHOICES_PACS.append((valor, nombre))

CLAVES_COMBUSTIBLE = ["15101506", "15101505", "15101509", "15101514", "15101515", "15101500"]


ADDENDAS = (
    ("", "-------"),
    ("agnico", "Agnico Eagle"),
    ("ahmsa", "AHMSA"),
    ("coppel", "Coppel"),
    ("loreal", "Loreal"),
    ("multiasistencia", "Multiasistencia"),
    ("pemex", "Pemex"),
    ("lacomer", "Comercial Mexicana"),
)

METODOS_PAGO = (
    #('NA', 'NA'),
    ("01", "01 Efectivo"),
    ("02", "02 Cheque nominativo"),
    ("03", "03 Transferencia electrónica de fondos"),
    ("04", "04 Tarjeta de crédito"),
    ("05", "05 Monedero electrónico"),
    ("06", "06 Dinero electrónico"),
    ("08", "08 Vales de despensa"),
    ("12", "12 Dación en pago"),
    ("13", "13 Pago por subrogación"),
    ("14", "14 Pago por consignación"),
    ("15", "15 Condonación"),
    ("17", "17 Compensación"),
    ("23", "23 Novación"),
    ("24", "24 Confusión"),
    ("25", "25 Remisión de deuda"),
    ("26", "26 Prescripción o caducidad"),
    ("27", "27 A satisfacción del acreedor"),
    ("28", "28 Tarjeta de débito"),
    ("29", "29 Tarjeta de servicio"),
    ("30", "30 Aplicación de anticipos"),
    ("31", "31 Intermediario pagos"),
    ("99", "99 Por definir")
)

MOTIVOS_CANCELACION_CFDI = (
    (
        "01", "Comprobante emitido con errores con relación", 
        """
        Aplica cuando la factura generada contiene un error en la clave del producto, 
        valor unitario, descuento o cualquier otro dato, por lo que se debe reexpedir.
        Primero se sustituye la factura y cuando se solicita la cancelación, 
        se incorpora el folio de la factura que sustituye a la cancelada.
        """
    ),

    (
        "02", "Comprobante emitido con errores sin relación", 
        """
        Aplica cuando la factura generada contiene un error en la clave del producto, 
        valor unitario, descuento o cualquier otro dato y no se requiera relacionar 
        con otra factura generada.
        """,
    ),
        
    (
        "03", "No se llevó a cabo la operación", 
        "Aplica cuando se facturó una operación que no se concreta."
    ),
    (
        "04", 
        "Operación nominativa relacionada en la factura global", 
        """
        Aplica cuando se incluye una venta en la factura global de operaciones 
        con el público en general y, posterior a ello, el cliente solicita su factura nominativa; 
        es decir, a su nombre y RFC. Se cancela la factura global, se reexpide sin incluir 
        la operación por la que se solicita factura. Se expide la factura nominativa.
        """
    ),
)

MOTIVOS_CANCELACION_CFDI_OP =[]
for mc in MOTIVOS_CANCELACION_CFDI:
    MOTIVOS_CANCELACION_CFDI_OP.append((mc[0], f"{mc[0]} {mc[1]}"))




REGIMEN_FISCAL_FISICA_OP =(
    #FISICA
    ("605", "Sueldos y Salarios e Ingresos Asimilados a Salarios"),
    ("606", "Arrendamiento"),
    ("608", "Demás ingresos"),
    ("611", "Ingresos por Dividendos (socios y accionistas)"),
    ("612", "Personas Físicas con Actividades Empresariales y Profesionales"),
    ("614", "Ingresos por intereses"),
    ("616", "Sin obligaciones fiscales"),
    ("621", "Incorporación Fiscal"),
    #("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras "),
    ("629", "De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales"),
    ("630", "Enajenación de acciones en bolsa de valores"),
    ("615", "Régimen de los ingresos por obtención de premios"),
    ("625", "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"),
    ("626", "Régimen Simplificado de Confianza"),
)

REGIMEN_FISCAL_MORAL_OP = (
    #MORAL
    ("601", "General de Ley Personas Morales" ),
    ("603", "Personas Morales con Fines no Lucrativos" ),
    ("609", "Consolidación" ),
    ("620", "Sociedades Cooperativas de Producción que optan por diferir sus ingresos" ),
    ("622", "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras "),
    ("623", "Opcional para Grupos de Sociedades" ),
    ("624", "Coordinados" ),
    ("628", "Hidrocarburos" ),
    ("607", "Régimen de Enajenación o Adquisición de Bienes" ),
    ("626", "Régimen Simplificado de Confianza"),
)

REGIMEN_FISCAL_TODOS = (
    REGIMEN_FISCAL_FISICA_OP +
    REGIMEN_FISCAL_MORAL_OP +
    (("610", "Residentes en el Extranjero sin Establecimiento Permanente en México" ), )
)

REGIMEN_FISCAL_OP = []
for TMPRF in REGIMEN_FISCAL_TODOS:
    REGIMEN_FISCAL_OP.append(
        (TMPRF[0], f"{TMPRF[0]} - {TMPRF[1]}"),
    )


TABLAS_RESICO_PF = (
    (25000.00, 1.0),
    (50000.00, 1.1),
    (83333.33, 1.5),
    (208333.33, 2.0),
    (3500000.00, 2.5),
)

REGIMEN_SOCIETARIOS = (
    "SA",
    "SAPI",
    "SAPIB",
    "SAB",
    "S DE RL",
    "S DE R L",
    "SC",
    "AC",
    "SAS",
    "S EN C",
    "S EN C POR A",
    "S EN NC",

    "SA DE CV",
    "SAPI DE CV",
    "SAB DE CV",
    "S DE RL DE CV",
    "S DE R L DE CV",
    "SAS DE CV",
    "S EN C DE CV",
    "S EN C POR A DE CV",
    "S EN NC DE CV",
    "SC DE CV",

)



CHOICES_REGIMEN_SOCIETARIOS = (
    ("SA", "SA - Sociedad anónima."),
    ("SA DE CV", "SA DE CV - Sociedad anónima de capital variable."),
    ("SAB", "SAB - Sociedad anómina bursátil."),
    ("SAB DE CV", "SAB DE CV - Sociedad anómina bursátil de capital variable."),
    ("SAPI", "SAPI - Sociedad anónima promotora de inversión."),
    ("SAPI DE CV", "SAPI DE CV - Sociedad anónima promotora de inversión de capital variable."),
    ("SAPIB", "SAPIB - Sociedad anónima promotora de inversión bursátil."),
    ("SC", "SC - Sociedad civil."),
    ("SC DE CV", "SC DE CV - Sociedad civil de capital variable."),
    ("S DE RL", "S DE RL - Sociedad de responsabilidad limitada."),
    ("S DE RL DE CV", "S DE RL DE CV - Sociedad de responsabilidad limitada de capital variable."),
    ("SAS", "SAS - Sociedad por acciones simplificada."),
    ("SAS DE CV", "SAS DE CV - Sociedad por acciones simplificada de capital variable."),
    ("S EN C", "S EN C - Sociedad en comandita simple."),
    ("S EN C DE CV", "S EN C DE CV - Sociedad en comandita simple de capital variable."),
    ("S EN C POR A", "S EN C POR A - Sociedad en comandita por acciones."),
    ("S EN C POR A DE CV", "S EN C POR A DE CV - Sociedad en comandita por acciones de capital variable."),
    ("S EN NC", "S EN NC - Sociedad en nombre colectivo."),
    ("S EN NC DE CV", "S EN NC DE CV - Sociedad en nombre colectivo de capital variable."),
    ("AC", "AC - Asociación civil."),
)


CLAVES_SERVICIOS_RETENCION_PF = [
    "80141600",
    "80141601",
    "80141602",
    "80141603",
    "80141604",
    "80141605",
    "80141606",
    "80141607",
    "80141609",
    "80141610",
    "80141611",
    "80141612",
    "80141613",
    "80141614",
    "80141615",
    "80141616",
    "80141617",
    "80141618",
    "80141619",
    "80141620",
    "80141621",
    "80141622",
    "80141623",
    "80141624",
    "80141625",
    "80141626",
    "80141627",
    "80141628",
    "80141629",
    "80141630",
]