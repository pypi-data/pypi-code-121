# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Oresat0(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field aprs_packet_data_type_identifier: ax25_frame.payload.ax25_info.aprs_packet_data_type_identifier
    :field aprs_packet_revision: ax25_frame.payload.ax25_info.aprs_packet_revision
    :field aprs_packet_satellite_id: ax25_frame.payload.ax25_info.aprs_packet_satellite_id
    :field c3_m4_oresat0_state: ax25_frame.payload.ax25_info.c3_m4_oresat0_state
    :field c3_m4_uptime: ax25_frame.payload.ax25_info.c3_m4_uptime
    :field c3_rtc_time: ax25_frame.payload.ax25_info.c3_rtc_time
    :field c3_wdt_num_power_cycles: ax25_frame.payload.ax25_info.c3_wdt_num_power_cycles
    :field c3_emmc_percent_full: ax25_frame.payload.ax25_info.c3_emmc_percent_full
    :field c3_l_rx_bytes_received: ax25_frame.payload.ax25_info.c3_l_rx_bytes_received
    :field c3_l_rx_valid_packets: ax25_frame.payload.ax25_info.c3_l_rx_valid_packets
    :field c3_l_rx_rssi: ax25_frame.payload.ax25_info.c3_l_rx_rssi
    :field c3_uhf_rx_bytes_received: ax25_frame.payload.ax25_info.c3_uhf_rx_bytes_received
    :field c3_uhf_rx_valid_packets: ax25_frame.payload.ax25_info.c3_uhf_rx_valid_packets
    :field c3_uhf_rx_rssi: ax25_frame.payload.ax25_info.c3_uhf_rx_rssi
    :field c3_fw_bank_current_and_next_bank: ax25_frame.payload.ax25_info.c3_fw_bank_current_and_next_bank
    :field c3_l_rx_sequence_number: ax25_frame.payload.ax25_info.c3_l_rx_sequence_number
    :field c3_l_rx_rejected_packets: ax25_frame.payload.ax25_info.c3_l_rx_rejected_packets
    :field battery_pack_1_vbatt: ax25_frame.payload.ax25_info.battery_pack_1_vbatt
    :field battery_pack_1_vcell: ax25_frame.payload.ax25_info.battery_pack_1_vcell
    :field battery_pack_1_vcell_max: ax25_frame.payload.ax25_info.battery_pack_1_vcell_max
    :field battery_pack_1_vcell_min: ax25_frame.payload.ax25_info.battery_pack_1_vcell_min
    :field battery_pack_1_vcell_1: ax25_frame.payload.ax25_info.battery_pack_1_vcell_1
    :field battery_pack_1_vcell_2: ax25_frame.payload.ax25_info.battery_pack_1_vcell_2
    :field battery_pack_1_vcell_avg: ax25_frame.payload.ax25_info.battery_pack_1_vcell_avg
    :field battery_pack_1_temperature: ax25_frame.payload.ax25_info.battery_pack_1_temperature
    :field battery_pack_1_temperature_avg: ax25_frame.payload.ax25_info.battery_pack_1_temperature_avg
    :field battery_pack_1_temperature_max: ax25_frame.payload.ax25_info.battery_pack_1_temperature_max
    :field battery_pack_1_temperature_min: ax25_frame.payload.ax25_info.battery_pack_1_temperature_min
    :field battery_pack_1_current: ax25_frame.payload.ax25_info.battery_pack_1_current
    :field battery_pack_1_current_avg: ax25_frame.payload.ax25_info.battery_pack_1_current_avg
    :field battery_pack_1_current_max: ax25_frame.payload.ax25_info.battery_pack_1_current_max
    :field battery_pack_1_current_min: ax25_frame.payload.ax25_info.battery_pack_1_current_min
    :field battery_pack_1_state: ax25_frame.payload.ax25_info.battery_pack_1_state
    :field battery_pack_1_reported_state_of_charge: ax25_frame.payload.ax25_info.battery_pack_1_reported_state_of_charge
    :field battery_pack_1_full_capacity: ax25_frame.payload.ax25_info.battery_pack_1_full_capacity
    :field battery_pack_1_reported_capacity: ax25_frame.payload.ax25_info.battery_pack_1_reported_capacity
    :field battery_pack_2_vbatt: ax25_frame.payload.ax25_info.battery_pack_2_vbatt
    :field battery_pack_2_vcell: ax25_frame.payload.ax25_info.battery_pack_2_vcell
    :field battery_pack_2_vcell_max: ax25_frame.payload.ax25_info.battery_pack_2_vcell_max
    :field battery_pack_2_vcell_min: ax25_frame.payload.ax25_info.battery_pack_2_vcell_min
    :field battery_pack_2_vcell_1: ax25_frame.payload.ax25_info.battery_pack_2_vcell_1
    :field battery_pack_2_vcell_2: ax25_frame.payload.ax25_info.battery_pack_2_vcell_2
    :field battery_pack_2_vcell_avg: ax25_frame.payload.ax25_info.battery_pack_2_vcell_avg
    :field battery_pack_2_temperature: ax25_frame.payload.ax25_info.battery_pack_2_temperature
    :field battery_pack_2_temperature_avg: ax25_frame.payload.ax25_info.battery_pack_2_temperature_avg
    :field battery_pack_2_temperature_max: ax25_frame.payload.ax25_info.battery_pack_2_temperature_max
    :field battery_pack_2_temperature_min: ax25_frame.payload.ax25_info.battery_pack_2_temperature_min
    :field battery_pack_2_current: ax25_frame.payload.ax25_info.battery_pack_2_current
    :field battery_pack_2_current_avg: ax25_frame.payload.ax25_info.battery_pack_2_current_avg
    :field battery_pack_2_current_max: ax25_frame.payload.ax25_info.battery_pack_2_current_max
    :field battery_pack_2_current_min: ax25_frame.payload.ax25_info.battery_pack_2_current_min
    :field battery_pack_2_state: ax25_frame.payload.ax25_info.battery_pack_2_state
    :field battery_pack_2_reported_state_of_charge: ax25_frame.payload.ax25_info.battery_pack_2_reported_state_of_charge
    :field battery_pack_2_full_capacity: ax25_frame.payload.ax25_info.battery_pack_2_full_capacity
    :field battery_pack_2_reported_capacity: ax25_frame.payload.ax25_info.battery_pack_2_reported_capacity
    :field solar_minus_x_voltage_avg: ax25_frame.payload.ax25_info.solar_minus_x_voltage_avg
    :field solar_minus_x_current_avg: ax25_frame.payload.ax25_info.solar_minus_x_current_avg
    :field solar_minus_x_power_avg: ax25_frame.payload.ax25_info.solar_minus_x_power_avg
    :field solar_minus_x_voltage_max: ax25_frame.payload.ax25_info.solar_minus_x_voltage_max
    :field solar_minus_x_current_max: ax25_frame.payload.ax25_info.solar_minus_x_current_max
    :field solar_minus_x_power_max: ax25_frame.payload.ax25_info.solar_minus_x_power_max
    :field solar_minus_x_energy: ax25_frame.payload.ax25_info.solar_minus_x_energy
    :field solar_minus_y_voltage_avg: ax25_frame.payload.ax25_info.solar_minus_y_voltage_avg
    :field solar_minus_y_current_avg: ax25_frame.payload.ax25_info.solar_minus_y_current_avg
    :field solar_minus_y_power_avg: ax25_frame.payload.ax25_info.solar_minus_y_power_avg
    :field solar_minus_y_voltage_max: ax25_frame.payload.ax25_info.solar_minus_y_voltage_max
    :field solar_minus_y_current_max: ax25_frame.payload.ax25_info.solar_minus_y_current_max
    :field solar_minus_y_power_max: ax25_frame.payload.ax25_info.solar_minus_y_power_max
    :field solar_minus_y_energy: ax25_frame.payload.ax25_info.solar_minus_y_energy
    :field solar_plus_x_voltage_avg: ax25_frame.payload.ax25_info.solar_plus_x_voltage_avg
    :field solar_plus_x_current_avg: ax25_frame.payload.ax25_info.solar_plus_x_current_avg
    :field solar_plus_x_power_avg: ax25_frame.payload.ax25_info.solar_plus_x_power_avg
    :field solar_plus_x_voltage_max: ax25_frame.payload.ax25_info.solar_plus_x_voltage_max
    :field solar_plus_x_current_max: ax25_frame.payload.ax25_info.solar_plus_x_current_max
    :field solar_plus_x_power_max: ax25_frame.payload.ax25_info.solar_plus_x_power_max
    :field solar_plus_x_energy: ax25_frame.payload.ax25_info.solar_plus_x_energy
    :field solar_plus_y_voltage_avg: ax25_frame.payload.ax25_info.solar_plus_y_voltage_avg
    :field solar_plus_y_current_avg: ax25_frame.payload.ax25_info.solar_plus_y_current_avg
    :field solar_plus_y_power_avg: ax25_frame.payload.ax25_info.solar_plus_y_power_avg
    :field solar_plus_y_voltage_max: ax25_frame.payload.ax25_info.solar_plus_y_voltage_max
    :field solar_plus_y_current_max: ax25_frame.payload.ax25_info.solar_plus_y_current_max
    :field solar_plus_y_power_max: ax25_frame.payload.ax25_info.solar_plus_y_power_max
    :field solar_plus_y_energy: ax25_frame.payload.ax25_info.solar_plus_y_energy
    :field star_tracker_emmc_capacity: ax25_frame.payload.ax25_info.star_tracker_emmc_capacity
    :field star_tracker_readable_files: ax25_frame.payload.ax25_info.star_tracker_readable_files
    :field star_tracker_updater_status: ax25_frame.payload.ax25_info.star_tracker_updater_status
    :field star_tracker_updates_cached: ax25_frame.payload.ax25_info.star_tracker_updates_cached
    :field star_tracker_right_ascension: ax25_frame.payload.ax25_info.star_tracker_right_ascension
    :field star_tracker_declination: ax25_frame.payload.ax25_info.star_tracker_declination
    :field star_tracker_roll: ax25_frame.payload.ax25_info.star_tracker_roll
    :field star_tracker_timestamp_of_last_measurement: ax25_frame.payload.ax25_info.star_tracker_timestamp_of_last_measurement
    :field gps_emmc_capacity: ax25_frame.payload.ax25_info.gps_emmc_capacity
    :field gps_readable_files: ax25_frame.payload.ax25_info.gps_readable_files
    :field gps_updater_status: ax25_frame.payload.ax25_info.gps_updater_status
    :field gps_updates_cached: ax25_frame.payload.ax25_info.gps_updates_cached
    :field gps_gps_status: ax25_frame.payload.ax25_info.gps_gps_status
    :field gps_num_of_sats_locked: ax25_frame.payload.ax25_info.gps_num_of_sats_locked
    :field gps_x_position: ax25_frame.payload.ax25_info.gps_x_position
    :field gps_y_postition: ax25_frame.payload.ax25_info.gps_y_postition
    :field gps_z_position: ax25_frame.payload.ax25_info.gps_z_position
    :field gps_x_velocity: ax25_frame.payload.ax25_info.gps_x_velocity
    :field gps_y_velocity: ax25_frame.payload.ax25_info.gps_y_velocity
    :field gps_z_velocity: ax25_frame.payload.ax25_info.gps_z_velocity
    :field gps_timestamp_of_last_packet: ax25_frame.payload.ax25_info.gps_timestamp_of_last_packet
    :field ads_gyro_roll_dot: ax25_frame.payload.ax25_info.ads_gyro_roll_dot
    :field ads_gyro_pitch_dot: ax25_frame.payload.ax25_info.ads_gyro_pitch_dot
    :field ads_gyro_yaw_dot: ax25_frame.payload.ax25_info.ads_gyro_yaw_dot
    :field ads_gyro_imu_temp: ax25_frame.payload.ax25_info.ads_gyro_imu_temp
    :field dxwifi_emmc_capacity: ax25_frame.payload.ax25_info.dxwifi_emmc_capacity
    :field dxwifi_readable_files: ax25_frame.payload.ax25_info.dxwifi_readable_files
    :field dxwifi_updater_status: ax25_frame.payload.ax25_info.dxwifi_updater_status
    :field dxwifi_updates_cached: ax25_frame.payload.ax25_info.dxwifi_updates_cached
    :field dxwifi_transmitting: ax25_frame.payload.ax25_info.dxwifi_transmitting
    :field aprs_packet_crc_minus_32: ax25_frame.payload.ax25_info.aprs_packet_crc_minus_32
    
    Attention: `rpt_callsign` cannot be accessed because `rpt_instance` is an
    array of unknown size at the beginning of the parsing process! Left an
    example in here.
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Oresat0.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Oresat0.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Oresat0.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Oresat0.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Oresat0.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Oresat0.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Oresat0.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Oresat0.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Oresat0.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Oresat0.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Oresat0.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Oresat0.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Oresat0.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Oresat0.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"KJ7SAT") or (self.callsign == u"SPACE ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Oresat0.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Oresat0.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Oresat0.SsidMask(self._io, self, self._root)


    class Repeater(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_instance = []
            i = 0
            while True:
                _ = Oresat0.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


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
            self.callsign_ror = Oresat0.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.aprs_packet_format = (self._io.read_bytes(3)).decode(u"ASCII")
            self.aprs_packet_satellite_id = self._io.read_u1()
            self.aprs_packet_revision = self._io.read_u1()
            self.c3_m4_oresat0_state = (self._io.read_bytes(1)).decode(u"ASCII")
            self.c3_m4_uptime = self._io.read_u4le()
            self.c3_rtc_time = self._io.read_u4le()
            self.c3_wdt_num_power_cycles = self._io.read_u2le()
            self.c3_emmc_percent_full = self._io.read_u1()
            self.c3_l_rx_bytes_received = self._io.read_u4le()
            self.c3_l_rx_valid_packets = self._io.read_u4le()
            self.c3_l_rx_rssi = self._io.read_s1()
            self.c3_uhf_rx_bytes_received = self._io.read_u4le()
            self.c3_uhf_rx_valid_packets = self._io.read_u4le()
            self.c3_uhf_rx_rssi = self._io.read_s1()
            self.c3_fw_bank_current_and_next_bank = self._io.read_u1()
            self.c3_l_rx_sequence_number = self._io.read_u4le()
            self.c3_l_rx_rejected_packets = self._io.read_u4le()
            self.battery_pack_1_vbatt = self._io.read_u2le()
            self.battery_pack_1_vcell = self._io.read_u2le()
            self.battery_pack_1_vcell_max = self._io.read_u2le()
            self.battery_pack_1_vcell_min = self._io.read_u2le()
            self.battery_pack_1_vcell_1 = self._io.read_u2le()
            self.battery_pack_1_vcell_2 = self._io.read_u2le()
            self.battery_pack_1_vcell_avg = self._io.read_u2le()
            self.battery_pack_1_temperature = self._io.read_s2le()
            self.battery_pack_1_temperature_avg = self._io.read_s2le()
            self.battery_pack_1_temperature_max = self._io.read_s2le()
            self.battery_pack_1_temperature_min = self._io.read_s2le()
            self.battery_pack_1_current = self._io.read_s2le()
            self.battery_pack_1_current_avg = self._io.read_s2le()
            self.battery_pack_1_current_max = self._io.read_s2le()
            self.battery_pack_1_current_min = self._io.read_s2le()
            self.battery_pack_1_state = self._io.read_u1()
            self.battery_pack_1_reported_state_of_charge = self._io.read_u1()
            self.battery_pack_1_full_capacity = self._io.read_u2le()
            self.battery_pack_1_reported_capacity = self._io.read_u2le()
            self.battery_pack_2_vbatt = self._io.read_u2le()
            self.battery_pack_2_vcell = self._io.read_u2le()
            self.battery_pack_2_vcell_max = self._io.read_u2le()
            self.battery_pack_2_vcell_min = self._io.read_u2le()
            self.battery_pack_2_vcell_1 = self._io.read_u2le()
            self.battery_pack_2_vcell_2 = self._io.read_u2le()
            self.battery_pack_2_vcell_avg = self._io.read_u2le()
            self.battery_pack_2_temperature = self._io.read_s2le()
            self.battery_pack_2_temperature_avg = self._io.read_s2le()
            self.battery_pack_2_temperature_max = self._io.read_s2le()
            self.battery_pack_2_temperature_min = self._io.read_s2le()
            self.battery_pack_2_current = self._io.read_s2le()
            self.battery_pack_2_current_avg = self._io.read_s2le()
            self.battery_pack_2_current_max = self._io.read_s2le()
            self.battery_pack_2_current_min = self._io.read_s2le()
            self.battery_pack_2_state = self._io.read_u1()
            self.battery_pack_2_reported_state_of_charge = self._io.read_u1()
            self.battery_pack_2_full_capacity = self._io.read_u2le()
            self.battery_pack_2_reported_capacity = self._io.read_u2le()
            self.solar_minus_x_voltage_avg = self._io.read_u2le()
            self.solar_minus_x_current_avg = self._io.read_s2le()
            self.solar_minus_x_power_avg = self._io.read_u2le()
            self.solar_minus_x_voltage_max = self._io.read_u2le()
            self.solar_minus_x_current_max = self._io.read_s2le()
            self.solar_minus_x_power_max = self._io.read_u2le()
            self.solar_minus_x_energy = self._io.read_u2le()
            self.solar_minus_y_voltage_avg = self._io.read_u2le()
            self.solar_minus_y_current_avg = self._io.read_s2le()
            self.solar_minus_y_power_avg = self._io.read_u2le()
            self.solar_minus_y_voltage_max = self._io.read_u2le()
            self.solar_minus_y_current_max = self._io.read_s2le()
            self.solar_minus_y_power_max = self._io.read_u2le()
            self.solar_minus_y_energy = self._io.read_u2le()
            self.solar_plus_x_voltage_avg = self._io.read_u2le()
            self.solar_plus_x_current_avg = self._io.read_s2le()
            self.solar_plus_x_power_avg = self._io.read_u2le()
            self.solar_plus_x_voltage_max = self._io.read_u2le()
            self.solar_plus_x_current_max = self._io.read_s2le()
            self.solar_plus_x_power_max = self._io.read_u2le()
            self.solar_plus_x_energy = self._io.read_u2le()
            self.solar_plus_y_voltage_avg = self._io.read_u2le()
            self.solar_plus_y_current_avg = self._io.read_s2le()
            self.solar_plus_y_power_avg = self._io.read_u2le()
            self.solar_plus_y_voltage_max = self._io.read_u2le()
            self.solar_plus_y_current_max = self._io.read_s2le()
            self.solar_plus_y_power_max = self._io.read_u2le()
            self.solar_plus_y_energy = self._io.read_u2le()
            self.star_tracker_emmc_capacity = self._io.read_u1()
            self.star_tracker_readable_files = self._io.read_u1()
            self.star_tracker_updater_status = self._io.read_u1()
            self.star_tracker_updates_cached = self._io.read_u1()
            self.star_tracker_right_ascension = self._io.read_s2le()
            self.star_tracker_declination = self._io.read_s2le()
            self.star_tracker_roll = self._io.read_s2le()
            self.star_tracker_timestamp_of_last_measurement = self._io.read_u4le()
            self.gps_emmc_capacity = self._io.read_u1()
            self.gps_readable_files = self._io.read_u1()
            self.gps_updater_status = self._io.read_u1()
            self.gps_updates_cached = self._io.read_u1()
            self.gps_gps_status = self._io.read_u1()
            self.gps_num_of_sats_locked = self._io.read_u1()
            self.gps_x_position = self._io.read_s4le()
            self.gps_y_postition = self._io.read_s4le()
            self.gps_z_position = self._io.read_s4le()
            self.gps_x_velocity = self._io.read_s4le()
            self.gps_y_velocity = self._io.read_s4le()
            self.gps_z_velocity = self._io.read_s4le()
            self.gps_timestamp_of_last_packet = self._io.read_u4le()
            self.ads_gyro_roll_dot = self._io.read_s2le()
            self.ads_gyro_pitch_dot = self._io.read_s2le()
            self.ads_gyro_yaw_dot = self._io.read_s2le()
            self.ads_gyro_imu_temp = self._io.read_s1()
            self.dxwifi_emmc_capacity = self._io.read_u1()
            self.dxwifi_readable_files = self._io.read_u1()
            self.dxwifi_updater_status = self._io.read_u1()
            self.dxwifi_updates_cached = self._io.read_u1()
            self.dxwifi_transmitting = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.aprs_packet_crc_minus_32 = self._io.read_u4le()



