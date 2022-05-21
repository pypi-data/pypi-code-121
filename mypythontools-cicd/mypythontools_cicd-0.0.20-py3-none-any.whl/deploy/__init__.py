"""
Allow to deploy project.

Possible destinations:

 - PyPi

Check `deploy_to_pypi` function docs for how to use it.

Usually this function is not called manually, but it's a part of `project_utils_pipeline` from cicd. Check it's
docs where it is described, how to use VS Code Task to be able to optionally test, push and deploy with tasks
(one button click).
"""
from mypythontools_cicd.deploy.deploy_internal import deploy_to_pypi

__all__ = ["deploy_to_pypi"]
