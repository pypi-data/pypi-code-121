"""
use_message_bus

    Define functions to use the message bus.
    These functions simplify the usage of the message bus.
"""
import os
import asyncio
import logging
import json
import inspect
from .message_bus import MessageBus

# pylint: disable=C0103,W0603
# Variable to allow dependency injection of MessageBus implementation
MessageBusClass = MessageBus


def listen_on_message_bus(subject, callback):
    """Subscribe and listen forever for events with with a subject.

    The callback must be a async function that is called with the message
    as an argument when an incoming message is received.
    """

    try:
        asyncio.run(__event_loop__(subject, callback))
    except Exception:
        pass


async def __event_loop__(subject, callback):
    """Add the subscription to the event bus using the MessageBus class."""

    async with MessageBusClass() as bus:
        sid = None
        try:
            sid = await bus.subscribe(subject, cb=callback)
            logging.info("Subscribed to '%s' events.", subject)
            await bus.wait()
        except Exception:
            logging.exception("Exit wait loop for '%s' because of exception.", subject)
            if sid is not None:
                logging.info("Unsubscribed to subject '%s'.", subject)
                await bus.unsubscribe(sid)


async def execute_with_class_and_reply(class_instance, subject, reply, json_message):
    """
    Execute a method from the class_instance with the json_message as an argument.
    Use the value of the 'op' attribute of the message to find the method name to execute.
    If there is no method with the value of the 'op' attribute execute the method handle_event().

    Publish a reply when finished with the value method result or an error message.
    The subject is specified only to log the subject for which the reply is sent.
    If reply is None, then no reply is published after the completion of the method call.
    """

    try:
        logging.info("Received message subject '%s' %s", subject, json_message)
        container_hydro_data_path = os.environ.get("CONTAINER_HYDRO_DATA_PATH", None)
        client_hydro_data_path = os.environ.get("CLIENT_HYDRO_DATA_PATH", None)
        if container_hydro_data_path is None or (
            not os.path.exists(container_hydro_data_path)
            and os.path.exists(client_hydro_data_path)
        ):
            # This means the job is probably running locally and not within a container
            # So set the CONTAINER_HYDRO_DATA_PATH so the job will read/write to the client_hydro_data_path
            os.environ["CONTAINER_HYDRO_DATA_PATH"] = client_hydro_data_path
        op = json_message.get('op', None)
        if op is not None and hasattr(class_instance, op):
            # Invoke the method with the value of the 'op' attribute
            f = getattr(class_instance, op)
            if inspect.iscoroutinefunction(f):
                response = await f(json_message)
            else:
                response = f(json_message)
        elif hasattr(class_instance, 'handle_event'):
            # Otherwise invoke the handle_event method
            if inspect.iscoroutinefunction(class_instance.handle_event):
                response = await class_instance.handle_event(json_message)
            else:
                response = class_instance.handle_event(json_message)
        elif op:
            raise Exception(
                f"No method '{op}' defined in class '{type(class_instance).__name__}'."
            )
        else:
            raise Exception(
                f"No method handle_event defined in class '{type(class_instance).__name__}'."
            )
        if reply:
            # Publish a message with reply as the subject with the response
            response = {} if response is None else response
            if isinstance(response, dict):
                response['status'] = 'success'
                response['request'] = json_message
                response['subject'] = subject
            logging.info(
                "Reply back with subject '%s' from message subject '%s'.",
                reply, subject
            )
            async with MessageBusClass() as bus:
                await bus.publish(reply, json.dumps(response))
    except Exception as e:
        logging.exception("Exception ocurred while handling message %s.", subject)
        async with MessageBusClass() as bus:
            await bus.publish(reply, json.dumps({'status': 'fail', 'message': str(e)}))


async def execute_with_function_and_reply(callback, subject, reply, json_message):
    """Execute the callback function with the json_message as an argument
    Publish a the response with the reply subject with the function result or an error message.
    """

    try:
        logging.info("Received message subject '%s' %s", subject, json_message)
        container_hydro_data_path = os.environ.get("CONTAINER_HYDRO_DATA_PATH", None)
        client_hydro_data_path = os.environ.get("CLIENT_HYDRO_DATA_PATH", None)
        if not os.path.exists(container_hydro_data_path) and os.path.exists(
            client_hydro_data_path
        ):
            # This means the job is probably running locally and not within a container
            # So set the CONTAINER_HYDRO_DATA_PATH so the job will read/write to the client_hydro_data_path
            os.environ["CONTAINER_HYDRO_DATA_PATH"] = client_hydro_data_path

        if inspect.iscoroutinefunction(callback):
            # this is an async function so call it with await
            response = await callback(json_message)
        else:
            response = callback(json_message)

        if reply:
            response = {} if response is None else response
            if isinstance(response, dict):
                response['status'] = 'success'
                response['request'] = json_message
                response['subject'] = subject
            async with MessageBusClass() as bus:
                await bus.publish(reply, json.dumps(response))
    except Exception as e:
        logging.exception("Exception ocurred while handling message %s.", subject)
        async with MessageBusClass() as bus:
            await bus.publish(reply, json.dumps({'status': 'fail', 'message': str(e)}))


async def send_request_message(message, subject):
    """Publish a synchronous request message and return the replied result."""

    response = None
    try:
        async with MessageBusClass() as bus:
            reply = await bus.request(subject, json.dumps(message))
            response = json.loads(reply)
    except Exception:
        error_message = f"Exception while sending request '{subject}' message to NATS"
        logging.exception(error_message)
        response = {'status': 'fail', 'message': error_message}
    return response


async def send_publish_message(message, subject):
    """Publish an asynchronous message with the subject to message bus."""

    response = None
    try:
        async with MessageBusClass() as bus:
            await bus.publish(subject, json.dumps(message))
            port = os.environ.get("NATS_PORT", None)
            server = os.environ.get("NATS_SERVER", None)
            response = {'message': f"sent '{subject}' subject to NATS {server}:{port}"}
    except Exception:
        error_message = f"Exception while sending '{subject}' message to NATS"
        logging.exception(error_message)
        response = {'status': 'fail', 'message': error_message}
    return response


def set_message_bus_class(c):
    """Set the message bus class to allow dependency injection for unit testing."""
    global MessageBusClass
    MessageBusClass = c
