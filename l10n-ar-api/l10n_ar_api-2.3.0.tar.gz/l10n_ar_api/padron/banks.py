try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import requests
from unidecode import unidecode
from l10n_ar_api.padron.contributor import Contributor


class Banks:

    @staticmethod
    def get_offline_banks_list():
        return [
            ['30500003886', '3', 'BANCO EUROPEO PARA AMERICA LATINA (BEAL) S.A.', 'ELIMINADO', 'Res.42/04(DI SERE'],
            ['30500001735', '7', 'BANCO DE GALICIA Y BUENOS AIRES S.A.U.', 'VIGENTE', 'Si'],
            ['30500010912', '11', 'BANCO DE LA NACION ARGENTINA', 'VIGENTE', 'SDG LTA', 'Si'],
            ['33999242109', '14', 'BANCO DE LA PROVINCIA DE BUENOS AIRES', 'VIGENTE', 'RES.86/10(DISERE)'],
            ['30709447846', '15', 'INDUSTRIAL AND COMMERCIAL BANK OF CHINA (ARGENTINA) S.A.', 'VIGENTE', '052/13(DI SERE)'],
            ['30500005625', '16', 'CITIBANK N.A.', 'VIGENTE', 'SDG LTA'],
            ['30500003193', '17', 'BANCO BBVA ARGENTINA S.A.', 'VIGENTE', 'SDG LTA'],
            ['30999228565', '20', 'BANCO DE LA PROVINCIA DE CORDOBA S.A.', 'VIGENTE', 'R.100/11 (DI SERE)'],
            ['25', 'BANCO SANTANDER S.A.', 'ELIMINADO'],
            ['33500005179', '27', 'BANCO SUPERVIELLE S.A.', 'VIGENTE', '113/05 (DI SERE)', 'Si'],
            ['30999032083', '29', 'BANCO DE LA CIUDAD DE BUENOS AIRES', 'VIGENTE', 'SDG LTA'],
            ['30500011382', '30', 'CENTRAL DE LA REPUBLICA ARGENTINA', 'VIGENTE'],
            ['31', 'CORREO ARGENTINO S.A.', 'ELIMINADO'],
            ['30500006613', '34', 'BANCO PATAGONIA S.A.', 'VIGENTE', '045/05 (DI SERE)'],
            ['30500011072', '44', 'BANCO HIPOTECARIO SA', 'VIGENTE', '079/09 (DI SERE)'],
            ['30500009442', '45', 'BANCO DE SAN JUAN S.A.', 'VIGENTE', 'SDG LTA'],
            ['33999181819', '65', 'BANCO MUNICIPAL DE ROSARIO', 'VIGENTE', 'SDG LTA'],
            ['30500008454', '72', 'BANCO SANTANDER RIO S.A.', 'VIGENTE', 'RES79/07(DI SERE)', 'Si'],
            ['76', 'DE LA NACION ARGENTINA (SUC.IMP.INT.)', 'ELIMINADO'],
            ['78', 'DE LA CIUDAD DE BUENOS AIRES', 'ELIMINADO'],
            ['81', 'BANCO SOCIAL DE CORDOBA', 'ELIMINADO'],
            ['30500012990', '83', 'BANCO DEL CHUBUT S.A.', 'VIGENTE', 'SDG LTA'],
            ['30500098801', '86', 'BANCO DE SANTA CRUZ S.A.', 'VIGENTE', 'SDG LTA'],
            ['30500012516', '93', 'BANCO DE LA PAMPA SOCIEDAD DE ECONOMIA MIXTA', 'VIGENTE', 'RES104/07(DISERE)'],
            ['30500010602', '94', 'BANCO DE CORRIENTES S.A.', 'VIGENTE'],
            ['30500014047', '97', 'BANCO PROVINCIA DEL NEUQUEN S.A.', 'VIGENTE', 'SDG LTA'],
            ['30715899716', '143', 'BRUBANK S.A.U.', 'VIGENTE'],
            ['144', 'BANCO ARGENTINO DE INVERSION S.A.', 'ELIMINADO'],
            ['30522714417', '147', 'BANCO INTERFINANZAS S.A.', 'VIGENTE', 'Res.Nº46/13(DI SERE)'],
            ['33537186009', '150', 'HSBC BANK ARGENTINA S.A.', 'VIGENTE', 'SDG LTA', 'Si'],
            ['162', 'BANCO MAYO COOPERATIVO LIMITADO', 'ELIMINADO'],
            ['30583137943', '165', 'JP MORGAN CHASE BANK NA (SUCURSAL BUENOS AIRES)', 'VIGENTE', 'RES.137/05(DI SERE)'],
            ['30571421352', '191', 'BANCO CREDICOOP COOPERATIVO LIMITADO', 'VIGENTE', 'SDG LTA'],
            ['30576124275', '198', 'BANCO DE VALORES S.A.', 'VIGENTE', 'SDG LTA'],
            ['222', 'CAJA DE VALORES S.A.', 'ELIMINADO'],
            ['231', 'BANCO DE RIO TERCERO COOP.LTDO.', 'ELIMINADO'],
            ['236', 'BANCO DO ESTADO DE SAO PAULO S.A.', 'ELIMINADO'],
            ['30535610440', '247', 'BANCO ROELA S.A.', 'VIGENTE'],
            ['30516420444', '254', 'BANCO MARIVA S.A.', 'VIGENTE', 'SDG LTA'],
            ['256', 'CITICORP BANCO DE INVERSION S.A.', 'ELIMINADO'],
            ['30580189411', '259', 'BANCO ITAU ARGENTINA S.A.', 'VIGENTE', 'Res106/08(DISERE)'],
            ['260', 'BANCO EXTERIOR DE AMERICA S.A.', 'ELIMINADO'],
            ['30500050558', '262', 'BANK OF AMERICA NATIONAL ASSOCIATION', 'VIGENTE'],
            ['30584727566', '266', 'BNP PARIBAS', 'VIGENTE', 'SDG LTA', 'Si'],
            ['30575655781', '268', 'BANCO PROVINCIA DE TIERRA DEL FUEGO', 'VIGENTE', 'SDG LTA'],
            ['30588337843', '269', 'BANCO DE LA REP. ORIENTAL DEL URUGUAY', 'VIGENTE', 'SDG LTA', 'Si'],
            ['274', 'OF CREDIT AND COMMERCE', 'ELIMINADO'],
            ['30534672434', '277', 'BANCO SAENZ  S.A.', 'VIGENTE'],
            ['30534487491', '281', 'BANCO MERIDIAN S.A.', 'VIGENTE', 'R.103/08(DISERE)', 'Si'],
            ['30500010084', '285', 'BANCO MACRO S.A.', 'VIGENTE', '52/07 (DI SERE)'],
            ['287', 'BANCO MEDEFIN UNB S.A.', 'ELIMINADO'],
            ['298', 'BANCO AUSTRAL S.A.', 'ELIMINADO'],
            ['30604731018', '299', 'BANCO COMAFI S.A.', 'VIGENTE', 'SDG LTA'],
            ['30651129083', '300', 'BANCO DE INVERSION Y COMERCIO EXTERIOR S.A.', 'VIGENTE'],
            ['30569151763', '301', 'BANCO PIANO S.A.', 'VIGENTE', 'SDG LTA'],
            ['302', 'BANCO EXTRADER S.A.', 'ELIMINADO'],
            ['30518954241', '303', 'BANCO FINANSUR S.A.', 'ELIMINADO', 'Res.079/17(DI SERE)'],
            ['30657441216', '305', 'BANCO JULIO S.A.', 'VIGENTE', 'SDG LTA'],
            ['306', 'BANCO PRIVADO DE INVERSIONES S.A.', 'ELIMINADO'],
            ['307', 'BANCO MAYORISTA DEL PLATA S.A.', 'ELIMINADO'],
            ['30671859339', '309', 'BANCO RIOJA SOCIEDAD ANÓNIMA UNIPERSONAL', 'VIGENTE', 'RES. 88/16(DI SERE)'],
            ['30677937560', '310', 'BANCO DEL SOL S.A.', 'VIGENTE'],
            ['30670157799', '311', 'NUEVO BANCO DEL CHACO S.A.', 'VIGENTE', '076/09 (DI SERE)'],
            ['30546741636', '312', 'BANCO VOII S.A.', 'VIGENTE'],
            ['30671375900', '315', 'BANCO DE FORMOSA S.A.', 'VIGENTE'],
            ['316', 'BANCO DE MISIONES S.A.', 'ELIMINADO'],
            ['30576614299', '319', 'BANCO CMF S.A.', 'VIGENTE', 'SDG LTA'],
            ['33686664649', '321', 'BANCO DE SANTIAGO DEL ESTERO S.A.', 'VIGENTE'],
            ['30685029959', '322', 'BANCO INDUSTRIAL S.A.', 'VIGENTE', '075/10 (DI SERE)'],
            ['328', 'BANCO MENDOZA S.A.', 'ELIMINADO'],
            ['30692432661', '330', 'NUEVO BANCO DE SANTA FE S.A.', 'VIGENTE', '29/05 (DI SERE)'],
            ['30697306362', '331', 'BANCO CETELEM ARGENTINA S.A.', 'VIGENTE'],
            ['30697265895', '332', 'BANCO DE SERVICIOS FINANCIEROS S.A.', 'VIGENTE'],
            ['30701255557', '336', 'BANCO BRADESCO ARGENTINA SA', 'VIGENTE'],
            ['337', 'BANCO URQUIJO SA', 'ELIMINADO'],
            ['30704960995', '338', 'BANCO DE SERVICIOS Y TRANSACCIONES S.A.', 'VIGENTE'],
            ['30707108343', '339', 'RCI BANQUE S.A.', 'VIGENTE'],
            ['30707227415', '340', 'BACS BANCO DE CREDITO Y SECURITIZACION S.A.', 'VIGENTE'],
            ['30540618263', '341', 'MAS VENTAS S.A.', 'VIGENTE'],
            ['30715654632', '384', 'WILOBANK S.A.', 'VIGENTE'],
            ['33707995519', '386', 'NUEVO BANCO DE ENTRE RIOS S.A.', 'VIGENTE', 'R.74/03 (DI SERE)'],
            ['30517637498', '389', 'BANCO COLUMBIA S.A.', 'VIGENTE'],
            ['30516544542', '405', 'FORD CREDIT CIA. FINAN. S.A.', 'VIGENTE'],
            ['30538006404', '408', 'COMPAÑIA FINANCIERA ARGENTINA S.A.', 'VIGENTE'],
            ['30581385516', '413', 'MONTEMAR CIA. FINAN. S.A.', 'VIGENTE'],
            ['30628284357', '415', 'TRANSATLANTICA COMPAÑIA FINANCIERA S.A.', 'VIGENTE'],
            ['30712331239', '426', 'BANCO BICA S.A.', 'VIGENTE'],
            ['30714195960', '431', 'BANCO COINAG S.A.', 'VIGENTE'],
            ['30542033637', '432', 'BANCO DE COMERCIO S.A.', 'VIGENTE', 'RES 41/17(DI SERE)', 'Si'],
            ['30716226944', '434', 'CREDITO REGIONAL COMPAÑIA FINANCIERA S.A.', 'VIGENTE'],
            ['30716090333', '435', 'BANCO SUCREDITO S.A.', 'VIGENTE'],
            ['30682419578', '437', 'VOLKSWAGEN FINANCIAL SERVICES COMPAÑIA FINANCIERA S.A.', 'VIGENTE'],
            ['30701810852', '438', 'CORDIAL COMPAÑIA FINANCIERA S.A.', 'VIGENTE'],
            ['30692304884', '440', 'FCA Compañía Financiera S.A.', 'VIGENTE'],
            ['30678564822', '441', 'GPAT COMPAÑIA FINANCIERA S.A.', 'VIGENTE'],
            ['30707002294', '442', 'MERCEDES-BENZ COMPAÑIA FINANCIERA ARGENTINA S.A.', 'VIGENTE'],
            ['33707124909', '443', 'ROMBO CIA. FINAN. S.A.', 'VIGENTE'],
            ['30707024859', '444', 'JOHN DEERE CREDIT CIA. FINAN. S.A.', 'VIGENTE'],
            ['30707847367', '445', 'PSA FINANCE ARGENTINA CIA. FINAN. S.A.', 'VIGENTE'],
            ['30709000426', '446', 'TOYOTA COMPAÑIA FINANCIERA DE ARGENTINA S.A.', 'VIGENTE'],
            ['30712592407', '448', 'BANCO DINO S.A.', 'VIGENTE'],
            ['30716395452', '515', 'BANK OF CHINA LIMITED, SUCURSAL BUENOS AIRES', 'VIGENTE'],
            ['33663293309', '992', 'PROVINCANJE SOCIEDAD ANONIMA', 'VIGENTE'],
            ['993', 'AFIP Seti DJ', 'VIGENTE'],
            ['33546663669', '998', 'CONSEJO PROFESIONAL DE CIENCIAS ECONOMICAS DE CABA', 'VIGENTE']
        ]

    @staticmethod
    def get_banks_list():
        """
        Obtiene la lista de bancos desde AFIP utilizando
        la libreria BeautifulSoup para webscraping
        """

        banks = []
        try:
            url = 'http://www.afip.gov.ar/genericos/emisorasGarantias/formularioCompa%C3%B1ias.asp?completo=1&ent=3'
            f = requests.post(url).content
            soup = BeautifulSoup(f)
            table = soup.find('table', attrs={"class": "contenido"})
            for row in table.findAll('tr')[2:]:
                banks.append([td.text.strip() for td in row.findAll('td') if td.text.strip()])
            return banks
        except Exception as e:
            return Banks.get_offline_banks_list()

    @staticmethod
    def get_values(banks_list):
        """
        :param banks_list: Lista de bancos.
        :return: Lista de diccionarios con los valores de cada banco
        """

        values = []
        for bank_list in banks_list:

            bank_values = {}

            if bank_list:

                # Validamos el cuit del banco para comprobar existencia
                if Contributor.is_valid_cuit(bank_list[0]):

                    bank_values['cuit'] = bank_list[0]
                    bank_values['code'] = bank_list[1]
                    bank_values['name'] = unidecode(bank_list[2])
                    values.append(bank_values)

        return values
