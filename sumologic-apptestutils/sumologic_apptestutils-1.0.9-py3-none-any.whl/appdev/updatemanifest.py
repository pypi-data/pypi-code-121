import json
import os
import sys
import traceback
import uuid
import re
from shlex import quote
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.common.logger import get_logger
from sumoappclient.pkggenerator.utils import upload_code_in_S3
from sumoappclient.common.utils import get_normalized_path
from sumoapputils.common.utils import run_cmd, delete_batch_files_in_s3, slugify


logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log", LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)


BUCKET_NAME = "sumologic-partner-appsdata"
BUCKET_REGION = "us-east-1"

def get_manifest_file():
    for fname in os.listdir(os.getcwd()):
        if fname.endswith("manifest.json"):
            return fname
    return None


def get_json(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def save_manifest(filepath, manifest_json):
    prettyJsonOutput = json.dumps(manifest_json, sort_keys=True, indent=4, separators=(',', ': '))
    with open(filepath, 'w') as file:
        file.write(prettyJsonOutput)

def update_manifest_json(manifest_json, app_name_slug, screenshot_urls, icon_url):
    '''
        In dynamodb it saves the normalized partner app name and its uuid (generates one if doesn't exists).
        Updates the manifest with screenshot, icon and uuid.
    '''
    op_cli = ProviderFactory.get_provider("aws")
    store = op_cli.get_storage("keyvalue", 'partner_app_ids', logger=logger)

    # Todo ideally get and set should be synchronous(acquire lock on key) to avoid generating multiple appuuids
    app_uuid = store.get(app_name_slug, None)
    if not app_uuid:
        app_uuid = str(uuid.uuid4())
        store.set(app_name_slug, app_uuid)

    manifest_json["uuid"] = app_uuid

    if screenshot_urls:
        manifest_json["screenshotURLs"] = screenshot_urls

    if icon_url:
        manifest_json["iconURL"] = icon_url


    return manifest_json

def push_new_changes(filepath, branch):
    print("pushing changes", branch)
    return_code, _ = run_cmd("git diff-index --quiet HEAD")
    if return_code == 1:
        run_cmd('git add %s' % quote(filepath))
        return_code, _ = run_cmd('git commit -m \"manifest updated\"')
        if return_code != 1:
            run_cmd('git push origin %s' % quote(branch))

def get_resource_url(bucket_name, resource_type, appname, filename):
    return "https://%s.s3.amazonaws.com/%s/%s/%s" % (bucket_name, resource_type, appname, filename)


def normalize_name(name):
    '''
        This follows the same guidelines given by platform team for screenshot naming convention
    '''

    # replacing any contiguous sequence of non alphabet(spaces, "_" etc) with underscore `-`
    name = re.sub(r"[ @_!#$%^&*()<>?/\|}{~:`',\\]+", '-', name.strip())
    # replacing any contiguous - with single -
    name = re.sub(r"[-]+", '-', name.strip())

    # remove last -
    name = name.strip("-")
    return name

def upload_screenshots(app_dir, appname):
    '''
        screenshots are uploaded in dashboards/appname/ folder
    '''
    screenshot_urls = []
    resource_type = "dashboards"
    app_folder_name = normalize_name(appname)
    screenshot_dir = os.path.join(app_dir, "resources", "screenshots")
    delete_batch_files_in_s3(BUCKET_NAME, BUCKET_REGION, prefix="%s/%s/" % (resource_type, app_folder_name))
    for fname in os.listdir(screenshot_dir):
        fpath = os.path.join(screenshot_dir, fname)
        upload_code_in_S3(fpath, BUCKET_NAME, BUCKET_REGION, is_public=True, prefix="%s/%s/" % (resource_type, app_folder_name))
        screenshot_urls.append(get_resource_url(BUCKET_NAME,resource_type,app_folder_name, fname))

    logger.info("%d screenshots uploaded for %s" % (len(screenshot_urls), appname))
    return screenshot_urls

def upload_icons(app_dir, appname):
    '''

        icons are uploaded in icons/appname/ folder
    '''
    icon_url = ""
    resource_type = "icons"
    icon_dir = os.path.join(app_dir, "resources", "icon")
    app_folder_name = normalize_name(appname)
    delete_batch_files_in_s3(BUCKET_NAME, BUCKET_REGION, prefix="%s/%s/" % (resource_type, app_folder_name))
    for fname in os.listdir(icon_dir):
        fpath = os.path.join(icon_dir, fname)
        upload_code_in_S3(fpath, BUCKET_NAME, BUCKET_REGION, is_public=True, prefix="%s/%s/" % (resource_type, app_folder_name))
        icon_url = get_resource_url(BUCKET_NAME,resource_type, app_folder_name, fname)

    logger.info("%s icons uploaded for %s" % (icon_url, appname))
    return icon_url


def update_manifest(repo_full_name, branch_name, target_dir=None):
    '''
        clones the partner repo (submodule based individual repo) and updates the manifest
    '''
    print(repo_full_name, branch_name)
    print("Branch quotes: ", branch_name.startswith("\""), branch_name.startswith("\'"))
    exit_status = 0
    repo_name = repo_full_name.split('/')[1]
    try:

        if target_dir is None:
            repo_path = 'git@github.com:%s.git' % repo_full_name
            run_cmd('git clone %s' % quote(repo_path))
            repo_dir = os.path.join(os.getcwd(), repo_name)
        else:
            if target_dir.startswith("/"):
                repo_dir = target_dir
            else:
                repo_dir = get_normalized_path(target_dir)

        os.chdir(repo_dir)
        run_cmd('git checkout %s' % quote(branch_name))
        fname = get_manifest_file()
        if fname:
            manifest_json = get_json(fname)
            appname = manifest_json["name"]
            screenshot_urls = upload_screenshots(repo_dir, appname)
            icon_url = upload_icons(repo_dir, appname)
            manifest_json = update_manifest_json(manifest_json, slugify(appname), screenshot_urls, icon_url)
            save_manifest(fname, manifest_json)
            push_new_changes(fname, branch_name)
    except Exception as e:
        logger.error("Error: %s Traceback: %s" % (e, traceback.format_exc()))
        exit_status = 1

    sys.exit(exit_status)


def update_manifest_in_forked_repo(branch_name, changedappsfile, nocommit=False):

    with open(changedappsfile, "r") as fp:
        changed_app_files = fp.readlines()
        for line in changed_app_files:
            appfile, manifestfile = line.strip().split(":")
            manifest_json = get_json(manifestfile)
            appname = manifest_json["name"]
            app_dir = os.path.dirname(appfile)
            logger.info("Updating manifest for  %s" % manifestfile)
            screenshot_urls = upload_screenshots(app_dir, appname)
            icon_url = upload_icons(app_dir, appname)
            manifest_json = update_manifest_json(manifest_json, slugify(appname), screenshot_urls, icon_url)
            save_manifest(manifestfile, manifest_json)
            run_cmd('git add %s' % quote(manifestfile))

    if not nocommit:
        print("pushing changes", branch_name)
        return_code, _ = run_cmd("git diff-index --quiet HEAD")
        if return_code == 1:
            return_code, _ = run_cmd('git commit -m \"manifest updated\"')
            if return_code != 1:
                run_cmd('git push origin %s' % quote(branch_name))

if __name__ == '__main__':
    update_manifest("", "")

