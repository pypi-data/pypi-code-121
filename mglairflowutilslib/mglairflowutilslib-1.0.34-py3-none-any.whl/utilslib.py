import requests
from json_logic.builtins import BUILTINS
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, date, timedelta
import dateutil.parser as parser
import string
import random
import shortuuid
import hashlib
from json_logic import jsonLogic
from enum import Enum
from airflow.models import Variable

DT_FMT_HMSf = '%H%M%S%f'


class HttpMethodEnum(Enum):
    POST = 'POST'
    PUT = 'PUT'
    GET = 'GET'
    DELETE = 'DELETE'


def invoke_http_request(endpoint, method, headers, payload=None, json_data=None, timeout=61, response_type="json"):
    """ here two exception block. one is for request exception and other is for json decoder exception.
    RequestException raise when some error occur in API response
    JSONDecodeError: sometimes we don't know our API response is in json format or not so, when we return
    response.json() it raise error if it not json format.
    """
    _request = requests_retry_session()
    _request.headers.update({
        **headers
    })
    try:
        response = None
        if method == HttpMethodEnum.GET.value:
            response = _request.get(url=endpoint, data=payload, timeout=timeout)
        if method == HttpMethodEnum.POST.value:
            response = _request.post(url=endpoint, data=payload, json=json_data, timeout=timeout)
        if method == HttpMethodEnum.PUT.value:
            response = _request.put(url=endpoint, data=payload, timeout=timeout)
        if method == HttpMethodEnum.DELETE.value:
            response = _request.delete(url=endpoint, data=payload, timeout=timeout)
        log_failed_http_request(endpoint, response.text, response.status_code)
        if response_type != "json":
            return response.text, response.status_code

        return response.json(), response.status_code
    except requests.exceptions.RequestException:
        print('Error raised while invoking %s', endpoint)
        raise
    except json.decoder.JSONDecodeError:
        print('JSON Decode Error raised while invoking %s', endpoint)
        return response, response.status_code


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def log_failed_http_request(endpoint, response, status_code):
    if not is_success_request(status_code):
        msg = 'Http {} | Error-{} : {}'.format(endpoint, status_code, response)
        print('Error raised ', msg)


def is_success_request(status_code):
    return 200 <= status_code <= 299


def date_within_next(date, number, period):
    if period == "days":
        return datetime.utcnow() <= str_to_datetime(date) <= (
                datetime.utcnow() + timedelta(days=int(number)))
    elif period == "weeks":
        return datetime.utcnow() <= str_to_datetime(date) <= (
                datetime.utcnow() + timedelta(weeks=int(number)))


def date_within_last(date, number, period):
    if period == "days":
        return (datetime.utcnow() - timedelta(
            days=int(number))) <= str_to_datetime(date) <= datetime.utcnow()
    elif period == "weeks":
        return (datetime.utcnow() - timedelta(
            weeks=int(number))) <= str_to_datetime(date) <= datetime.utcnow()


def str_to_datetime(date_time, str_format="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.strptime(date_time, str_format)
    except ValueError:
        return datetime.strptime(date_time, '%Y-%m-%d')


def get_datetime(date_string):
    """ this function will return datetime object with 2022-01-10 00:00:00 format"""
    return parser.parse(date_string)


def get_unique_key():
    """
    This method is used to get 32 bit unique key
    Steps:
        1. Get current timestamp in "%H%M%S%f" string format
        2. Select random string of 8 char and add with timestamp
        3. Generate 12 bit random string using shortuuid
    :return: 32 bit Unique key
    """

    timestamp = datetime.now().strftime(DT_FMT_HMSf)
    random_str = timestamp + ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(8))
    uuid_str = shortuuid.ShortUUID().random(length=12)
    return '{}{}'.format(uuid_str, random_str)


