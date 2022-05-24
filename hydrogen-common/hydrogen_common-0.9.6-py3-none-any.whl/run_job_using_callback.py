"""
run_job_using_callback

    Define a function to run a job using an async callback function.
    This is intended to support asynchronous jobs such as Argo
    workflow jobs.
"""

import os
import asyncio
import logging
import json


def run_job_using_callback(subject, callback, environment_variables):
    """Run a job using an asynchronous callback methods.
    Pass specified environment variable values as arguments.
    """

    try:
        # Create a NATS message with the environment variable values as data
        class Message:
            """Abstraction for a message used in call to callback."""
            def __init__(self):
                self.subject = None
                self.data = None

        message = Message()
        message.subject = subject
        data = {}
        for var in environment_variables:
            data[var] = os.environ.get(var, None)
        message.data = json.dumps(data).encode()

        # Set the CONTAINER_HYDRO_DATA_PATH env variable to work in DOCKER and locally
        container_hydro_data_path = os.environ.get("CONTAINER_HYDRO_DATA_PATH", None)
        client_hydro_data_path = os.environ.get("CLIENT_HYDRO_DATA_PATH", None)
        if not os.path.exists(container_hydro_data_path) and os.path.exists(
            client_hydro_data_path
        ):
            # This means the job is probably running locally and not within a container
            # So set the CONTAINER_HYDRO_DATA_PATH so the job will read/write to the client_hydro_data_path
            os.environ["CONTAINER_HYDRO_DATA_PATH"] = client_hydro_data_path

        # Invoke the NATS callback method to run the job and send back the reply
        asyncio.run(callback(message))
    except Exception:
        logging.exception(
            "Unable to run_job_subscribe_callback with subject '%s'.",
            subject,
        )
