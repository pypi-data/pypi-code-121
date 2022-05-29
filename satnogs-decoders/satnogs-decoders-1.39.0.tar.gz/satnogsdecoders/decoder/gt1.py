# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Gt1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field packet_type: ax25_frame.payload.data_payload.packet_type
    :field sys_time1: ax25_frame.payload.data_payload.data_payload.sys_time1
    :field switch_status: ax25_frame.payload.data_payload.data_payload.switch_status
    :field currentstate: ax25_frame.payload.data_payload.data_payload.currentstate
    :field startingstate: ax25_frame.payload.data_payload.data_payload.startingstate
    :field kissnuminvaliddownlinks: ax25_frame.payload.data_payload.data_payload.kissnuminvaliddownlinks
    :field kissnuminvaliduplinks: ax25_frame.payload.data_payload.data_payload.kissnuminvaliduplinks
    :field commandsdispatched: ax25_frame.payload.data_payload.data_payload.commandsdispatched
    :field commanderrors: ax25_frame.payload.data_payload.data_payload.commanderrors
    :field raw_value_atmega: ax25_frame.payload.data_payload.data_payload.raw_value_atmega
    :field raw_value_sp1: ax25_frame.payload.data_payload.data_payload.raw_value_sp1
    :field raw_value_sp2: ax25_frame.payload.data_payload.data_payload.raw_value_sp2
    :field raw_value_sp3: ax25_frame.payload.data_payload.data_payload.raw_value_sp3
    :field raw_value_sp4: ax25_frame.payload.data_payload.data_payload.raw_value_sp4
    :field time_remaining_0: ax25_frame.payload.data_payload.data_payload.time_remaining_0
    :field time_remaining_1: ax25_frame.payload.data_payload.data_payload.time_remaining_1
    :field timer_length_0: ax25_frame.payload.data_payload.data_payload.timer_length_0
    :field timer_length_1: ax25_frame.payload.data_payload.data_payload.timer_length_1
    :field atmegarobot_interactions: ax25_frame.payload.data_payload.data_payload.atmegarobot_interactions
    :field beacon_interval: ax25_frame.payload.data_payload.data_payload.beacon_interval
    :field beacon_separation: ax25_frame.payload.data_payload.data_payload.beacon_separation
    :field burn_wire_duration: ax25_frame.payload.data_payload.data_payload.burn_wire_duration
    :field burn_wire_attempts: ax25_frame.payload.data_payload.data_payload.burn_wire_attempts
    :field timer_length: ax25_frame.payload.data_payload.data_payload.timer_length
    :field magfield_x: ax25_frame.payload.data_payload.data_payload.magfield_x
    :field magfield_y: ax25_frame.payload.data_payload.data_payload.magfield_y
    :field magfield_z: ax25_frame.payload.data_payload.data_payload.magfield_z
    :field scale_factor: ax25_frame.payload.data_payload.data_payload.scale_factor
    :field reference_voltage: ax25_frame.payload.data_payload.data_payload.reference_voltage
    :field rgmaxtime_1hz: ax25_frame.payload.data_payload.data_payload.rgmaxtime_1hz
    :field rgcycleslips_1hz: ax25_frame.payload.data_payload.data_payload.rgcycleslips_1hz
    :field rgmaxtime_2hz: ax25_frame.payload.data_payload.data_payload.rgmaxtime_2hz
    :field rgcycleslips_2hz: ax25_frame.payload.data_payload.data_payload.rgcycleslips_2hz
    :field rgmaxtime_10hz: ax25_frame.payload.data_payload.data_payload.rgmaxtime_10hz
    :field rgcycleslips_10hz: ax25_frame.payload.data_payload.data_payload.rgcycleslips_10hz
    :field uart0_bytes_sent: ax25_frame.payload.data_payload.data_payload.uart0_bytes_sent
    :field uart0_bytes_recv: ax25_frame.payload.data_payload.data_payload.uart0_bytes_recv
    :field shiftregdata: ax25_frame.payload.data_payload.data_payload.shiftregdata
    :field eps_i2c_errors: ax25_frame.payload.data_payload.data_payload.eps_i2c_errors
    :field eps_vbatt_critical: ax25_frame.payload.data_payload.data_payload.eps_vbatt_critical
    :field config2_batt_maxvoltage: ax25_frame.payload.data_payload.data_payload.config2_batt_maxvoltage
    :field config2_batt_safevoltage: ax25_frame.payload.data_payload.data_payload.config2_batt_safevoltage
    :field config2_batt_criticalvoltage: ax25_frame.payload.data_payload.data_payload.config2_batt_criticalvoltage
    :field config2_batt_normalvoltage: ax25_frame.payload.data_payload.data_payload.config2_batt_normalvoltage
    :field sys_time2: ax25_frame.payload.data_payload.data_payload.sys_time2
    :field hk1_vboost1: ax25_frame.payload.data_payload.data_payload.hk1_vboost1
    :field hk1_vboost2: ax25_frame.payload.data_payload.data_payload.hk1_vboost2
    :field hk1_vboost3: ax25_frame.payload.data_payload.data_payload.hk1_vboost3
    :field hk1_vbatt: ax25_frame.payload.data_payload.data_payload.hk1_vbatt
    :field hk1_vcurin1: ax25_frame.payload.data_payload.data_payload.hk1_vcurin1
    :field hk1_vcurin2: ax25_frame.payload.data_payload.data_payload.hk1_vcurin2
    :field hk1_vcurin3: ax25_frame.payload.data_payload.data_payload.hk1_vcurin3
    :field hk1_vcursun: ax25_frame.payload.data_payload.data_payload.hk1_vcursun
    :field hk1_vcursys: ax25_frame.payload.data_payload.data_payload.hk1_vcursys
    :field hk1_vcurout1: ax25_frame.payload.data_payload.data_payload.hk1_vcurout1
    :field hk1_vcurout2: ax25_frame.payload.data_payload.data_payload.hk1_vcurout2
    :field hk1_vcurout3: ax25_frame.payload.data_payload.data_payload.hk1_vcurout3
    :field hk1_vcurout4: ax25_frame.payload.data_payload.data_payload.hk1_vcurout4
    :field hk1_vcurout5: ax25_frame.payload.data_payload.data_payload.hk1_vcurout5
    :field hk1_vcurout6: ax25_frame.payload.data_payload.data_payload.hk1_vcurout6
    :field hk1_output1: ax25_frame.payload.data_payload.data_payload.hk1_output1
    :field hk1_output2: ax25_frame.payload.data_payload.data_payload.hk1_output2
    :field hk1_output3: ax25_frame.payload.data_payload.data_payload.hk1_output3
    :field hk1_output4: ax25_frame.payload.data_payload.data_payload.hk1_output4
    :field hk1_output5: ax25_frame.payload.data_payload.data_payload.hk1_output5
    :field hk1_output6: ax25_frame.payload.data_payload.data_payload.hk1_output6
    :field hk1_output7: ax25_frame.payload.data_payload.data_payload.hk1_output7
    :field hk1_output8: ax25_frame.payload.data_payload.data_payload.hk1_output8
    :field hk1_latchup1: ax25_frame.payload.data_payload.data_payload.hk1_latchup1
    :field hk1_latchup2: ax25_frame.payload.data_payload.data_payload.hk1_latchup2
    :field hk1_latchup3: ax25_frame.payload.data_payload.data_payload.hk1_latchup3
    :field hk1_latchup4: ax25_frame.payload.data_payload.data_payload.hk1_latchup4
    :field hk1_latchup5: ax25_frame.payload.data_payload.data_payload.hk1_latchup5
    :field hk1_latchup6: ax25_frame.payload.data_payload.data_payload.hk1_latchup6
    :field hk1_wdt_i2c_time_left: ax25_frame.payload.data_payload.data_payload.hk1_wdt_i2c_time_left
    :field hk1_wdt_gnd_time_left: ax25_frame.payload.data_payload.data_payload.hk1_wdt_gnd_time_left
    :field hk1_counter_wdt_i2c: ax25_frame.payload.data_payload.data_payload.hk1_counter_wdt_i2c
    :field hk1_counter_wdt_gnd: ax25_frame.payload.data_payload.data_payload.hk1_counter_wdt_gnd
    :field hk1_counter_boot: ax25_frame.payload.data_payload.data_payload.hk1_counter_boot
    :field hk1_temp1: ax25_frame.payload.data_payload.data_payload.hk1_temp1
    :field hk1_temp2: ax25_frame.payload.data_payload.data_payload.hk1_temp2
    :field hk1_temp3: ax25_frame.payload.data_payload.data_payload.hk1_temp3
    :field hk1_temp4: ax25_frame.payload.data_payload.data_payload.hk1_temp4
    :field hk1_temp5: ax25_frame.payload.data_payload.data_payload.hk1_temp5
    :field hk1_temp6: ax25_frame.payload.data_payload.data_payload.hk1_temp6
    :field hk1_bootcause: ax25_frame.payload.data_payload.data_payload.hk1_bootcause
    :field hk1_battmode: ax25_frame.payload.data_payload.data_payload.hk1_battmode
    :field hk1_pptmode: ax25_frame.payload.data_payload.data_payload.hk1_pptmode
    :field hk1_config1_ppt_mode: ax25_frame.payload.data_payload.data_payload.hk1_config1_ppt_mode
    :field hk1_config1_battheater_mode: ax25_frame.payload.data_payload.data_payload.hk1_config1_battheater_mode
    :field hk1_config1_battheater_low: ax25_frame.payload.data_payload.data_payload.hk1_config1_battheater_low
    :field hk1_config1_battheater_high: ax25_frame.payload.data_payload.data_payload.hk1_config1_battheater_high
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Gt1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Gt1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Gt1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Gt1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Gt1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Gt1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Gt1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Gt1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Gt1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Gt1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Gt1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Gt1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.data_payload = Gt1.Gt1Payload(self._io, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"KK4UVG") or (self.callsign == u"KN4ZNS") or (self.callsign == u"W4AQL ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class SsidMask(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ssid_mask = self._io.read_u1()

        @property
        def ssid(self):
            if hasattr(self, '_m_ssid'):
                return self._m_ssid if hasattr(self, '_m_ssid') else None

            self._m_ssid = ((self.ssid_mask & 15) >> 1)
            return self._m_ssid if hasattr(self, '_m_ssid') else None


    class Gt1payload2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sys_time2 = self._io.read_u4le()
            self.hk1_vboost1 = self._io.read_u2le()
            self.hk1_vboost2 = self._io.read_u2le()
            self.hk1_vboost3 = self._io.read_u2le()
            self.hk1_vbatt = self._io.read_u2le()
            self.hk1_vcurin1 = self._io.read_u2le()
            self.hk1_vcurin2 = self._io.read_u2le()
            self.hk1_vcurin3 = self._io.read_u2le()
            self.hk1_vcursun = self._io.read_u2le()
            self.hk1_vcursys = self._io.read_u2le()
            self.hk1_vcurout1 = self._io.read_u2le()
            self.hk1_vcurout2 = self._io.read_u2le()
            self.hk1_vcurout3 = self._io.read_u2le()
            self.hk1_vcurout4 = self._io.read_u2le()
            self.hk1_vcurout5 = self._io.read_u2le()
            self.hk1_vcurout6 = self._io.read_u2le()
            self.hk1_output1 = self._io.read_u1()
            self.hk1_output2 = self._io.read_u1()
            self.hk1_output3 = self._io.read_u1()
            self.hk1_output4 = self._io.read_u1()
            self.hk1_output5 = self._io.read_u1()
            self.hk1_output6 = self._io.read_u1()
            self.hk1_output7 = self._io.read_u1()
            self.hk1_output8 = self._io.read_u1()
            self.hk1_latchup1 = self._io.read_u2le()
            self.hk1_latchup2 = self._io.read_u2le()
            self.hk1_latchup3 = self._io.read_u2le()
            self.hk1_latchup4 = self._io.read_u2le()
            self.hk1_latchup5 = self._io.read_u2le()
            self.hk1_latchup6 = self._io.read_u2le()
            self.hk1_wdt_i2c_time_left = self._io.read_u4le()
            self.hk1_wdt_gnd_time_left = self._io.read_u4le()
            self.hk1_counter_wdt_i2c = self._io.read_u4le()
            self.hk1_counter_wdt_gnd = self._io.read_u4le()
            self.hk1_counter_boot = self._io.read_u4le()
            self.hk1_temp1 = self._io.read_s2le()
            self.hk1_temp2 = self._io.read_s2le()
            self.hk1_temp3 = self._io.read_s2le()
            self.hk1_temp4 = self._io.read_s2le()
            self.hk1_temp5 = self._io.read_s2le()
            self.hk1_temp6 = self._io.read_s2le()
            self.hk1_bootcause = self._io.read_u1()
            self.hk1_battmode = self._io.read_u1()
            self.hk1_pptmode = self._io.read_u1()
            self.hk1_config1_ppt_mode = self._io.read_u1()
            self.hk1_config1_battheater_mode = self._io.read_u1()
            self.hk1_config1_battheater_low = self._io.read_s1()
            self.hk1_config1_battheater_high = self._io.read_s1()


    class CallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_callsign_ror = self._io.read_bytes(6)
            self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
            _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
            self.callsign_ror = Gt1.Callsign(_io__raw_callsign_ror, self, self._root)


    class Gt1payload1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sys_time1 = self._io.read_u4le()
            self.switch_status = self._io.read_u1()
            self.currentstate = self._io.read_u4le()
            self.startingstate = self._io.read_u4le()
            self.kissnuminvaliddownlinks = self._io.read_u4le()
            self.kissnuminvaliduplinks = self._io.read_u4le()
            self.commandsdispatched = self._io.read_u4le()
            self.commanderrors = self._io.read_u4le()
            self.raw_value_atmega = self._io.read_u2le()
            self.raw_value_sp1 = self._io.read_u2le()
            self.raw_value_sp2 = self._io.read_u2le()
            self.raw_value_sp3 = self._io.read_u2le()
            self.raw_value_sp4 = self._io.read_u2le()
            self.time_remaining_0 = self._io.read_u4le()
            self.time_remaining_1 = self._io.read_u4le()
            self.timer_length_0 = self._io.read_u4le()
            self.timer_length_1 = self._io.read_u4le()
            self.atmegarobot_interactions = self._io.read_u4le()
            self.beacon_interval = self._io.read_u2le()
            self.beacon_separation = self._io.read_u2le()
            self.burn_wire_duration = self._io.read_u1()
            self.burn_wire_attempts = self._io.read_u1()
            self.timer_length = self._io.read_u2le()
            self.magfield_x = self._io.read_f4le()
            self.magfield_y = self._io.read_f4le()
            self.magfield_z = self._io.read_f4le()
            self.scale_factor = self._io.read_f4le()
            self.reference_voltage = self._io.read_f4le()
            self.rgmaxtime_1hz = self._io.read_u4le()
            self.rgcycleslips_1hz = self._io.read_u4le()
            self.rgmaxtime_2hz = self._io.read_u4le()
            self.rgcycleslips_2hz = self._io.read_u4le()
            self.rgmaxtime_10hz = self._io.read_u4le()
            self.rgcycleslips_10hz = self._io.read_u4le()
            self.uart0_bytes_sent = self._io.read_u4le()
            self.uart0_bytes_recv = self._io.read_u4le()
            self.shiftregdata = self._io.read_u4le()
            self.eps_i2c_errors = self._io.read_u2le()
            self.eps_vbatt_critical = self._io.read_u2le()
            self.config2_batt_maxvoltage = self._io.read_u2le()
            self.config2_batt_safevoltage = self._io.read_u2le()
            self.config2_batt_criticalvoltage = self._io.read_u2le()
            self.config2_batt_normalvoltage = self._io.read_u2le()


    class Gt1Payload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_type = self._io.read_u1()
            _on = self.packet_type
            if _on == 1:
                self.data_payload = Gt1.Gt1payload1(self._io, self, self._root)
            elif _on == 2:
                self.data_payload = Gt1.Gt1payload2(self._io, self, self._root)