ops = {
    **BUILTINS,
    'starts_with': lambda data, a, b: a.startswith(b),
    'ends_with': lambda data, a, b: a.endswith(b),
    'date_between': lambda data, a, b, c: str_to_datetime(b) <= str_to_datetime(a) <= str_to_datetime(c),
    'date_within_next': lambda data, a, b, c: date_within_next(a, b, c),
    'date_within_last': lambda data, a, b, c: date_within_last(a, b, c),
    'date_after': lambda data, a, b: str_to_datetime(a) > str_to_datetime(b),
    'date_before': lambda data, a, b: str_to_datetime(a) < str_to_datetime(b),
    'date_yesterday': lambda data, a: str_to_datetime(a).date() == datetime.utcnow().date() - timedelta(days=1),
    'date_today': lambda data, a: str_to_datetime(a).date() == datetime.utcnow().date(),
    'date_tomorrow': lambda data, a: str_to_datetime(a).date() == datetime.utcnow().date() + timedelta(days=1),
    'date_is_empty': lambda data, a: a == ""
}


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def buildquery(json_object):
    """ This function can convert json form query to sql query. Note: Don't use single quotes ('') for input query"""

    if 'field' in json_object.keys():
        # In this case the json_object is an object which describes a single query
        if json_object.get("operator") == 'IN':
            value = json_object.get("value")
            value = tuple(num for num in value.replace('(', '').replace(')', '').replace('...', '').split(', '))
            return json_object.get("field") + " " + json_object.get("operator") + " " + str(value) + " "
        if json_object.get("operator") != 'BETWEEN':
            return json_object.get("field") + " " + json_object.get("operator") + " '" + json_object.get("value") + "' "
        else:
            return json_object.get("field") + " " + json_object.get("operator") + " '" + json_object.get(
                "value") + "' " + 'AND' + " '" + json_object.get("value2") + "' "

    # else it is an "condition+filters" JSON - Object
    else:
        i = 0
        # result = "("
        result = ""
        filter_array = json_object.get("filters")
        while i < len(filter_array):
            # Add (maybe nested) expression
            result += " " + buildquery(filter_array[i]) + " "

            # if we are already at the end of our filters array, do not add condition string
            # or we WOULD end up with something like ( a OR b OR c OR )

            if i != len(filter_array) - 1:
                result += json_object.get("condition")
            i = i + 1
        # result += ")"
        return result


module_id_dict = {'Campaigns': '1', 'Invoice': '2', 'SalesOrder': '3', 'PurchaseOrder': '4', 'Quotes': '5', 'Faq': '6',
                  'Vendors': '7', 'PriceBooks': '8', 'Calendar': '9', 'Leads': '10', 'Accounts': '11', 'Contacts': '12',
                  'Potentials': '13', 'Products': '14', 'Documents': '15', 'Emails': '16', 'HelpDesk': '17',
                  'Events': '18', 'Users': '19', 'Groups': '20', 'Currency': '21', 'DocumentFolders': '22',
                  'CompanyDetails': '23', 'Services': '24', 'ServiceContracts': '25', 'PBXManager': '26',
                  'ProjectMilestone': '27', 'ProjectTask': '28', 'Project': '29', 'Assets': '30', 'ModComments': '31',
                  'SMSNotifier': '32', 'LineItem': '33', 'Tax': '34', 'ProductTaxes': '35', 'PolicyPlan': '36',
                  'Commission': '37', 'AgentCommission': '38', 'VTERoundRobin': '41', 'VTESLALog': '42',
                  'VTEButtons': '43', 'VTEEmailPreview': '46', 'VReports': '49', 'RepliedSMSLog': '51',
                  'VTELabelEditor': '55', 'ToolbarIcons': '68', 'VTEFeedback': '88', 'AgentCommissionCFG': '90',
                  'Predicting': '91', 'Notifications': '95'}


