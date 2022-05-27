import pandas as pd
from datetime import datetime


def check_if_column_in_dataset(required_columns_subset: list, df_columns: pd.DataFrame.index):
    """
    static helper function to check if a line is used or not. Helpful to dynamically write lines to the export file where necessary.
    :param required_columns_subset: set of mandatory columns per line
    :param df_columns: df.columns
    :return: boolean true or false or exception with error message
    """
    if any(column in required_columns_subset for column in df_columns):
        if not all(column in df_columns for column in required_columns_subset):
            missing_columns = {}
            for column in required_columns_subset:
                if column not in df_columns:
                    missing_columns[column] = get_field_info(column)
            raise Exception(f"You are missing: {', '.join(missing_columns.keys())} from the following required columns : {', '.join(required_columns_subset)}. {[f'Colomn {column} should contain: {missing_columns[column]}' for column in missing_columns]}")
        else:
            return True
    else:
        return False


def get_field_info(info_field: str):
    info = {
        'lastname': 'Employees last name',
        'firstname': 'Employees first name',
        'birthname': 'Employees birth name',
        'street': 'Street of living address',
        'housenumber': 'Housenumber of living address, including any additions',
        'postalcode': 'Postal code of living address',
        'postalcode_foreign_country': 'Postal code of living address in foreign country',
        'city': 'City of living address',
        'date_of_birth': 'Employees date of birth',
        'place_of_birth': 'Employees city of birth',
        'country_of_birth': 'Employees country of birth (find the accepted codes in the DATEV documentation at: 4214 Nationalitätenschlüssel Lohn)',
        'gender': 'Employees gender (find the accepted codes in the DATEV documentaiton at: 4767 GESCHLECHT KIND)',
        'social_security_number': 'Health insurance or social security number',
        'nationality': 'Employees nationality (find the accepted codes in the DATEV documentation at: 4214 Nationalitätenschlüssel Lohn)',
        'iban': 'Employees IBAN',
        'bic': 'Employees bank BIC code',
        'disabled': 'Boolean disabled employee or not. 0 or 1',
        'type_of_employee': 'Type of employee (find the accepted codes in the DATEV documetation at: 4663 MITARBEITERTYP',
        'costcenter': 'Employees costcenter code',
        'costcenter_percentage': 'Percentage that the employee works at the given costcenter',
        'costcarrier': 'Employees costcarrier code',
        'costcarrier_percentage': 'Percentage that the employee works at the given costcarrier',
        'date_in_service': 'Date that the employee first worked for the company',
        'payment_type': 'Payment type. Should be 5 for SEPA. See 4181 KENNZEICHEN ZAHLUNGSART in DATEV documentation',
        'first_day_of_employment': 'Startdate of current employment',
        'salary_amount': 'Salary amount that employee is payed each month',
        'tracking_number': 'Salary entry tracking number',
        'company_bicycle_amount': 'Amount that employee receives for a company bicycle monthly',
        'hourly_wage': 'Employees hourly salary',
        'insurancefund_number': 'Code of insurance fund (krankenkasse) for the employee',
        'unemployment_insurance': 'Boolean if employee has unemployment insurance. 0 or 1',
        'health_insurance': 'Boolean if employee has health insurance. 0 or 1',
        'healthcare_insurance': 'Boolean if employee has healthcare insurance. 0 or 1',
        'pension_insurance': 'Boolean if employee has pension insurance. 0 or 1',
        'mandatory_insurance': 'Boolean if employee has mandatory accident insurance. 0 or 1',
        'hourly_wager': 'Boolean if employee is an hourly paid worker. 0 or 1',
        'person_group': 'Type of social insurance group. See DATEV documentation at: 4209 Personengruppe Sozialversicherung',
        'position': 'Berufsbezeichnung',
        'place_of_work': 'City where this employee works',
        'job_performed': 'Ausgeübte Tätigkeit',
        'job_performed_description': 'LDFNR Ausgeübte Tätigkeit, trackingnumber Ausgeübte Tätigkeit',
        'highest_degree': 'Code for highest degree received. See 4534 KZ BILDUNGSABSCHLUSS EF41 in DATEV documentation',
        'highest_training': 'Code for highest training received. See 4601 HOECHSTER AUSBILDUNGSABSCHLUSS in DATEV documentation',
        'type_of_contract': 'Type of employment. See 4603 VERTRAGSFORM in DATEV documentation for accepted values',
        'employee_type_social_insurance': 'Type of employee for insurance. See 4097 RENTENVERSICHERUNGS-BEITAGSGRUPPE in DATEV documentation',
        'tax_class': 'Tax bracket code for the employee. Number between 0-6',
        'main_employer': 'Boolean if employer is employees main employer. 0 or 1',
        'religion': 'Code of employees religion (find the accepted codes in the DATEV documentation at: 4624 KONFESSION )',
        'taxnumber': 'Employees tax number',
        'hours_per_week': 'Amount of hours weekly that an employee works according to timetable',
        'hours_monday': 'Amount of hours that an employee works according to timetable on mondays',
        'hours_tuesday': 'Amount of hours that an employee works according to timetable on tuesdays',
        'hours_wednesday': 'Amount of hours that an employee works according to timetable on wednesdays',
        'hours_thursday': 'Amount of hours that an employee works according to timetable on thursdays',
        'hours_friday': 'Amount of hours that an employee works according to timetable on fridays',
        'hours_saturday': 'Amount of hours that an employee works according to timetable on saturdays',
        'hours_sunday': 'Amount of hours that an employee works according to timetable on sundays',
        'yearly_vacation_hours': 'Hours of leave that an employee is entitled to yearly'
    }

    return info[info_field]


