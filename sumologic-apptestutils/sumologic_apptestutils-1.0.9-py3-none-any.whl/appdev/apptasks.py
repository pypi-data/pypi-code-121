from logging import exception
from shlex import quote
import click
from sumoappclient.common.logger import get_logger
from sumoappclient.provider.factory import ProviderFactory
import os
import re
import json
import requests
from collections import OrderedDict
from sumoapputils.appdev.runapptests import validate_sumo_secrets
from sumoapputils.common.utils import ENVIRONMENT, get_app_config_key, get_content_dirpath, ALL_APPS_FILENAME, get_file_data
from sumoapputils.common.testutils import is_new_appjson_format, get_test_class
from sumoapputils.appdev.appdeployapi import push_app_api, delete_app_api, push_app_api_v2, export_folder, \
    import_folder, get_endpoint, get_importable_content
from sumologic import SumoLogic
from sumoapputils.common.utils import run_cmd, EXCLUDED_APP_PREFIXES
from sumoapputils.appdev.generate_test_config import filter_app_files
from sumoapputils.appdev.updatemanifest import save_manifest

from sumoapputils.appdev.utils import default_extract_keys, show_vimdiff, generate_mini_appfile
from bs4 import BeautifulSoup

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

SUMO_DEPLOYMENTS = ['nite', 'stag', 'long','us1','us2']


@click.group()
def appcmd():
    pass

@appcmd.command(help="For saving sumo logic deployment configuration")
@click.option('-d', "--deployment", required=True, default=lambda : ENVIRONMENT.SUMO_DEPLOYMENT, prompt=True, type=click.Choice(SUMO_DEPLOYMENTS), help="Sets deployment_name")
@click.option('-k', '--access_id', required=True, prompt=True, help='Sets access_id')
@click.option('-c', '--access_key', required=True, prompt=True, help='Sets access key')
def save_sumo_config(deployment, access_id, access_key):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    sumoconfig[deployment] = {"access_id": access_id, "access_key": access_key}
    store.set("sumoconfig", sumoconfig)
    logger.info("Deployment config updated for %s" % deployment)


@appcmd.command(help="For deleting sumo logic deployment configuration")
@click.option('-d', "--deployment", required=True, default=lambda : ENVIRONMENT.SUMO_DEPLOYMENT, prompt=True, help="Sets deployment_name")
def delete_sumo_config(deployment):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    if deployment in sumoconfig:
        del sumoconfig[deployment]
        store.set("sumoconfig", sumoconfig)
        logger.info("Deployment config updated for %s" % deployment)
    else:
        logger.info("Deployment config doesnot exists for %s" % deployment)


@appcmd.command(help="For showing sumo logic deployment configuration")
def show_sumo_config():
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    for d, v in sumoconfig.items():
        click.echo("Deployment: %s AccessId: %s AccessKey: %s" % (d, v['access_id'], v['access_key']))

@appcmd.command(help="For showing app configuration")
@click.option('-s', '--sourcefile', type=click.Path(exists=True), help='Set filepath for appjson')
@click.option('--printall', '-a', is_flag=True, help="Print all app config")
def show_app_config(sourcefile, printall):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    app_config = store.get("app_config", {})
    if not sourcefile and printall:
        for k, v in app_config.items():
            print(k, v)
    elif sourcefile:
        app_config_key = get_app_config_key(sourcefile)
        current_app_config = app_config.get(app_config_key, {})
        print(current_app_config)
    else:
        logger.error("Please provide sourcefile parameter.")

@appcmd.command(help="For resetting app configuration")
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
def reset_app_config(sourcefile):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    app_config = store.get("app_config", {})
    app_config_key = get_app_config_key(sourcefile)
    if app_config:
        app_config[app_config_key] =  {}
        store.set("app_config", app_config)
        logger.info("successfully reset app config for %s" % app_config_key)
    else:
        logger.info("app config doesnot exists for %s" % app_config_key)


