"""Run pipeline if using ``python -m mypythontools_cicd``.

This can be better than console_script when want to ensure that libraries from current venv will be used.
"""

from mypythontools_cicd.project_utils import project_utils_pipeline

if __name__ == "__main__":
    # Function is configured via sys args
    project_utils_pipeline()
