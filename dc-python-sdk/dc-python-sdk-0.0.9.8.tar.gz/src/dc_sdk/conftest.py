import os
import sys
import pytest
from dotenv import load_dotenv
from os import environ
import random
import string
import shutil


def pytest_addoption(parser):
    """
    adds the option to write --file=<your path to connector.py>
    """
    parser.addoption(
        "--source", action="store_true", default=False, help="run source tests"
    )
    parser.addoption(
        "--destination", action="store_true", default=False, help="run destination tests"
    )


@pytest.fixture(scope="session")
def root_dir():
    return os.path.dirname(os.path.abspath(".env.credentials"))


def add_root_dir_to_path(root_dir):
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), root_dir))
    print(path)
    if path not in sys.path:
        sys.path.insert(1, path)


@pytest.fixture(scope="session", autouse=True)
def copy_ini_to_root(root_dir):
    add_root_dir_to_path(root_dir)
    shutil.copy(os.path.join(os.path.dirname(__file__), "pytest.txt"),
                os.path.abspath("pytest.ini"))


@pytest.fixture(scope="session")
def module_name(pytestconfig):
    return pytestconfig.getoption("lib-path")


@pytest.fixture(scope="session",
                autouse=True)
def connector_class(root_dir):
    """ This takes in the connector file name and tries to import it """
    try:
        add_root_dir_to_path(root_dir)
        import src.connector as _conn
        return _conn
    except Exception:
        raise Exception("Error: cannot locate Connector class in session <session name>")


@pytest.fixture(scope="session")
def env_file(pytestconfig):
    return ".env.credentials"


def pytest_configure(config):
    config.addinivalue_line("markers", "source: mark test as a source function")


# def pytest_collection_modifyitems(config, items):
    # """ This function makes pytest skip the source or destination tests, depending if the --source or --destination
    # flag is not present. """
    # if not config.getoption("--source"):
    #     # makes the test print the reason the test was skipped
    #     skip_source = pytest.mark.skip(reason="need --source option to run")
    #     for item in items:
    #         if "source" in item.keywords:
    #             item.add_marker(skip_source)
    #
    # if not config.getoption("--destination"):
    #     skip_destination = pytest.mark.skip(reason="need --destination option to run")
    #     for item in items:
    #         if "destination" in item.keywords:
    #             item.add_marker(skip_destination)


@pytest.fixture(scope="session")
def env(env_file):
    load_dotenv(env_file)
    return environ


@pytest.fixture(scope="session")
def good_object_id(env):
    return env["OBJECT_ID"]


@pytest.fixture(scope="session")
def bad_object_id(env):
    return env["OBJECT_ID"] + "_bad"


@pytest.fixture(scope="session")
def good_credentials(env):
    """ This takes the credentials in the env file and converts it to a dictionary """
    keys = list(env.keys())
    values = list(env.values())
    res = {keys[i].lower(): values[i] for i in range(len(keys))}
    if "USER_NAME" in env.keys():
        res["username"] = env["USER_NAME"]
    return res


@pytest.fixture(scope="session")
def bad_credentials(env):
    """ This has all the keys in the credentials object but those keys are mapped to random integers """
    keys = list(env.keys())
    res = {keys[i].lower(): str(i) for i in range(len(keys))}
    return res


@pytest.fixture(scope="session")
def connector(connector_class, good_credentials):
    connector = connector_class.Connector(good_credentials)
    return connector


@pytest.fixture(scope="session")
def good_authentication(connector):
    results = connector.authenticate()
    return results


@pytest.fixture(scope="session")
def get_good_objects(connector):
    connector.authenticate()
    objects = connector.get_objects()
    return objects


@pytest.fixture(scope="session")
def get_good_fields(good_object_id, connector):
    connector.authenticate()
    results = connector.get_fields(good_object_id)
    return results


@pytest.fixture(scope="session")
def get_all_good_field_ids(good_object_id, connector):
    connector.authenticate()
    results = connector.get_fields(good_object_id)
    return [result["field_id"] for result in results]


@pytest.fixture(scope="session")
def get_three_good_field_ids(good_object_id, connector):
    connector.authenticate()
    results = connector.get_fields(good_object_id)
    field_ids = [result["field_id"] for result in results]
    return field_ids[:3]


@pytest.fixture(scope="session")
def bad_field_ids(get_all_good_field_ids):
    FIELD_ID_LEN = 10

    # create a random 10-char string to add to get_good_field_ids
    letters = string.ascii_lowercase
    field_id = ''.join(random.choice(letters) for i in range(FIELD_ID_LEN))

    # if the random string happens to be a valid field id for this object, try again
    num_tries = 0
    while field_id in get_all_good_field_ids:
        num_tries += 1

        # if it tries 15 times and is still a valid field id, throw an exception
        if num_tries > 15:
            raise Exception
        field_id = ''.join(random.choice(letters) for i in range(FIELD_ID_LEN))

    # changing the last valid field id for the invalid one
    field_ids = get_all_good_field_ids
    field_ids[-1] = field_id
    return field_ids


@pytest.fixture(scope="session")
def bad_filters_data_type(env):
    # ? maybe have a field called "FILTERED_COLUMN_NM_WRONG_DATA_TYPE"?
    return {
        "filtered_column_nm": env["FILTERED_COLUMN_NM"],
        "start_selection_nm": env["FILTERED_SELECTION_NM"],
        "end_selection_nm": env["END_SELECTION_NM"],
        "start_value_txt": env["START_VALUE_TXT"],
        "end_value_txt": env["END_VALUE_TXT"],
        "timezone_offset_nbr": int(env["TIMEZONE_OFFSET_NBR"])
    }


@pytest.fixture(scope="session")
def get_good_data_small(connector, good_object_id, get_all_good_field_ids):
    connector.authenticate()
    # Since we are using a test account, we should have made some data for the selected object_id
    data = connector.get_data(object_id=good_object_id, field_ids=get_all_good_field_ids, n_rows=5)
    return data


@pytest.fixture(scope="session")
def get_good_meta_data(connector):
    connector.authenticate()
    meta = connector.get_meta_data()
    return meta
