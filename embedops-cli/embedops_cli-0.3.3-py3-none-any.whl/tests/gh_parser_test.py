"""
`gl_parser_test`
=======================================================================
Unit tests for the parser to pull job contexts from .gitlab-ci.yml files
* Author(s): Bailey Steinfadt
"""
import pytest
from embedops_cli.yaml_tools import gh_parser, yaml_utilities
from embedops_cli.eo_types import BadYamlFileException
from tests import GHYML_FILENAME


GHYML_INVALID_INDENTATION_FILENAME = "tests/test-invalid-indentation-.github-ci.yml"
GHYML_INVALID_JOB_NAME_FILENAME = "tests/test-invalid-job-name-.github-ci.yml"
GHYML_NO_STEPS_FILENAME = "tests/test-no-steps-.github-ci.yml"


def test_get_job_list_with_invalid_indentation_exception():
    """test that exception is raised for job with invalid indentation"""
    with pytest.raises(BadYamlFileException):
        assert gh_parser.get_job_list(GHYML_INVALID_INDENTATION_FILENAME)


def test_get_job_list_with_invalid_name_exception():
    """test that exception is raised for job with invalid name"""
    with pytest.raises(BadYamlFileException):
        assert gh_parser.get_job_list(GHYML_INVALID_JOB_NAME_FILENAME)


def test_get_job_list_without_steps_exception():
    """test that exception is raised for job without steps section"""
    with pytest.raises(BadYamlFileException):
        assert gh_parser.get_job_list(GHYML_NO_STEPS_FILENAME)


def test_get_job_list():
    """Test retrieving the list of complete local run context from the YAML"""
    job_list = gh_parser.get_job_list(GHYML_FILENAME)
    assert len(job_list) >= 3
    filtered_job_list = [
        job for job in job_list if job.job_name == "JobContainsOnlyLetters"
    ]
    assert len(filtered_job_list) == 1
    assert (
        filtered_job_list[0].docker_tag
        == "registry.embedops.com/dojofive/build-images/cppcheck"
    )
    assert filtered_job_list[0].script[0] == 'echo "Job contains only letters"'


def test_get_job_name_list_with_invalid_indentation_exception():
    """test that exception is raised for job with invalid indentation"""
    with pytest.raises(BadYamlFileException):
        assert gh_parser.get_job_name_list(GHYML_INVALID_INDENTATION_FILENAME)


def test_get_job_name_list_with_invalid_name_exception():
    """test that exception is raised for job with invalid name"""
    with pytest.raises(BadYamlFileException):
        assert gh_parser.get_job_name_list(GHYML_INVALID_JOB_NAME_FILENAME)


def test_get_job_name_list():
    """Test retrieving the list of job names from the YAML"""
    job_name_list = gh_parser.get_job_name_list(GHYML_FILENAME)
    assert len(job_name_list) >= 3
    assert (
        len(
            [
                job_name
                for job_name in job_name_list
                if job_name == "JobContainsOnlyLetters"
            ]
        )
        == 1
    )
    assert (
        len(
            [
                job_name
                for job_name in job_name_list
                if job_name == "_Job_Starts_With_Underscore"
            ]
        )
        == 1
    )
    assert (
        len(
            [
                job_name
                for job_name in job_name_list
                if job_name == "Job-Separated-By-Dash"
            ]
        )
        == 1
    )


def test_get_job_context():
    """Test getting the job context for an indicated job"""
    requested_name = "Job_Contains-A1123Valid-Characters"
    job = yaml_utilities.get_job_context_for_name(
        gh_parser, GHYML_FILENAME, requested_name
    )
    assert job.job_name == requested_name


def test_get_pipeline_variables():
    """Test getting variables defined outside of job definitions"""
    job_list = gh_parser.get_job_list(GHYML_FILENAME)
    job = [job for job in job_list if job.job_name == "Job1Contains2Numbers34567890"][0]
    # The job only has access to the PROJ_DIR variable
    assert "PROJ_DIR" in job.variables
    assert "MY_VAR" not in job.variables
    assert "MY_SUB_VAR" not in job.variables


def test_get_job_variables():
    """Test getting variables defined in a job"""
    job_list = gh_parser.get_job_list(GHYML_FILENAME)
    job = [job for job in job_list if job.job_name == "JobWithEnvVariable"][0]
    # The job only has access to the PROJ_DIR and MY_VAR variables
    assert "PROJ_DIR" in job.variables
    assert "MY_VAR" in job.variables
    assert "MY_SUB_VAR" not in job.variables


def test_get_step_variables():
    """Test getting variables defined in a step"""
    job_list = gh_parser.get_job_list(GHYML_FILENAME)
    job = [job for job in job_list if job.job_name == "JobWithStepLevelEnvVariable"][0]
    # The job only has access to the PROJ_DIR and MY_SUB_VAR variables
    assert "PROJ_DIR" in job.variables
    assert "MY_VAR" not in job.variables
    assert "MY_SUB_VAR" in job.variables


def test_job_with_run_in_sub_step():
    """Test getting run command defined in a sub-step"""
    job_list = gh_parser.get_job_list(GHYML_FILENAME)
    job = [job for job in job_list if job.job_name == "JobWithRunInSubstep"][0]
    assert job.script[0] == 'echo "Job with run in sub-step"'


def test_job_with_literal_multiline_block():
    """Test retrieving a literal multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        gh_parser, GHYML_FILENAME, "JobWithLiteralMultilineBlock"
    )
    assert (
        job.script[0]
        == 'FILE=.clang-format\nif [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi\n'
    )


def test_step_with_folded_multiline_block():
    """Test retrieving a folded multiline block"""
    job = yaml_utilities.get_job_context_for_name(
        gh_parser, GHYML_FILENAME, "JobWithFoldedMultilineBlock"
    )
    assert (
        job.script[0]
        == 'FILE=.clang-format\nif [ -f "$FILE" ]; then echo "$FILE exists. Use repository $FILE."; else echo "$FILE does not exist. Use container $FILE."; cp /tools/.clang-format .clang-format; fi\n'
    )