def get_session_name(vtiger_access):
    vtiger_url = vtiger_access.get('vtiger_url')
    vtiger_username = vtiger_access.get('vtiger_username')
    access_key_encoded = vtiger_access.get('vtiger_access_key')

    if vtiger_url and vtiger_username and access_key_encoded:

        login_url = "{vtiger_url}/webservice.php".format(vtiger_url=vtiger_url)
        payload = 'operation=login&username={vtiger_username}&accessKey={access_key}'.format(
            access_key=access_key_encoded, vtiger_username=vtiger_username)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response, status = invoke_http_request(login_url, 'POST', headers, payload)

        if status == 200 and response.get('result', ''):
            print("existing session expired. New session id is: ", response.get('result').get('sessionName'))
            return response.get('result').get('sessionName')
        else:
            print("Can not get Session name from Vtiger. Error occurred with Status", status)
    else:
        print("unable to get required data from vtiger_access")


def trigger_workflow(workflow, event_type, data, service_url, api_access_key, source_module):
    """ call API to trigger any workflow
        Required params: 1. workflow 2. event_type 3. data"""

    headers = {'content_type': 'application/json', 'Authorization': api_access_key}

    endpoint = '{service_url}/api/v1/trigger-external-workflow'.format(service_url=service_url)

    print(f"Endpoint: {endpoint}")
    print(f"Event Type: {event_type}")
    print(f"Data Type: {data}")
    print(f"Service URl: {service_url}")
    print(f"source_module: {source_module}")
    if data:
        payload = {
            "workflow": workflow,
            "data": data,
            "eventtype": event_type,
            "source_module": source_module
        }

        response, status = invoke_http_request(endpoint, 'POST', headers, json_data=payload, timeout=61)
        print("response", response, "status", status)
    else:
        print("Can not trigger workflow. data is missing")


def json_logic_replace_data(rule, data, string_data=None, json_data=None):
    replace_data = jsonLogic(rule, data, ops)
    it = iter(replace_data)
    res_dct = dict(zip(it, it))

    if string_data:
        for key, val in res_dct.items():
            string_data = string_data.replace(key, str(val))

        return string_data
    elif json_data:

        str_json_data = json.dumps(json_data)
        for key, val in res_dct.items():
            str_json_data = str_json_data.replace(key, str(val))
        json_data = json.loads(str_json_data)
        return json_data


