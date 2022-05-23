"""
`gl_parser_test`
=======================================================================
Unit tests for the parser to pull job contexts from .gitlab-ci.yml files
* Author(s): Bailey Steinfadt
"""
from operator import contains
import pytest

from embedops_cli.yaml_tools import gl_parser, yaml_utilities
from embedops_cli.eo_types import (
    BadYamlFileException,
)
from tests import GLYML_FILENAME

GLYML_MISSING_IMAGE_VALUE_FILENAME = "tests/test-missing-image-value-.gitlab-ci.yml"
GLYML_MISSING_SCRIPT_VALUE_FILENAME = "tests/test-missing-script-value-.gitlab-ci.yml"


def test_get_job_list_with_missing_image_value_exception():
    """test that exception is raised for job with missing image value"""
    with pytest.raises(BadYamlFileException):
        assert gl_parser.get_job_list(GLYML_MISSING_IMAGE_VALUE_FILENAME)


def test_get_job_list_with_missing_script_value_exception():
    """test that exception is raised for job with missing script value"""
    with pytest.raises(BadYamlFileException):
        assert gl_parser.get_job_list(GLYML_MISSING_SCRIPT_VALUE_FILENAME)


def test_get_job_name_list():
    """Test retrieving the list of job names from the YAML"""
    job_name_list = gl_parser.get_job_name_list(GLYML_FILENAME)
    assert len(job_name_list) >= 3
    assert (
        len([job_name for job_name in job_name_list if job_name == "StepScript"]) == 1
    )
    assert (
        len([job_name for job_name in job_name_list if job_name == "StepNoImage"]) == 1
    )
    assert (
        len([job_name for job_name in job_name_list if job_name == "StepNoScript"]) == 1
    )


def test_get_job_list():
    """Test retrieving the list of complete local run context from the YAML"""
    job_list = gl_parser.get_job_list(GLYML_FILENAME)
    assert len(job_list) >= 3
    filtered_job_list = [job for job in job_list if job.job_name == "StepScript"]
    assert len(filtered_job_list) == 1
    assert len(filtered_job_list[0].docker_tag) > 0
    assert len(filtered_job_list[0].script) > 0


def test_get_job_list_default_image():
    """Test retrieving the list of jobs from the YAML,
    check that default image job is as expected"""
    job_list = gl_parser.get_job_list(GLYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepNoImage"][0]
    assert job.job_name == "StepNoImage"
    assert len(job.docker_tag) > 0
    assert len(job.script) > 0


def test_get_job_list_no_script():
    """Test retrieving the list of jobs from the YAML, check that no script job is as expected"""
    job_list = gl_parser.get_job_list(GLYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepNoScript"][0]
    assert job.job_name == "StepNoScript"
    assert len(job.docker_tag) > 0
    assert len(job.script) == 0


def test_get_job_context():
    """Test getting the job context for an indicated job"""
    requested_name = "StepScript"
    job = yaml_utilities.get_job_context_for_name(
        gl_parser, GLYML_FILENAME, requested_name
    )
    assert job.job_name == requested_name


def test_get_job_variables():
    """Test getting variables defined in the job"""
    job_list = gl_parser.get_job_list(GLYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepWithVariable"][0]
    assert "VARYING_THING" in job.variables


def test_get_pipeline_variables():
    """Test getting variables defined outside of job definitions"""
    job_list = gl_parser.get_job_list(GLYML_FILENAME)
    job = [job for job in job_list if job.job_name == "StepWithVariable"][0]
    assert len(job.variables) >= 2
    assert "PROJ_DIR" in job.variables


def test_step_with_literal_multiline_block():
    """Test retrieving a literal multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        gl_parser, GLYML_FILENAME, "StepWithLiteralMultilineBlock"
    )
    assert len(job.script) == 2
    assert job.script[0] == "FILE=.clang-format"
    assert (
        job.script[1]
        == 'if [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi'
    )


def test_step_with_folded_multiline_block():
    """Test retrieving a folded multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        gl_parser, GLYML_FILENAME, "StepWithFoldedMultilineBlock"
    )
    assert len(job.script) == 2
    assert job.script[0] == "FILE=.clang-format"
    assert (
        job.script[1]
        == 'if [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi'
    )


def test_global_var_is_dereferenced():
    """
    Test that when a local variable uses a global one,
    the global var is derefrenced correctly.
    Global:
        PROJ_DIR: "firmware"
    Locals:
        SPECIFIC_DIR: "$PROJ_DIR/spec_dir"
        OTHER_DIR: "${PROJ_DIR}/other_dir"
    """
    job = yaml_utilities.get_job_context_for_name(
        gl_parser, GLYML_FILENAME, "StepWithVariable"
    )
    job_vars = job.variables

    # check the dumb stuff first, everything THERE?
    assert "PROJ_DIR" in job_vars
    assert "SPECIFIC_DIR" in job_vars
    assert "OTHER_DIR" in job_vars

    # Check that the values were dereferenced
    assert job_vars["SPECIFIC_DIR"] == "firmware/spec_dir"
    assert job_vars["OTHER_DIR"] == "firmware/other_dir"
