import json
import os
import uuid
from shlex import quote
from collections import defaultdict
import click
import pyAesCrypt
from sumoappclient.common.utils import get_normalized_path
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.pkggenerator.utils import upload_code_in_S3
from sumoapputils.appdev.apptasks import generate_mini_appfile
from sumoapputils.appdev.fifoqueue import FifoQueue
from sumoapputils.appdev.updatemanifest import update_manifest, update_manifest_in_forked_repo
from sumoapputils.appdev.updatesubmodules import add_or_update_submodule, update_all_private_submodules, update_all_public_submodules, remove_submodule
from sumoapputils.appdev.generate_test_config import generate_partner_app_config, generate_appdev_app_config, get_app_config, generate_all_partner_app_config
from sumoapputils.appdev.utils import default_extract_keys
from sumoapputils.common.utils import run_cmd, get_content_dirpath, ALL_APPS_FILENAME, EXCLUDED_APP_PREFIXES
from sumoappclient.common.logger import get_logger
from sumoapputils.appdev.appdeployapi import list_apps
from sumoapputils.common.testapp import TestApp

logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

@click.group()
def partnercicdcmd():
    pass

TEST_JOB_QUEUE = "run_tests_jobs"

@partnercicdcmd.command(help="For generating uuid and pushing changes")
@click.option('-r', '--repo_full_name', required=True, help='Sets repo_full_name')
@click.option('-b', '--branch_name', required=True, help='Sets branch_name')
@click.option('-f', '--repo_folder',default=None, type=click.Path(exists=True), help='Sets repo folder')
def update_manifest_in_partner_repo(repo_full_name, branch_name, repo_folder):
    update_manifest(repo_full_name, branch_name, repo_folder)

@partnercicdcmd.command(help="For generating job config used in scheduler job for triggering downstream jobs")
@click.option('-n', '--num_items', default=5, type=click.INT, help = 'Sets num of items to pull from queue')
def generate_partner_jenkins_job_config(num_items):
    jobs = FifoQueue(TEST_JOB_QUEUE).deque(num_items)
    print("%d jobs found" % len(jobs))
    with open("job_config.json", "w") as fp:
        json.dump(jobs, fp)

@partnercicdcmd.command(help="For adding or updating submodule")
@click.option('-r', '--submodule_repo_full_name', required=True, help='Sets submodule_repo_full_name')
def sync_main_partner_repo(submodule_repo_full_name):
    add_or_update_submodule(submodule_repo_full_name)

@partnercicdcmd.command(help="For updating all private submodules")
@click.option('-p', '--parent_repo_folder',default=None, type=click.Path(exists=True), help='Sets repo folder which contains submodules')
@click.option('-n', '--num_items', default=5, type=click.INT, help = 'Sets num of items to pull from queue')
def update_private_submodules(parent_repo_folder, num_items):
    update_all_private_submodules(parent_repo_folder, num_items)

@partnercicdcmd.command(help="For updating all public submodules")
@click.option('-n', '--num_items', default=5, type=click.INT, help = 'Sets num of items to pull from queue')
@click.option('-p', '--parent_repo_folder',default=None, type=click.Path(exists=True), help='Sets repo folder which contains submodules')
def update_public_submodules(parent_repo_folder, num_items):
    update_all_public_submodules(parent_repo_folder, num_items)


@partnercicdcmd.command(help="For generating test config for partner jenkins tests")
@click.option('-r', '--repo_full_name', required=True, help='Sets repo_full_name')
@click.option('-p', '--pr_id', required=True, help='Sets PR ID')
def generate_partner_app_metadata_config(repo_full_name, pr_id):
    repo_full_name = repo_full_name.replace("/", "-")
    unique_suffix = "%s-%s" %(repo_full_name, pr_id)
    generate_partner_app_config(unique_suffix)