def run_external_workflow(conf, task_id, vtiger_access):
    """ this function will get check if conditions are satisfied for triggering external workflow or not.
        input:  1.conf : conf object
                2.task_id: current task id
                3.vtiger_access: vtiger_access config dict

        1. get external_workflow_config : config dictionary containing workflow, event_type, search_object
        2. get configs and create query.
        3. replace data using json logic.
        4. call trigger workflow function if conditions are satisfied.
        """

    if conf.get('external_workflow_config', ''):

        if task_id in conf.get('external_workflow_config', ''):
            external_workflow_config = conf.get('external_workflow_config').get(task_id, '')

        if external_workflow_config:

            data = conf.get('data', '')
            source_module = conf.get('source_module', '')
            workflow = external_workflow_config.get('workflow', '')
            event_type = external_workflow_config.get('event_type', '')

            search_object = external_workflow_config.get('search_object', '')
            print(f"Data: {data} \n Workflow: {workflow} \n Event Type: {event_type} \n Search Object: {search_object}")
            if search_object and search_object.get('condition_object', ''):
                rule = search_object.get('rule', '')

                # prepare query
                condition = buildquery(search_object.get('condition_object'))
                module = search_object.get('search_module').get('name')
                limit = str(search_object.get('fetch_record', ''))

                if event_type != 'import' and event_type != 'manual':
                    limit = '1'

                order_by = ''
                if search_object.get('sort', ''):
                    order_by = search_object.get('sort').get('column') + " " + search_object.get('sort').get(
                        'type', "")

                if limit and order_by:
                    query = 'SELECT * FROM {module} WHERE {condition} order by {order_by} LIMIT {limit};'.format(
                        module=module,
                        condition=condition,
                        order_by=order_by,
                        limit=limit)
                elif limit:
                    query = 'SELECT * FROM {module} WHERE {condition} LIMIT {limit};'.format(
                        module=module,
                        condition=condition,
                        limit=limit)
                elif order_by:
                    query = 'SELECT * FROM {module} WHERE {condition} order by {order_by};'.format(
                        module=module,
                        condition=condition,
                        order_by=order_by,
                    )
                else:
                    query = 'SELECT * FROM {module} WHERE {condition};'.format(
                        module=module,
                        condition=condition,
                    )

                # replace variable name with data using JSON_LOGIC.
                print(f"Query: {query}")
                if rule:
                    query = json_logic_replace_data(rule, conf, query)

                session_name = vtiger_access.get('vtiger_session', '')
                print("Session name: {}".format(session_name))
                if not session_name:
                    print("unable to get session id from vtiger access. Please try again")
                    return None

                url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query={query}'.format(
                    sessionName=session_name, query=query, vtiger_url=vtiger_access.get('vtiger_url'))
                print(f"Url: {url}")
                headers = {'content-type': 'application/json'}
                request_type = 'GET'
                response, status = invoke_http_request(url, request_type, headers)

                print(f"Response: {response}")

                if response:
                    if not response.get('success', ''):
                        if response.get('error', ''):
                            if response.get('error').get('code') in ["INVALID_USER_CREDENTIALS", "INVALID_SESSIONID"]:
                                session_name = get_session_name(vtiger_access)

                                # retry to execute query

                                url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query={query}'.format(
                                    sessionName=session_name, query=query, vtiger_url=vtiger_access.get('vtiger_url'))
                                response, status = invoke_http_request(url, request_type, headers)

                                vtiger_access['vtiger_session'] = session_name
                                Variable.update(key='vtiger_access', value=vtiger_access, serialize_json=True)

                if response:
                    # trigger only if condition is satisfied
                    if response.get('result') and workflow and event_type and module:

                        if event_type == 'import' or event_type == 'manual':
                            # if event type = import/ manual then pass list

                            trigger_workflow(workflow, event_type, response.get('result'),
                                             vtiger_access.get('service_url'), vtiger_access.get('api_access_key'), module)
                        else:
                            trigger_workflow(workflow, event_type, response.get('result')[0],
                                             vtiger_access.get('service_url'), vtiger_access.get('api_access_key'), module)
            elif workflow and event_type and data and source_module:
                # trigger without condition
                if event_type == 'import' or event_type == 'manual':
                    list_of_data = [data]
                    trigger_workflow(workflow, event_type, list_of_data, vtiger_access.get('service_url'),
                                     vtiger_access.get('api_access_key'), source_module)
                else:
                    trigger_workflow(workflow, event_type, data, vtiger_access.get('service_url'),
                                     vtiger_access.get('api_access_key'), source_module)

            else:
                print("Unable to get required data: workflow, event_type, data and source_module from payload ")
        else:
            print("external_workflow_config not found for task id:", task_id)
    else:
        print("external_workflow_config not found in conf")


