from datetime import datetime
from odoo.addons.sm_maintenance.models.models_sm_utils import sm_utils

class report_helper(object):
  _name = 'report_helper'

  __instance = None

  @staticmethod
  def get_instance():
    if report_helper.__instance is None:
      report_helper()
    return report_helper.__instance

  def __init__(self):
    if report_helper.__instance is not None:
      raise Exception("This class is a singleton!")
    else:
      report_helper.__instance = self

  def get_without_false(self, field):
    if not field:
      return ""
    return str(field)

  def fill_document(self, objects_to_iterate, worksheet):

    row = 1
    col = 0

    day_format = "%d/%m/%Y"
    hour_format = "%H:%M"
    for object in objects_to_iterate:
      # DADES DE L’ESTABLIMENT
      if object.member_id.cs_user_type == 'maintenance':
        pagador = object.env.user.company_id.partner_id
      else:

        if object.related_company_object:
          pagador = object.related_company_object
        else:
          pagador = object.member_id

      worksheet.write_string(row, col + 0, "SOM MOBILITAT SCCL")
      worksheet.write_string(row, col + 1, "F66835125".upper())
      worksheet.write_string(row, col + 2, "Carrer Tolón 26".upper())
      worksheet.write_string(row, col + 3, "Mataró".upper())
      worksheet.write_string(row, col + 4, "Barcelona".upper())

      # DADES DEL PAGADOR

      is_company = False
      if pagador.company_type == 'company':
        is_company = True

      if not is_company:
        worksheet.write_string(row, col + 5, self.get_without_false(pagador.firstname).upper())
      else:
        worksheet.write_string(row, col + 5, self.get_without_false(pagador.name).upper())

      if not is_company:
        worksheet.write_string(row, col + 6, self.get_without_false(pagador.lastname).upper())
        worksheet.write_string(row, col + 7, "")  # SEGON COGNOM
        #worksheet.write_string(row, col + 7,
        #  self.get_without_false(pagador.second_surname).upper())  # SEGON COGNOM

      else:
        worksheet.write_string(row, col + 6, "")
        worksheet.write_string(row, col + 7, "")  # SEGON COGNOM
      if not is_company:
        if pagador.birthdate_date:
          birthdate = datetime.strptime(str(pagador.birthdate_date), "%Y-%m-%d")
          worksheet.write_string(row, col + 8,
            self.get_without_false(birthdate.strftime(day_format)).upper())
        else:
          worksheet.write_string(row, col + 8, "")

      else:
        worksheet.write_string(row, col + 8, "")

      if str(pagador.id_document_type).upper() == "DNI" or is_company:
        worksheet.write_string(row, col + 9, "ESPANYA")  # NACIONALITAT
      else:
        worksheet.write_string(row, col + 9, "")  # NACIONALITAT

      type_doc = ""
      if is_company:
        worksheet.write_string(row, col + 10, "CIF")  # TIPUS DOC
        worksheet.write_string(row, col + 11, self.get_without_false(pagador.vat).upper())
      else:
        if pagador.id_document_type:
          type_doc = pagador.id_document_type

        worksheet.write_string(row, col + 10, type_doc.upper())  # TIPUS DOC
        worksheet.write_string(row, col + 11, self.get_without_false(pagador.vat).upper())
      if str(type_doc).upper() == "DNI" or is_company:
        worksheet.write_string(row, col + 12, "ESPANYA")  # PAIS DOCUMENT
      else:
        worksheet.write_string(row, col + 12, "")  # PAIS DOCUMENT
      street = pagador.street
      zip = pagador.zip
      city = pagador.computed_city
      state = pagador.computed_state

      address = ""
      if street:
        address += street
      if zip:
        address += ", " + zip
      if city:
        address += ", " + city
      if state:
        address += ", " + state
      worksheet.write_string(row, col + 13, address.upper())
      worksheet.write_string(row, col + 14, self.get_without_false(pagador.phone).upper())
      worksheet.write_string(row, col + 15, self.get_without_false(pagador.email).upper())
      if object.member_id.cs_user_type == 'maintenance':
        worksheet.write_string(row, col + 16, "")
      else:
        worksheet.write_string(row, col + 16, "D")

      worksheet.write_string(row, col + 17, "")  # TARGETA BANCARIA

      # CONDUCTOR HABITUAL -------------------

      if object.member_id.reporting_related_member_id:
        conductor = object.member_id.reporting_related_member_id
      else:
        conductor = object.member_id

      worksheet.write_string(row, col + 18, self.get_without_false(conductor.firstname).upper())
      worksheet.write_string(row, col + 19, self.get_without_false(conductor.lastname).upper())
      worksheet.write_string(row, col + 20, "")  # SEGON COGNOM
      #worksheet.write_string(row, col + 20,
      #  self.get_without_false(conductor.second_surname).upper())  # SEGON COGNOM

      if conductor.birthdate_date:
        birthdate_date = datetime.strptime(str(conductor.birthdate_date), "%Y-%m-%d")
        worksheet.write_string(row, col + 21,
          self.get_without_false(birthdate_date.strftime(day_format)).upper())
      else:
        worksheet.write_string(row, col + 21, self.get_without_false("").upper())
      type_doc = ""
      if conductor.id_document_type:
        type_doc = conductor.id_document_type

      if str(type_doc).upper() == "DNI":
        worksheet.write_string(row, col + 22, "ESPANYA")  # NACIONALITAT
      else:
        worksheet.write_string(row, col + 22, "")  # NACIONALITAT

      worksheet.write_string(row, col + 23, type_doc.upper())  # TIPUS DOC
      worksheet.write_string(row, col + 24,
        self.get_without_false(conductor.vat).upper())
      worksheet.write_string(row, col + 25,
        self.get_without_false(conductor.vat).upper())  # NUM PERMIS CONDUCCIO
      if str(conductor.id_document_type).upper() == "DNI":
        if conductor.vat:
          worksheet.write_string(row, col + 26, "ESPANYA")
        else:
          worksheet.write_string(row, col + 26, "")
      # PAIS PERMIS CONDUCCIO
      else:
        worksheet.write_string(row, col + 26, "")

      street = conductor.street
      zip = conductor.zip
      city = conductor.computed_city
      state = conductor.computed_state

      address = ""
      if street:
        address += street
      if zip:
        address += ", " + zip
      if city:
        address += ", " + city
      if state:
        address += ", " + state

      worksheet.write_string(row, col + 27, address.upper())
      worksheet.write_string(row, col + 28, "")  # DOMICILI ACCIDENTAL
      worksheet.write_string(row, col + 29, self.get_without_false(conductor.phone).upper())
      worksheet.write_string(row, col + 30, self.get_without_false(conductor.email).upper())
      # SEGON CONDUCOTR-----------------------------------------------------------------------

      worksheet.write_string(row, col + 31, "")
      worksheet.write_string(row, col + 32, "")
      worksheet.write_string(row, col + 33, "")
      worksheet.write_string(row, col + 34, "")
      worksheet.write_string(row, col + 35, "")
      worksheet.write_string(row, col + 36, "")
      worksheet.write_string(row, col + 37, "")
      worksheet.write_string(row, col + 38, "")
      worksheet.write_string(row, col + 39, "")
      worksheet.write_string(row, col + 40, "")
      worksheet.write_string(row, col + 41, "")
      worksheet.write_string(row, col + 42, "")
      worksheet.write_string(row, col + 43, "")

      # DADS OPERACIO-------------------------------------------------------------------
      worksheet.write_string(row, col + 44, str(object.id))  # NUMERO ORDRE
      worksheet.write_string(row, col + 45, "")  # LLIURAMENT RETORN
      worksheet.write_string(row, col + 46,
        self.get_without_false(object.name).upper())  # REFERENCIA DEL CONTRACTE

      startTime = sm_utils.utc_to_local_datetime(str(object.startTime))

      effectiveStartTime = sm_utils.utc_to_local_datetime(str(object.effectiveStartTime))

      worksheet.write_string(row, col + 47, self.get_without_false(startTime.strftime(day_format)).upper())
      worksheet.write_string(row, col + 48,
                   self.get_without_false(effectiveStartTime.strftime(hour_format)).upper())  # DAY

      endTime = sm_utils.utc_to_local_datetime(str(object.endTime))

      effectiveEndTime = sm_utils.utc_to_local_datetime(str(object.effectiveEndTime))

      worksheet.write_string(row,
        col + 49, self.get_without_false(endTime.strftime(day_format)).upper())  # DAY
      worksheet.write_string(row,
        col + 50, self.get_without_false(effectiveEndTime.strftime(day_format)).upper())  # DAY
      worksheet.write_string(row,
        col + 51, self.get_without_false(effectiveEndTime.strftime(hour_format)).upper())  # HORA

      # TODO: change db car into fleet vehicle!
      car = object.related_current_car
      if car:
        worksheet.write_string(row, col + 52, self.get_without_false(car.vehicle_type).upper())
        worksheet.write_string(row, col + 53, self.get_without_false(car.model_id.brand_id.name).upper())
        worksheet.write_string(row, col + 54, self.get_without_false(car.model_id.name).upper())
        worksheet.write_string(row, col + 55, self.get_without_false(car.license_plate).upper())
        worksheet.write_string(row, col + 56, self.get_without_false(car.vin_sn).upper())
        worksheet.write_string(row, col + 57, "")  # QUILOMETRTEGATGE
        worksheet.write_string(row, col + 58, self.get_without_false(car.color).upper())
      else:
        worksheet.write_string(row, col + 52, "")
        worksheet.write_string(row, col + 53, "")
        worksheet.write_string(row, col + 54, "")
        worksheet.write_string(row, col + 55, "")
        worksheet.write_string(row, col + 56, "")
        worksheet.write_string(row, col + 57, "")  # QUILOMETRTEGATGE
        worksheet.write_string(row, col + 58, "")

      if car.has_gps:
        worksheet.write_string(row, col + 59, "S")
      else:
        worksheet.write_string(row, col + 59, "N")

      row += 1

  def generate_header(self, workbook):
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    worksheet.write('A1', 'RAÓ SOCIAL', bold)
    worksheet.write('B1', 'CIF/NIF/NIE', bold)
    worksheet.write('C1', "ADREÇA DE L'ESTABLIMENT (tipus de via, nom de la via, núm., pis, porta", bold)
    worksheet.write('D1', 'MUNICIPI', bold)
    worksheet.write('E1', 'PROVÍNCIA', bold)

    # PAGADOR
    worksheet.write('F1', 'NOM  (PAGADOR)', bold)
    worksheet.write('G1', 'PRIMER COGNOM', bold)
    worksheet.write('H1', 'SEGON COGNOM (si en té)', bold)
    worksheet.write('I1', 'DATA DE NAIXEMENT (dd/mm/aaaa)', bold)
    worksheet.write('J1', 'NACIONALITAT', bold)
    worksheet.write('K1', 'TIPUS DE DOCUMENT', bold)
    worksheet.write('L1', 'NÚMERO DEL DOCUMENT', bold)
    worksheet.write('M1', 'PAÍS DEL DOCUMENT', bold)
    worksheet.write('N1',
            'DOMICILI HABITUAL (tipus de via, nom de la via, núm., pis, porta, municipi, codi postal, província, país)',
            bold)
    worksheet.write('O1', 'TELÈFON DE CONTACTE', bold)
    worksheet.write('P1', 'CORREU ELECTRÒNIC', bold)
    worksheet.write('Q1', 'FORMA DE PAGAMENT (M: metàl·lic; D: domiciliació bancària; T: targeta de crèdit)', bold)
    worksheet.write('R1', 'NÚMERO DE LA TARGETA BANCÀRIA (quan sigui el cas)', bold)

    # PRIMER CONDUCTOR
    worksheet.write('S1', 'NOM (CONDUCTOR HABITUAL)', bold)
    worksheet.write('T1', 'PRIMER COGNOM', bold)
    worksheet.write('U1', 'SEGON COGNOM (si en té)', bold)
    worksheet.write('V1', 'DATA DE NAIXEMENT (dd/mm/aaaa)', bold)
    worksheet.write('W1', 'NACIONALITAT', bold)
    worksheet.write('X1', 'TIPUS DE DOCUMENT', bold)
    worksheet.write('Y1', 'NÚMERO DEL DOCUMENT', bold)
    worksheet.write('Z1', 'NÚMERO DEL PERMÍS DE CONDUCCIÓ', bold)
    worksheet.write('AA1', 'PAÍS DEL PERMÍS DE CONDUCCIÓ', bold)
    worksheet.write('AB1',
      'DOMICILI HABITUAL (tipus de via, nom de la via, núm., pis, porta, municipi, codi postal, província, país)',
      bold)
    worksheet.write(
      'AC1',
      'DOMICILI ACCIDENTAL (tipus de via, nom de la via, núm., pis, porta, municipi, codi postal, província, país)',
      bold)
    worksheet.write('AD1', 'TELÈFON DE CONTACTE', bold)
    worksheet.write('AE1', 'CORREU ELECTRÒNIC', bold)

    # SEGON CONDUCTOR
    worksheet.write('AF1', 'NOM (SEGON CONDUCTOR)', bold)
    worksheet.write('AG1', 'PRIMER COGNOM', bold)
    worksheet.write('AH1', 'SEGON COGNOM (si en té)', bold)
    worksheet.write('AI1', 'DATA DE NAIXEMENT (dd/mm/aaaa)', bold)
    worksheet.write('AJ1', 'NACIONALITAT', bold)
    worksheet.write('AK1', 'TIPUS DE DOCUMENT', bold)
    worksheet.write('AL1', 'NÚMERO DEL DOCUMENT', bold)
    worksheet.write('AM1', 'NÚMERO DEL PERMÍS DE CONDUCCIÓ', bold)
    worksheet.write('AN1', 'PAÍS DEL PERMÍS DE CONDUCCIÓ', bold)
    worksheet.write('AO1',
      'DOMICILI HABITUAL (tipus de via, nom de la via, núm., pis, porta, municipi, codi postal, província, país)',
      bold)
    worksheet.write('AP1',
      'DOMICILI ACCIDENTAL (tipus de via, nom de la via, núm., pis, porta, municipi, codi postal, província, país)',
      bold)
    worksheet.write('AQ1', 'TELÈFON DE CONTACTE', bold)
    worksheet.write('AR1', 'CORREU ELECTRÒNIC', bold)

    worksheet.write('AS1', "NÚMERO D'ORDRE DEL REGISTRE", bold)
    worksheet.write('AT1', 'TIPUS D’OPERACIÓ (L: lliurament; R: retorn)', bold)
    worksheet.write('AU1', 'REFERÈNCIA DEL CONTRACTE', bold)
    worksheet.write('AV1', 'DATA DE LLOGUER (dd/m/aaaa)', bold)
    worksheet.write('AW1', 'HORA DE LLIURAMENT DEL VEHICLE (hh:mm)', bold)
    worksheet.write('AX1', 'DATA PREVISTA DE RETORN (dd/mm/aaaa)', bold)
    worksheet.write('AY1', 'DATA DE RETORN (dd/mm/aaaa)', bold)
    worksheet.write('AZ1', 'HORA DE RETORN DEL VEHICLE (hh:mm)', bold)
    worksheet.write('BA1', 'TIPUS DE VEHICLE', bold)
    worksheet.write('BB1', 'MARCA DEL VEHICLE', bold)
    worksheet.write('BC1', 'MODEL DEL VEHICLE', bold)
    worksheet.write('BD1', 'MATRÍCULA DEL VEHICLE', bold)
    worksheet.write('BE1', 'NÚMERO DE BASTIDOR', bold)
    worksheet.write('BF1', 'QUILOMETRATGE', bold)
    worksheet.write('BG1', 'COLOR DEL VEHICLE', bold)
    worksheet.write('BH1', 'GPS INTEGRAT AL VEHICLE (S: si; N: no)', bold)

    return worksheet