@partnercicdcmd.command(help="For removing submodule")
@click.option('-r', '--repo_full_name', required=True, help='Sets repo_full_name')
def remove_submodule_from_partner_repo(repo_full_name):
    remove_submodule(repo_full_name)


@partnercicdcmd.command(help="For generating test config for central public partner repo")
@click.option('-r', '--repo_full_name', required=True, help='Sets repo_full_name')
@click.option('-p', '--pr_id', required=True, help='Sets PR ID')
@click.option('-b', '--branch_name', required=True, help='Sets branch_name')
def generate_changed_partner_apps_metadata_config(repo_full_name, pr_id, branch_name):
    return_code, err = run_cmd("git remote add mainRepo git@github.com:SumoLogic/sumologic-public-partner-apps.git")
    if return_code != 0:
        logger.error("Unable to add remote url")
        return

    return_code, err = run_cmd("git fetch mainRepo")
    if return_code != 0:
        logger.error("Unable to fetch mainRepo")
        return

    return_code, err = run_cmd("git diff-tree --no-commit-id --name-only -r HEAD $(git merge-base mainRepo/master HEAD) > changed-files")
    if return_code == 0:
        repo_full_name = repo_full_name.replace("/", "-")
        unique_suffix = "%s-%s" % (repo_full_name, pr_id)
        generate_all_partner_app_config(unique_suffix, changed_files_path="changed-files")
    else:
        logger.error("Unable to generate diff file Error: %s" % err)


@partnercicdcmd.command(help="For generating uuid and pushing changes in forked partner repo")
@click.option('-b', '--branch_name', required=True, help='Sets branch_name')
@click.option('-f', '--changedappsfile', required=True, type=click.Path(exists=True), help='Set filepath for file contains list of changed apps')
@click.option('--nocommit', is_flag=True, help="Set the flag to not commit and push the changes")
def update_manifest_in_forked_partner_repo(branch_name, changedappsfile, nocommit):
    changedappsfile = get_normalized_path(changedappsfile)
    update_manifest_in_forked_repo(branch_name, changedappsfile, nocommit)


@click.group()
def appdevcicdcmd():
    pass

@appdevcicdcmd.command(help="For uploading file in S3")
@click.option('-f', '--filepath', type=click.Path(exists=True), help='Set filepath for file')
@click.option('-b', '--bucket_name', type=str, required=True, help='Sets bucket_name')
@click.option('-r', '--bucket_region', default="us-east-1", type=str, required=True, help='Sets bucket_region')
@click.option('-p', '--prefix', default="", type=str, help='Sets prefix folder')
@click.option('--public', is_flag=True, help='Sets the file as public')
def upload_file(filepath, bucket_name, bucket_region, prefix, public):

    upload_code_in_S3(filepath, bucket_name, bucket_region, is_public=public, prefix=prefix)

@appdevcicdcmd.command(help="For generating test config for appdev jenkins tests")
def generate_app_metadata_config():
    return_code, err = run_cmd("git diff-tree --no-commit-id --name-only -r HEAD HEAD^ > changed-files")
    if return_code == 0:
        unique_file_suffix = os.environ.get("ghprbPullId", uuid.uuid4().hex[:8])
        generate_appdev_app_config(unique_file_suffix, changed_files_path="changed-files")
    else:
        logger.error("Unable to generate diff file Error: %s" % err)