def trigger_set_value_task(set_value_fields, conf, rule, session_name, vtiger_access, record_id):
    """   this function will execute revise query on vtiger for setting values
            params:
            1.set_value_fields : json object which have list of json payload of values to be set
            2.conf : conf object
            3.rule : json logic rule
            4.session_name : vtiger session
            3.vtiger_access : json object containing vtiger credentials

            Execution:
            1. get configs and create query and replace data using json logic.
            2. execute revise API on vtiger
            """

    print("Inside trigger_set_value_task")
    id = conf.get('data').get('id', '')
    lead_id = conf.get('data').get('leadid', '')
    record_module = conf.get('source_module', '')
    if not record_module:
        print("unable to get source module from conf  object")
        return None
    module = module_id_dict.get(record_module, '')
    print("Id: {}".format(id))
    print("lead_id: {}".format(lead_id))
    final_id = id if id else lead_id
    final_id = record_id if record_id else final_id
    print("Module {}".format(module))
    print("final_id {}".format(final_id))
    if final_id and record_module:
        id = final_id if "x" in final_id else module + 'x' + final_id
        element = {"id": str(id)}

        for record in set_value_fields:
            name = record.get('name')
            type = record.get('type')
            value = record.get('value')

            if type == 'static':
                if rule:
                    value = json_logic_replace_data(rule, conf, string_data=value)
                element[str(name)] = str(value)

            elif type == 'function':
                if rule:
                    value = json_logic_replace_data(rule, conf, string_data=value)
                element[str(name)] = str(eval(value))

        # call set value API
        payload = {'operation': 'revise', 'sessionName': session_name, 'element': json.dumps(element)}
        url = '{vtiger_url}/webservice.php'.format(vtiger_url=vtiger_access.get('vtiger_url'))
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        request_type = 'POST'

        print("Url: {}".format(url))
        print("Payload: {}".format(payload))

        response, status = invoke_http_request(url, request_type, headers, payload=payload)

        if response:
            if not response.get('success', ''):
                if response.get('error', ''):
                    if response.get('error').get('code') in ["INVALID_USER_CREDENTIALS", "INVALID_SESSIONID"]:
                        session_name = get_session_name(vtiger_access)

                        # retry to execute query

                        payload = {'operation': 'revise', 'sessionName': session_name, 'element': json.dumps(element)}
                        response, status = invoke_http_request(url, request_type, headers, payload=payload)

                        vtiger_access['vtiger_session'] = session_name
                        Variable.update(key='vtiger_access', value=vtiger_access, serialize_json=True)

        print("Response: {}".format(response))
        if is_success_request(status):
            return response
        else:
            print("something went wrong while invoking revise API for set value. status:", status, "response:",
                  response)
            return None


def invoke_set_value_task(conf, task_id, vtiger_access, record_id=None):
    """   this function will execute set value task.
            params:
            1.conf : conf object
            2.task_id: current task id
            3.vtiger_access : json object containing vtiger credentials

            Execution:
            1. get set_value_configs : conf dictionary containing rule, search_module_object, set_value_fields
            2. get configs and create query and replace data using json logic.
            3. check if conditions are satisfied using get query.
            4. call trigger_set_value_task function if conditions are satisfied.
            """

    print("Set value task invoked")
    if conf.get('set_value_configs', ''):

        if task_id in conf.get('set_value_configs', ''):
            set_value_configs = conf.get('set_value_configs').get(task_id, '')

        if set_value_configs:
            set_value_fields = set_value_configs.get('set_value_fields', '')
            search_module_object = set_value_configs.get('search_module_object', '')
            rule = set_value_configs.get('rule', '')

            session_name = vtiger_access.get('vtiger_session', '')
            print("Session name: {}".format(session_name))
            if not session_name:
                print("unable to get session id from vtiger access. Please try again")
                return None

            print("Search module object: {}".format(search_module_object))
            print("Set value fields: {}".format(set_value_fields))
            if search_module_object and search_module_object.get('condition_object', ''):
                condition = buildquery(search_module_object.get('condition_object'))

                print("Condition {}".format(condition))

                module = search_module_object.get('name')

                limit = str(search_module_object.get('fetch_record', ''))

                # prepare query using search_module_object

                order_by = ''
                if search_module_object.get('sort', ''):
                    order_by = search_module_object.get('sort').get('column') + " " + search_module_object.get(
                        'sort').get(
                        'type', "")

                if limit and order_by:
                    query = 'SELECT * FROM {module} WHERE {condition} order by {order_by} LIMIT {limit};'.format(
                        module=module,
                        condition=condition,
                        order_by=order_by,
                        limit=limit)
                elif limit:
                    query = 'SELECT * FROM {module} WHERE {condition} LIMIT {limit};'.format(
                        module=module,
                        condition=condition,
                        limit=limit)
                elif order_by:
                    query = 'SELECT * FROM {module} WHERE {condition} order by {order_by};'.format(
                        module=module,
                        condition=condition,
                        order_by=order_by,
                    )
                else:
                    query = 'SELECT * FROM {module} WHERE {condition};'.format(
                        module=module,
                        condition=condition,
                    )

                if rule:
                    query = json_logic_replace_data(rule, conf, string_data=query)

                url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query={query}'.format(
                    sessionName=session_name, query=query, vtiger_url=vtiger_access.get('vtiger_url'))

                url = url.replace("''", "' '")
                print("URL {}".format(url))

                headers = {'content-type': 'application/json'}
                request_type = 'GET'
                response, status = invoke_http_request(url, request_type, headers)
                if response:
                    if not response.get('success', ''):
                        if response.get('error', ''):
                            if response.get('error').get('code') in ["INVALID_USER_CREDENTIALS", "INVALID_SESSIONID"]:
                                session_name = get_session_name(vtiger_access)

                                # retry to execute query


                                url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query={query}'.format(
                                    sessionName=session_name, query=query, vtiger_url=vtiger_access.get('vtiger_url'))
                                url = url.replace("''", "' '")
                                response, status = invoke_http_request(url, request_type, headers)


                                vtiger_access['vtiger_session'] = session_name
                                Variable.update(key='vtiger_access', value=vtiger_access, serialize_json=True)

                print("Query Response: ")

                if response:
                    print(response)
                    if response.get('result') and set_value_fields:
                        set_value_response = trigger_set_value_task(set_value_fields, conf, rule, session_name,
                                                                    vtiger_access, record_id)
                        return set_value_response

            elif set_value_fields:

                set_value_response = trigger_set_value_task(set_value_fields, conf, rule, session_name, vtiger_access,
                                                            record_id)
                return set_value_response
        else:
            print("set_value_configs not found for task id:", task_id)
    else:
        print("set_value_configs not found in conf")


