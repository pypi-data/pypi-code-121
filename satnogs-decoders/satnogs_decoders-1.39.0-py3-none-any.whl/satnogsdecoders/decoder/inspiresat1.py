# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Inspiresat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field ccsds_version: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.ccsds_version
    :field packet_type: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_type
    :field secondary_header_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.secondary_header_flag
    :field application_process_id: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.application_process_id
    :field sequence_flags: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.sequence_flags
    :field sequence_count: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.sequence_count
    :field packet_length: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_length
    :field sh_coarse: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.sh_coarse
    :field sh_fine: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.sh_fine
    :field cmd_recv_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_recv_count
    :field cmd_fail_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_fail_count
    :field cmd_succ_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_succ_count
    :field cmd_succ_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_succ_op
    :field cmd_fail_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_fail_op
    :field cmd_fail_code: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_fail_code
    :field eclipse_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.eclipse_state
    :field pwr_status_sd1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_sd1
    :field pwr_status_sd0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_sd0
    :field pwr_status_htr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_htr
    :field pwr_status_sband: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_sband
    :field pwr_status_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_adcs
    :field pwr_status_cip: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_cip
    :field pwr_status_daxss: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pwr_status_daxss
    :field sd_read_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_misc
    :field sd_read_scic: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_scic
    :field sd_read_scid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_scid
    :field sd_read_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_adcs
    :field sd_read_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_beacon
    :field sd_read_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_read_log
    :field sd_write_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_misc
    :field sd_write_scic: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_scic
    :field sd_write_scid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_scid
    :field sd_write_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_adcs
    :field sd_write_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_beacon
    :field sd_write_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sd_write_log
    :field cmd_loss_timer: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cmd_loss_timer
    :field clt_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.clt_state
    :field alive_daxss: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_daxss
    :field alive_cip: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_cip
    :field alive_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_adcs
    :field alive_sband: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_sband
    :field alive_uhf: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_uhf
    :field alive_sd1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_sd1
    :field alive_sd0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.alive_sd0
    :field cip_comstat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_comstat
    :field cip_temp1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_temp1
    :field cip_temp2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_temp2
    :field cip_temp3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_temp3
    :field uhf_temp_buff: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_temp_buff
    :field uhf_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_temp
    :field uhf_locked: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_locked
    :field uhf_readback: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_readback
    :field uhf_swd: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_swd
    :field uhf_afc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_afc
    :field uhf_echo: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_echo
    :field uhf_channel: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_channel
    :field sband_pa_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_pa_curr
    :field sband_pa_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_pa_volt
    :field sband_rf_pwr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_rf_pwr
    :field sband_pa_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_pa_temp
    :field sband_top_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_top_temp
    :field sband_bottom_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_bottom_temp
    :field adcs_cmd_acpt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_cmd_acpt
    :field adcs_cmd_fail: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_cmd_fail
    :field adcs_time: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_time
    :field adcs_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_att_valid
    :field adcs_refs_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_refs_valid
    :field adcs_time_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_time_valid
    :field adcs_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_mode
    :field adcs_recom_sun_pt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_recom_sun_pt
    :field adcs_sun_pt_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_sun_pt_state
    :field adcs_star_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_star_temp
    :field adcs_wheel_temp1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_temp1
    :field adcs_wheel_temp2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_temp2
    :field adcs_wheel_temp3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_temp3
    :field adcs_digi_bus_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_digi_bus_volt
    :field adcs_sun_vec1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_sun_vec1
    :field adcs_sun_vec2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_sun_vec2
    :field adcs_sun_vec3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_sun_vec3
    :field adcs_wheel_sp1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_sp1
    :field adcs_wheel_sp2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_sp2
    :field adcs_wheel_sp3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_wheel_sp3
    :field adcs_body_rt1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_body_rt1
    :field adcs_body_rt2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_body_rt2
    :field adcs_body_rt3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_body_rt3
    :field daxss_time_sec: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_time_sec
    :field daxss_cmd_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_cmd_op
    :field daxss_cmd_succ: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_cmd_succ
    :field daxss_cmd_fail: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_cmd_fail
    :field daxss_cdh_enables: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_cdh_enables
    :field daxss_cdh_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_cdh_temp
    :field daxss_sps_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_sps_rate
    :field daxss_sps_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_sps_x
    :field daxss_sps_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_sps_y
    :field daxss_slow_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_slow_count
    :field bat_fg1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat_fg1
    :field daxss_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_curr
    :field daxss_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.daxss_volt
    :field cdh_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cdh_curr
    :field cdh_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cdh_volt
    :field sband_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_curr
    :field sband_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sband_volt
    :field uhf_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_curr
    :field uhf_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uhf_volt
    :field heater_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.heater_curr
    :field heater_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.heater_volt
    :field sp2_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp2_curr
    :field sp2_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp2_volt
    :field sp1_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp1_curr
    :field sp1_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp1_volt
    :field sp0_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp0_curr
    :field sp0_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp0_volt
    :field bat_vcell: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat_vcell
    :field gps_12v_2_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.gps_12v_2_curr
    :field gps_12v_2_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.gps_12v_2_volt
    :field gps_12v_1_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.gps_12v_1_curr
    :field gps_12v_1_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.gps_12v_1_volt
    :field bat_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat_curr
    :field bat_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat_volt
    :field adcs_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_curr
    :field adcs_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_volt
    :field v3p3_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.v3p3_curr
    :field v3p3_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.v3p3_volt
    :field cip_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_curr
    :field cip_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.cip_volt
    :field obc_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.obc_temp
    :field eps_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.eps_temp
    :field int_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.int_temp
    :field sp0_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp0_temp
    :field bat0_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat0_temp
    :field sp1_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp1_temp
    :field bat1_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat1_temp
    :field sp2_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sp2_temp
    :field bat_fg3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat_fg3
    :field bat0_temp_conv: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat0_temp_conv
    :field bat1_temp_conv: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.bat1_temp_conv
    :field mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.mode
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Inspiresat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Inspiresat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Inspiresat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Inspiresat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Inspiresat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Inspiresat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Inspiresat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Inspiresat1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Inspiresat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Inspiresat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Inspiresat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Inspiresat1.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Inspiresat1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"IS-1  ") or (self.callsign == u"BCT   ")) :
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
            self.ax25_info = Inspiresat1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class DataSectionT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._parent.packet_primary_header.secondary_header_flag:
                self._raw_secondary_header = self._io.read_bytes(6)
                _io__raw_secondary_header = KaitaiStream(BytesIO(self._raw_secondary_header))
                self.secondary_header = Inspiresat1.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)

            _on = self._parent.packet_primary_header.application_process_id
            if _on == 1:
                self.user_data_field = Inspiresat1.Is1BeaconT(self._io, self, self._root)


    class SecondaryHeaderT(KaitaiStruct):
        """The Secondary Header is a feature of the Space Packet which allows
        additional types of information that may be useful to the user
        application (e.g., a time code) to be included.
        See: 4.1.3.2 in CCSDS 133.0-B-1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sh_coarse = self._io.read_u4le()
            self.sh_fine = self._io.read_u2le()


    class PacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.application_process_id = self._io.read_bits_int_be(11)
            self.sequence_flags = self._io.read_bits_int_be(2)
            self.sequence_count = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_length = self._io.read_u2be()


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
            self.callsign_ror = Inspiresat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class Is1BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd_recv_count = self._io.read_u1()
            self.cmd_fail_count = self._io.read_u1()
            self.cmd_succ_count = self._io.read_u1()
            self.cmd_succ_op = self._io.read_u1()
            self.cmd_fail_op = self._io.read_u1()
            self.cmd_fail_code = self._io.read_u1()
            self.eclipse_state = self._io.read_bits_int_be(1) != 0
            self.pwr_status_sd1 = self._io.read_bits_int_be(1) != 0
            self.pwr_status_sd0 = self._io.read_bits_int_be(1) != 0
            self.pwr_status_htr = self._io.read_bits_int_be(1) != 0
            self.pwr_status_sband = self._io.read_bits_int_be(1) != 0
            self.pwr_status_adcs = self._io.read_bits_int_be(1) != 0
            self.pwr_status_cip = self._io.read_bits_int_be(1) != 0
            self.pwr_status_daxss = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sd_read_misc = self._io.read_u4le()
            self.sd_read_scic = self._io.read_u4le()
            self.sd_read_scid = self._io.read_u4le()
            self.sd_read_adcs = self._io.read_u4le()
            self.sd_read_beacon = self._io.read_u4le()
            self.sd_read_log = self._io.read_u4le()
            self.sd_write_misc = self._io.read_u4le()
            self.sd_write_scic = self._io.read_u4le()
            self.sd_write_scid = self._io.read_u4le()
            self.sd_write_adcs = self._io.read_u4le()
            self.sd_write_beacon = self._io.read_u4le()
            self.sd_write_log = self._io.read_u4le()
            self.cmd_loss_timer = self._io.read_u4le()
            self.clt_state = self._io.read_bits_int_be(1) != 0
            self.alive_daxss = self._io.read_bits_int_be(1) != 0
            self.alive_cip = self._io.read_bits_int_be(1) != 0
            self.alive_adcs = self._io.read_bits_int_be(1) != 0
            self.alive_sband = self._io.read_bits_int_be(1) != 0
            self.alive_uhf = self._io.read_bits_int_be(1) != 0
            self.alive_sd1 = self._io.read_bits_int_be(1) != 0
            self.alive_sd0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.cip_comstat = self._io.read_u4le()
            self.cip_temp1 = self._io.read_s2le()
            self.cip_temp2 = self._io.read_s2le()
            self.cip_temp3 = self._io.read_s2le()
            self.uhf_temp_buff = self._io.read_bits_int_be(2)
            self.uhf_temp = self._io.read_bits_int_be(6)
            self.uhf_locked = self._io.read_bits_int_be(1) != 0
            self.uhf_readback = self._io.read_bits_int_be(2)
            self.uhf_swd = self._io.read_bits_int_be(1) != 0
            self.uhf_afc = self._io.read_bits_int_be(1) != 0
            self.uhf_echo = self._io.read_bits_int_be(1) != 0
            self.uhf_channel = self._io.read_bits_int_be(2)
            self._io.align_to_byte()
            self.sband_pa_curr = self._io.read_u2le()
            self.sband_pa_volt = self._io.read_u2le()
            self.sband_rf_pwr = self._io.read_u2le()
            self.sband_pa_temp = self._io.read_u2le()
            self.sband_top_temp = self._io.read_u2le()
            self.sband_bottom_temp = self._io.read_u2le()
            self.adcs_cmd_acpt = self._io.read_u1()
            self.adcs_cmd_fail = self._io.read_u1()
            self.adcs_time = self._io.read_s4le()
            self.adcs_att_valid = self._io.read_bits_int_be(1) != 0
            self.adcs_refs_valid = self._io.read_bits_int_be(1) != 0
            self.adcs_time_valid = self._io.read_bits_int_be(1) != 0
            self.adcs_mode = self._io.read_bits_int_be(1) != 0
            self.adcs_recom_sun_pt = self._io.read_bits_int_be(1) != 0
            self.adcs_sun_pt_state = self._io.read_bits_int_be(3)
            self._io.align_to_byte()
            self.adcs_star_temp = self._io.read_s1()
            self.adcs_wheel_temp1 = self._io.read_s2le()
            self.adcs_wheel_temp2 = self._io.read_s2le()
            self.adcs_wheel_temp3 = self._io.read_s2le()
            self.adcs_digi_bus_volt = self._io.read_s2le()
            self.adcs_sun_vec1 = self._io.read_s2le()
            self.adcs_sun_vec2 = self._io.read_s2le()
            self.adcs_sun_vec3 = self._io.read_s2le()
            self.adcs_wheel_sp1 = self._io.read_s2le()
            self.adcs_wheel_sp2 = self._io.read_s2le()
            self.adcs_wheel_sp3 = self._io.read_s2le()
            self.adcs_body_rt1 = self._io.read_s4le()
            self.adcs_body_rt2 = self._io.read_s4le()
            self.adcs_body_rt3 = self._io.read_s4le()
            self.pad1 = self._io.read_u4le()
            self.pad2 = self._io.read_u4le()
            self.pad3 = self._io.read_u4le()
            self.daxss_time_sec = self._io.read_u4le()
            self.daxss_cmd_op = self._io.read_u1()
            self.daxss_cmd_succ = self._io.read_u1()
            self.daxss_cmd_fail = self._io.read_u1()
            self.daxss_cdh_enables = self._io.read_u2le()
            self.daxss_cdh_temp = self._io.read_s2le()
            self.daxss_sps_rate = self._io.read_u4le()
            self.daxss_sps_x = self._io.read_u2le()
            self.daxss_sps_y = self._io.read_u2le()
            self.daxss_slow_count = self._io.read_u2le()
            self.bat_fg1 = self._io.read_u2le()
            self.daxss_curr = self._io.read_u2le()
            self.daxss_volt = self._io.read_u2le()
            self.cdh_curr = self._io.read_u2le()
            self.cdh_volt = self._io.read_u2le()
            self.sband_curr = self._io.read_u2le()
            self.sband_volt = self._io.read_u2le()
            self.uhf_curr = self._io.read_u2le()
            self.uhf_volt = self._io.read_u2le()
            self.heater_curr = self._io.read_u2le()
            self.heater_volt = self._io.read_u2le()
            self.sp2_curr = self._io.read_u2le()
            self.sp2_volt = self._io.read_u2le()
            self.sp1_curr = self._io.read_u2le()
            self.sp1_volt = self._io.read_u2le()
            self.sp0_curr = self._io.read_u2le()
            self.sp0_volt = self._io.read_u2le()
            self.bat_vcell = self._io.read_u2le()
            self.gps_12v_2_curr = self._io.read_u2le()
            self.gps_12v_2_volt = self._io.read_u2le()
            self.gps_12v_1_curr = self._io.read_u2le()
            self.gps_12v_1_volt = self._io.read_u2le()
            self.bat_curr = self._io.read_u2le()
            self.bat_volt = self._io.read_u2le()
            self.adcs_curr = self._io.read_u2le()
            self.adcs_volt = self._io.read_u2le()
            self.v3p3_curr = self._io.read_u2le()
            self.v3p3_volt = self._io.read_u2le()
            self.cip_curr = self._io.read_u2le()
            self.cip_volt = self._io.read_u2le()
            self.obc_temp = self._io.read_u2le()
            self.eps_temp = self._io.read_u2le()
            self.int_temp = self._io.read_u2le()
            self.sp0_temp = self._io.read_u2le()
            self.bat0_temp = self._io.read_u2le()
            self.sp1_temp = self._io.read_u2le()
            self.bat1_temp = self._io.read_u2le()
            self.sp2_temp = self._io.read_u2le()
            self.bat_fg3 = self._io.read_u2le()
            self.bat0_temp_conv = self._io.read_f4le()
            self.bat1_temp_conv = self._io.read_f4le()
            self.mode = self._io.read_u1()


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Inspiresat1.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Inspiresat1.DataSectionT(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Inspiresat1.CcsdsSpacePacketT(self._io, self, self._root)



