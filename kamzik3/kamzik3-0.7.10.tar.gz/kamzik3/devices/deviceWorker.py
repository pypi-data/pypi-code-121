import json
import logging
from threading import Thread

from kamzik3.devices.deviceClient import DeviceClient

import kamzik3
from kamzik3 import CommandFormatException, DeviceServerError, DeviceError
from kamzik3.constants import *
from kamzik3.snippets.snippetDataAccess import rgetattr
from kamzik3.snippets.snippetsJson import JsonKamzikHook, JsonKamzikEncoder
from kamzik3.snippets.snippetsZmq import Worker


class DeviceWorker(Worker, Thread):
    """
    This is Worker which servers the purpose of dealing with requests on Device.
    Server spawns multiple workers and then executing command from the client on free worker.
    This Worker is executing requests on the Device which is registered in the Session.
    DeviceClient sends request to the Server, then Server delegates this request to the Worker.
    Worker is then formulating response, which is send back to the client.
    """

    def __init__(self, id, master_host, master_port, zmq_context=None):
        """
        Initiate worker.
        Each worker, can respond to specific set of commands.
        Therefore we have to set instruction_set list.
        :param id:
        :param master_host:
        :param master_port:
        :param zmq_context:
        """
        self.logger = logging.getLogger("Console.DeviceWorker@{}".format(id))
        Thread.__init__(self)
        Worker.__init__(self, id, master_host, master_port, zmq_context)
        # Always override instruction set after worker initialization
        self.instructions_set += [
            INSTRUCTION_COMMAND,
            INSTRUCTION_GET,
            INSTRUCTION_SET,
            INSTRUCTION_METHOD,
            INSTRUCTION_POLL,
            INSTRUCTION_INIT,
        ]

    def get_payload(self, request):
        """
        Get input data, process and return result.
        :param list request: input data
        :return list:  [status, token, msg_type, response]
        """
        # Setting default response values
        status, token, response = RESPONSE_ERROR, 0, "Unknown error"

        try:
            instruction, device_id = request[0], request[1].decode()
            device = kamzik3.session.get_device(device_id)

            # Execute command directly on devices
            if instruction == INSTRUCTION_COMMAND:
                command, with_token = request[2].decode(), int(request[3])
                token = device.command(command, with_token=int(with_token))
                status, response = RESPONSE_OK, str(len(request[3]))

            # Get devices attribute
            elif instruction == INSTRUCTION_GET:
                attribute = json.loads(request[2].decode(), object_hook=JsonKamzikHook)
                response = device._get(attribute)
                response = json.dumps(
                    response, cls=JsonKamzikEncoder, ensure_ascii=True
                )
                status, token = RESPONSE_OK, 0

            # Set devices attribute
            elif instruction == INSTRUCTION_SET:
                attribute, attribute_value = json.loads(
                    request[2].decode(), object_hook=JsonKamzikHook
                )
                set_token = device.set_attribute(attribute, attribute_value)
                status, token, response = RESPONSE_OK, set_token, str(len(request[2]))

            # Execute devices method with attributes
            elif instruction == INSTRUCTION_METHOD:
                method, attributes = request[2].decode(), json.loads(
                    request[3].decode(), object_hook=JsonKamzikHook
                )
                response = rgetattr(device, method)(**attributes)
                response = json.dumps(
                    response, cls=JsonKamzikEncoder, ensure_ascii=True
                )
                status, token = RESPONSE_OK, 0

            # Poll devices for activity
            elif instruction == INSTRUCTION_POLL:
                status, token, response = RESPONSE_OK, 0, "1"

            # Init devices
            elif instruction == INSTRUCTION_INIT:
                if device is None or not device.in_statuses(READY_DEVICE_STATUSES):
                    raise DeviceServerError(
                        "Device {} is not registered on the server or publisher is not ready".format(
                            device_id
                        )
                    )
                else:
                    device_proxy = False
                    if isinstance(device, DeviceClient):
                        device_proxy = (device.host, device.port)
                    device_publisher = (
                        kamzik3.session.publisher.host,
                        kamzik3.session.publisher.port,
                    )
                    response = json.dumps(
                        (
                            device.attributes,
                            device.attributes_sharing_map,
                            device.exposed_methods,
                            device.qualified_name,
                            device_proxy,
                            device_publisher,
                        ),
                        cls=JsonKamzikEncoder,
                        ensure_ascii=True,
                    )
                    status, token = RESPONSE_OK, 0
            # None of above, request not implemented
            else:
                status, token, response = RESPONSE_ERROR, 0, str(len(request[3]))

        except CommandFormatException as e:
            status, token, response = RESPONSE_ERROR, 0, "Command format error"
            self.logger.error("Command format error {} {}".format(str(request), e))
        except DeviceServerError as e:
            status, token, response = RESPONSE_ERROR, 0, "Device server error"
            self.logger.error("Device server error {} {}".format(str(request), e))
        except DeviceError as e:
            status, token, response = RESPONSE_ERROR, 0, "Command error: {}".format(e)
            self.logger.error("Command error {} {}".format(str(request), e))
        except (AttributeError, KeyError) as e:
            status, token, response = RESPONSE_ERROR, 0, "Attribute error: {}".format(e)
            self.logger.error("Attribute error {} {}".format(str(request), e))
        except Exception as e:
            status, token, response = RESPONSE_ERROR, 0, "Unknown error: {}".format(e)
            self.logger.error("Unknown error {} {}".format(str(request), e))
        finally:
            # FIXME: Is it an error if an exception gets swallowed?
            return [status.encode(), str(token).encode(), MSG_JSON, response.encode()]