def invoke_web_service_task(conf, task_id, response_type="json"):
    """ Web service task:
        params:
        1. conf: conf object
        2. task_id: current task id
        3. response_type: response type of request

        Execution:
        1. get request object and rule from conf
        2. replace data using json_logic
        3. get request parameters and invoke http request"""
    if conf.get('web_service_configs', ''):

        if task_id in conf.get('web_service_configs', ''):
            web_service_configs = conf.get('web_service_configs').get(task_id, '')

        if web_service_configs:

            rule = web_service_configs.get('rule', '')
            request_object = web_service_configs.get('request_object', '')

            if request_object:

                if rule:
                    request_object = json_logic_replace_data(rule, conf, json_data=request_object)
                url = request_object.get("url")
                url = url.replace("''", "' '")
                url = url.replace("%%", "% %")
                headers = request_object.get("header")
                request_type = request_object.get("type")
                payload = request_object.get("payload")

                if payload:
                    if headers.get('content-type', '') == 'application/json':
                        response, status = invoke_http_request(url, request_type, headers, json_data=payload,
                                                               response_type=response_type)
                    else:
                        response, status = invoke_http_request(url, request_type, headers, payload=payload,
                                                               response_type=response_type)
                else:
                    response, status = invoke_http_request(url, request_type, headers, response_type=response_type)
                if is_success_request(status):
                    return response
        else:
            print("web_service_configs not found for task id:", task_id)
    else:
        print("web_service_configs not found in conf")


