import json
from typing import AnyStr,  Iterable, List, Optional
import requests
from itertools import count
import logging
from re import findall
from calendar import monthrange
import unidecode


class RequestsPortal(object):
    def __init__(self, url_login: str = None, username: str = None,
                 password: AnyStr = None):

        self.url_login = url_login
        self.username = username
        self.password = password

    def get_cg(self, url, filter: str = None):

        """
        :param url: url -> Link
        :return: returns values referring to the endpoint
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)

        if filter:
            headers = {'Authorization': 'Token ' + key_headers['key']}
            return_inform = requests.get(url=f'{url}{filter}', headers=headers, verify=True)
            return_inform_format = json.loads(return_inform.text)
            return return_inform_format
        else:
            headers = {'Authorization': 'Token ' + key_headers['key']}
            return_inform = requests.get(url=url, headers=headers, verify=True)
            return_inform_format = json.loads(return_inform.text)

            return return_inform_format

    def post_cg(self, url, json_request):
        """
        :param url: url -> Link
        :param json_request: json for request
        :return: return status code
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)
        headers = {'Authorization': 'Token ' + key_headers['key'],
                   'Content-type': 'application/json',
                   'Accept': 'application/json'}
        try:
            x = requests.post(url=url, data=json.dumps(json_request),
                              headers=headers, verify=True)
        except:
            pass

    def patch_cg(self, url, json_request, filter: str = None):
        """
        :param url: url -> Link
        :param json_request: json with request
        :param filter: filter for request -> Exemple: ID or empresa__cnpj=0003131
        :return: return status code
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)
        headers = {'Authorization': 'Token ' + key_headers['key'],
                   'Content-type': 'application/json',
                   'Accept': 'application/json'}

        if filter:
            requests.patch(url=f'{url}{filter}', data=json.dumps(json_request),
                           headers=headers, verify=True)
        else:
            print('Não é possivel realizar um patch sem passar o Indice')

    def patch_file_cg(self, url, path, filter):
        """
        :param url: url -> Link
        :param path: file path
        :param filter: filter for request -> Exemple: ID or empresa__cnpj=0003131
        :return: return status code
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)
        headers = {'Authorization': 'Token ' + key_headers['key']}

        file_ob = {'arquivo': open(path, 'rb')}

        if filter:
            requests.patch(f'{url}{filter}', headers=headers, files=file_ob)
        else:
            print('Não é possivel realizar um patch sem passar o Indice')

    def delete_cg_generic(self, url, id, dict_inform, other_url):
        """
        :param url: url -> Link
        :param dict_inform: dict with informs for date iterable
        :param other_url: url for delete
        :param json_request: json with request
        :param id: filter for request -> Exemple: ID
        :return: return status code
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)

        headers = {'Authorization': 'Token ' + key_headers['key'],
                   'Content-type': 'application/json',
                   'Accept': 'application/json'
                   }

        return_inform = requests.get(url=f'{url}{id}/', headers=headers, verify=True)
        return_inform_format = json.loads(return_inform.text)

        n = count(0)

        for i_return_portal in return_inform_format['colaborador']:
            num = next(n)
            if str(dict_inform['id']) == str(i_return_portal['id']):
                return_inform_format['colaborador'].pop(num)

        try:
            x = requests.patch(url=f'{other_url}{return_inform_format["id"]}/',
                               data=json.dumps(return_inform_format),
                               headers=headers, verify=True)
        except:
            pass

    """ Generic Gets in projects the Portal """

    def get_generic_holerite(self, url, filter_cnpj, filter_competence, filter_type_competence):

        """
        :param url: url: url -> Link
        :param filter_cnpj: cnpj for filter
        :param filter_competence: date for filter
        :param filter_type_competence: type_competence for filter, Exemple: Adiantamento or Mensal
        :return: returns values referring to the endpoint
        """

        params = {
            'username': self.username,
            'password': self.password
        }
        key = requests.post(self.url_login, data=params)
        key_headers = json.loads(key.text)

        headers = {'Authorization': 'Token ' + key_headers['key']}
        return_inform = requests.get(url=f'{url}?empresa__cnpj={filter_cnpj}&competencia__competencia='
                                         f'{filter_competence}&tipo_calculo={filter_type_competence}',
                                     headers=headers, verify=True)

        return_inform_format = json.loads(return_inform.text)

        return return_inform_format


class SigHandler:
    def __init__(self, url_sig_company_events: str = AnyStr, url_sig_company_events_task: str = AnyStr):
        self.url_sig_company_events = url_sig_company_events
        self.url_sig_company_events_task = url_sig_company_events_task

    def mark_on_sig(self, id_task: list = List, id_dominio: str = AnyStr, event: str = AnyStr, tag: str = AnyStr,
             user: str = AnyStr):
        """

        :param user: user id which will be shown in sig
        :param id_task: list with the ids that will be marked
        :param id_dominio: str with the 'id dominio' of the company
        :param event: str with the event that will be marked, ex.: 'BALANCETE'
        :param tag: str with the key, ex.: 'nome_evento', 'nome_evento_tarefa'...
        :return: bool, True if marked or False if not marked
        """
        logging.warning("Starting to mark...")
        data_dictionary = json.loads(requests.get(self.url_sig_company_events, verify=False).text)["dados"]
        mark = False
        for data in data_dictionary:
            if (data["id_dominio"] == id_dominio) and (unidecode.unidecode(data[tag]) == event or
                                                       event in unidecode.unidecode(data[tag])):
                for dice in data["tarefas"]:
                    for ID in id_task:
                        if dice["id_tarefa"] == ID:
                            url2 = self.url_sig_company_events_task.format(dice["id_empresa_evento_tarefa"])
                            task_completed = {"dados": json.dumps({"status": "CON", "id_usuario": user})}
                            headers = {'Accept': 'application/json, text/plain, */*',
                                       'Content-Type': 'application/x-www-form-urlencoded'}
                            requests.put(url=url2, data=task_completed, headers=headers, verify=False)
                            mark = True
        logging.warning("Finished marking")
        return mark

    def check_sig(self, id_dominio: str = AnyStr, event: str = AnyStr, tag: str = AnyStr):
        """

        :param tag: str with the key, ex.: 'nome_evento', 'nome_evento_tarefa'...
        :param event: str with the event that will be checked, ex.: 'BALANCETE'
        :param id_dominio: str with the 'id dominio' of the company
        :return: dict with the tasks ids and status, true if the task has been marked else false
        """
        logging.warning("Starting to check...")
        data_dictionary = json.loads(requests.get(self.url_sig_company_events, verify=False).text)["dados"]
        task = {}
        for data in data_dictionary:
            if (data["id_dominio"] == id_dominio) and (unidecode.unidecode(data[tag]) == event or
                                                       event in unidecode.unidecode(data[tag])):
                for dice in data["tarefas"]:
                    task.update({dice["id_tarefa"]: False if dice["status"] == "NCON" else True})
        logging.warning("Finished checking")
        return task


class IntranetRequests:
    def __init__(self, id_dominio: str = Optional, id_company: str = Optional):
        self.id_dominio = id_dominio
        self.id_company = id_company

    def tax_amount(self, url_tax_amount: str = AnyStr, code: int = Iterable, date: str = AnyStr):
        """

        :param url_tax_amount:
        :param date: str containing the competence of the file being worked on
        :param code: int with the tax code for identification on the intranet
        :return: float with the tax value
        """
        logging.warning("Extracting value...")

        date = date.split('.')
        last_day = monthrange(int(date[1]), int(date[0]))
        first_date = f"{str(date[1])}-{str(date[0])}-01"
        last_date = f"{str(date[1])}-{str(date[0])}-{str(last_day[1])}"
        url = url_tax_amount.format(self.id_dominio, first_date, last_date, str(code))
        req = requests.get(url, verify=False)
        text = req.text
        text = (text.replace('Array', '')).replace('  ', '')
        lines = text.splitlines()
        data_list = []

        for line in lines:
            if findall('[a-z]', line):
                data_list.append(line)
        value = float((data_list[-1]).split(' ')[-1])
        logging.warning(f"The value that was extracted: {value}")
        return value

    def get_intranet(self, url, filter: str = None):

        """
        :param url: Url do GET - Deve ser informada no .env
        :return: Informacoes do Intranet
        """

        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json'}
        if filter:
            return_inform = requests.get(url=f'{url}{filter}', headers=headers, verify=True)
            return_inform_format = json.loads(return_inform.text)

            return return_inform_format
        else:
            return_inform = requests.get(url=url, headers=headers, verify=True)
            return_inform_format = json.loads(return_inform.text)

            return return_inform_format

    def get_company_email(self, url_client_email: str = AnyStr, company: str = AnyStr, sector: str = AnyStr,
                          tag_number: str = AnyStr):
        """

        :param url_client_email:
        :param company: str with the company name
        :param sector: str with the sector number and name, ex.: '2-Fiscal'
        :param tag_number: str with the tag number in the db
        :return: dict with data and status of the request
        """
        logging.warning("Extracting company email...")

        req = requests.get(url_client_email + self.id_company, verify=False)
        text = req.text

        text_json = json.loads(text)
        data = text_json["dados"]
        group = [company, self.id_dominio]
        email = []

        if not data:
            if group not in email:
                logging.warning("Email not found")
                return {"data": '', "status": False}
        else:
            for dat in data:
                try:
                    if sector in dat["setores"] and tag_number in dat["tags"]:
                        email.append(dat['email'])
                except TypeError:
                    continue
            if not email:
                logging.warning("Email not found")
                return {"data": '', "status": False}
        for item in email:
            try:
                if '@' in item:
                    logging.warning("Extracted email")
                    return {"data": email, "status": True}
            except TypeError:
                continue
        logging.warning("Email not found")
        return {"data": '', "status": False}

    def get_deadline(self, url_deadline: str = AnyStr, event: str = AnyStr, tag: str = AnyStr):
        """

        :param url_deadline:
        :param event: str with the event that will be marked, ex.: 'BALANCETE'
        :param tag: str with the key, ex.: 'nome_evento', 'nome_evento_tarefa'...
        :return: str with the deadline
        """
        logging.warning("Extracting deadline...")
        data_dictionary = json.loads(requests.get(url_deadline, verify=False).text)["dados"]
        deadline = AnyStr
        for dic in data_dictionary:
            try:
                if dic['id_dominio'] == self.id_dominio:
                    if dic[tag] == event or event in dic[tag]:
                        date = str(dic['prazo_final']).split('-')
                        deadline = f"{date[2]}/{date[1]}/{date[0]}"
            except:
                continue
        logging.warning("Extracted deadline")
        return deadline


