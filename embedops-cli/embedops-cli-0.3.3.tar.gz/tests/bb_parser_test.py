"""
`bb_parser_test`
=======================================================================
Unit tests for the parser to pull job contexts from bitbucket-pipelines.yml files
* Author(s): Bailey Steinfadt
"""
import pytest

from embedops_cli.yaml_tools import bb_parser, yaml_utilities
from embedops_cli.eo_types import (
    BadYamlFileException,
)
from tests import BBYML_FILENAME

BBYML_UNNAMED_STEP_FILENAME = "tests/test-unnamed-step-bitbucket-pipelines.yml"
BBYML_MISSING_STEP_NAME_VALUE_FILENAME = (
    "tests/test-missing-step-name-value-bitbucket-pipelines.yml"
)
BBYML_MISSING_IMAGE_NAME_VALUE_FILENAME = (
    "tests/test-missing-image-name-value-bitbucket-pipelines.yml"
)
BBYML_MISSING_SCRIPT_VALUE_FILENAME = (
    "tests/test-missing-script-value-bitbucket-pipelines.yml"
)


def test_get_job_list_with_unnamed_step_exception():
    """test that exception is raised for job with unnamed step"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_list(BBYML_UNNAMED_STEP_FILENAME)


def test_get_job_name_list_with_unnamed_step_exception():
    """test that exception is raised for job with unnamed step"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_name_list(BBYML_UNNAMED_STEP_FILENAME)


def test_get_job_list_with_missing_step_name_value_exception():
    """test that exception is raised for job with missing step name value"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_list(BBYML_MISSING_STEP_NAME_VALUE_FILENAME)


def test_get_job_name_list_with_missing_step_name_value_exception():
    """test that exception is raised for job with missing step name value"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_name_list(BBYML_MISSING_STEP_NAME_VALUE_FILENAME)


def test_get_job_list_with_missing_image_name_value_exception():
    """test that exception is raised for job with missing image name value"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_list(BBYML_MISSING_IMAGE_NAME_VALUE_FILENAME)


def test_get_job_list_with_missing_script_value_exception():
    """test that exception is raised for job with missing script value"""
    with pytest.raises(BadYamlFileException):
        assert bb_parser.get_job_list(BBYML_MISSING_SCRIPT_VALUE_FILENAME)


def test_get_job_name_list():
    """Test retrieving the list of job names from the YAML"""
    job_name_list = bb_parser.get_job_name_list(BBYML_FILENAME)
    assert len(job_name_list) == 13
    assert job_name_list[0] == "StepScript"
    assert job_name_list[5] == "ParallelNoImage"


def test_get_job_list():
    """Test retrieving the list of complete local run context from the YAML"""
    job_list = bb_parser.get_job_list(BBYML_FILENAME)
    assert len(job_list) == 13
    assert job_list[0].job_name == "StepScript"
    assert len(job_list[0].docker_tag) > 0
    assert len(job_list[0].script) > 0
    assert job_list[5].job_name == "ParallelNoImage"
    assert len(job_list[5].docker_tag) == 0
    assert len(job_list[5].script) > 0


def test_get_job_list_default_image():
    """Test retrieving the list of complete local run context from the YAML
    where the step uses the default image"""
    job_list = bb_parser.get_job_list(BBYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepNoImage"][0]
    assert job.job_name == "StepNoImage"
    assert len(job.docker_tag) > 0
    assert len(job.script) > 0


def test_get_job_list_no_script():
    """Test retrieving the list of complete local run context from the YAML
    when the step has no script"""
    job_list = bb_parser.get_job_list(BBYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepNoScript"][0]
    assert job.job_name == "StepNoScript"
    assert len(job.docker_tag) > 0
    assert len(job.script) == 0


def test_get_job_context():
    """Test getting the job context for an indicated job"""
    requested_name = "StepScript"
    job = yaml_utilities.get_job_context_for_name(
        bb_parser, BBYML_FILENAME, requested_name
    )
    assert job.job_name == requested_name

    requested_name_parallel = "ParallelScript"
    job = yaml_utilities.get_job_context_for_name(
        bb_parser, BBYML_FILENAME, requested_name_parallel
    )
    assert job.job_name == requested_name_parallel


def test_step_with_literal_multiline_block():
    """Test retrieving a literal multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        bb_parser, BBYML_FILENAME, "StepWithLiteralMultilineBlock"
    )
    assert (
        job.script[0]
        == 'FILE=.clang-format\nif [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi\n'
    )


def test_step_with_folded_multiline_block():
    """Test retrieving a folded multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        bb_parser, BBYML_FILENAME, "StepWithFoldedMultilineBlock"
    )
    assert (
        job.script[0]
        == 'FILE=.clang-format\nif [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi\n'
    )