@appcmd.command(help="For deploying app to appcatalog")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.Choice(SUMO_DEPLOYMENTS), help='Set deployment')
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option('-m', '--manifestfile', required=True, type=click.Path(exists=True), help='Set filepath for manifest json')
@click.option("-k", "--access_id",  help="access_id for deployment(required)", callback = validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment(required)", callback = validate_sumo_secrets)
def deploy_app(deployment, sourcefile, manifestfile, access_id, access_key):
    # Todo [-a <get|push|delete>] [-p appuuid]

    if is_new_appjson_format(appfile=sourcefile):
        status, response = push_app_api_v2(deployment, sourcefile, manifestfile, access_id, access_key)
        if status:
            logger.info("App Deployment(via new API endpoint) on deployment: %s API Response: %s" % (deployment, response))
    else:
        status, response = push_app_api(deployment, sourcefile, manifestfile, access_id, access_key)
        if status:
            logger.info("App Deployment(via old API endpoint) on deployment: %s API Response: %s" % (deployment, response))
    if not status:
        logger.error("Failed to deploy app API Response: %s" % response)



@appcmd.command(help="For removing app from appcatalog")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.Choice(SUMO_DEPLOYMENTS), help='Set deployment')
@click.option('-p', '--app_uuid', required=True, help='Set filepath for appjson')
@click.option("-k", "--access_id",  help="access_id for deployment", callback = validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment", callback = validate_sumo_secrets)
def undeploy_app(deployment, app_uuid, access_id, access_key):

    status, response = delete_app_api(deployment, app_uuid, access_id, access_key)
    if status:
        logger.info("App Deployment API Response: %s" % response)
    else:
        logger.error("App Deployment Failed API Response: %s" % response)
    return status, response


def get_folder_id(deployment, access_id, access_key, folder_name):


    endpoint = get_endpoint(deployment)
    sumologic_cli = SumoLogic(access_id, access_key, endpoint=endpoint)
    response = sumologic_cli.get_personal_folder()
    personal_folder_id = response.json()['id']
    response = sumologic_cli.get_folder(personal_folder_id)

    folder_id = [item["id"] for item in response.json()["children"] if item["name"] == folder_name]
    if not folder_id:
        raise click.BadOptionUsage(option_name="folder_name", message="%s doesn't exists in Personal Folder" % folder_name)

    return folder_id[0]


@appcmd.command(help="For exporting app to your sumologic org")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.Choice(SUMO_DEPLOYMENTS),
              help='Set deployment')
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option("-k", "--access_id", help="access_id for deployment", callback=validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment", callback=validate_sumo_secrets)
@click.option("-f", "--folder_name", required=True, type=str, help="app folder name")
def export_app(deployment, sourcefile, folder_name, access_id, access_key):
    folder_id = get_folder_id(deployment, access_id, access_key, folder_name)
    export_folder(deployment, access_id, access_key, sourcefile, folder_id)


@appcmd.command(help="For importing app to your sumologic org")
@click.option('-d', '--deployment', is_flag=False, required=True, type=click.Choice(SUMO_DEPLOYMENTS),
              help='Set deployment')
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option("-k", "--access_id", help="access_id for deployment", callback=validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment", callback=validate_sumo_secrets)
def import_app(deployment, sourcefile, access_id, access_key):
    import_folder(deployment, access_id, access_key, sourcefile)

@appcmd.command(help="For generating importable content by replacing parameters with source categories.")
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
def generate_importable_app(sourcefile):

    appcontent = get_importable_content(sourcefile)
    replaced_file = sourcefile.replace(".json", ".replaced_sc.json")
    prettyJsonOutput = json.dumps(appcontent, sort_keys=True, indent=4, separators=(',', ': '))

    with open(replaced_file, 'w') as f:
        f.write(prettyJsonOutput)
    logger.info("Successfully generated importable content in file: %s" % replaced_file)


def validate_commit_expression(ctx, param, value):
    if value:
        sourcefile = ctx.params.get('sourcefile')
        gitpath = value if ":" in value else "%s:./%s" % (value, sourcefile)
        return_code, cmd = run_cmd("git show %s" % quote(gitpath))

        if return_code:
            raise click.BadOptionUsage(option_name=param.name, message="Error in running cmd %s. Make sure you have a git client and you are running this command from inside a git repo where the path to sourcefile exists." % cmd, ctx=ctx)

    return value


@appcmd.command(help="For generating a minimalistic diff of changes in app content")
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
@click.option('-d', '--diff_file', required=False, type=click.Path(exists=True), help='Set filepath for old generated file and shows its diff with current generated file')
@click.option('-c', '--commit_id', required=False, type=str, help='Set old commit_id to show diff with current commit head', callback=validate_commit_expression)
@click.option('-k', '--extract_keys', required=False, type=str, help="Set comma separated keys to extract from json use following format *.<keyname> or key1.key2.", default=",".join(default_extract_keys))
@click.option('-o', "--output_file", required=False, type=str, help="Set output file name")
def review_app_query(sourcefile, diff_file, commit_id, extract_keys, output_file):
    extract_keys = extract_keys.split(",")
    current_mini_appjson = generate_mini_appfile(sourcefile, extract_keys)
    current_mini_appjsonstr = json.dumps(current_mini_appjson, indent=4, separators=(',', ': '), sort_keys=False)

    if output_file:
        mini_appjson_path = os.path.join(os.path.dirname(sourcefile), output_file + ".min.json")
    else:
        mini_appjson_path = sourcefile.replace(".json", ".min.json")
    with open(mini_appjson_path, 'w') as f:
        f.write(current_mini_appjsonstr)

    if diff_file:
        show_vimdiff(diff_file, mini_appjson_path)

    elif commit_id:
        gitpath = commit_id if ":" in commit_id else "%s:./%s" % (commit_id, sourcefile)
        status_code, output = run_cmd("git show %s" % quote(gitpath))
        old_appjson_path = sourcefile.replace(".json", ".%s.json" % commit_id[:7])
        with open(old_appjson_path, 'w') as f:
            f.write(output.decode("utf-8"))

        old_mini_appjson = generate_mini_appfile(old_appjson_path, extract_keys)
        old_mini_appjsonstr = json.dumps(old_mini_appjson, indent=4, separators=(',', ': '), sort_keys=False)

        if output_file:
            old_mini_appjson_path = os.path.join(os.path.dirname(old_appjson_path), output_file + ".%s.min.json" % commit_id[:7])
        else:
            old_mini_appjson_path = old_appjson_path.replace(".json", ".min.json")


        with open(old_mini_appjson_path, 'w') as f:
            f.write(old_mini_appjsonstr)

        show_vimdiff(old_mini_appjson_path, mini_appjson_path)

# def set_folder_id():
#     pass


@appcmd.command(help="For generating scr file for SCR")
@click.option('-b', '--num_commits_back', default=1, type=int, help='Sets num of commits to go back to generate diff')
@click.option('-p', '--all_app_config_path', default=os.path.join(get_content_dirpath(), "bin", ALL_APPS_FILENAME), help='Set the path to full_app_list.txt')
def generate_scr_file(num_commits_back, all_app_config_path):
    return_code, err = run_cmd("git diff-tree --no-commit-id --name-only -r HEAD HEAD%s > changed-files" % ("^"*num_commits_back))
    if return_code == 0:
        with open("changed-files", "r") as fp:
            changed_app_files = fp.readlines()
            filtered_app_files = filter_app_files(changed_app_files, all_app_config_path)
            with open("scr_app_list.txt", "w") as cfg:
                for line in filtered_app_files:
                    cfg.write("%s\n" % line)

    else:
        logger.error("Unable to generate diff file Error: %s" % err)


def slugify_screenshot_text(text):
    # replacing any contiguous sequence of non alphabet(spaces, "_" etc) with underscore `-`
    text = re.sub(r"[ @_!#$%^&*()<>?/\|}{~:`',\\]+", '-', text.strip())
    # replacing any contiguous - with single -
    text = re.sub(r"[-]+", '-', text.strip())

    # remove last -
    text = text.strip("-")
    return text


def get_screenshot_url(appName, dashboard_name, dest_bucket="sumologic-app-data-v2", file_ext="png"):

    key = "dashboards/%s/%s.%s" % (slugify_screenshot_text(appName), slugify_screenshot_text(dashboard_name), file_ext)
    return "https://%s.s3.amazonaws.com/%s" % (dest_bucket, key)


@appcmd.command(help="For generating screenshot urls")
@click.option('-s', '--sourcefile', required=True, type=click.Path(exists=True), help='Set filepath for appjson')
def generate_screenshot_urls(sourcefile):
    appjson = get_file_data(sourcefile)
    appDict = json.loads(appjson, object_pairs_hook=OrderedDict)
    dashboard_class = get_test_class(appjson=appDict)
    dashboards, searches = dashboard_class.get_content(appDict)
    for dash in dashboards:
        print(get_screenshot_url(appDict["name"], dash.get("name")))


@appcmd.command(help="For updating helpDocIds for apps in catalog")
@click.option('-m', '--manifestfile', required=True, type=click.Path(exists=True), help='Set filepath for manifest json')
def update_helpdocid(manifestfile):
    update_helpDocIdAPI(manifestfile)


def update_helpDocIdAPI(manifestfile):
    manifestJson = get_file_data(manifestfile)
    manifestJson = json.loads(manifestJson, object_pairs_hook=OrderedDict)
    if "helpDocIdMap" in manifestJson:
        logger.info("HelpDocIdMap already present in manifest for app: " + manifestJson["name"])
        return 2
    appName = manifestJson["family"] if "family" in manifestJson else manifestJson["name"]
    # replacing Metrics,ULM,Global Intelligence etc keywords as collection doc titles do not have this keyword
    appName = appName.replace("Metrics", "").replace("ULM","").replace("Global Intelligence", "(GI|Global Intelligence)").replace("Azure Kubernetes Service (AKS)", "AKS").replace(" ", "\ ").strip()
    all_doc_page_ids = 'https://help.sumologic.com/@api/deki/pages'
    page = requests.get(all_doc_page_ids)
    soup = BeautifulSoup(page.text, 'html.parser')
    try:
        foundTitleTag = soup.find(string = re.compile(".*(Collect|Set up|Configure Log).*"+ appName +".*",re.IGNORECASE)).parent.parent['id']
    except Exception as e:
        logger.error("Exception occured in fetching helpDocId, please check manually " + appName + " collection doc exists in " + all_doc_page_ids)
        return 1
    if foundTitleTag is None:
        logger.error("HelpDoc title tag not found in: " + all_doc_page_ids + " for " + appName)
        return 1
    else:
        idEntry = {"helpDocIdMap": {"en": foundTitleTag}}
        manifestJson.update(idEntry)
        save_manifest(manifestfile, manifestJson)
        logger.info("Manifest successfully updated app: " + appName)
        return 3


@appcmd.command(help="For updating the helpdocids of all apps in their manifestfiles")
@click.option('-f', '--filepath', required=True, type=click.Path(exists=True), help='Set filepath for file containing list of all apps')
def update_all_helpdocids(filepath):
    with open(filepath, 'r') as f:
        app_files = f.readlines()

    excludeAppsWithNoDocs = ("Partners/","PCF/","SumoLogic/","Auth0/","RealUserMonitoring/","Tracing/","Atlassian/","CrowdStrike/ThreatIntelQuickAnalysis/","kubernetes/GIS_Kubernetes_Devops/","LogAnalysis/") + EXCLUDED_APP_PREFIXES
    filtered_app_files = filter(lambda x: x and x.strip() and not (
        x.startswith(excludeAppsWithNoDocs)), app_files)

    app_dir = get_content_dirpath() + "/src/main/app-package/"
    hasError = alreadyExists = successfullyUpdated = 0

    errorFiles = []
    for row in filtered_app_files:
        appfile, manifestfile = row.strip().split(":")
        appfile = os.path.join(app_dir, appfile)
        manifestfile = os.path.join(app_dir, manifestfile)
        status_code = update_helpDocIdAPI(manifestfile)
        if status_code == 1:
            hasError += 1
            errorFiles.append(row)
        elif status_code == 2:
            alreadyExists += 1
        elif status_code == 3:
            successfullyUpdated += 1
    logger.info(f"Results : total errors : {hasError} , aleady existing ids : {alreadyExists} , successfully updated ids : {successfullyUpdated}")
    print("\n".join(errorFiles))


def file_browser(starting_folder,executor_func,*args,**kwargs):
   """
   Function to browse recursively a folder, then call a processing function
   :param starting_folder:
   :param process_func:
   :return:
   """
   logger.debug(f"Starting folder: {starting_folder}")
   try:
      with os.scandir(path=starting_folder) as iter:
         for entry in iter:
            if (entry.is_file() and entry.name.endswith('.manifest.json')):
               executor_func(entry.path,*args,**kwargs)
            elif entry.is_dir():
               file_browser(entry.path,executor_func,*args,**kwargs)
   except Exception as e:
         logger.error(e)

class AppEntry(object):
    """
    Represent each App entry in the Demo yaml
    """
    NAME_FIELD                  = "name"
    MANIFEST_PATH_FIELD         = "manifest_path"
    SOURCE_PATH_FIELD           = "source_path"
    DEMO_INPUT_MAPPING_FIELD    = "demo_input_mapping"
    INPUT_NAME_FIELD            = "input_name"
    INPUT_CATEGORY_FIELD        = "input_category_map"

    @staticmethod
    def get_loggen_mapping(app_name,cur_category_mapping,parameterName):
        """
        Category Mapper for special apps. NOTE: This has not fully accounted for all apps we have in Catalog by 09/27/2021
        """
        print(f"Processing app: {app_name}")
        if ("CloudTrail" in app_name):
            return "AWS/CloudTrail*"
        if ("Config" in app_name):
            return "AWS/Config"
        if (("AWS Elastic Load Balancer - Application" == app_name) or ("AWS Elastic Load Balancing ULM - Application" == app_name)):
            return "AWS/ALB*"
        if (("AWS Elastic Load Balancer - Classic" == app_name) or ("AWS Elastic Load Balancing ULM - Classic" == app_name)):
            return "AWS/ELB*"
        if ("Lambda" in app_name):
            if parameterName == "logsrccw":
                #cloudwatch lambda logs
                return "AWS/Lambda*"
            else:
                #cloudtrail lambda logs, "logsrcct"
                return "AWS/CloudTrail"
        if ("AWS Network Firewall" == app_name):
            return "AWS/Vanta*"
        if ("AWS Security Hub" in app_name):
            return "AWS/SecurityHub*"
        if ("AWS WAF" in app_name):
            return "AWS/WAF*"
        if ("Active Directory JSON" in app_name):
            return "windows-jsonformat"
        if ("Active Directory Legacy"  == app_name):
            return "Windows/OS/Windows"
        if ("Amazon CloudFront"  == app_name):
            return "AWS/CloudFront"
        if ("DynamoDB"  in app_name):
            return "AWS/DynamoDB*"
        if ("GuardDuty"  in app_name):
            return "AWS/GuardDuty*"
        if ("Inspector"  in app_name):
            return "AWS/Inspector*"
        if ("Kinesis"  in app_name):
            return "AWS/CloudTrail/Kinesis*"
        if ("Redshift"  in app_name):
            if parameterName == "AuditLogSrc":
                #Audit logs
                return "AWS/Redshift/Audit*"
            else:
                #cloudtrail Redshift logs, "CloudTrailLogSrc"
                return "AWS/CloudTrail"
        if ("S3 Audit"  in app_name):
            return "AWS/S3*"
        if ("SES"  in app_name):
            return "AWS/SES*"
        if ("SNS"  in app_name):
            return "AWS/SNS*"
        if ("Amazon VPC Flow"  in app_name):
            return "AWS/VPC*"
        if ("Amazon VPC Flow"  in app_name):
            return "AWS/VPC*"
        if ("Aqua"  in app_name):
            return "Aqua*"
        if ("Atlassian"  in app_name):
            if parameterName == "jiralogsrc":
                #Jira
                return "jira*"
            else:
                if parameterName == "bblogsrc":
                    # Bitbucket
                    return "bitbucket*"
                else:
                    # Bitbucket
                    return "Opsgenie_alerts*"
        if ("Aurora MySQL"  in app_name):
            if parameterName == "ErrorLogSrc":
                # Error
                return "AWS/RDS/Aurora/MySQL/Error"
            if parameterName == "SlowQueryLogSrc":
                # Slow Query 
                return "AWS/RDS/Aurora/MySQL/SlowQuery"
            if parameterName == "AuditLogSrc":
                #Audit
                return "AWS/RDS/Aurora/MySQL/Audit"
            if parameterName == "GeneralLogSrc":
                #General Logs
                return "AWS/RDS/Aurora/MySQL/Audit"
            if parameterName == "CloudTrailLogSrc":
                #CloudTrail
                return "AWS/Cloudtrail*"
        if ("Aurora PostgreSQL"  in app_name):
            if parameterName == "CloudTrailLogSrc":
                # Error
                return "AWS/CloudTrail*"
        # DUC: 09/27/21: There are many more that need to be customized, probabaly not worth it to add more vs just adding directly to yaml file 
        return f"{cur_category_mapping}*" 


def _extract_manifest(file_name,*args,**kwargs):
    """
    Extract dashboard names
    :param file_name:
    :return:
    """

    if (args is None ):
        print(f"No app list provided")
        exit(0) 

    base_name = os.path.basename(file_name)
    dir_name = os.path.dirname(file_name)
    source_name = base_name[0:base_name.find('.manifest.json')]
    full_source_name =os.path.join(dir_name,f"{source_name}.json")
    # Extract the directory path after app-package
    endIdx = file_name.find(base_name)
    startIdx = file_name.find('app-package/')
    directory_prefix = file_name[startIdx+12:endIdx-1]
    app_entry = {}
    if (not os.path.exists(full_source_name)):
        print(f"ERROR: Source file {full_source_name} does not exist!\n")
    else:
        # Parse manifest file
        with open(file_name) as fp:
            logger.info(f"Reading file: {file_name}")
            content_obj = json.load(fp)
            if not ('categories' in content_obj):
                logger.warning(f" File {file_name} doesn't seem to be a valid App manifest object")
            else:
                app_entry[AppEntry.NAME_FIELD] = content_obj['name']
                app_entry[AppEntry.MANIFEST_PATH_FIELD] = f"{directory_prefix}/{base_name}"
                app_entry[AppEntry.SOURCE_PATH_FIELD] = f"{directory_prefix}/{os.path.basename(full_source_name)}"
                input_mapping_list = []
                for input in content_obj['parameters']:
                    input_mapping = {}
                    if (input['dataSourceType']=='LOG'):
                        input_mapping[AppEntry.INPUT_NAME_FIELD] = input['parameterId']
                        # We'll use the immediate parent directory name for source category mapping
                        category_mapping = AppEntry.get_loggen_mapping(content_obj['name'],os.path.basename(dir_name),input['parameterId'])
                        input_mapping[AppEntry.INPUT_CATEGORY_FIELD] = f"_sourceCategory = Labs/{category_mapping}"
                        input_mapping_list.append(input_mapping)
                app_entry[AppEntry.DEMO_INPUT_MAPPING_FIELD] = input_mapping_list
        logger.debug(f"Mapping entry for {file_name} is {app_entry}") 
    args[0].append(app_entry)

@appcmd.command(help="Enumerating yaml file for App Deployment ")
@click.option('-f', '--filepath', required=False, type=click.Path(exists=True), help='Absolute path to for file containing list of all apps')
@click.option('-o', '--outfile', required=False, type=click.STRING, help='Output file name')
def enumerate_app_manifests(filepath,outfile):
    app_list = []
    if (filepath is not None):
        app_dir = filepath + "/src/main/app-package/"
    else:
        app_dir = get_content_dirpath() + "/src/main/app-package/"
    file_browser(app_dir,_extract_manifest,app_list) 
    app_list.sort(key= lambda entry:entry[AppEntry.NAME_FIELD])

    with open(outfile if outfile is not None else "app_list_out.yaml",'w') as fo:
        yaml.dump({'apps':app_list},fo,sort_keys=False) 
    #print(f"Final result: {app_list}")