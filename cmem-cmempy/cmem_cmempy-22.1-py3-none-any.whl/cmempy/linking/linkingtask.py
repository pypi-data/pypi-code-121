"""API methods for working with linking tasks."""
from cmem.cmempy import config
from cmem.cmempy.api import send_request


def get_task_uri():
    """Get endpoint URI pattern for a linking task."""
    return config.get_di_api_endpoint() + "/linking/tasks/{}/{}"


def get_rule_uri():
    """Get endpoint URI pattern for a linking task rule."""
    return config.get_di_api_endpoint() + "/linking/tasks/{}/{}/rule"


def get_linking_task(project_name, task_name):
    """GET retrieve linking task."""
    response = send_request(
        get_task_uri().format(project_name, task_name),
        method="GET"
    )
    return response.decode("utf-8")


# pylint: disable-msg=too-many-arguments
def make_new_linking_task(project_name, task_name, source,
                          target, output, source_type=None, target_type=None,
                          source_restriction=None, target_restriction=None):
    """Create empty linking task."""
    params = {
        "source": source,
        "target": target,
        "sourceType": source_type,
        "targetType": target_type,
        "sourceRestriction": source_restriction,
        "targetRestriction": target_restriction,
        "output": output
    }
    send_request(
        get_task_uri().format(project_name, task_name),
        method="PUT",
        params=params
    )


def delete_linking_task(project_name, task_name):
    """DELETE remove linking task."""
    send_request(get_task_uri().format(project_name, task_name),
                 method="DELETE")


def get_linking_rule(project_name, task_name):
    """
    GET Return linking rule.

    Linking rule format:
    <?xml version="1.0" encoding="UTF-8"?>
    <LinkageRule linkType="&lt;http://www.w3.org/2002/07/owl#sameAs&gt;">
      <Compare id="equality1" required="false" weight="1"
      metric="equality" threshold="0.0" indexing="true">
        <TransformInput id="lowerCase1" function="lowerCase">
          <Input id="sourcePath1" path="/title"/>
        </TransformInput>
        <TransformInput id="lowerCase2" function="lowerCase">
          <Input id="targetPath1" path="/title"/>
        </TransformInput>
      </Compare>
      <Filter/>
    </LinkageRule>
    """
    response = send_request(
        get_rule_uri().format(project_name, task_name),
        method="GET"
    )
    return response.decode("utf-8")


def create_new_linking_rule(project_name, task_name, data):
    """PUT create new linking rule."""
    headers = {"Content-Type": "application/xml"}
    send_request(
        get_rule_uri().format(project_name, task_name),
        method="PUT",
        data=data,
        headers=headers
    )
