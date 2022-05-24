import click
import os
from sumologic import SumoLogic
import json
import time
from collections import OrderedDict
from sumoappclient.common.logger import get_logger
from sumoapputils.appdev.apptasks import SUMO_DEPLOYMENTS,AppEntry
from sumoapputils.appdev.runapptests import validate_sumo_secrets
from sumoapputils.common.utils import get_file_data
from sumoapputils.appdev.appdeployapi import get_endpoint
import yaml

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log",
                    LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

class AppDeploy(object):
    def __init__(self, sumologic_client):
        self._client = sumologic_client

    def share_content_with_org(self, content_id, org_id, isAdminMode):
        """ Share a given content item """
        payload = {"contentPermissionAssignments": [
            {
                "permissionName": "View",
                "sourceType": "org",
                "sourceId": org_id,
                "contentId": content_id
            }],
            "notifyRecipients": False,
            "notificationMessage": ""
        }
        headers = {'isAdminMode': 'true'} if isAdminMode else {}
        response = self._client.put(f"/content/{content_id}/permissions/add", params=payload,headers=headers, version="v2")
        if response.status_code==200:
            return response
        else:
            raise Exception(f"Unable to share {content_id} in org: {org_id}")

    def get(self, method, params=None, headers=None, version=None):
        """ Overwrite to use headers """
        version = version or self._client.DEFAULT_VERSION
        endpoint = self._client.get_versioned_endpoint(version)
        r = self._client.session.get(
            endpoint + method, params=params, headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def delete(self, method, params=None, headers=None, version=None):
        version = version or self._client.DEFAULT_VERSION
        endpoint = self._client.get_versioned_endpoint(version)
        r = self._client.session.delete(endpoint + method, params=params, headers=headers)
        if 400 <= r.status_code < 600:
            r.reason = r.text
        r.raise_for_status()
        return r

    def install_app(self, app_uuid, app_name, app_description, source_values, target_id, isAdminMode):
        """ Install an app under the target_id (in hexadecimal format) folder, and return "Success" if successful, None otherwise """
        payload = {"name": app_name, "description": app_description, "destinationFolderId": target_id,
                   "dataSourceValues": source_values}
        headers = {'isAdminMode': 'true'} if isAdminMode else {}
        response = self._client.post(f"/apps/{app_uuid}/install", params=payload, headers=headers)
        if (response.status_code == 200):
            job_id = json.loads(response.text)["id"]
            # now wait and retrieve install job status
            logger.debug(f"Got Installation job {job_id}, now checking for status")
            while True:
                status_response = self._client.get(f"/apps/install/{job_id}/status", version="v1")
                if (json.loads(status_response.text)["status"] == "InProgress"):
                    logger.debug(f'{app_name} App install job in progress')
                    time.sleep(1)
                else:
                    if (json.loads(status_response.text)["status"] == "Failed"):
                        raise Exception(f"{app_name} App Install Failed: {status_response.text}")
                    else:
                        click.echo(f'{app_name} App Install Successfull')
                        return json.loads(status_response.text)
        else:
            raise Exception(f"{app_name} App Install StartJob Failed: {response.text}")

    def find_app_in_admin_recommended(self, app_name, isAdminMode):
        """ Sync call to return the information (folder id, permissions) about an app shared under Admin Recommended folder,
                or None if app is not there """
        app_list = self.get_admin_recommended(isAdminMode)["children"]
        for app in app_list:
            if (app["name"] == app_name):
                return app
        return None

    def find_app_folder_by_name(self, folder_name, target_folder_id, isAdminMode):
        if isAdminMode:
            self._client.session.headers.update({"isAdminMode":"true"})
        response = self._client.get_folder(target_folder_id)
        if response.ok:
            app_list = response.json()["children"]
        else:
            raise Exception(f"Unable to get target_folder_id: {target_folder_id}")

        logger.debug(f"Found {len(app_list)} in {target_folder_id}")
        folder_id = [item["id"] for item in app_list if item["name"] == folder_name]
        if not folder_id:
            return None
        return folder_id[0]

    def delete_folder_if_exists(self, folder_name, target_folder_id, isAdminMode):
        '''
            deletes folder by target_folder_id in hexadecimal format
        '''
        app_folder_id = self.find_app_folder_by_name(folder_name, target_folder_id, isAdminMode)
        if app_folder_id:
            if isAdminMode:
                headers = {"isAdminMode": "true"}
                response = self.delete('/content/folders/%s/delete' % app_folder_id, version='v2', headers=headers)
            else:
                response = self._client.delete('/content/folders/%s/delete' % app_folder_id, version='v2')

            if response.status_code == 200:
                job_id = json.loads(response.text)["id"]
                # now wait and retrieve install job status
                logger.debug(f"Got deletion job {job_id}, now checking for status")
                while True:
                    status_response = self._client.get(f"/content/folders/{app_folder_id}/delete/{job_id}/status", version="v2")
                    if (json.loads(status_response.text)["status"] == "InProgress"):
                        logger.debug(f'Folder Deletion job in progress')
                        time.sleep(5)
                    else:
                        if (json.loads(status_response.text)["status"] == "Failed"):
                            raise Exception(f"{folder_name} Folder deletion Failed: {status_response.text}")
                        else:
                            click.echo(f"{folder_name} Folder deleted successfully")
                            return json.loads(status_response.text)

            else:
                raise Exception(f"{folder_name} Folder deletion start job failed response: {response}")
        else:
            click.echo(f"{folder_name} Folder doesn't exists in target_folder_id: {target_folder_id}")

    def get_admin_recommended_id(self, isAdminMode):
        """ Sync call to  get the Admin Recommended folder Id """
        return self.get_admin_recommended(isAdminMode)["id"]

    def get_admin_recommended(self, isAdminMode):
        """ Sync call to  get the Admin Recommended folder content """
        headers = {"isAdminMode": "true"} if isAdminMode else None
        job_response = self.get(
            "/content/folders/adminRecommended", headers=headers, version="v2")
        job_id = json.loads(job_response.text)["id"]

        logger.debug(f"Got Admin Recommended job {job_id}, now checking for status")
        while True:
            status_response = self.get(f"/content/folders/adminRecommended/{job_id}/status", headers=headers, version="v2")
            if (json.loads(status_response.text)["status"] == "InProgress"):
                logger.debug(f'Admin Recommended job in progress')
                time.sleep(1)
            else:
                if (json.loads(status_response.text)["status"] == "Failed"):
                    raise Exception("Not able to fetch Admin Recommended Folder")
                else:
                    status_response = self.get(f"/content/folders/adminRecommended/{job_id}/result", headers=headers, version="v2")
                    return json.loads(status_response.text)

    def share_app_by_id(self, app_folder_id, org_id, isAdminMode):
        """ This shares an app identified by its Id under the Admin Recommended folder """
        response = self.share_content_with_org(app_folder_id, org_id, isAdminMode)
        if response.status_code==200:
            click.echo(f'Shared {app_folder_id} in org {org_id}')
        else:
            raise Exception(f"Folder Sharing Failed for folder id: {app_folder_id} in {org_id} response: {response.text}")


def get_source_category(source_type, label, parameter_id):
    # Todo create a file with app and loggen source category mapping so that user input is not required

    value = click.prompt(f"Enter {source_type} source category(same as in loggen) for param: {parameter_id} with label: {label} > ")
    value = value.strip()
    if value and value.startswith("Labs"):
        return {parameter_id: f"_sourceCategory={value}"}
    else:
        click.echo("Incorrect source category value!")
        return validate_choice(ctx, param, value)


@click.group()
def appinstallcmd():
    pass

@appinstallcmd.command(help="For installing app (in Personal folder by default) and sharing folder ")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.Choice(SUMO_DEPLOYMENTS), help='Set deployment')
@click.option('-m', '--manifestfile', required=True, type=click.Path(exists=True), help='Set filepath for manifest json')
@click.option("-o", "--org_id",  required=True, help="org_id in hexadecimal(required)")
@click.option("-k", "--access_id",  help="access_id for deployment(required)", callback=validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment(required)", callback=validate_sumo_secrets)
@click.option('-i', '--folderid', required=False, type=click.STRING, help='Optional target folderId, if not install directly under the Admin folder')
@click.option('--admin', '-a', "is_admin_folder", default=False, is_flag=True, help="To install app in admin folder. By default it will install in personal folder")
def install_and_share(deployment, manifestfile, org_id, access_id, access_key, folderid,is_admin_folder,source_mapping = None):
    """
        installs & shares the app in admin recommended folder by default(or else the personal folder id)
    """
    manifestJson = get_file_data(manifestfile)
    manifestJson = json.loads(manifestJson, object_pairs_hook=OrderedDict)
    app_name = manifestJson["name"]
    app_uuid = manifestJson["uuid"]
    app_desc = "This App is installed via automation.DO NOT DELETE since its shared."
    if (source_mapping is None):
        source_filters = {}
    else:
        source_filters = source_mapping
    click.echo(f'App to be installed: {app_name}, UUID: {app_uuid}')

    if (source_mapping is None):
        # ask source category for parameters
        for param_json in manifestJson['parameters']:
            source_filters.update(get_source_category(param_json['dataSourceType'], param_json['label'], param_json['parameterId']))
    endpoint = get_endpoint(deployment)
    sumologic_cli = SumoLogic(access_id, access_key, endpoint=endpoint)
    appInstallAPI = AppDeploy(sumologic_cli)

    if is_admin_folder:
        if (folderid is not None):
            logger.info(f"Installing under {folderid}")
            target_folder_id = str(folderid)
        else:
            target_folder_id = appInstallAPI.get_admin_recommended_id(isAdminMode=True)
            logger.info(f"Installing under the Admin folder ({target_folder_id})")
    else:
        response = sumologic_cli.get_personal_folder()
        target_folder_id = response.json()['id']

    # check whether app is there or not if yes then removes it
    appInstallAPI.delete_folder_if_exists(app_name, target_folder_id, is_admin_folder)

    # install app
    response = appInstallAPI.install_app(
        app_uuid, app_name, app_desc, source_filters, target_folder_id, is_admin_folder)
    app_folder_id = response["statusMessage"].split(":")[-1]

    # share it with org, if installed directly under Admin folder
    if (is_admin_folder and folderid is not None):
        appInstallAPI.share_app_by_id(app_folder_id, org_id, is_admin_folder)





@appinstallcmd.command(help="For installing apps to different Demo environments")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.STRING, help='Set target demo org:  sedemo|sumolabs|partner|training')
@click.option('-p', '--path', required=True, type=click.Path(exists=True), help='Absolute path to parent directory of app files')
@click.option('-a', '--applist', required=True, type=click.Path(exists=True), help='Path to app list yaml file')
@click.option('-t', '--targetconfig', required=True, type=click.Path(exists=True), help='Set filepath for destination config yaml')
@click.option("-k", "--access_id",  help="access_id for deployment(required)", callback=validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment(required)", callback=validate_sumo_secrets)
@click.pass_context
def deploy_demo_apps(ctx,deployment,path,applist,targetconfig, access_id, access_key):
    with open(targetconfig,'r') as f1:
        target_config = yaml.load(f1,Loader=yaml.FullLoader)['demo_orgs']
    if (deployment not in target_config):
        print(f"Target Demo Org {deployment} not found in target config file {targetconfig}")
        exit(0)
    else:
        real_deployment = f"{target_config[deployment]['deployment']}"
        org_id = f"{target_config[deployment]['org_id']}"
        folderid = f"{target_config[deployment]['targetFolderId']}" if f"{target_config[deployment]['isAdminSubfolder']}" == "true" else None
    print(f"Deploying to {deployment} using app list from {applist}")
    with open(applist,'r') as f:
        app_list = yaml.load(f,Loader=yaml.FullLoader)['apps']
    for app in app_list:
        print(f"Reading {app[AppEntry.NAME_FIELD]}. Will installing using manifest: {path}/{app[AppEntry.MANIFEST_PATH_FIELD]}\n")
        source_mapping = {} 
        for input in app[AppEntry.DEMO_INPUT_MAPPING_FIELD]:
            source_mapping.update({input[AppEntry.INPUT_NAME_FIELD]: input[AppEntry.INPUT_CATEGORY_FIELD]})
        print(f"Using deployment={real_deployment}, manifestfile= {path}/{app[AppEntry.MANIFEST_PATH_FIELD]}, org_id={org_id}, access_id={access_id}, access_key={access_key}, folderid={folderid},is_admin_folder =True,source_mapping = {source_mapping}")
        ctx.invoke(install_and_share,deployment=real_deployment,manifestfile= f"{path}/{app[AppEntry.MANIFEST_PATH_FIELD]}", org_id=org_id, access_id=access_id, access_key=access_key, 
                        folderid=folderid,is_admin_folder =True,source_mapping = source_mapping)





