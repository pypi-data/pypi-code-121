import traceback
from unittest import TestSuite
from sumoapputils.common.basetestrunner import CustomTextTestRunner
from sumoapputils.common.testapp import TestClassicDashboards, TestClassicDashboardsV2, TestApp
from sumoapputils.common.utils import get_test_logger
logger = get_test_logger()

def get_test_class(appfile=None, appjson=None):
    if appjson is None:
        appjson = TestApp.get_valid_json(appfile)
    return TestClassicDashboards if appjson["type"] == "Folder" else TestClassicDashboardsV2


def is_new_appjson_format(appfile=None, appjson=None):
    if appjson is None:
        appjson = TestApp.get_valid_json(appfile)
    return False if appjson["type"] == "Folder" else True


def run_test(manifestfile, appfile, deployment_name, access_id, access_key, test_names):

    logger.info("Starting Tests for manifestfile: %s appfile: %s" % (manifestfile, appfile))
    suite = TestSuite()
    result = None
    has_warnings = has_failures = False
    try:
        DashboardTestClass = get_test_class(appfile=appfile)
        for test_name in test_names:

            suite.addTest(DashboardTestClass(manifestfile, appfile,
                                  deployment_name, access_id,
                                  access_key, test_name))

        result = CustomTextTestRunner().run(suite)
    except BaseException as e:
        logger.error("Error in run_test: %s\n%s" % (e, traceback.format_exc()))
    finally:
        if not result:
            has_failures = True  # must have failed on initialization
            logger.debug("Results - Failed to initialize")
        else:
            has_failures = not result.wasSuccessful()
            has_warnings = len(result.warnings) > 0

    logger.info("%s\n" % ("="*130))

    return has_failures, has_warnings
