import os
import pytest  # type: ignore
import random
from argparse import Namespace
from datetime import datetime
import warnings
import yaml

import dbt.flags as flags
from dbt.config.runtime import RuntimeConfig
from dbt.adapters.factory import get_adapter, register_adapter, reset_adapters, get_adapter_by_type
from dbt.events.functions import setup_event_logger
from dbt.tests.util import (
    write_file,
    run_sql_with_adapter,
    TestProcessingException,
    get_connection,
)


# These are the fixtures that are used in dbt core functional tests
#
# The main functional test fixture is the 'project' fixture, which combines
# other fixtures, writes out a dbt project in a temporary directory, creates a temp
# schema in the testing database, and returns a `TestProjInfo` object that
# contains information from the other fixtures for convenience.
#
# The models, macros, seeds, snapshots, tests, and analysis fixtures all
# represent directories in a dbt project, and are all dictionaries with
# file name keys and file contents values.
#
# The other commonly used fixture is 'project_config_update'. Other
# occasionally used fixtures are 'profiles_config_update', 'packages',
# and 'selectors'.
#
# Most test cases have fairly small files which are best included in
# the test case file itself as string variables, to make it easy to
# understand what is happening in the test. Files which are used
# in multiple test case files can be included in a common file, such as
# files.py or fixtures.py. Large files, such as seed files, which would
# just clutter the test file can be pulled in from 'data' subdirectories
# in the test directory.
#
# Test logs are written in the 'logs' directory in the root of the repo.
# Every test case writes to a log directory with the same 'prefix' as the
# test's unique schema.
#
# These fixture have "class" scope. Class scope fixtures can be used both
# in classes and in single test functions (which act as classes for this
# purpose). Pytest will collect all classes starting with 'Test', so if
# you have a class that you want to be subclassed, it's generally best to
# not start the class name with 'Test'. All standalone functions starting with
# 'test_' and methods in classes starting with 'test_' (in classes starting
# with 'Test') will be collected.
#
# Please see the pytest docs for further information:
#     https://docs.pytest.org


# Used in constructing the unique_schema and logs_dir
@pytest.fixture(scope="class")
def prefix():
    # create a directory name that will be unique per test session
    _randint = random.randint(0, 9999)
    _runtime_timedelta = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    _runtime = (int(_runtime_timedelta.total_seconds() * 1e6)) + _runtime_timedelta.microseconds
    prefix = f"test{_runtime}{_randint:04}"
    return prefix


# Every test has a unique schema
@pytest.fixture(scope="class")
def unique_schema(request, prefix) -> str:
    test_file = request.module.__name__
    # We only want the last part of the name
    test_file = test_file.split(".")[-1]
    unique_schema = f"{prefix}_{test_file}"
    return unique_schema


# Create a directory for the profile using tmpdir fixture
@pytest.fixture(scope="class")
def profiles_root(tmpdir_factory):
    return tmpdir_factory.mktemp("profile")


# Create a directory for the project using tmpdir fixture
@pytest.fixture(scope="class")
def project_root(tmpdir_factory):
    # tmpdir docs - https://docs.pytest.org/en/6.2.x/tmpdir.html
    project_root = tmpdir_factory.mktemp("project")
    print(f"\n=== Test project_root: {project_root}")
    return project_root


# This is for data used by multiple tests, in the 'tests/data' directory
@pytest.fixture(scope="session")
def shared_data_dir(request):
    return os.path.join(request.config.rootdir, "tests", "data")


# This is for data for a specific test directory, i.e. tests/basic/data
@pytest.fixture(scope="module")
def test_data_dir(request):
    return os.path.join(request.fspath.dirname, "data")


# This contains the profile target information, for simplicity in setting
# up different profiles, particularly in the adapter repos.
# Note: because we load the profile to create the adapter, this
# fixture can't be used to test vars and env_vars or errors. The
# profile must be written out after the test starts.
@pytest.fixture(scope="class")
def dbt_profile_target():
    return {
        "type": "postgres",
        "threads": 4,
        "host": "localhost",
        "port": int(os.getenv("POSTGRES_TEST_PORT", 5432)),
        "user": os.getenv("POSTGRES_TEST_USER", "root"),
        "pass": os.getenv("POSTGRES_TEST_PASS", "password"),
        "dbname": os.getenv("POSTGRES_TEST_DATABASE", "dbt"),
    }


# This fixture can be overridden in a project. The data provided in this
# fixture will be merged into the default project dictionary via a python 'update'.
@pytest.fixture(scope="class")
def profiles_config_update():
    return {}


