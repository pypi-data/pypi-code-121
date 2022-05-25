import struct

from Open_LISA_SDK.logging import log
from ..exceptions.sdk_exception import OpenLISAException
from ..exceptions.invalid_command import InvalidCommandException

FORMAT_STRING = "str"
FORMAT_DOUBLE = "double"
FORMAT_BYTEARRAY = "bytearray"
FORMAT_BYTES = "bytes"
FORMAT_INT32 = "int"

AVAILABLE_RESPONSE_FORMATS_FOR_BYTEARRAY = [FORMAT_BYTEARRAY, FORMAT_BYTES]
AVAILABLE_RESPONSE_FORMATS_FOR_STRING = [FORMAT_STRING, FORMAT_DOUBLE, FORMAT_INT32]


class Instrument:
  def __init__(self, id, description, brand, model, status, client_protocol, default_string_response_conversion, default_bytearray_response_conversion) -> None:
      self.ID = id
      self.description = description
      self.brand = brand
      self.model = model
      self.status = status
      self._client_protocol = client_protocol
      self._default_string_response_conversion = default_string_response_conversion
      self._default_bytearray_response_conversion = default_bytearray_response_conversion


  def __repr__(self) -> str:
      return 'ID: {}, Description: {}, Brand: {}, Model: {}, Status: {}'.format(self.ID, self.description, self.brand, self.model, self.status)

  def set_default_string_response_conversion(self, v):
    self._default_string_response_conversion = v

  def set_default_bytearray_response_conversion(self, v):
    self._default_bytearray_response_conversion = v

  @staticmethod
  def from_dict(d, client_protocol, def_str, def_bytearr):
    mandatory_keys = ['id', 'description', 'brand', 'model', 'status']
    if all(key in d for key in mandatory_keys):
      return Instrument(id=d['id'], description=d['description'], brand=d['brand'], model=d['model'], status=d['status'], client_protocol=client_protocol, default_string_response_conversion=def_str, default_bytearray_response_conversion=def_bytearr)
    else:
      raise OpenLISAException("missing mandatory keys ({}) in dict {}".format(mandatory_keys, d))

  def available_commands(self):
    # todo: quizas parsear el JSON aca
    return self._client_protocol.get_instrument_commands(self.ID)

  def validate_command(self, command):
    try:
      self._client_protocol.validate_command(self.ID, command)
      print("{} is OK".format(command))
    except InvalidCommandException as e:
      print(e)

  def format_string_response(self, response, format):
    try:
      if format == FORMAT_STRING:
        return response.decode()
      if format == FORMAT_INT32:
        return int(float(response.decode()))
      if format == FORMAT_DOUBLE:
        return float(response.decode())
    except ValueError as e:
      error = "could not convert '{}' to type '{}'.".format(response, format)
      log.error(error)
      raise InvalidCommandException(error)
    except Exception as e:
      log.error(e.message)
      raise InvalidCommandException(e.message)

  def format_bytearray_response(self, response, format):
    try:
      if format == FORMAT_BYTEARRAY:
        return bytearray(response)
      elif format == FORMAT_BYTES:
        return bytes(response)
    except ValueError as e:
      error = "could not convert bytearray response to type '{}'.".format(format)
      log.error(error)
      raise InvalidCommandException(error)
    except Exception as e:
      log.error(e.message)
      raise InvalidCommandException(e.message)

  def send(self, command, convert_to=None):
    format, response = self._client_protocol.send_command(self.ID, command)
    if format == FORMAT_STRING:
      if convert_to:
        if convert_to not in AVAILABLE_RESPONSE_FORMATS_FOR_STRING:
          error = "command '{}' ask for invalid response format type '{}'. Available formats are {}".format(command, format, AVAILABLE_RESPONSE_FORMATS_FOR_BYTEARRAY)
          log.error(error)
          raise InvalidCommandException(error)
        else:
          return self.format_string_response(response, convert_to)
      else:
        return self.format_string_response(response, self._default_string_response_conversion)
    if format == FORMAT_BYTES:
      if convert_to:
        if convert_to not in AVAILABLE_RESPONSE_FORMATS_FOR_BYTEARRAY:
          error = "command '{}' ask for invalid response format type '{}'. Available formats are {}".format(command, format, AVAILABLE_RESPONSE_FORMATS_FOR_BYTEARRAY)
          log.error(error)
          raise InvalidCommandException(error)
        else:
          return self.format_bytearray_response(response, convert_to)
      else:
        return self.format_bytearray_response(response, self._default_bytearray_response_conversion)
