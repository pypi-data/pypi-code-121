import json
import os
import time
from json import JSONDecodeError

from sumoappclient.common.logger import get_logger
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.sumoclient.httputils import ClientMixin
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from sumologic import SumoLogic

from sumoapputils.common.utils import get_app_config_key

cli_logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log",
                            LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

def get_endpoint(deployment):
    if deployment == "us1":
        return "https://api.sumologic.com/api"
    elif deployment in ["ca", "au", "de", "eu", "jp", "us2", "fed", "in"]:
        return "https://api.%s.sumologic.com/api" % deployment
    else:
        return 'https://%s-api.sumologic.net/api' % deployment


def push_app_api(deployment, sourcefile, manifestfile, access_id, access_key):
    endpoint = get_endpoint(deployment)
    api_url = "%s/v1/content/app" % endpoint
    with open(sourcefile, 'rb') as sf:
        with open(manifestfile, 'rb') as mf:
            status, response = ClientMixin.make_request(url=api_url, method='post', is_file=True, TIMEOUT=120,
                                                        auth=HTTPBasicAuth(access_id, access_key),
                                                        files={'appDef': sf, 'manifest': mf})
            return status, response


def delete_app_api(deployment, app_uuid, access_id, access_key):
    endpoint = get_endpoint(deployment)
    api_url = "%s/v1/content/app/%s" % (endpoint, app_uuid)

    status, response = ClientMixin.make_request(url=api_url, method='delete', is_file=True, TIMEOUT=120,
                                                        auth=HTTPBasicAuth(access_id, access_key))
    return status, response

def push_app_api_v2(deployment, sourcefile, manifestfile, access_id, access_key):
    endpoint = get_endpoint(deployment)
    import_app_url = "%s/v1/apps/import" % endpoint
    with open(sourcefile, 'rb') as sf:
        with open(manifestfile, 'rb') as mf:
            status, response = ClientMixin.make_request(url=import_app_url, method='post', TIMEOUT=120,
                                                        auth=HTTPBasicAuth(access_id, access_key),
                                                        files={'appDefinition': sf, 'appManifest': mf})
            if status:
                job_id = response["id"]
                job_status_url = "%s/v1/apps/import/%s/status" % (endpoint, job_id)
                waiting = True
                while waiting:
                    status, response = ClientMixin.make_request(url=job_status_url, method='get', TIMEOUT=120,
                                                                auth=HTTPBasicAuth(access_id, access_key),
                                                                )
                    if response['status'] == "InProgress":
                        waiting = True
                        time.sleep(5)
                    else:
                        break

                if response['status'] == "Success":
                    return True, response
                else:
                    return False, response

            else:
                return status, response


def _wait_for_content_import(sumologic_cli, folder_id, job_id):
    print("waiting for content import folder_id %s job_id %s" % (folder_id, job_id))
    waiting = True
    response = None
    while waiting:
        response = sumologic_cli.check_import_status(folder_id, job_id)
        waiting = response.json()['status'] == "InProgress"
        time.sleep(5)

    return response.json()


def get_importable_content(app_file_path):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=cli_logger)
    app_config = store.get("app_config", {})
    app_config_key = get_app_config_key(app_file_path)
    current_app_config = app_config.get(app_config_key, {})
    param_mapping = current_app_config.get("param_mapping", {})
    appcontent = ""
    with open(app_file_path, "r") as fp:
        appcontent = fp.read()

    if not param_mapping:
        cli_logger.warn("No mapping found it won't replace source params")

    for param, sc_expr_list in param_mapping.items():
        for sc_expr in sc_expr_list:
            appcontent = appcontent.replace("$$%s" % param, sc_expr)
            cli_logger.debug("replacing %s with %s" % (param, sc_expr))

    return json.loads(appcontent)


def import_folder(deployment, access_id, access_key, sourcefile):
    endpoint = get_endpoint(deployment)
    sumologic_cli = SumoLogic(access_id, access_key, endpoint=endpoint)
    response = sumologic_cli.get_personal_folder()
    personal_folder_id = response.json()['id']
    appcontent = get_importable_content(sourcefile)
    response = sumologic_cli.import_content(personal_folder_id, appcontent, is_overwrite="true")

    if response.ok:
        job_id = response.json()['id']
        resp = _wait_for_content_import(sumologic_cli, personal_folder_id, job_id)
        if resp["status"] == "Success":
            cli_logger.info("Successfully imported content in file: %s in Personal Folder" % sourcefile)

def get_hexadecimal_id(val):
    if isinstance(val, int):
        return hex(val).replace('0x','').upper()
    return val


def _wait_for_content_export(sumologic_cli, folder_id, job_id):
    print("waiting for content export folder_id %s job_id %s" % (folder_id, job_id))
    waiting = True
    response = None
    while waiting:
        response = sumologic_cli.check_export_status(folder_id, job_id)
        waiting = response.json()['status'] == "InProgress"
        time.sleep(5)

    return response.json()


def export_folder(deployment, access_id, access_key, sourcefile, folder_id):
    folder_id = get_hexadecimal_id(folder_id)
    endpoint = get_endpoint(deployment)
    sumologic_cli = SumoLogic(access_id, access_key, endpoint=endpoint)
    response = sumologic_cli.export_content(folder_id)
    if response.ok:
        job_id = response.json()['id']
        resp = _wait_for_content_export(sumologic_cli, folder_id, job_id)
        if resp["status"] == "Success":
            response = sumologic_cli.get_export_content_result(folder_id, job_id)
            appcontent = response.json()
            with open(sourcefile, "w") as fp:
                json.dump(appcontent, fp, indent=4)

            cli_logger.info("Successfully exported content in file: %s" % sourcefile)


def list_apps(deployment, access_id, access_key):
    endpoint = get_endpoint(deployment)
    sumologic_cli = SumoLogic(access_id, access_key, endpoint=endpoint)
    resp = ""
    try:
        resp = sumologic_cli.get("/apps")
        if resp.status_code == 200:
            data = resp.json() if len(resp.content) > 0 else {}
            if "apps" in data:
                return True, data["apps"]
            else:
                err_msg = "Unable to list apps: %s" % resp
        else:
            err_msg = f'''Request Failed: {resp.content}  status_code: {resp.status_code} reason: {resp.reason}'''

    except JSONDecodeError as err:
        err_msg = f'''Error in Decoding response {err}'''

    except RequestException as e:
        err_msg = "Unable to list apps: %s error: %s" % (resp, str(e))

    cli_logger.error(err_msg)
    return False, {"error": err_msg}



