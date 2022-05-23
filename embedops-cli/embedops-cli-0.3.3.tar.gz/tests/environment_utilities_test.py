"""
`environment_utilities_test`
=======================================================================
Unit tests for the module that manages environment context for the CLI
* Author(s): Bailey Steinfadt
"""
import os
from embedops_cli import environment_utilities as envutil


def test_create_and_delete_job_env_file():
    """
    Test that a file is made with no errors.
    And that it's gone after deletion.
    """
    # create file
    testdict = {"key": "value"}
    envutil.create_job_env_file(testdict)

    assert os.path.exists(envutil.JOB_ENV_FILE)

    # Check the file contains what we think
    contents = ""
    with open(envutil.JOB_ENV_FILE, encoding="utf-8") as env_file:
        contents = env_file.read()
    assert "key=value" in contents

    # delete file
    envutil.delete_job_env_file()

    assert os.path.exists(envutil.JOB_ENV_FILE) is False


def test_clean_env_file():
    """
    Test that the scrubbing fuction works
    to put data into an env file for dockr use
    """

    dirty_env_contents = [
        "# Comments that should not be copied   \n",
        '# COMMENTED_ENV_VAR="should not be copied"\n',
        "ENV_NO_QUOTES=unchanged\n",
        'ENV_WITH_QUOTES="now_no_quotes"\n',
        "\n",  # Empty line
        "ENV_WITH_SINGLE_QUOTES='now_no_quotes'\n",
    ]

    clean_env_contents = envutil._clean_env_file(dirty_env_contents)

    # Check that the "bad" lines got removed
    assert len(clean_env_contents) == 3
    assert dirty_env_contents[0] not in clean_env_contents
    assert dirty_env_contents[1] not in clean_env_contents
    assert dirty_env_contents[4] not in clean_env_contents

    # check that the good lines were unchanged or just had two chars removed
    assert dirty_env_contents[2] in clean_env_contents
    assert len(dirty_env_contents[3]) - 2 == len(clean_env_contents[1])
    assert len(dirty_env_contents[5]) - 2 == len(clean_env_contents[2])
