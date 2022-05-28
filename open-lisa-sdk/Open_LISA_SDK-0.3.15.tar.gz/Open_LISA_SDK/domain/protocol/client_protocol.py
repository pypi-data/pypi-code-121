import json
from time import time
from ..exceptions.sdk_exception import OpenLISAException
from ..exceptions.invalid_command import InvalidCommandException
from ...logging import log

SUCCESS_RESPONSE = "OK"
ERROR_RESPONSE = "ERROR"

COMMAND_DISCONNECT = "DISCONNECT"
COMMAND_GET_INSTRUMENTS = "GET_INSTRUMENTS"
COMMAND_GET_INSTRUMENT = "GET_INSTRUMENT"
COMMAND_GET_INSTRUMENT_COMMANDS = "GET_INSTRUMENT_COMMANDS"
COMMAND_VALIDATE_COMMAND = "VALIDATE_COMMAND"
COMMAND_SEND_COMMAND = "SEND_COMMAND"

class ClientProtocol:
  def __init__(self, message_protocol):
    self._message_protocol = message_protocol

  def __is_valid_response(self, response):
    if response == SUCCESS_RESPONSE:
      return True
    if response == ERROR_RESPONSE:
      return False

    raise Exception("unknown response type: '{}'".format(response))

  def disconnect(self):
    log.debug("[LATENCY_MEASURE][INIT][{}]".format('disconnect'))
    ts = time()
    self._message_protocol.send_msg(COMMAND_GET_INSTRUMENTS)
    te = time()
    log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('disconnect', te-ts))
    return

  def get_instruments(self):
    log.debug("[LATENCY_MEASURE][INIT][{}]".format('get_instruments'))
    ts = time()
    self._message_protocol.send_msg(COMMAND_GET_INSTRUMENTS)
    result = self._message_protocol.receive_msg()
    te = time()
    log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('get_instruments', te-ts))
    return json.loads(result)

  def get_instrument(self, id):
    log.debug("[LATENCY_MEASURE][INIT][{}]".format('get_instrument'))
    ts = time()
    self._message_protocol.send_msg(COMMAND_GET_INSTRUMENT)
    self._message_protocol.send_msg(id)
    response_type = self._message_protocol.receive_msg()
    result_msg = self._message_protocol.receive_msg()
    te = time()
    log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('get_instrument', te-ts))
    if self.__is_valid_response(response_type):
      return json.loads(result_msg)
    else:
      raise OpenLISAException(result_msg)

  def get_instrument_commands(self, id):
    log.debug("[LATENCY_MEASURE][INIT][{}]".format('get_instrument_commands'))
    ts = time()
    self._message_protocol.send_msg(COMMAND_GET_INSTRUMENT_COMMANDS)
    self._message_protocol.send_msg(id)
    response_type = self._message_protocol.receive_msg()
    result_msg = self._message_protocol.receive_msg()
    te = time()
    log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('get_instrument_commands', te-ts))
    if self.__is_valid_response(response_type):
      return json.loads(result_msg)
    else:
      raise OpenLISAException(result_msg)

  def validate_command(self, id, command):
    log.debug("[LATENCY_MEASURE][INIT][{}]".format('validate_command'))
    ts = time()
    self._message_protocol.send_msg(COMMAND_VALIDATE_COMMAND)
    self._message_protocol.send_msg(id)
    self._message_protocol.send_msg(command)
    response_type = self._message_protocol.receive_msg()
    if not self.__is_valid_response(response_type):
      err = self._message_protocol.receive_msg()
      te = time()
      log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('validate_command', te-ts))
      raise InvalidCommandException("command '{}' is not valid: {}".format(command, err))

    te = time()
    log.debug("[LATENCY_MEASURE][FINISH][{}][ELAPSED={} seconds]".format('validate_command', te-ts))

  def send_command(self, id, command):
    log.debug("[LATENCY_MEASURE][INIT][{}][command={}]".format('send_command', command))
    ts = time()
    self._message_protocol.send_msg(COMMAND_SEND_COMMAND)
    self._message_protocol.send_msg(id)
    self._message_protocol.send_msg(command)
    response_type = self._message_protocol.receive_msg()
    if self.__is_valid_response(response_type):
      format = self._message_protocol.receive_msg()
      response = self._message_protocol.receive_msg(decode=False)
      te = time()
      log.debug("[LATENCY_MEASURE][FINISH][{}][command={}][ELAPSED={} seconds]".format('send_command', command, te-ts))
      return format, response
    else:
      err = self._message_protocol.receive_msg()
      te = time()
      log.debug("[LATENCY_MEASURE][FINISH][{}][command={}][ELAPSED={} seconds]".format('send_command', command, te-ts))
      raise InvalidCommandException("command '{}' for instrument {} is not valid: {}".format(command, id, err))
