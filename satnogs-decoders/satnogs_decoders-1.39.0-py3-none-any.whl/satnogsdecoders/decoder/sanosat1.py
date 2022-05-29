# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sanosat1(KaitaiStruct):
    """:field delimiter: sanosat1_telemetry.delimiter
    :field callsign: sanosat1_telemetry.callsign
    :field packet_type: sanosat1_telemetry.packet_type
    :field com_temperature: sanosat1_telemetry.com_temperature
    :field battery_voltage: sanosat1_telemetry.battery_voltage
    :field charging_current: sanosat1_telemetry.charging_current
    :field battery_temperature: sanosat1_telemetry.battery_temperature
    :field radiation_level: sanosat1_telemetry.radiation_level
    :field no_of_resets: sanosat1_telemetry.no_of_resets
    :field antenna_deployment_status: sanosat1_telemetry.antenna_deployment_status
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.sanosat1_telemetry = Sanosat1.Sanosat1TelemetryT(self._io, self, self._root)

    class Sanosat1TelemetryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.delimiter = self._io.read_s4le()
            if not  ((self.delimiter == 65535)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.delimiter, self._io, u"/types/sanosat1_telemetry_t/seq/0")
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(7), 0, False)).decode(u"ASCII")
            if not  ((self.callsign == u"AM9NPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/sanosat1_telemetry_t/seq/1")
            self.packet_type = self._io.read_s2le()
            self.com_temperature = self._io.read_s2le()
            self.battery_voltage = self._io.read_s2le()
            self.charging_current = self._io.read_s2le()
            self.battery_temperature = self._io.read_s2le()
            self.radiation_level = self._io.read_s2le()
            self.no_of_resets = self._io.read_s2le()
            self.antenna_deployment_status = self._io.read_u1()



