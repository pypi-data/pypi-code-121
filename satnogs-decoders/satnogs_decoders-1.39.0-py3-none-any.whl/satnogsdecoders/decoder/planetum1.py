# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Planetum1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field obc_pass_packet_type: ax25_frame.payload.ax25_info.body.obc_pass_packet_type
    :field obc_reset_cnt: ax25_frame.payload.ax25_info.body.obc_reset_cnt
    :field obc_uptime: ax25_frame.payload.ax25_info.body.obc_uptime
    :field obc_uptime_tot: ax25_frame.payload.ax25_info.body.obc_uptime_tot
    :field obc_bat: ax25_frame.payload.ax25_info.body.obc_bat
    :field obc_temp_mcu: ax25_frame.payload.ax25_info.body.obc_temp_mcu
    :field obc_temp_brd: ax25_frame.payload.ax25_info.body.obc_temp_brd
    :field obc_temp_zn: ax25_frame.payload.ax25_info.body.obc_temp_zn
    :field obc_temp_xp: ax25_frame.payload.ax25_info.body.obc_temp_xp
    :field obc_temp_yp: ax25_frame.payload.ax25_info.body.obc_temp_yp
    :field obc_temp_yn: ax25_frame.payload.ax25_info.body.obc_temp_yn
    :field obc_temp_xn: ax25_frame.payload.ax25_info.body.obc_temp_xn
    :field obc_temp_zp: ax25_frame.payload.ax25_info.body.obc_temp_zp
    :field obc_freemem: ax25_frame.payload.ax25_info.body.obc_freemem
    :field psu_reset_cnt: ax25_frame.payload.ax25_info.body.psu_reset_cnt
    :field psu_uptime: ax25_frame.payload.ax25_info.body.psu_uptime
    :field psu_uptime_tot: ax25_frame.payload.ax25_info.body.psu_uptime_tot
    :field psu_battery: ax25_frame.payload.ax25_info.body.psu_battery
    :field psu_temp_sys: ax25_frame.payload.ax25_info.body.psu_temp_sys
    :field psu_temp_bat: ax25_frame.payload.ax25_info.body.psu_temp_bat
    :field psu_cur_in: ax25_frame.payload.ax25_info.body.psu_cur_in
    :field psu_cur_out: ax25_frame.payload.ax25_info.body.psu_cur_out
    :field psu_ch_state_num: ax25_frame.payload.ax25_info.body.psu_ch_state_num
    :field psu_ch0_state: ax25_frame.payload.ax25_info.body.psu_ch0_state
    :field psu_ch1_state: ax25_frame.payload.ax25_info.body.psu_ch1_state
    :field psu_ch2_state: ax25_frame.payload.ax25_info.body.psu_ch2_state
    :field psu_ch3_state: ax25_frame.payload.ax25_info.body.psu_ch3_state
    :field psu_ch4_state: ax25_frame.payload.ax25_info.body.psu_ch4_state
    :field psu_ch5_state: ax25_frame.payload.ax25_info.body.psu_ch5_state
    :field psu_ch6_state: ax25_frame.payload.ax25_info.body.psu_ch6_state
    :field psu_sys_state: ax25_frame.payload.ax25_info.body.psu_sys_state
    :field uhf_uptime: ax25_frame.payload.ax25_info.body.uhf_uptime
    :field uhf_uptime_tot: ax25_frame.payload.ax25_info.body.uhf_uptime_tot
    :field uhf_reset_cnt: ax25_frame.payload.ax25_info.body.uhf_reset_cnt
    :field uhf_trx_temp: ax25_frame.payload.ax25_info.body.uhf_trx_temp
    :field uhf_rf_temp: ax25_frame.payload.ax25_info.body.uhf_rf_temp
    :field uhf_pa_temp: ax25_frame.payload.ax25_info.body.uhf_pa_temp
    :field uhf_digipeater_cnt: ax25_frame.payload.ax25_info.body.uhf_digipeater_cnt
    :field uhf_last_digipeater: ax25_frame.payload.ax25_info.body.uhf_last_digipeater
    :field uhf_rx_cnt: ax25_frame.payload.ax25_info.body.uhf_rx_cnt
    :field uhf_tx_cnt: ax25_frame.payload.ax25_info.body.uhf_tx_cnt
    :field uhf_act_rssi_raw: ax25_frame.payload.ax25_info.body.uhf_act_rssi_raw
    :field uhf_dcd_rssi_raw: ax25_frame.payload.ax25_info.body.uhf_dcd_rssi_raw
    :field vhf_uptime: ax25_frame.payload.ax25_info.body.vhf_uptime
    :field vhf_uptime_tot: ax25_frame.payload.ax25_info.body.vhf_uptime_tot
    :field vhf_reset_cnt: ax25_frame.payload.ax25_info.body.vhf_reset_cnt
    :field vhf_trx_temp: ax25_frame.payload.ax25_info.body.vhf_trx_temp
    :field vhf_rf_temp: ax25_frame.payload.ax25_info.body.vhf_rf_temp
    :field vhf_pa_temp: ax25_frame.payload.ax25_info.body.vhf_pa_temp
    :field vhf_digipeater_cnt: ax25_frame.payload.ax25_info.body.vhf_digipeater_cnt
    :field vhf_last_digipeater: ax25_frame.payload.ax25_info.body.vhf_last_digipeater
    :field vhf_rx_cnt: ax25_frame.payload.ax25_info.body.vhf_rx_cnt
    :field vhf_tx_cnt: ax25_frame.payload.ax25_info.body.vhf_tx_cnt
    :field vhf_act_rssi_raw: ax25_frame.payload.ax25_info.body.vhf_act_rssi_raw
    :field vhf_dcd_rssi_raw: ax25_frame.payload.ax25_info.body.vhf_dcd_rssi_raw
    :field monitor: ax25_frame.payload.ax25_info.monitor
    :field packet_type_q: ax25_frame.payload.ax25_info.packet_type_q
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Planetum1.Ax25Frame(self._io, self, self._root)

    class Psu(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.psu_pass_packet_type = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_rst_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_temp_sys_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_temp_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_cur_in_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_cur_out_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_ch_state_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_sys_state_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def psu_ch3_state(self):
            if hasattr(self, '_m_psu_ch3_state'):
                return self._m_psu_ch3_state if hasattr(self, '_m_psu_ch3_state') else None

            self._m_psu_ch3_state = ((self.psu_ch_state_num >> 3) & 1)
            return self._m_psu_ch3_state if hasattr(self, '_m_psu_ch3_state') else None

        @property
        def psu_reset_cnt(self):
            if hasattr(self, '_m_psu_reset_cnt'):
                return self._m_psu_reset_cnt if hasattr(self, '_m_psu_reset_cnt') else None

            self._m_psu_reset_cnt = int(self.psu_rst_cnt_str)
            return self._m_psu_reset_cnt if hasattr(self, '_m_psu_reset_cnt') else None

        @property
        def psu_uptime_tot(self):
            if hasattr(self, '_m_psu_uptime_tot'):
                return self._m_psu_uptime_tot if hasattr(self, '_m_psu_uptime_tot') else None

            self._m_psu_uptime_tot = int(self.psu_uptime_tot_str)
            return self._m_psu_uptime_tot if hasattr(self, '_m_psu_uptime_tot') else None

        @property
        def psu_temp_bat(self):
            if hasattr(self, '_m_psu_temp_bat'):
                return self._m_psu_temp_bat if hasattr(self, '_m_psu_temp_bat') else None

            self._m_psu_temp_bat = int(self.psu_temp_bat_str)
            return self._m_psu_temp_bat if hasattr(self, '_m_psu_temp_bat') else None

        @property
        def psu_ch5_state(self):
            if hasattr(self, '_m_psu_ch5_state'):
                return self._m_psu_ch5_state if hasattr(self, '_m_psu_ch5_state') else None

            self._m_psu_ch5_state = ((self.psu_ch_state_num >> 5) & 1)
            return self._m_psu_ch5_state if hasattr(self, '_m_psu_ch5_state') else None

        @property
        def psu_ch0_state(self):
            if hasattr(self, '_m_psu_ch0_state'):
                return self._m_psu_ch0_state if hasattr(self, '_m_psu_ch0_state') else None

            self._m_psu_ch0_state = ((self.psu_ch_state_num >> 0) & 1)
            return self._m_psu_ch0_state if hasattr(self, '_m_psu_ch0_state') else None

        @property
        def psu_uptime(self):
            if hasattr(self, '_m_psu_uptime'):
                return self._m_psu_uptime if hasattr(self, '_m_psu_uptime') else None

            self._m_psu_uptime = int(self.psu_uptime_str)
            return self._m_psu_uptime if hasattr(self, '_m_psu_uptime') else None

        @property
        def psu_sys_state(self):
            if hasattr(self, '_m_psu_sys_state'):
                return self._m_psu_sys_state if hasattr(self, '_m_psu_sys_state') else None

            self._m_psu_sys_state = int(self.psu_sys_state_str)
            return self._m_psu_sys_state if hasattr(self, '_m_psu_sys_state') else None

        @property
        def psu_ch_state_num(self):
            if hasattr(self, '_m_psu_ch_state_num'):
                return self._m_psu_ch_state_num if hasattr(self, '_m_psu_ch_state_num') else None

            self._m_psu_ch_state_num = int(self.psu_ch_state_str, 16)
            return self._m_psu_ch_state_num if hasattr(self, '_m_psu_ch_state_num') else None

        @property
        def psu_ch6_state(self):
            if hasattr(self, '_m_psu_ch6_state'):
                return self._m_psu_ch6_state if hasattr(self, '_m_psu_ch6_state') else None

            self._m_psu_ch6_state = ((self.psu_ch_state_num >> 6) & 1)
            return self._m_psu_ch6_state if hasattr(self, '_m_psu_ch6_state') else None

        @property
        def psu_cur_out(self):
            if hasattr(self, '_m_psu_cur_out'):
                return self._m_psu_cur_out if hasattr(self, '_m_psu_cur_out') else None

            self._m_psu_cur_out = int(self.psu_cur_out_str)
            return self._m_psu_cur_out if hasattr(self, '_m_psu_cur_out') else None

        @property
        def psu_ch2_state(self):
            if hasattr(self, '_m_psu_ch2_state'):
                return self._m_psu_ch2_state if hasattr(self, '_m_psu_ch2_state') else None

            self._m_psu_ch2_state = ((self.psu_ch_state_num >> 2) & 1)
            return self._m_psu_ch2_state if hasattr(self, '_m_psu_ch2_state') else None

        @property
        def psu_temp_sys(self):
            if hasattr(self, '_m_psu_temp_sys'):
                return self._m_psu_temp_sys if hasattr(self, '_m_psu_temp_sys') else None

            self._m_psu_temp_sys = int(self.psu_temp_sys_str)
            return self._m_psu_temp_sys if hasattr(self, '_m_psu_temp_sys') else None

        @property
        def psu_cur_in(self):
            if hasattr(self, '_m_psu_cur_in'):
                return self._m_psu_cur_in if hasattr(self, '_m_psu_cur_in') else None

            self._m_psu_cur_in = int(self.psu_cur_in_str)
            return self._m_psu_cur_in if hasattr(self, '_m_psu_cur_in') else None

        @property
        def psu_ch1_state(self):
            if hasattr(self, '_m_psu_ch1_state'):
                return self._m_psu_ch1_state if hasattr(self, '_m_psu_ch1_state') else None

            self._m_psu_ch1_state = ((self.psu_ch_state_num >> 1) & 1)
            return self._m_psu_ch1_state if hasattr(self, '_m_psu_ch1_state') else None

        @property
        def psu_ch4_state(self):
            if hasattr(self, '_m_psu_ch4_state'):
                return self._m_psu_ch4_state if hasattr(self, '_m_psu_ch4_state') else None

            self._m_psu_ch4_state = ((self.psu_ch_state_num >> 4) & 1)
            return self._m_psu_ch4_state if hasattr(self, '_m_psu_ch4_state') else None

        @property
        def psu_battery(self):
            if hasattr(self, '_m_psu_battery'):
                return self._m_psu_battery if hasattr(self, '_m_psu_battery') else None

            self._m_psu_battery = int(self.psu_bat_str)
            return self._m_psu_battery if hasattr(self, '_m_psu_battery') else None


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Planetum1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Planetum1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Planetum1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Planetum1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Planetum1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Planetum1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Planetum1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Planetum1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Planetum1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Planetum1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Planetum1.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Planetum1.Repeater(self._io, self, self._root)

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
            self.ax25_info = Planetum1.Tlm(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Uhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.uhf_packet_id_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_trx_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_rf_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_pa_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_digipeater_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_last_digipeater_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_rx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_tx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_act_rssi_raw_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_dcd_rssi_raw_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def uhf_act_rssi_raw(self):
            if hasattr(self, '_m_uhf_act_rssi_raw'):
                return self._m_uhf_act_rssi_raw if hasattr(self, '_m_uhf_act_rssi_raw') else None

            self._m_uhf_act_rssi_raw = int(self.uhf_act_rssi_raw_str)
            return self._m_uhf_act_rssi_raw if hasattr(self, '_m_uhf_act_rssi_raw') else None

        @property
        def uhf_last_digipeater(self):
            if hasattr(self, '_m_uhf_last_digipeater'):
                return self._m_uhf_last_digipeater if hasattr(self, '_m_uhf_last_digipeater') else None

            self._m_uhf_last_digipeater = self.uhf_last_digipeater_str
            return self._m_uhf_last_digipeater if hasattr(self, '_m_uhf_last_digipeater') else None

        @property
        def uhf_pa_temp(self):
            if hasattr(self, '_m_uhf_pa_temp'):
                return self._m_uhf_pa_temp if hasattr(self, '_m_uhf_pa_temp') else None

            self._m_uhf_pa_temp = int(self.uhf_pa_temp_str)
            return self._m_uhf_pa_temp if hasattr(self, '_m_uhf_pa_temp') else None

        @property
        def uhf_uptime_tot(self):
            if hasattr(self, '_m_uhf_uptime_tot'):
                return self._m_uhf_uptime_tot if hasattr(self, '_m_uhf_uptime_tot') else None

            self._m_uhf_uptime_tot = int(self.uhf_uptime_tot_str)
            return self._m_uhf_uptime_tot if hasattr(self, '_m_uhf_uptime_tot') else None

        @property
        def uhf_tx_cnt(self):
            if hasattr(self, '_m_uhf_tx_cnt'):
                return self._m_uhf_tx_cnt if hasattr(self, '_m_uhf_tx_cnt') else None

            self._m_uhf_tx_cnt = int(self.uhf_tx_cnt_str)
            return self._m_uhf_tx_cnt if hasattr(self, '_m_uhf_tx_cnt') else None

        @property
        def uhf_rf_temp(self):
            if hasattr(self, '_m_uhf_rf_temp'):
                return self._m_uhf_rf_temp if hasattr(self, '_m_uhf_rf_temp') else None

            self._m_uhf_rf_temp = int(self.uhf_rf_temp_str)
            return self._m_uhf_rf_temp if hasattr(self, '_m_uhf_rf_temp') else None

        @property
        def uhf_dcd_rssi_raw(self):
            if hasattr(self, '_m_uhf_dcd_rssi_raw'):
                return self._m_uhf_dcd_rssi_raw if hasattr(self, '_m_uhf_dcd_rssi_raw') else None

            self._m_uhf_dcd_rssi_raw = int(self.uhf_dcd_rssi_raw_str)
            return self._m_uhf_dcd_rssi_raw if hasattr(self, '_m_uhf_dcd_rssi_raw') else None

        @property
        def uhf_uptime(self):
            if hasattr(self, '_m_uhf_uptime'):
                return self._m_uhf_uptime if hasattr(self, '_m_uhf_uptime') else None

            self._m_uhf_uptime = int(self.uhf_uptime_str)
            return self._m_uhf_uptime if hasattr(self, '_m_uhf_uptime') else None

        @property
        def uhf_rx_cnt(self):
            if hasattr(self, '_m_uhf_rx_cnt'):
                return self._m_uhf_rx_cnt if hasattr(self, '_m_uhf_rx_cnt') else None

            self._m_uhf_rx_cnt = int(self.uhf_rx_cnt_str)
            return self._m_uhf_rx_cnt if hasattr(self, '_m_uhf_rx_cnt') else None

        @property
        def uhf_reset_cnt(self):
            if hasattr(self, '_m_uhf_reset_cnt'):
                return self._m_uhf_reset_cnt if hasattr(self, '_m_uhf_reset_cnt') else None

            self._m_uhf_reset_cnt = int(self.uhf_reset_cnt_str)
            return self._m_uhf_reset_cnt if hasattr(self, '_m_uhf_reset_cnt') else None

        @property
        def uhf_digipeater_cnt(self):
            if hasattr(self, '_m_uhf_digipeater_cnt'):
                return self._m_uhf_digipeater_cnt if hasattr(self, '_m_uhf_digipeater_cnt') else None

            self._m_uhf_digipeater_cnt = int(self.uhf_digipeater_cnt_str)
            return self._m_uhf_digipeater_cnt if hasattr(self, '_m_uhf_digipeater_cnt') else None

        @property
        def uhf_trx_temp(self):
            if hasattr(self, '_m_uhf_trx_temp'):
                return self._m_uhf_trx_temp if hasattr(self, '_m_uhf_trx_temp') else None

            self._m_uhf_trx_temp = int(self.uhf_trx_temp_str)
            return self._m_uhf_trx_temp if hasattr(self, '_m_uhf_trx_temp') else None


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
            self.ax25_info = Planetum1.Tlm(_io__raw_ax25_info, self, self._root)


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


    class Vhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vhf_packet_id_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_trx_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_rf_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_pa_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_digipeater_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_last_digipeater_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_rx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_tx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_act_rssi_raw_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_dcd_rssi_raw_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def vhf_digipeater_cnt(self):
            if hasattr(self, '_m_vhf_digipeater_cnt'):
                return self._m_vhf_digipeater_cnt if hasattr(self, '_m_vhf_digipeater_cnt') else None

            self._m_vhf_digipeater_cnt = int(self.vhf_digipeater_cnt_str)
            return self._m_vhf_digipeater_cnt if hasattr(self, '_m_vhf_digipeater_cnt') else None

        @property
        def vhf_tx_cnt(self):
            if hasattr(self, '_m_vhf_tx_cnt'):
                return self._m_vhf_tx_cnt if hasattr(self, '_m_vhf_tx_cnt') else None

            self._m_vhf_tx_cnt = int(self.vhf_tx_cnt_str)
            return self._m_vhf_tx_cnt if hasattr(self, '_m_vhf_tx_cnt') else None

        @property
        def vhf_rx_cnt(self):
            if hasattr(self, '_m_vhf_rx_cnt'):
                return self._m_vhf_rx_cnt if hasattr(self, '_m_vhf_rx_cnt') else None

            self._m_vhf_rx_cnt = int(self.vhf_rx_cnt_str)
            return self._m_vhf_rx_cnt if hasattr(self, '_m_vhf_rx_cnt') else None

        @property
        def vhf_last_digipeater(self):
            if hasattr(self, '_m_vhf_last_digipeater'):
                return self._m_vhf_last_digipeater if hasattr(self, '_m_vhf_last_digipeater') else None

            self._m_vhf_last_digipeater = self.vhf_last_digipeater_str
            return self._m_vhf_last_digipeater if hasattr(self, '_m_vhf_last_digipeater') else None

        @property
        def vhf_pa_temp(self):
            if hasattr(self, '_m_vhf_pa_temp'):
                return self._m_vhf_pa_temp if hasattr(self, '_m_vhf_pa_temp') else None

            self._m_vhf_pa_temp = int(self.vhf_pa_temp_str)
            return self._m_vhf_pa_temp if hasattr(self, '_m_vhf_pa_temp') else None

        @property
        def vhf_uptime(self):
            if hasattr(self, '_m_vhf_uptime'):
                return self._m_vhf_uptime if hasattr(self, '_m_vhf_uptime') else None

            self._m_vhf_uptime = int(self.vhf_uptime_str)
            return self._m_vhf_uptime if hasattr(self, '_m_vhf_uptime') else None

        @property
        def vhf_rf_temp(self):
            if hasattr(self, '_m_vhf_rf_temp'):
                return self._m_vhf_rf_temp if hasattr(self, '_m_vhf_rf_temp') else None

            self._m_vhf_rf_temp = int(self.vhf_rf_temp_str)
            return self._m_vhf_rf_temp if hasattr(self, '_m_vhf_rf_temp') else None

        @property
        def vhf_uptime_tot(self):
            if hasattr(self, '_m_vhf_uptime_tot'):
                return self._m_vhf_uptime_tot if hasattr(self, '_m_vhf_uptime_tot') else None

            self._m_vhf_uptime_tot = int(self.vhf_uptime_tot_str)
            return self._m_vhf_uptime_tot if hasattr(self, '_m_vhf_uptime_tot') else None

        @property
        def vhf_trx_temp(self):
            if hasattr(self, '_m_vhf_trx_temp'):
                return self._m_vhf_trx_temp if hasattr(self, '_m_vhf_trx_temp') else None

            self._m_vhf_trx_temp = int(self.vhf_trx_temp_str)
            return self._m_vhf_trx_temp if hasattr(self, '_m_vhf_trx_temp') else None

        @property
        def vhf_dcd_rssi_raw(self):
            if hasattr(self, '_m_vhf_dcd_rssi_raw'):
                return self._m_vhf_dcd_rssi_raw if hasattr(self, '_m_vhf_dcd_rssi_raw') else None

            self._m_vhf_dcd_rssi_raw = int(self.vhf_dcd_rssi_raw_str)
            return self._m_vhf_dcd_rssi_raw if hasattr(self, '_m_vhf_dcd_rssi_raw') else None

        @property
        def vhf_reset_cnt(self):
            if hasattr(self, '_m_vhf_reset_cnt'):
                return self._m_vhf_reset_cnt if hasattr(self, '_m_vhf_reset_cnt') else None

            self._m_vhf_reset_cnt = int(self.vhf_reset_cnt_str)
            return self._m_vhf_reset_cnt if hasattr(self, '_m_vhf_reset_cnt') else None

        @property
        def vhf_act_rssi_raw(self):
            if hasattr(self, '_m_vhf_act_rssi_raw'):
                return self._m_vhf_act_rssi_raw if hasattr(self, '_m_vhf_act_rssi_raw') else None

            self._m_vhf_act_rssi_raw = int(self.vhf_act_rssi_raw_str)
            return self._m_vhf_act_rssi_raw if hasattr(self, '_m_vhf_act_rssi_raw') else None


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Planetum1.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Planetum1.SsidMask(self._io, self, self._root)


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
                _ = Planetum1.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class Obc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc_pass_packet_type = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_rst_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_mcu_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_brd_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_zn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_zp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_freemem_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def obc_uptime(self):
            if hasattr(self, '_m_obc_uptime'):
                return self._m_obc_uptime if hasattr(self, '_m_obc_uptime') else None

            self._m_obc_uptime = int(self.obc_uptime_str)
            return self._m_obc_uptime if hasattr(self, '_m_obc_uptime') else None

        @property
        def obc_temp_xp(self):
            if hasattr(self, '_m_obc_temp_xp'):
                return self._m_obc_temp_xp if hasattr(self, '_m_obc_temp_xp') else None

            self._m_obc_temp_xp = int(self.obc_temp_xp_str)
            return self._m_obc_temp_xp if hasattr(self, '_m_obc_temp_xp') else None

        @property
        def obc_temp_yp(self):
            if hasattr(self, '_m_obc_temp_yp'):
                return self._m_obc_temp_yp if hasattr(self, '_m_obc_temp_yp') else None

            self._m_obc_temp_yp = int(self.obc_temp_yp_str)
            return self._m_obc_temp_yp if hasattr(self, '_m_obc_temp_yp') else None

        @property
        def obc_freemem(self):
            if hasattr(self, '_m_obc_freemem'):
                return self._m_obc_freemem if hasattr(self, '_m_obc_freemem') else None

            self._m_obc_freemem = int(self.obc_freemem_str)
            return self._m_obc_freemem if hasattr(self, '_m_obc_freemem') else None

        @property
        def obc_temp_zn(self):
            if hasattr(self, '_m_obc_temp_zn'):
                return self._m_obc_temp_zn if hasattr(self, '_m_obc_temp_zn') else None

            self._m_obc_temp_zn = int(self.obc_temp_zn_str)
            return self._m_obc_temp_zn if hasattr(self, '_m_obc_temp_zn') else None

        @property
        def obc_temp_brd(self):
            if hasattr(self, '_m_obc_temp_brd'):
                return self._m_obc_temp_brd if hasattr(self, '_m_obc_temp_brd') else None

            self._m_obc_temp_brd = int(self.obc_temp_brd_str)
            return self._m_obc_temp_brd if hasattr(self, '_m_obc_temp_brd') else None

        @property
        def obc_bat(self):
            if hasattr(self, '_m_obc_bat'):
                return self._m_obc_bat if hasattr(self, '_m_obc_bat') else None

            self._m_obc_bat = int(self.obc_bat_str)
            return self._m_obc_bat if hasattr(self, '_m_obc_bat') else None

        @property
        def obc_uptime_tot(self):
            if hasattr(self, '_m_obc_uptime_tot'):
                return self._m_obc_uptime_tot if hasattr(self, '_m_obc_uptime_tot') else None

            self._m_obc_uptime_tot = int(self.obc_uptime_tot_str)
            return self._m_obc_uptime_tot if hasattr(self, '_m_obc_uptime_tot') else None

        @property
        def obc_reset_cnt(self):
            if hasattr(self, '_m_obc_reset_cnt'):
                return self._m_obc_reset_cnt if hasattr(self, '_m_obc_reset_cnt') else None

            self._m_obc_reset_cnt = int(self.obc_rst_cnt_str)
            return self._m_obc_reset_cnt if hasattr(self, '_m_obc_reset_cnt') else None

        @property
        def obc_temp_yn(self):
            if hasattr(self, '_m_obc_temp_yn'):
                return self._m_obc_temp_yn if hasattr(self, '_m_obc_temp_yn') else None

            self._m_obc_temp_yn = int(self.obc_temp_yn_str)
            return self._m_obc_temp_yn if hasattr(self, '_m_obc_temp_yn') else None

        @property
        def obc_temp_xn(self):
            if hasattr(self, '_m_obc_temp_xn'):
                return self._m_obc_temp_xn if hasattr(self, '_m_obc_temp_xn') else None

            self._m_obc_temp_xn = int(self.obc_temp_xn_str)
            return self._m_obc_temp_xn if hasattr(self, '_m_obc_temp_xn') else None

        @property
        def obc_temp_mcu(self):
            if hasattr(self, '_m_obc_temp_mcu'):
                return self._m_obc_temp_mcu if hasattr(self, '_m_obc_temp_mcu') else None

            self._m_obc_temp_mcu = int(self.obc_temp_mcu_str)
            return self._m_obc_temp_mcu if hasattr(self, '_m_obc_temp_mcu') else None

        @property
        def obc_temp_zp(self):
            if hasattr(self, '_m_obc_temp_zp'):
                return self._m_obc_temp_zp if hasattr(self, '_m_obc_temp_zp') else None

            self._m_obc_temp_zp = int(self.obc_temp_zp_str)
            return self._m_obc_temp_zp if hasattr(self, '_m_obc_temp_zp') else None


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
            self.callsign_ror = Planetum1.Callsign(_io__raw_callsign_ror, self, self._root)


    class Tlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.packet_type_q
            if _on == 79:
                self.body = Planetum1.Obc(self._io, self, self._root)
            elif _on == 80:
                self.body = Planetum1.Psu(self._io, self, self._root)
            elif _on == 85:
                self.body = Planetum1.Uhf(self._io, self, self._root)
            elif _on == 86:
                self.body = Planetum1.Vhf(self._io, self, self._root)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor if hasattr(self, '_m_monitor') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_monitor = (self._io.read_bytes_full()).decode(u"utf8")
            self._io.seek(_pos)
            return self._m_monitor if hasattr(self, '_m_monitor') else None

        @property
        def packet_type_q(self):
            if hasattr(self, '_m_packet_type_q'):
                return self._m_packet_type_q if hasattr(self, '_m_packet_type_q') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_packet_type_q = self._io.read_u1()
            self._io.seek(_pos)
            return self._m_packet_type_q if hasattr(self, '_m_packet_type_q') else None



