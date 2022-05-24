"""
job_main
    Defines a function to be used in files that implement code
    to handle message bus events. This function can be used
    to wait for message bus event either by subscribing to the event
    and waiting or by just waiting for the process to be invoked.

    This method looks for the -listen command line argument to know
    which method to use.
"""
import sys
import logging
from .use_message_bus import listen_on_message_bus
from .run_job_using_callback import run_job_using_callback


def job_main(subject, callback, env_variables=None):
    """Wait for events either by listening on the message bus or waiting for Argo to start process"""

    if sys.argv and len(sys.argv) > 1 and sys.argv[1] == '-listen':
        logging.info("Starting service listening on NATS for %s.", subject)
        listen_on_message_bus(subject, callback)
    else:
        env_variables = env_variables if env_variables else []
        logging.info("Running %s workflow for Argo.", subject)
        run_job_using_callback(subject, callback, env_variables)