# The profile dictionary, used to write out profiles.yml. It will pull in updates
# from two separate sources, the 'profile_target' and 'profiles_config_update'.
# The second one is useful when using alternative targets, etc.
@pytest.fixture(scope="class")
def dbt_profile_data(unique_schema, dbt_profile_target, profiles_config_update):
    profile = {
        "config": {"send_anonymous_usage_stats": False},
        "test": {
            "outputs": {
                "default": {},
            },
            "target": "default",
        },
    }
    target = dbt_profile_target
    target["schema"] = unique_schema
    profile["test"]["outputs"]["default"] = target

    if profiles_config_update:
        profile.update(profiles_config_update)
    return profile


# Write out the profile data as a yaml file
@pytest.fixture(scope="class")
def profiles_yml(profiles_root, dbt_profile_data):
    os.environ["DBT_PROFILES_DIR"] = str(profiles_root)
    write_file(yaml.safe_dump(dbt_profile_data), profiles_root, "profiles.yml")
    yield dbt_profile_data
    del os.environ["DBT_PROFILES_DIR"]


# Data used to update the dbt_project config data.
@pytest.fixture(scope="class")
def project_config_update():
    return {}


# Combines the project_config_update dictionary with project_config defaults to
# produce a project_yml config and write it out as dbt_project.yml
@pytest.fixture(scope="class")
def dbt_project_yml(project_root, project_config_update, logs_dir):
    project_config = {
        "config-version": 2,
        "name": "test",
        "version": "0.1.0",
        "profile": "test",
        "log-path": logs_dir,
    }
    if project_config_update:
        project_config.update(project_config_update)
    write_file(yaml.safe_dump(project_config), project_root, "dbt_project.yml")
    return project_config


# Fixture to provide packages as either yaml or dictionary
@pytest.fixture(scope="class")
def packages():
    return {}


# Write out the packages.yml file
@pytest.fixture(scope="class")
def packages_yml(project_root, packages):
    if packages:
        if isinstance(packages, str):
            data = packages
        else:
            data = yaml.safe_dump(packages)
        write_file(data, project_root, "packages.yml")


# Fixture to provide selectors as either yaml or dictionary
@pytest.fixture(scope="class")
def selectors():
    return {}


# Write out the selectors.yml file
@pytest.fixture(scope="class")
def selectors_yml(project_root, selectors):
    if selectors:
        if isinstance(selectors, str):
            data = selectors
        else:
            data = yaml.safe_dump(selectors)
        write_file(data, project_root, "selectors.yml")


# This creates an adapter that is used for running test setup, such as creating
# the test schema, and sql commands that are run in tests prior to the first
# dbt command. After a dbt command is run, the project.adapter property will
# return the current adapter (for this adapter type) from the adapter factory.
# The adapter produced by this fixture will contain the "base" macros (not including
# macros from dependencies).
#
# Anything used here must be actually working (dbt_project, profile, project and internal macros),
# otherwise this will fail. So to test errors in those areas, you need to copy the files
# into the project in the tests instead of putting them in the fixtures.
@pytest.fixture(scope="class")
def adapter(unique_schema, project_root, profiles_root, profiles_yml, dbt_project_yml):
    # The profiles.yml and dbt_project.yml should already be written out
    args = Namespace(
        profiles_dir=str(profiles_root), project_dir=str(project_root), target=None, profile=None
    )
    flags.set_from_args(args, {})
    runtime_config = RuntimeConfig.from_args(args)
    register_adapter(runtime_config)
    adapter = get_adapter(runtime_config)
    # We only need the base macros, not macros from dependencies, and don't want
    # to run 'dbt deps' here.
    adapter.load_macro_manifest(base_macros_only=True)
    yield adapter
    adapter.cleanup_connections()
    reset_adapters()


# Start at directory level.
def write_project_files(project_root, dir_name, file_dict):
    path = project_root.mkdir(dir_name)
    if file_dict:
        write_project_files_recursively(path, file_dict)


# Write files out from file_dict. Can be nested directories...
def write_project_files_recursively(path, file_dict):
    if type(file_dict) is not dict:
        raise TestProcessingException(f"Error creating {path}. Did you forget the file extension?")
    for name, value in file_dict.items():
        if name.endswith(".sql") or name.endswith(".csv") or name.endswith(".md"):
            write_file(value, path, name)
        elif name.endswith(".yml") or name.endswith(".yaml"):
            if isinstance(value, str):
                data = value
            else:
                data = yaml.safe_dump(value)
            write_file(data, path, name)
        else:
            write_project_files_recursively(path.mkdir(name), value)


# models, macros, seeds, snapshots, tests, analysis
# Provide a dictionary of file names to contents. Nested directories
# are handle by nested dictionaries.

# models directory
@pytest.fixture(scope="class")
def models():
    return {}


# macros directory
@pytest.fixture(scope="class")
def macros():
    return {}


# seeds directory
@pytest.fixture(scope="class")
def seeds():
    return {}


# snapshots directory
@pytest.fixture(scope="class")
def snapshots():
    return {}


# tests directory
@pytest.fixture(scope="class")
def tests():
    return {}