def invoke_provider_manager_task(conf, task_id):
    """ Provider Manager task:
        params:
        1. conf: conf object
        2. task_id: current task id

        Execution:
        1. get request object and rule from conf
        2. replace data using json_logic
        3. get request parameters and invoke http request"""
    if conf.get('provider_manager_config', ''):

        if task_id in conf.get('provider_manager_config', ''):
            provider_manager_config = conf.get('provider_manager_config').get(task_id, '')

        if provider_manager_config:

            rule = provider_manager_config.get('rule', '')
            request_object = provider_manager_config.get('request_object', '')

            if request_object:

                if rule:
                    request_object = json_logic_replace_data(rule, conf, json_data=request_object)
                url = request_object.get("url")
                headers = request_object.get("header")
                request_type = request_object.get("type")
                payload = request_object.get("payload")

                if payload:
                    if headers.get('content-type', '') == 'application/json':
                        response, status = invoke_http_request(url, request_type, headers, json_data=payload)
                    else:
                        response, status = invoke_http_request(url, request_type, headers, payload=payload)
                else:
                    response, status = invoke_http_request(url, request_type, headers)
                if is_success_request(status):
                    return response
        else:
            print("provider_manager_config not found for task id:", task_id)
    else:
        print("provider_manager_config not found in conf")


def invoke_conditional_task(conf, task_id, true_task, false_task):
    """ this will execute conditional task.
        params:
        1. conf: conf object
        2. task_id: current task id
        3. true_task: task to be triggered if condition is true
        4. false_task: task to be triggered if condition is false
        """
    if conf.get('conditions', ''):

        if task_id in conf.get('conditions', ''):
            condition = conf.get('conditions').get(task_id, '')

        if condition:

            is_valid = jsonLogic(condition, conf, ops)

            if is_valid:
                return true_task
            else:
                return false_task
        else:
            print("conditions not found for task id:", task_id)
    else:
        print("conditions not found in conf")


def invoke_start_task(conf, condition=None, true_task=None, false_task=None, default_task=None):
    """ This task is invoked as starting point of any workflow
        - this task will run start task if triggered directly
        - will trigger next task if triggered from delay task (delay mysql tbl)
        params:
        1. conf: conf object
        2. condition: condition object
        3. true_task: task to be triggered if condition is true
        4. false_task: task to be triggered if condition is false
        5. default_task: default task to be triggered if there is no condition or next task found
        """

    if conf.get('next_task', ''):
        return conf.get('next_task')
    elif condition and true_task and false_task:

        is_valid = jsonLogic(condition, conf, ops)

        if is_valid:
            return true_task
        else:
            return false_task

    elif default_task:
        return default_task


def add_delay_task(conf, task_id, vtiger_access):
    print("task_id", task_id)
    """ This task is useful to insert delayed task data in MySQL database.
            params:
            1. conf: conf object
            2. task_id: current task id
            3. vtiger_access : json object containing vtiger credentials
            """
    delay_task_configs = conf['delay_task_configs']
    eventtype = conf.get('eventtype', '')
    if eventtype:
        if eventtype == 'import' or eventtype == 'manual':
            # send list of payload if event type is import or manual
            conf['data'] = [conf['data']]
    if task_id in delay_task_configs:
        delay_task_configs = delay_task_configs[task_id]
        print("delay_task_configs : ", delay_task_configs)
        payload = {
            "conf": conf,
            "delay_task_configs": delay_task_configs
        }

    endpoint = '{service_url}/api/v1/add-delayed-data'.format(service_url=vtiger_access.get('service_url'))
    headers = {'content_type': 'application/json', 'Authorization': vtiger_access.get('api_access_key')}

    response, status = invoke_http_request(endpoint, 'POST', headers, json_data=payload, timeout=61)
    print("response from add delayed task", response, "status", status)