class Datev(object):
    def __init__(self, berater_nr: int, mandanten_nr: int):
        self.berater_nr = berater_nr
        self.mandanten_nr = mandanten_nr

    def export_to_template(self, df: pd.DataFrame,
                           filepath: str, valid_from: str = datetime.today().strftime('%d.%m.%Y'),
                           use_alternative_employee_number: bool = False,
                           filename: str = f"importfile_{datetime.now().strftime('%B')}_{datetime.now().year}.txt"):
                           # , wagecomponents: dict = None):
        """
        This method has the Datev template for LODAS. Calling this with the right parameters will result in an export file generated for each line in the df to the filepath specified
        :param df: dataframe from which the data is to be extracted
        :param filepath: folder to which the export files will be written
        :param filename: filename if you want to use a custom filename. Otherwise will be importfile_month_year.txt
        :param valid_from: field to determine from when the data is valid
        :param use_alternative_employee_number: bool to use BetrieblichePNr yes or no.
        :param wagecomponents: dictionary of wagecomponents and corresponding info. should be following format: {"wagecomponent": 123, "amount": 500}
        :return: nothing
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                return f'Column {field} is required. Required columns are: {tuple(required_fields)}'

        template_headers = ["[Allgemein]\n",
                            "Ziel=LODAS\n",
                            "Version_SST=1.0\n",
                            f"BeraterNr={self.berater_nr}\n",
                            f"MandantenNr={self.mandanten_nr}\n",
                            "Kommentarzeichen=*\n",
                            "Feldtrennzeichen=;\n",
                            "Zahlenkomma=,\n",
                            "Datumsformat=TT.MM.JJJJ\n",
                            # f"StammdatenGueltigAb={valid_from}\n",
                            f"{'BetrieblichePNrVerwenden=Ja' if use_alternative_employee_number else 'BetrieblichePNrVerwenden=Nein'}" + '\n' + '\n']
        template_description = "[Satzbeschreibung]\n"\
                               f"100;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};{'pnr#psd' if use_alternative_employee_number else 'pnr_betriebliche#psd'};duevo_familienname#psd;duevo_vorname#psd;gebname#psd;adresse_strassenname#psd;adresse_strasse_nr#psd;adresse_plz#psd;adresse_plz_ausland#psd;adresse_ort#psd;\n" \
                               f"101;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};geburtsdatum_ttmmjj#psd;gebort#psd;geburtsland#psd;geschlecht#psd;sozialversicherung_nr#psd;staatsangehoerigkeit#psd;email#psd;\n" \
                               f"102;u_lod_psd_ma_bank;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};ma_iban#psd;ma_bic#psd;ma_bank_zahlungsart#psd;\n" \
                               f"103;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};schwerbeschaedigt#psd;mitarbeitertyp#psd;\n" \
                               f"104;u_lod_psd_kstellen_verteil;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kostenstelle#psd;prozentsatz_kst#psd;\n" \
                               f"105;u_lod_psd_ktraeger_verteil;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kostentraeger#psd;prozentsatz_ktr#psd;\n" \
                               f"200;u_lod_psd_mitarbeiter;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};ersteintrittsdatum#psd;vorweg_abr_abruf_termin_kz#psd;\n" \
                               f"201;u_lod_psd_beschaeftigung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};eintrittdatum#psd;austrittdatum#psd;\n" \
                               f"235;u_lod_psd_besonderheiten;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};entlohnungsform#psd;\n" \
                               f"240;u_lod_psd_festbezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};betrag#psd;festbez_id#psd;intervall#psd;kuerzung#psd;kz_monatslohn#psd;lohnart_nr#psd;\n" \
                               f"262;u_lod_psd_lohn_gehalt_bezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};std_lohn_1#psd;\n" \
                               f"287;u_lod_psd_sozialversicherung;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};kk_nr#psd;av_bgrs#psd;kv_bgrs#psd;pv_bgrs#psd;rv_bgrs#psd;uml_schluessel#psd;nbl1_kz#psd;\n" \
                               f"292;u_lod_psd_sv_unfall;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};uv_kz_pflichtig#psd;uv_kz_stundenerm#psd;\n" \
                               f"300;u_lod_psd_taetigkeit;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};persgrs#psd;berufsbezeichnung#psd;beschaeft_nr#psd;ausg_taetigkeit#psd;ausg_taetigkeit_lfdnr#psd;schulabschluss#psd;ausbildungsabschluss#psd;\n" \
                               f"400;u_lod_psd_taetigkeit;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};arbeitnehmerueberlassung#psd;vertragsform#psd;rv_beitragsgruppe#psd;\n" \
                               f"503;u_lod_psd_taetigkeit;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};stammkostenstelle#psd;stammkostentraeger#psd;kst_abteilungs_nr#psd;\n" \
                               f"701;u_lod_psd_steuer;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};st_klasse#psd;faktor#psd;kfb_anzahl#psd;els_2_haupt_ag_kz#psd;konf_an#psd;\n" \
                               f"702;u_lod_psd_steuer;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};identifikationsnummer#psd;pausch_einhtl_2#psd;\n" \
                               f"800;u_lod_psd_arbeitszeit_regelm;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};az_wtl_indiv#psd;regelm_az_mo#psd;regelm_az_di#psd;regelm_az_mi#psd;regelm_az_do#psd;regelm_az_fr#psd;regelm_az_sa#psd;regelm_az_so#psd;\n" \
                               f"801;u_lod_psd_arbeitszeit_regelm;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};url_tage_jhrl#psd;\n"
    # 241;u_lod_psd_festbezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};betrag#psd;festbez_id#psd;intervall#psd;kuerzung#psd;kz_monatslohn#psd;lohnart_nr#psd;
        template_body = '\n' + "[Stammdaten]"

        # This is the custom export that is different per customer. This one makes a txt for every new employee and adds information in the template with a string format.
        # template = self.get_template(valid_from, use_alternative_employee_number)
        with open(f"{filepath}{filename}", 'w', encoding="cp1252", newline='\r\n') as file:
            file.writelines(template_headers + [template_description] + [template_body])
            body = []
            numeric_columns = []
            for column in list(df.columns.values):
                # if column name is a digit, it is a wagecomponent
                if column.isdigit():
                    numeric_columns.append(column)

            for index, dfrow in df.iterrows():

                required_columns_subset = ['lastname', 'firstname', 'birthname', 'street', 'housenumber', 'postalcode', 'city']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"100;{dfrow['employee_id']};{dfrow['alternative_employee_id'] + ';' if 'alternative_employee_id' in df.columns.values else ''}{dfrow['lastname']};{dfrow['firstname']};{dfrow['birthname']};{dfrow['street']};{dfrow['housenumber']};{dfrow['postalcode']};{dfrow['postalcode_foreign_country']};{dfrow['city']};" + "\n")

                required_columns_subset = ['date_of_birth', 'place_of_birth', 'country_of_birth', 'gender', 'social_security_number', 'nationality']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"101;{dfrow['employee_id']};{dfrow['date_of_birth']};{dfrow['place_of_birth']};{dfrow['country_of_birth']};{dfrow['gender']};{dfrow['social_security_number']};{dfrow['nationality']};{dfrow['mail']};" + "\n")

                required_columns_subset = ['iban', 'bic']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"102;{dfrow['employee_id']};{dfrow['iban']};{dfrow['bic']};5;" + "\n")

                required_columns_subset = ['disabled', 'type_of_employee']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"103;{dfrow['employee_id']};{dfrow['disabled']};{dfrow['type_of_employee']};" + "\n")

                required_columns_subset = ['costcenter', 'costcenter_percentage','costcarrier', 'costcarrier_percentage', 'department']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"104;{dfrow['employee_id']};{dfrow['costcenter']};{dfrow['costcenter_percentage']};" + "\n")
                    body.append(f"105;{dfrow['employee_id']};{dfrow['costcarrier']};{dfrow['costcarrier_percentage']};" + "\n")
                    body.append(f"503;{dfrow['employee_id']};{dfrow['costcenter']};{dfrow['costcarrier']};{dfrow['department']};" + "\n")

                # required_columns_subset = ['costcarrier', 'costcarrier_percentage']
                # if check_if_column_in_dataset(required_columns_subset, df.columns):

                required_columns_subset = ['date_in_service']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"200;{dfrow['employee_id']};{dfrow['date_in_service']};{dfrow['payment_type'] if 'payment_type' in dfrow.keys() else '5'};" + "\n")

                required_columns_subset = ['first_day_of_employment']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"201;{dfrow['employee_id']};{dfrow['first_day_of_employment']};{dfrow['enddate_employment'] if 'enddate_employment' in df.columns.values else ''};" + "\n")

                for column in numeric_columns:
                    if len(dfrow[column]) > 0 and dfrow[column] != '0' and dfrow[column] != '0,0':
                        body.append(f"240;{dfrow['employee_id']};{dfrow[column]};1;0;1;;{column};" + "\n")

                required_columns_subset = ['worker_salary_type']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"235;{dfrow['employee_id']};{dfrow['worker_salary_type']};" + "\n")

                required_columns_subset = ['salary_amount', 'tracking_number']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    if len(dfrow['salary_amount']) > 0:
                        body.append(f"240;{dfrow['employee_id']};{dfrow['salary_amount']};{dfrow['tracking_number']};0;{dfrow['discount'] if 'discount' in dfrow.keys() else 0};;200;" + "\n")

                required_columns_subset = ['company_bicycle_amount']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    if len(dfrow['company_bicycle_amount']) > 0:
                        body.append(f"240;{dfrow['employee_id']};{dfrow['company_bicycle_amount']};99;0;1;;233;" + "\n")

                required_columns_subset = ['hourly_wage']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"262;{dfrow['employee_id']};{dfrow['hourly_wage']};" + "\n")

                required_columns_subset = ['insurancefund_number', 'unemployment_insurance', 'health_insurance', 'healthcare_insurance', 'pension_insurance', 'health_insurance_region', 'umlage_schluessel']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"287;{dfrow['employee_id']};{dfrow['insurancefund_number']};{dfrow['unemployment_insurance']};{dfrow['health_insurance']};{dfrow['healthcare_insurance']};{dfrow['pension_insurance']};{dfrow['umlage_schluessel']};{dfrow['health_insurance_region']};" + "\n")

                required_columns_subset = ['mandatory_insurance', 'hourly_wager']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"292;{dfrow['employee_id']};{dfrow['mandatory_insurance']};{dfrow['hourly_wager']};" + "\n")

                required_columns_subset = ['person_group', 'position', 'place_of_work', 'job_performed', 'job_performed_description'] # , 'highest_degree', 'highest_training'
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(
                        f"300;{dfrow['employee_id']};{dfrow['person_group']};{dfrow['position']};{dfrow['place_of_work']};{dfrow['job_performed']};{dfrow['job_performed_description']};{dfrow['highest_degree'] if 'highest_degree' in df.columns else ''};{dfrow['highest_training'] if 'highest_training' in df.columns else ''};" + "\n")

                required_columns_subset = ['type_of_contract', 'employee_type_social_insurance', 'commercial_temporary_employment']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"400;{dfrow['employee_id']};{dfrow['commercial_temporary_employment']};{dfrow['type_of_contract']};{dfrow['employee_type_social_insurance']};" + "\n")

                required_columns_subset = ['tax_class', 'main_employer', 'religion']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"701;{dfrow['employee_id']};{dfrow['tax_class']};;;{dfrow['main_employer']};{dfrow['religion']};" + "\n")

                required_columns_subset = ['taxnumber', 'flat_rate_tax']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"702;{dfrow['employee_id']};{dfrow['taxnumber']};{dfrow['flat_rate_tax']};" + "\n")

                required_columns_subset = ['hours_per_week', 'hours_monday', 'hours_tuesday', 'hours_wednesday', 'hours_thursday', 'hours_friday', 'hours_saturday', 'hours_sunday']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(
                        f"800;{dfrow['employee_id']};{dfrow['hours_per_week']};{dfrow['hours_monday']};{dfrow['hours_tuesday']};{dfrow['hours_wednesday']};{dfrow['hours_thursday']};{dfrow['hours_friday']};{dfrow['hours_saturday']};{dfrow['hours_sunday']};" + "\n")

                required_columns_subset = ['yearly_vacation_hours']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"801;{dfrow['employee_id']};{dfrow['yearly_vacation_hours']};" + "\n")

            file.writelines(['\n'] + body)

    def export_hours(self, df: pd.DataFrame, filepath: str, use_alternative_employee_number: bool = False, filename: str = f"importfile_hours_{datetime.now().strftime('%B')}_{datetime.now().year}.txt"):
        """
        This method has the Datev template for LODAS. Calling this with the right parameters will result in an export file generated for each line in the df to the filepath specified
        :param df: dataframe from which the data is to be extracted
        :param filepath: folder to which the export files will be written
        :param filename: filename if you want to use a custom filename. Otherwise will be importfile_month_year.txt
        :param valid_from: field to determine from when the data is valid
        :param use_alternative_employee_number: bool to use BetrieblichePNr yes or no.
        :return: nothing
        """

        required_fields = []
        for field in required_fields:
            if field not in df.columns:
                return f'Column {field} is required. Required columns are: {tuple(required_fields)}'

        template_headers = ["[Allgemein]\n",
                            "Ziel=LODAS\n",
                            f"BeraterNr={self.berater_nr}\n",
                            f"MandantenNr={self.mandanten_nr}\n",
                            "Datumsformat=TT/MM/JJJJ\n",
                            f"{'BetrieblichePNrVerwenden=Ja' if use_alternative_employee_number else 'BetrieblichePNrVerwenden=Nein'}" + '\n' + '\n']

        template_description = "[Satzbeschreibung]\n"\
                               f"1;u_lod_bwd_buchung_standard;abrechnung_zeitraum#bwd;bs_nr#bwd;bs_wert_butab#bwd;la_eigene#bwd;kostenstelle#bwd;kostentraeger#bwd;abw_allg_zuschlag#bwd;abw_lohnfaktor#bwd;lohnver_proz_satz#bwd;pers_zuschlag#bwd;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};\n"

        # 241;u_lod_psd_festbezuege;{'pnr_betriebliche#psd' if use_alternative_employee_number else 'pnr#psd'};betrag#psd;festbez_id#psd;intervall#psd;kuerzung#psd;kz_monatslohn#psd;lohnart_nr#psd;
        template_body = '\n' + "[Bewegungsdaten]"

        # This is the custom export that is different per customer. This one makes a txt for every new employee and adds information in the template with a string format.
        # template = self.get_template(valid_from, use_alternative_employee_number)
        with open(f"{filepath}{filename}", 'w', encoding="cp1252", newline='\r\n') as file:
            file.writelines(template_headers + [template_description] + [template_body])
            body = []

            for index, dfrow in df.iterrows():

                required_columns_subset = ['year', 'period', 'value', 'type_of_hours', 'employee_id']
                if check_if_column_in_dataset(required_columns_subset, df.columns):
                    body.append(f"1;{datetime(dfrow['year'], dfrow['period'], 1).strftime('%d/%m/%Y')};1;{str(dfrow['value']).replace('.', ',')};{dfrow['type_of_hours']};;;;;;;{dfrow['employee_id']};\n")

            file.writelines(['\n'] + body)
