# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bdsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field obc_pass_packet_type: ax25_frame.payload.ax25_info.body.obc_pass_packet_type
    :field obc_rst_cnt_str: ax25_frame.payload.ax25_info.body.obc_rst_cnt_str
    :field obc_uptime_str: ax25_frame.payload.ax25_info.body.obc_uptime_str
    :field obc_bat_str: ax25_frame.payload.ax25_info.body.obc_bat_str
    :field obc_temp_obc_str: ax25_frame.payload.ax25_info.body.obc_temp_obc_str
    :field obc_temp_zn_str: ax25_frame.payload.ax25_info.body.obc_temp_zn_str
    :field obc_temp_xp_str: ax25_frame.payload.ax25_info.body.obc_temp_xp_str
    :field obc_temp_yp_str: ax25_frame.payload.ax25_info.body.obc_temp_yp_str
    :field obc_temp_yn_str: ax25_frame.payload.ax25_info.body.obc_temp_yn_str
    :field obc_temp_xn_str: ax25_frame.payload.ax25_info.body.obc_temp_xn_str
    :field obc_freemem_str: ax25_frame.payload.ax25_info.body.obc_freemem_str
    :field obc_pld_state_str: ax25_frame.payload.ax25_info.body.obc_pld_state_str
    :field obc_pld_prog_str: ax25_frame.payload.ax25_info.body.obc_pld_prog_str
    :field obc_pld_hw_state_str: ax25_frame.payload.ax25_info.body.obc_pld_hw_state_str
    :field obc_psu_uptime_str: ax25_frame.payload.ax25_info.body.obc_psu_uptime_str
    :field obc_crc_str: ax25_frame.payload.ax25_info.body.obc_crc_str
    :field obc_reset_cnt: ax25_frame.payload.ax25_info.body.obc_reset_cnt
    :field obc_uptime: ax25_frame.payload.ax25_info.body.obc_uptime
    :field obc_bat: ax25_frame.payload.ax25_info.body.obc_bat
    :field obc_temp_obc: ax25_frame.payload.ax25_info.body.obc_temp_obc
    :field obc_temp_zn: ax25_frame.payload.ax25_info.body.obc_temp_zn
    :field obc_temp_xp: ax25_frame.payload.ax25_info.body.obc_temp_xp
    :field obc_temp_yp: ax25_frame.payload.ax25_info.body.obc_temp_yp
    :field obc_temp_yn: ax25_frame.payload.ax25_info.body.obc_temp_yn
    :field obc_temp_xn: ax25_frame.payload.ax25_info.body.obc_temp_xn
    :field obc_freemem: ax25_frame.payload.ax25_info.body.obc_freemem
    :field obc_pld_state: ax25_frame.payload.ax25_info.body.obc_pld_state
    :field obc_pld_prog: ax25_frame.payload.ax25_info.body.obc_pld_prog
    :field obc_pld_hw_state: ax25_frame.payload.ax25_info.body.obc_pld_hw_state
    :field obc_psu_uptime: ax25_frame.payload.ax25_info.body.obc_psu_uptime
    :field trx_uptime_str: ax25_frame.payload.ax25_info.body.trx_uptime_str
    :field trx_uptime_total_str: ax25_frame.payload.ax25_info.body.trx_uptime_total_str
    :field trx_reset_cnt_str: ax25_frame.payload.ax25_info.body.trx_reset_cnt_str
    :field trx_trx_temp_str: ax25_frame.payload.ax25_info.body.trx_trx_temp_str
    :field trx_rf_temp_str: ax25_frame.payload.ax25_info.body.trx_rf_temp_str
    :field trx_pa_temp_str: ax25_frame.payload.ax25_info.body.trx_pa_temp_str
    :field trx_digipeater_cnt_str: ax25_frame.payload.ax25_info.body.trx_digipeater_cnt_str
    :field trx_last_digipeater_str: ax25_frame.payload.ax25_info.body.trx_last_digipeater_str
    :field trx_rx_cnt_str: ax25_frame.payload.ax25_info.body.trx_rx_cnt_str
    :field trx_tx_cnt_str: ax25_frame.payload.ax25_info.body.trx_tx_cnt_str
    :field trx_act_rssi_raw_str: ax25_frame.payload.ax25_info.body.trx_act_rssi_raw_str
    :field trx_dcd_rssi_raw_str: ax25_frame.payload.ax25_info.body.trx_dcd_rssi_raw_str
    :field trx_uptime: ax25_frame.payload.ax25_info.body.trx_uptime
    :field trx_uptime_total: ax25_frame.payload.ax25_info.body.trx_uptime_total
    :field trx_reset_cnt: ax25_frame.payload.ax25_info.body.trx_reset_cnt
    :field trx_trx_temp: ax25_frame.payload.ax25_info.body.trx_trx_temp
    :field trx_rf_temp: ax25_frame.payload.ax25_info.body.trx_rf_temp
    :field trx_pa_temp: ax25_frame.payload.ax25_info.body.trx_pa_temp
    :field trx_digipeater_cnt: ax25_frame.payload.ax25_info.body.trx_digipeater_cnt
    :field trx_last_digipeater: ax25_frame.payload.ax25_info.body.trx_last_digipeater
    :field trx_rx_cnt: ax25_frame.payload.ax25_info.body.trx_rx_cnt
    :field trx_tx_cnt: ax25_frame.payload.ax25_info.body.trx_tx_cnt
    :field trx_act_rssi_raw: ax25_frame.payload.ax25_info.body.trx_act_rssi_raw
    :field trx_dcd_rssi_raw: ax25_frame.payload.ax25_info.body.trx_dcd_rssi_raw
    :field monitor: ax25_frame.payload.ax25_info.monitor
    :field packet_type_q: ax25_frame.payload.ax25_info.packet_type_q
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Bdsat.Ax25Frame(self._io, self, self._root)

    class Trx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.trx_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_uptime_total_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_trx_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_rf_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_pa_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_digipeater_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_last_digipeater_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_rx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_tx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_act_rssi_raw_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.trx_dcd_rssi_raw_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def trx_act_rssi_raw(self):
            if hasattr(self, '_m_trx_act_rssi_raw'):
                return self._m_trx_act_rssi_raw if hasattr(self, '_m_trx_act_rssi_raw') else None

            self._m_trx_act_rssi_raw = int(self.trx_act_rssi_raw_str)
            return self._m_trx_act_rssi_raw if hasattr(self, '_m_trx_act_rssi_raw') else None

        @property
        def trx_uptime(self):
            if hasattr(self, '_m_trx_uptime'):
                return self._m_trx_uptime if hasattr(self, '_m_trx_uptime') else None

            self._m_trx_uptime = int(self.trx_uptime_str)
            return self._m_trx_uptime if hasattr(self, '_m_trx_uptime') else None

        @property
        def trx_uptime_total(self):
            if hasattr(self, '_m_trx_uptime_total'):
                return self._m_trx_uptime_total if hasattr(self, '_m_trx_uptime_total') else None

            self._m_trx_uptime_total = int(self.trx_uptime_total_str)
            return self._m_trx_uptime_total if hasattr(self, '_m_trx_uptime_total') else None

        @property
        def trx_last_digipeater(self):
            if hasattr(self, '_m_trx_last_digipeater'):
                return self._m_trx_last_digipeater if hasattr(self, '_m_trx_last_digipeater') else None

            self._m_trx_last_digipeater = self.trx_last_digipeater_str
            return self._m_trx_last_digipeater if hasattr(self, '_m_trx_last_digipeater') else None

        @property
        def trx_rf_temp(self):
            if hasattr(self, '_m_trx_rf_temp'):
                return self._m_trx_rf_temp if hasattr(self, '_m_trx_rf_temp') else None

            self._m_trx_rf_temp = int(self.trx_rf_temp_str)
            return self._m_trx_rf_temp if hasattr(self, '_m_trx_rf_temp') else None

        @property
        def trx_tx_cnt(self):
            if hasattr(self, '_m_trx_tx_cnt'):
                return self._m_trx_tx_cnt if hasattr(self, '_m_trx_tx_cnt') else None

            self._m_trx_tx_cnt = int(self.trx_tx_cnt_str)
            return self._m_trx_tx_cnt if hasattr(self, '_m_trx_tx_cnt') else None

        @property
        def trx_digipeater_cnt(self):
            if hasattr(self, '_m_trx_digipeater_cnt'):
                return self._m_trx_digipeater_cnt if hasattr(self, '_m_trx_digipeater_cnt') else None

            self._m_trx_digipeater_cnt = int(self.trx_digipeater_cnt_str)
            return self._m_trx_digipeater_cnt if hasattr(self, '_m_trx_digipeater_cnt') else None

        @property
        def trx_rx_cnt(self):
            if hasattr(self, '_m_trx_rx_cnt'):
                return self._m_trx_rx_cnt if hasattr(self, '_m_trx_rx_cnt') else None

            self._m_trx_rx_cnt = int(self.trx_rx_cnt_str)
            return self._m_trx_rx_cnt if hasattr(self, '_m_trx_rx_cnt') else None

        @property
        def trx_reset_cnt(self):
            if hasattr(self, '_m_trx_reset_cnt'):
                return self._m_trx_reset_cnt if hasattr(self, '_m_trx_reset_cnt') else None

            self._m_trx_reset_cnt = int(self.trx_reset_cnt_str)
            return self._m_trx_reset_cnt if hasattr(self, '_m_trx_reset_cnt') else None

        @property
        def trx_trx_temp(self):
            if hasattr(self, '_m_trx_trx_temp'):
                return self._m_trx_trx_temp if hasattr(self, '_m_trx_trx_temp') else None

            self._m_trx_trx_temp = int(self.trx_trx_temp_str)
            return self._m_trx_trx_temp if hasattr(self, '_m_trx_trx_temp') else None

        @property
        def trx_dcd_rssi_raw(self):
            if hasattr(self, '_m_trx_dcd_rssi_raw'):
                return self._m_trx_dcd_rssi_raw if hasattr(self, '_m_trx_dcd_rssi_raw') else None

            self._m_trx_dcd_rssi_raw = int(self.trx_dcd_rssi_raw_str)
            return self._m_trx_dcd_rssi_raw if hasattr(self, '_m_trx_dcd_rssi_raw') else None

        @property
        def trx_pa_temp(self):
            if hasattr(self, '_m_trx_pa_temp'):
                return self._m_trx_pa_temp if hasattr(self, '_m_trx_pa_temp') else None

            self._m_trx_pa_temp = int(self.trx_pa_temp_str)
            return self._m_trx_pa_temp if hasattr(self, '_m_trx_pa_temp') else None


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Bdsat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Bdsat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Bdsat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Bdsat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Bdsat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Bdsat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Bdsat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Bdsat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Bdsat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Bdsat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Bdsat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Bdsat.Repeater(self._io, self, self._root)

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
            self.ax25_info = Bdsat.Tlm(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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
            self.ax25_info = Bdsat.Tlm(_io__raw_ax25_info, self, self._root)


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
            self.rpt_callsign_raw = Bdsat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Bdsat.SsidMask(self._io, self, self._root)


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
                _ = Bdsat.Repeaters(self._io, self, self._root)
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
            self.obc_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_obc_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_zn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_freemem_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_pld_state_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_pld_prog_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_pld_hw_state_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_psu_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_crc_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def obc_pld_hw_state(self):
            if hasattr(self, '_m_obc_pld_hw_state'):
                return self._m_obc_pld_hw_state if hasattr(self, '_m_obc_pld_hw_state') else None

            self._m_obc_pld_hw_state = int(self.obc_pld_hw_state_str)
            return self._m_obc_pld_hw_state if hasattr(self, '_m_obc_pld_hw_state') else None

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
        def obc_psu_uptime(self):
            if hasattr(self, '_m_obc_psu_uptime'):
                return self._m_obc_psu_uptime if hasattr(self, '_m_obc_psu_uptime') else None

            self._m_obc_psu_uptime = int(self.obc_psu_uptime_str)
            return self._m_obc_psu_uptime if hasattr(self, '_m_obc_psu_uptime') else None

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
        def obc_pld_prog(self):
            if hasattr(self, '_m_obc_pld_prog'):
                return self._m_obc_pld_prog if hasattr(self, '_m_obc_pld_prog') else None

            self._m_obc_pld_prog = int(self.obc_pld_prog_str)
            return self._m_obc_pld_prog if hasattr(self, '_m_obc_pld_prog') else None

        @property
        def obc_temp_zn(self):
            if hasattr(self, '_m_obc_temp_zn'):
                return self._m_obc_temp_zn if hasattr(self, '_m_obc_temp_zn') else None

            self._m_obc_temp_zn = int(self.obc_temp_zn_str)
            return self._m_obc_temp_zn if hasattr(self, '_m_obc_temp_zn') else None

        @property
        def obc_temp_obc(self):
            if hasattr(self, '_m_obc_temp_obc'):
                return self._m_obc_temp_obc if hasattr(self, '_m_obc_temp_obc') else None

            self._m_obc_temp_obc = int(self.obc_temp_obc_str)
            return self._m_obc_temp_obc if hasattr(self, '_m_obc_temp_obc') else None

        @property
        def obc_bat(self):
            if hasattr(self, '_m_obc_bat'):
                return self._m_obc_bat if hasattr(self, '_m_obc_bat') else None

            self._m_obc_bat = int(self.obc_bat_str)
            return self._m_obc_bat if hasattr(self, '_m_obc_bat') else None

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
        def obc_pld_state(self):
            if hasattr(self, '_m_obc_pld_state'):
                return self._m_obc_pld_state if hasattr(self, '_m_obc_pld_state') else None

            self._m_obc_pld_state = int(self.obc_pld_state_str)
            return self._m_obc_pld_state if hasattr(self, '_m_obc_pld_state') else None


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
            self.callsign_ror = Bdsat.Callsign(_io__raw_callsign_ror, self, self._root)


    class Tlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.packet_type_q
            if _on == 79:
                self.body = Bdsat.Obc(self._io, self, self._root)
            else:
                self.body = Bdsat.Trx(self._io, self, self._root)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor if hasattr(self, '_m_monitor') else None

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_monitor = (self._io.read_bytes_full()).decode(u"ASCII")
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



