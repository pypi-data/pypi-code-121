#!/usr/bin/env python
import sys
from unittest import TestLoader
import click

from sumoapputils.common.utils import get_test_logger
from sumoapputils.common.testapp import TestApp

from sumoapputils.common.testutils import run_test

logger = get_test_logger()


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
    PARTNER_ONLY_TESTS_FOR_JENKINS = (DEPLOYMENT_TEST, "test_uuid_matches_stored_value", "test_has_valid_screenshots")
    test_names = list(filter(lambda x, testset=PARTNER_ONLY_TESTS_FOR_JENKINS: x not in testset, test_names))

    return test_names


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


@apptestcmd.command(help="For running app unit tests")
@click.option('-i', '--includetests', default=','.join(get_test_names()), show_default=True, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option('-e', '--excludetests', default='', show_default=False, is_flag=False, metavar='<testnames>', type=click.STRING, help="specify testnames separated by comma ex: test_not_using_default_lookup, test_file_path_exists_in_applist", callback=validate_testnames)
@click.option("-m", "--manifestfile", required=True, type=click.Path(exists=True), help="manifest file path Ex: src/<path to json>")
@click.option("-s", "--sourceappfile", required=True, type=click.Path(exists=True), help="appjson file path Ex: src/<path to json>")
def run_app_tests(includetests, excludetests, manifestfile, sourceappfile, deployment='', access_id='', access_key=''):

    test_names = get_test_names(includetests, excludetests)
    has_failures, _ = run_test(manifestfile, sourceappfile,
                               deployment, access_id,
                               access_key, test_names)

    exit_status = 1 if has_failures else 0
    sys.exit(exit_status)