@appdevcicdcmd.command(help="For generating test config for appdev jenkins tests for given apps")
@click.option('-o', '--outputfile_suffix', default=uuid.uuid4().hex[:8], help='Sets outputfile file name')
@click.option('-f', '--appsfile', default=os.path.join(get_content_dirpath(), "bin", ALL_APPS_FILENAME), type=click.Path(exists=True), help='Set filepath for file contains list of changed apps')
def generate_app_config_withpaneldata(appsfile, outputfile_suffix):
    content_dir_path = get_content_dirpath()
    with open(appsfile, "r") as all_apps:
        app_list = all_apps.readlines()

    filtered_app_files = filter(lambda x: x and x.strip() and not (
        x.startswith(EXCLUDED_APP_PREFIXES)), app_list)

    filtered_app_files = map(lambda x: x.strip(), filtered_app_files)

    app_config_file = "app-config-%s.json" % outputfile_suffix
    all_data = []

    for line in filtered_app_files:
        appfile, manifestfile = line.split(":")
        appfile = os.path.join(content_dir_path, "src", "main", "app-package", appfile)
        manifestfile = os.path.join(content_dir_path, "src", "main", "app-package", manifestfile)
        all_data.append(get_app_config(manifestfile, appfile, withpaneldata=True))

    with open(app_config_file, "w") as cfg:
        json_data = json.dumps(all_data, indent=4)
        cfg.write("%s\n" % json_data)
    print("generated files %s" % app_config_file)


@appdevcicdcmd.command(help="For generating min.json for all the apps in the changedapps file")
@click.option('-f', '--changedappsfile', required=True, type=click.Path(exists=True), help='Set filepath for file contains list of changed apps')
def generate_and_push_review_file(changedappsfile):
    app_dir = os.path.join(get_content_dirpath(), "src", "main", "app-package")
    branch = os.getenv("GIT_BRANCH")
    with open(changedappsfile) as fp:
        app_files = fp.readlines()

    run_cmd('git checkout %s' % quote(branch))
    for row in app_files:
        appfile, manifestfile = row.strip().split(":")
        appfile = os.path.join(app_dir, appfile)
        current_mini_appjson = generate_mini_appfile(appfile, default_extract_keys)
        current_mini_appjsonstr = json.dumps(current_mini_appjson, indent=4, separators=(',', ': '))

        mini_appjson_path = appfile.replace(".json", ".miniappfile.json")
        with open(mini_appjson_path, 'w') as f:
            f.write(current_mini_appjsonstr)

        run_cmd('git add %s' % quote(mini_appjson_path))
    return_code, _ = run_cmd('git commit -m \"miniappfile generated for review\"')
    if return_code != 1:
        run_cmd('git push origin %s' % quote(branch))

bufferSize = 64 * 1024


@appdevcicdcmd.command(help="For generating test config for appdev jenkins tests")
@click.option('-f', '--file', default=os.path.join(os.path.dirname(__file__), "secret.json.encrypted"), type=click.Path(exists=True), help='Set filepath for file to decrypt')
@click.option('--password', '-p', envvar="SUMO_SECRET_API", type=str, help='Sets the password')
def decrypt_populate_credentials(file, password):
    encrypted_filepath = file
    decrypted_filepath = encrypted_filepath.replace(".encrypted", "")
    pyAesCrypt.decryptFile(encrypted_filepath, decrypted_filepath, password, bufferSize)
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    with open(decrypted_filepath) as fp:
        cred_obj = json.load(fp)
        for deployment, cfg in cred_obj.items():
            sumoconfig[deployment] = {"access_id": cfg["access_id"], "access_key": cfg["access_key"]}
    logger.info("Deployment config decrypted and configured")
    store.set("sumoconfig", sumoconfig)


@appdevcicdcmd.command(help="For generating test config for appdev jenkins tests")
@click.option('-f', '--file', default=os.path.join(__file__, "secret.json"), type=click.Path(exists=True), help='Set filepath for file to encrypt')
@click.option('--password', '-p', envvar="SUMO_SECRET_API", type=str, help='Sets the password')
def encrypt_credentials(file, password):
    encrypted_filepath = file + ".encrypted"
    decrypted_filepath = file
    pyAesCrypt.encryptFile(decrypted_filepath, encrypted_filepath, password, bufferSize)
    logger.info("Deployment config encrypted")


def validate_sumo_deployments(ctx, param, value):
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    if value == "all":
        return sumoconfig.keys()
    else:
        values = value.split(",")
        values = [v.strip() for v in values]
        for deployment in values:
            if deployment not in sumoconfig:
                raise click.BadOptionUsage(option_name=param.name, message="%s deployment config is not present" % deployment, ctx=ctx)

        return values


