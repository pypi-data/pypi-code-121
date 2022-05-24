#!/usr/bin/env python
import traceback
import os
import sys
from unittest import TestLoader
import click
from sumoappclient.common.logger import get_logger

from sumoappclient.provider.factory import ProviderFactory
from sumoapputils.common.testutils import run_test
from sumoapputils.common.utils import  EXCLUDED_APP_PREFIXES, USER, ENVIRONMENT, get_test_logger
from sumoapputils.common.testapp import TestApp



logger = get_test_logger()


def test_all_apps(deployment_name, access_id, access_key,
                  test_names, all_app_config, base_dir=None):
    cnt = 0
    failed_tests_cnt = warning_tests_cnt = 0
    failed_apps = []
    warning_apps = []
    app_files = []

    app_dir = os.getcwd() if base_dir is None else base_dir

    with open(all_app_config) as fp:
        app_files = fp.readlines()

    filtered_app_files = filter(lambda x: x and x.strip() and not (
        x.startswith(EXCLUDED_APP_PREFIXES)), app_files)

    for row in filtered_app_files:
        appfile, manifestfile = row.strip().split(":")
        appfile = os.path.join(app_dir, appfile)
        manifestfile = os.path.join(app_dir, manifestfile)
        cnt += 1
        has_failures, has_warnings = run_test(manifestfile, appfile,
                                              deployment_name, access_id,
                                              access_key, test_names)

        if has_failures:
            failed_tests_cnt += 1
            failed_apps.append(row.strip())
        elif has_warnings:
            warning_tests_cnt += 1
            warning_apps.append(row.strip())

    logger.info("Tests Results=> Total Apps Tested: %d Total Apps Failing Tests: %d Total Apps Passed With Warnings: %d \nFiles with Failures: %s \nFiles with Warnings: %s" % (cnt, failed_tests_cnt, warning_tests_cnt, failed_apps, warning_apps))
    with open("failed_apps.txt", "w") as fp:
        fp.write("\n".join(failed_apps))

    has_any_warnings = True if warning_tests_cnt > 0 else False
    has_any_failures = True if failed_tests_cnt > 0 else False

    return has_any_failures, has_any_warnings


def get_test_names(includetests=None, excludetests=None):

    test_loader = TestLoader()
    test_names = test_loader.getTestCaseNames(TestApp)
    if includetests:
        includetests = [test.strip() for test in includetests]
        test_names = includetests
    if excludetests:
        excludetests = [test.strip() for test in excludetests]
        test_names = filter(lambda x:  x not in excludetests, test_names)

    test_names = list(test_names)

    DEPLOYMENT_TEST = "test_is_deployable"
    PARTNER_ONLY_TESTS = ("test_folder_structure", "test_image_size_and_format", "test_uuid_matches_stored_value")

    if not os.environ.get("ENABLE_PARTNER_CICD_COMMANDS", None):
        test_names = list(filter(lambda x, testset=PARTNER_ONLY_TESTS: x not in testset, test_names))


    if DEPLOYMENT_TEST in test_names:
        # putting deployment test in last
        test_names.remove(DEPLOYMENT_TEST)
        test_names.append(DEPLOYMENT_TEST)

    return test_names


def validate_sumo_secrets(ctx, param, value):
    logger = get_logger(__name__, LOG_FILEPATH="/tmp/sumoapptestutils.log",
                        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"))
    if not value:
        deployment = ctx.params.get('deployment') or ENVIRONMENT.SUMO_DEPLOYMENT
        op_cli = ProviderFactory.get_provider("onprem")
        store = op_cli.get_storage("keyvalue", name='sumoapputils', db_dir="~/sumo", logger=logger)
        sumo_config = store.get('sumoconfig', {})
        if not sumo_config.get(deployment):
            raise click.BadOptionUsage(option_name=param.name, message="%s is not set for deployment %s. Please run sumo_config command to save the configuration or pass them as parameters" % (param.name, deployment), ctx=ctx)
        value = sumo_config[deployment][param.name]
    return value


def validate_testnames(ctx, param, value):
    ''' cannot be moved to common because get_test_names function is different in both appdev and partner modules'''
    testnames = []
    if value:
        all_test_names = get_test_names()
        testnames = [c.strip() for c in value.split(',')]
        for c in testnames:
            if c not in all_test_names:
                raise click.BadOptionUsage(option_name=param.name, message="%s is not an available test name." % c, ctx=ctx)

    return testnames


@click.group()
def apptestcmd():
    pass


@apptestcmd.command(help="For running unit tests for multiple apps using config file")
@click.option('-i', '--includetests', default=','.join(get_test_names()), show_default=True, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option('-e', '--excludetests', default='', show_default=False, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option('-f', '--filepath', required=True, type=click.Path(exists=True), help='Set filepath for file containing list of apps in following format appjsonfile:manifestfile')
@click.option('-b', '--basedirectory', default=None, type=click.Path(exists=True), help='Set directory path from where appjson:manifestfile entries are accessible')
@click.option('-d', "--deployment", required=True, default=lambda : ENVIRONMENT.SUMO_DEPLOYMENT, type=click.Choice(['nite', 'stag', 'long']), help="deployment_name nite/stag/long.")
@click.option("-k", "--access_id",  help="access_id for deployment(required)", callback = validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment(required)", callback = validate_sumo_secrets)
def run_all_app_tests(includetests, excludetests, filepath, basedirectory=None, deployment='', access_id='', access_key=''):
    test_names = get_test_names(includetests, excludetests)
    has_failures, _ = test_all_apps(deployment, access_id,
                                    access_key, test_names, filepath, basedirectory)


    exit_status = 1 if has_failures else 0
    sys.exit(exit_status)



@apptestcmd.command(help="For running app unit tests")
@click.option('-i', '--includetests', default=','.join(get_test_names()), show_default=True, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option('-e', '--excludetests', default='', show_default=False, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option("-m", "--manifestfile", required=True, type=click.Path(exists=True), help="manifest file path Ex: src/<path to json>")
@click.option("-s", "--sourceappfile", required=True, type=click.Path(exists=True), help="appjson file path Ex: src/<path to json>")
@click.option('-d', "--deployment", required=True, default=lambda : ENVIRONMENT.SUMO_DEPLOYMENT, type=click.Choice(['nite', 'stag', 'long']), help="deployment_name nite/stag/long.")
@click.option("-k", "--access_id",  help="access_id for deployment(required)", callback = validate_sumo_secrets)
@click.option("-c", "--access_key", help="access_key for deployment(required)", callback = validate_sumo_secrets)
def run_app_tests(includetests, excludetests, manifestfile, sourceappfile, deployment='', access_id='', access_key=''):

    test_names = get_test_names(includetests, excludetests)
    has_failures, _ = run_test(manifestfile, sourceappfile,
                               deployment, access_id,
                               access_key, test_names)

    exit_status = 1 if has_failures else 0
    sys.exit(exit_status)



