import os
import re
import json
import logging
import requests

from alira.instance import Instance
from alira.modules.module import Connection, Module


PIPELINE_SMS_MODULE_NAME = "sms"


class Notification(Connection):
    def __init__(
        self,
        module_id: str,
        filtering: str = None,
        **kwargs,
    ):
        super().__init__(
            module_id=module_id,
            **kwargs,
        )

        self.filtering = self._load_function(filtering)

    def _load_template(self, instance: Instance, template_file):
        with open(
            os.path.join(self.configuration_directory, template_file),
            encoding="UTF-8",
        ) as file:
            template = file.read()

        variables_pattern = re.compile(r"\[\[(.*\]*\[*)\]\]")

        variables = variables_pattern.findall(template)
        for variable in variables:
            value = str(instance.get_attribute(variable, default=""))
            logging.info(f"Replacing variable {variable} with value {value}")
            template = template.replace(f"[[{variable}]]", value)

        logging.info(f"Final template: \n{template}")

        return template


class SocketIO(Module):
    def __init__(
        self,
        pipeline_id: str,
        endpoint: str,
        event: str = "dispatch",
        **kwargs,
    ):
        super().__init__(
            pipeline_id=pipeline_id,
            **kwargs,
        )
        self.endpoint = endpoint
        self.event = event

    def run(self, instance: Instance, **kwargs):
        payload = {
            "message": "pipeline-new-instance",
            "data": instance.__dict__,
            "pipeline_id": self.pipeline_id,
        }

        self.emit(self.event, payload)

        return None

    def emit(self, event: str, payload=None):
        if not self.endpoint:
            return

        logging.info(
            f"Sending Socket IO notification to {self.endpoint}. "
            f"Namespace: {self.pipeline_id}"
        )

        payload["event"] = event
        payload["namespace"] = self.pipeline_id

        try:
            requests.post(
                url=self.endpoint,
                data=json.dumps(payload),
                headers={"Content-type": "application/json"},
            )
        except Exception:
            logging.exception("There was an error sending the socket io notification")