def get_crm_records(vtiger_access, conf):
    """ This function will get record id and will fetch record data for that id from Vtiger.
       NOTE: set return value in context["dag_run"].conf['data'] while calling this function.
       params:
       vtiger_access: vtiger access dictionary
       conf: conf object"""

    if 'data' in conf and 'id' in conf.get('data'):

        # call vtiger api to get data
        record_id = conf['data']['id']
        source_module = conf['data']['module']
        id = "{module}x{record_id}".format(module=module_id_dict[source_module], record_id=record_id)
        session_name = vtiger_access.get('vtiger_session', '')
        print("Session name: {}".format(session_name))
        if not session_name:
            print("unable to get session id from vtiger access. Please try again")
            return None

        url = "{vtiger_url}/webservice.php?operation=retrieve&id={record_id}&sessionName={sessionName}".format(
            record_id=id, sessionName=session_name, vtiger_url=vtiger_access.get('vtiger_url'))
        response, status = invoke_http_request(url, 'GET', {'content_type': 'application/json'})

        # request session if existing one is expired

        if response:
            if not response.get('success', ''):
                if response.get('error', ''):
                    if response.get('error').get('code') in ["INVALID_USER_CREDENTIALS", "INVALID_SESSIONID"]:
                        session_name = get_session_name(vtiger_access)

                        # retry to execute query

                        url = "{vtiger_url}/webservice.php?operation=retrieve&id={record_id}&sessionName={sessionName}".format(
                            record_id=id, sessionName=session_name, vtiger_url=vtiger_access.get('vtiger_url'))
                        response, status = invoke_http_request(url, 'GET', {'content_type': 'application/json'})

                        vtiger_access['vtiger_session'] = session_name
                        Variable.update(key='vtiger_access', value=vtiger_access, serialize_json=True)

        if 'success' in response and response['success'] and 'result' in response:
            return response['result']
        else:
            print("unable to get record details from Vtiger. Response: ", response.text)

    else:
        print("unable to get id & data from conf object")


def get_record_details_from_crm(vtiger_access, data):
    """ This function will prepare list of record ids and will fetch record data for those ids from Vtiger.
       NOTE: set return value in context["dag_run"].conf['data'] while calling this function.
       params:
       vtiger_access: vtiger access dictionary
       data: data of conf object"""

    if data:

        # get source module
        source_module = data[0].get('module')
        if not source_module:
            print("unable to get source module from data")
            return []

        module_id = module_id_dict[source_module]

        # prepare list of ids
        user_id_list = []

        for element in data:
            id = element.get('id', '')
            if id:
                # prepare query id using source module
                record_id = id if "x" in id else "{module}x{record_id}".format(module=module_id, record_id=id)

                user_id_list.append(record_id)
        print("user id list received: ", user_id_list)

        # call vtiger api to get data

        session_name = vtiger_access.get('vtiger_session', '')
        print("Session name: {}".format(session_name))
        if not session_name:
            print("unable to get session id from vtiger access. Please try again")
            return None

        url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query=SELECT * FROM {source_module} WHERE id in ('.format(
            vtiger_url=vtiger_access.get('vtiger_url'), sessionName=session_name, source_module=source_module) + ','.join((str(n) for n in user_id_list)) + ');'

        response, status = invoke_http_request(url, 'GET', {'content_type': 'application/json'})

        # request session if existing one is expired

        if response:
            if not response.get('success', ''):
                if response.get('error', ''):
                    if response.get('error').get('code') in ["INVALID_USER_CREDENTIALS", "INVALID_SESSIONID"]:
                        session_name = get_session_name(vtiger_access)

                        # retry to execute query

                        url = '{vtiger_url}/webservice.php?operation=query&sessionName={sessionName}&query=SELECT * FROM {source_module} WHERE id in ('.format(
                            vtiger_url=vtiger_access.get('vtiger_url'), sessionName=session_name,
                            source_module=source_module) + ','.join((str(n) for n in user_id_list)) + ');'

                        print("url", url)
                        response, status = invoke_http_request(url, 'GET', {'content_type': 'application/json'})

                        print("response, status", response, status)
                        vtiger_access['vtiger_session'] = session_name
                        Variable.update(key='vtiger_access', value=vtiger_access, serialize_json=True)

        if 'success' in response and response['success'] and 'result' in response:
            # return list of user records
            return response['result']
        else:
            print("unable to get record details from Vtiger. Response: ", response.text)

    else:
        print("unable to get id & data from conf object")