# analysis directory
@pytest.fixture(scope="class")
def analysis():
    return {}


# Write out the files provided by models, macros, snapshots, seeds, tests, analysis
@pytest.fixture(scope="class")
def project_files(project_root, models, macros, snapshots, seeds, tests, analysis):
    write_project_files(project_root, "models", models)
    write_project_files(project_root, "macros", macros)
    write_project_files(project_root, "snapshots", snapshots)
    write_project_files(project_root, "seeds", seeds)
    write_project_files(project_root, "tests", tests)
    write_project_files(project_root, "analysis", analysis)


# We have a separate logs dir for every test
@pytest.fixture(scope="class")
def logs_dir(request, prefix):
    return os.path.join(request.config.rootdir, "logs", prefix)


# This fixture is for customizing tests that need overrides in adapter
# repos. Example in dbt.tests.adapter.basic.test_base.
@pytest.fixture(scope="class")
def test_config():
    return {}


# This class is returned from the 'project' fixture, and contains information
# from the pytest fixtures that may be needed in the test functions, including
# a 'run_sql' method.
class TestProjInfo:
    def __init__(
        self,
        project_root,
        profiles_dir,
        adapter_type,
        test_dir,
        shared_data_dir,
        test_data_dir,
        test_schema,
        database,
        test_config,
    ):
        self.project_root = project_root
        self.profiles_dir = profiles_dir
        self.adapter_type = adapter_type
        self.test_dir = test_dir
        self.shared_data_dir = shared_data_dir
        self.test_data_dir = test_data_dir
        self.test_schema = test_schema
        self.database = database
        self.test_config = test_config

    @property
    def adapter(self):
        # This returns the last created "adapter" from the adapter factory. Each
        # dbt command will create a new one. This allows us to avoid patching the
        # providers 'get_adapter' function.
        return get_adapter_by_type(self.adapter_type)

    # Run sql from a path
    def run_sql_file(self, sql_path, fetch=None):
        with open(sql_path, "r") as f:
            statements = f.read().split(";")
            for statement in statements:
                self.run_sql(statement, fetch)

    # Run sql from a string, using adapter saved at test startup
    def run_sql(self, sql, fetch=None):
        return run_sql_with_adapter(self.adapter, sql, fetch=fetch)

    # Create the unique test schema. Used in test setup, so that we're
    # ready for initial sql prior to a run_dbt command.
    def create_test_schema(self):
        with get_connection(self.adapter):
            relation = self.adapter.Relation.create(
                database=self.database, schema=self.test_schema
            )
            self.adapter.create_schema(relation)

    # Drop the unique test schema, usually called in test cleanup
    def drop_test_schema(self):
        with get_connection(self.adapter):
            relation = self.adapter.Relation.create(
                database=self.database, schema=self.test_schema
            )
            self.adapter.drop_schema(relation)

    # This return a dictionary of table names to 'view' or 'table' values.
    def get_tables_in_schema(self):
        sql = """
                select table_name,
                        case when table_type = 'BASE TABLE' then 'table'
                             when table_type = 'VIEW' then 'view'
                             else table_type
                        end as materialization
                from information_schema.tables
                where {}
                order by table_name
                """
        sql = sql.format("{} ilike '{}'".format("table_schema", self.test_schema))
        result = self.run_sql(sql, fetch="all")
        return {model_name: materialization for (model_name, materialization) in result}


# This is the main fixture that is used in all functional tests. It pulls in the other
# fixtures that are necessary to set up a dbt project, and saves some of the information
# in a TestProjInfo class, which it returns, so that individual test cases do not have
# to pull in the other fixtures individually to access their information.
@pytest.fixture(scope="class")
def project(
    project_root,
    profiles_root,
    request,
    unique_schema,
    profiles_yml,
    dbt_project_yml,
    packages_yml,
    selectors_yml,
    adapter,
    project_files,
    shared_data_dir,
    test_data_dir,
    logs_dir,
    test_config,
):
    # Logbook warnings are ignored so we don't have to fork logbook to support python 3.10.
    # This _only_ works for tests in `tests/` that use the project fixture.
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="logbook")
    setup_event_logger(logs_dir)
    orig_cwd = os.getcwd()
    os.chdir(project_root)
    # Return whatever is needed later in tests but can only come from fixtures, so we can keep
    # the signatures in the test signature to a minimum.
    project = TestProjInfo(
        project_root=project_root,
        profiles_dir=profiles_root,
        adapter_type=adapter.type(),
        test_dir=request.fspath.dirname,
        shared_data_dir=shared_data_dir,
        test_data_dir=test_data_dir,
        test_schema=unique_schema,
        database=adapter.config.credentials.database,
        test_config=test_config,
    )
    project.drop_test_schema()
    project.create_test_schema()

    yield project

    project.drop_test_schema()
    os.chdir(orig_cwd)
