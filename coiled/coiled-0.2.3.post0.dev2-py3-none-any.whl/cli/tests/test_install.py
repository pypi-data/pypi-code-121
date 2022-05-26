import shutil
from uuid import uuid4

import pytest
from click.testing import CliRunner
from coiled.cli.install import install

from cloud.models import SoftwareEnvironment
from software_environments.type_defs import CondaSpec

pytestmark = pytest.mark.skipif(
    shutil.which("conda") is None,
    reason="Conda is needed to create local software environments",
)


@pytest.fixture
def senv_with_no_builds(sample_user):
    name = str(uuid4())
    conda_spec = CondaSpec(channels=["conda-forge"], dependencies=["backoff=1.6.0"])

    senv = SoftwareEnvironment.objects.create(
        container="dask/dask",
        conda=conda_spec,
        pip=["toolz"],
        conda_env_name="not-base",
        post_build=["export FOO=BARBAZ", "echo $FOO"],
        content_hash="blah",
        identifier=name,
        name=name,
        account=sample_user.account,
        private=True,
        creator=sample_user.user,
        environment_variables={"MY_TESTING_ENV": "VAR"},
    )
    return senv


def test_install_bad_name_raises(sample_user):
    bad_name = "not-a-software-environment"
    runner = CliRunner()
    result = runner.invoke(install, [bad_name])

    assert result.exit_code != 0
    err_msg = str(result.exception).lower()
    assert "could not find" in err_msg
    assert bad_name in err_msg