@appdevcicdcmd.command(help="For testing deployment of apps after SCR is implemented")
@click.option('-f', '--scr_file_path', required=True, type=click.Path(exists=True), help='Set filepath for scr file with format /path to appjson:/path to manifestfile')
@click.option('-d', '--deployments', default="all", help='Set deployments comma separated. Default is all', callback=validate_sumo_deployments)
@click.option('-b', '--basedirectory', default=None, type=click.Path(exists=True), help='Set directory path from where appjson:manifestfile entries are accessible')
def test_app_deployment(scr_file_path, deployments, basedirectory):
    # Todo add version deployment check
    # with installation flag
    applist = {}
    with open(scr_file_path) as f:
        for line in f.readlines():
            if line.startswith("//") or not line.strip():
                continue
            sourceappfile, manifestfile = line.strip().split(":")
            manifestfile = os.path.join(os.path.abspath(basedirectory), manifestfile)
            manifestjson = TestApp.get_valid_json(manifestfile)
            applist[manifestjson["uuid"]] = {"name": manifestjson["name"], "appVersion": manifestjson["version"]}

    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    result = {"missing_apps":{"total": 0}, "errors": []}
    for deployment in deployments:
        cfg = sumoconfig[deployment]
        result["missing_apps"][deployment] = {}
        logger.info("Checking on deployment %s" % deployment)
        status, data = list_apps(deployment, cfg["access_id"], cfg["access_key"])
        if status:
            app_uuids_present = set([app["appDefinition"]["uuid"] for app in data])

            missing_apps = {uuid: app for uuid, app in applist.items() if uuid not in app_uuids_present}
            present_apps = [app for uuid, app in applist.items() if uuid in app_uuids_present]
            logger.info("Apps present in Deployment %s : %s" % (deployment,present_apps))
            if missing_apps:
                result["missing_apps"][deployment]["apps"] = missing_apps
                result["missing_apps"][deployment]["total"] = len(missing_apps)
                result["missing_apps"]["total"] += len(missing_apps)
        else:
            result["errors"].append("Error in listing apps in %s resp: %s" % (deployment, data))

    print(json.dumps(result, indent=4))


@appdevcicdcmd.command(help="For comparing list of deployed apps in app catalog")
@click.option('-d', '--deployments', default="all", help='Set deployments comma separated. Default is all', callback=validate_sumo_deployments)
def compare_deployed_apps_list(deployments):
    # Todo add version missing
    applist = defaultdict(lambda : {"deployment_count": 0, "deployments": set(), "name": None})
    op_cli = ProviderFactory.get_provider("onprem")
    store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
    sumoconfig = store.get("sumoconfig", {})
    result = {"errors": [], "missing_apps": {}}
    NUM_SUMO_DEPLOYMENTS = len(deployments)
    all_deployments = set([deployment for deployment in deployments])
    for deployment in deployments:
        cfg = sumoconfig[deployment]
        logger.info("Checking on deployment %s" % deployment)
        status, data = list_apps(deployment, cfg["access_id"], cfg["access_key"])
        if status:
            for app in data:
                applist[app["appDefinition"]["uuid"]]["deployment_count"] += 1
                applist[app["appDefinition"]["uuid"]]["deployments"].add(deployment)
                applist[app["appDefinition"]["uuid"]]["name"] = app["appDefinition"]["name"]
        else:
            result["errors"].append("Error in listing apps in %s resp: %s" % (deployment, data))
    for uuid, appdata in applist.items():
        if appdata["deployment_count"] < NUM_SUMO_DEPLOYMENTS:
            result["missing_apps"][uuid] = {
                "deployments": list(all_deployments - appdata["deployments"]),
                "name": appdata["name"]
            }

    print(json.dumps(result, indent=4))
