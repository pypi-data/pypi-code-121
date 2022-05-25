import pytest

from src.zos_utilities import lpar


class Test_LPAR_Parse_D_M_CORE():

    @pytest.fixture
    def good_input_procview_cpu(self):
        return [
            'IEE174I 14.12.45 DISPLAY M 781                   ',
            'CORE STATUS: HD=Y   MT=1                         ',
            'ID    ST   ID RANGE   VP  ISCM  CPU THREAD STATUS',
            '0000   +   0000-0000  H   FC00  +                ',
            '0001   +   0001-0001  M   0000  +                ',
            '0002   +   0002-0002  LP  0000  +                ',
            '0003   +   0003-0003  LP  0000  +                ',
            '0004   +   0004-0004  LP  0000  +                ',
            '0005   +   0005-0005  LP  0000  +                ',
            '0006   +I  0006-0006  H   0200  +                ',
            '0007   +I  0007-0007  H   0200  +                ',
            '0008   +I  0008-0008  H   0200  +                ',
            '0009   +I  0009-0009  H   0200  +                ',
            '000A   -I  000A-000A                             ',
            '000B   -I  000B-000B                             ',
            '000C   -I  000C-000C                             ',
            '000D   -I  000D-000D                             ',
            '000E   -I  000E-000E                             ',
            '000F   -I  000F-000F                             ',
            '',
            'CPC ND = 008562.T02.IBM.02.0000000790A8                       ',
            'CPC SI = 8562.Z06.IBM.02.00000000000790A8                     ',
            '         Model: T02                                          ',
            'CPC ID = 00                                                   ',
            'CPC NAME = T256                                               ',
            'LP NAME = S5E        LP ID = 21                               ',
            'CSS ID  = 2                                                   ',
            'MIF ID  = 1                                                   ',
            '                                                             ',
            '+ ONLINE    - OFFLINE    N NOT AVAILABLE    / MIXED STATE    ',
            'W WLM-MANAGED                                                 ',
            '                                                             ',
            'I        INTEGRATED INFORMATION PROCESSOR (zIIP)              ',
            'CPC ND  CENTRAL PROCESSING COMPLEX NODE DESCRIPTOR            ',
            'CPC SI  SYSTEM INFORMATION FROM STSI INSTRUCTION              ',
            'CPC ID  CENTRAL PROCESSING COMPLEX IDENTIFIER                 ',
            'CPC NAME CENTRAL PROCESSING COMPLEX NAME                      ',
            'LP NAME  LOGICAL PARTITION NAME                               ',
            'LP ID    LOGICAL PARTITION IDENTIFIER                         ',
            'CSS ID   CHANNEL SUBSYSTEM IDENTIFIER                         ',
            'MIF ID   MULTIPLE IMAGE FACILITY IMAGE IDENTIFIER             '
        ]

    @pytest.fixture
    def good_input_procview_core(self):
        return ["IEE174I 14.41.05 DISPLAY M 124                  ",
                "CORE STATUS: HD=Y   MT=2  MT_MODE: CP=1  zIIP=2",
                "ID    ST   ID RANGE   VP  ISCM  CPU THREAD STATUS          ",
                "0000   +   0000-0001  H   FC00  +N                         ",
                "0001   +   0002-0003  M   0000  +N                         ",
                "0002   +   0004-0005  M   0000  +N                         ",
                "0003   +   0006-0007  LP  0000  +N                         ",
                "0004   +   0008-0009  LP  0000  +N                         ",
                "0005   +   000A-000B  LP  0000  +N                         ",
                "0006   +   000C-000D  LP  0000  +N                         ",
                "0007   +   000E-000F  LP  0000  +N                         ",
                "0008   +   0010-0011  LP  0000  +N                         ",
                "0009   +   0012-0013  LP  0000  +N                         ",
                "000A   +   0014-0015  LP  0000  +N                         ",
                "000B   +   0016-0017  LP  0000  +N                         ",
                "000C   +   0018-0019  LP  0000  +N                         ",
                "000D   +   001A-001B  LP  0000  +N                         ",
                "000E   +   001C-001D  LP  0000  +N                         ",
                "000F   +   001E-001F  LP  0000  +N                         ",
                "0010   +   0020-0021  LP  0000  +N                         ",
                "0011   +   0022-0023  LP  0000  +N                         ",
                "0012   +   0024-0025  LP  0000  +N                         ",
                "0013   +   0026-0027  LP  0000  +N                         ",
                "0014   +I  0028-0029  H   0200  ++                         ",
                "0015   +I  002A-002B  M   0200  ++                         ",
                "0016   +I  002C-002D  M   0200  ++                         ",
                "0017   -I  002E-002F                                       ",
                "0018   -I  0030-0031                                       ",
                "0019   -I  0032-0033                                       ",
                "001A   -I  0034-0035                                       ",
                "001B   -I  0036-0037                                       ",
                "001C   -I  0038-0039                                       ",
                "001D   -I  003A-003B                                       ",
                "001E   -I  003C-003D                                       ",
                "001F   -I  003E-003F                                       ",
                "0020   -I  0040-0041                                       ",
                "0021   -I  0042-0043                                       ",
                "0022   -I  0044-0045                                       ",
                "0023   -I  0046-0047                                       ",
                "0024   NI  0048-0049                                       ",
                "0025   NI  004A-004B                                       ",
                "0026   NI  004C-004D                                       ",
                "0027   NI  004E-004F                                       ",
                "0028   NI  0050-0051                                       ",
                "0029   NI  0052-0053                                       ",
                "002A   NI  0054-0055                                       ",
                "002B   NI  0056-0057                                       ",
                "",
                "CPC ND = 008561.T01.IBM.02.000000000078                    ",
                "CPC SI = 8561.776.IBM.02.0000000000000078                  ",
                "          Model: T01                                       ",
                "CPC ID = 00                                                ",
                "CPC NAME = T78                                             ",
                "LP NAME = CB8A       LP ID = 1B                            ",
                "CSS ID  = 1                                                ",
                "MIF ID  = B                                                ",
                "",
                "+ ONLINE    - OFFLINE    N NOT AVAILABLE    / MIXED STATE ",
                "W WLM-MANAGED                                              ",
                ""                                                          ","
                "I        INTEGRATED INFORMATION PROCESSOR (zIIP)           ",
                "CPC ND  CENTRAL PROCESSING COMPLEX NODE DESCRIPTOR         ",
                "CPC SI  SYSTEM INFORMATION FROM STSI INSTRUCTION           ",
                "CPC ID  CENTRAL PROCESSING COMPLEX IDENTIFIER              ",
                "CPC NAME CENTRAL PROCESSING COMPLEX NAME                   ",
                "LP NAME  LOGICAL PARTITION NAME                            ",
                "LP ID    LOGICAL PARTITION IDENTIFIER                      ",
                "CSS ID   CHANNEL SUBSYSTEM IDENTIFIER                      ",
                "MIF ID   MULTIPLE IMAGE FACILITY IMAGE IDENTIFIER          "
                ]

    def test_lpar_parse_d_m_core_procview_cpu(self, good_input_procview_cpu):
        test_lpar = lpar.LPAR()

        test_lpar.parse_d_m_core(good_input_procview_cpu)

        assert test_lpar.hiperdispatch is True
        assert test_lpar.mt_mode == 1
        assert test_lpar.cp_mt_mode is None
        assert test_lpar.ziip_mt_mode is None

        assert len(test_lpar.logical_processors) == 16

        core_000A = test_lpar.logical_processors["000A"]

        assert core_000A.type == "zIIP"
        assert core_000A.online is False
        assert core_000A.lowid == "000A"
        assert core_000A.highid == "000A"
        assert core_000A.polarity is None
        assert core_000A.parked is False
        assert core_000A.subclassmask is None
        assert core_000A.core_1_state is None
        assert core_000A.core_2_state is None

        assert test_lpar.cpc_nd == "008562.T02.IBM.02.0000000790A8"
        assert test_lpar.cpc_si == "8562.Z06.IBM.02.00000000000790A8"
        assert test_lpar.cpc_model == "T02"
        assert test_lpar.cpc_id == "00"
        assert test_lpar.cpc_name == "T256"
        assert test_lpar.lpar_name == "S5E"
        assert test_lpar.lpar_id == "21"
        assert test_lpar.css_id == "2"
        assert test_lpar.mif_id == "1"


    def test_lpar_parse_d_m_core_procview_cpu_with_leading_spaces(self, good_input_procview_cpu):
        test_lpar = lpar.LPAR()

        leading_spaces_input = ['  {} '.format(x) for x in good_input_procview_cpu]

        test_lpar.parse_d_m_core(leading_spaces_input)

        assert test_lpar.hiperdispatch is True
        assert test_lpar.mt_mode == 1
        assert test_lpar.cp_mt_mode is None
        assert test_lpar.ziip_mt_mode is None

        assert len(test_lpar.logical_processors) == 16

        core_000A = test_lpar.logical_processors["000A"]

        assert core_000A.type == "zIIP"
        assert core_000A.online is False
        assert core_000A.lowid == "000A"
        assert core_000A.highid == "000A"
        assert core_000A.polarity is None
        assert core_000A.parked is False
        assert core_000A.subclassmask is None
        assert core_000A.core_1_state is None
        assert core_000A.core_2_state is None

        assert test_lpar.cpc_nd == "008562.T02.IBM.02.0000000790A8"
        assert test_lpar.cpc_si == "8562.Z06.IBM.02.00000000000790A8"
        assert test_lpar.cpc_model == "T02"
        assert test_lpar.cpc_id == "00"
        assert test_lpar.cpc_name == "T256"
        assert test_lpar.lpar_name == "S5E"
        assert test_lpar.lpar_id == "21"
        assert test_lpar.css_id == "2"
        assert test_lpar.mif_id == "1"


    def test_lpar_parse_d_m_core_procview_core(self, good_input_procview_core):
        test_lpar = lpar.LPAR()
        test_lpar.parse_d_m_core(good_input_procview_core)

        assert test_lpar.hiperdispatch is True
        assert test_lpar.mt_mode == 2
        assert test_lpar.cp_mt_mode == 1
        assert test_lpar.ziip_mt_mode == 2

        assert len(test_lpar.logical_processors) == 44

        core_0014 = test_lpar.logical_processors["0014"]

        assert core_0014.type == "zIIP"
        assert core_0014.online is True
        assert core_0014.lowid == "0028"
        assert core_0014.highid == "0029"
        assert core_0014.polarity == "H"
        assert core_0014.parked is False
        assert core_0014.subclassmask == "0200"
        assert core_0014.core_1_state == "online"
        assert core_0014.core_2_state == "online"

        assert test_lpar.cpc_nd == "008561.T01.IBM.02.000000000078"
        assert test_lpar.cpc_si == "8561.776.IBM.02.0000000000000078"
        assert test_lpar.cpc_model == "T01"
        assert test_lpar.cpc_id == "00"
        assert test_lpar.cpc_name == "T78"
        assert test_lpar.lpar_name == "CB8A"
        assert test_lpar.lpar_id == "1B"
        assert test_lpar.css_id == "1"
        assert test_lpar.mif_id == "B"

    def test_missing_IEE174I(self, good_input_procview_core):
        bad_input = ["14.41.05 DISPLAY M 124                  "] + \
                    good_input_procview_core[1:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_hyperdispatch_value_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=L   MT=2  MT_MODE: CP=1  zIIP=2"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_mt_statement_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=Y   TM=2  MT_MODE:2 CP=1  zIIP=2"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_mt_mode_value_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=Y   MT=L  MT_MODE: CP=1  zIIP=2"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_cp_mt_mode_value_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=Y   MT=L  MT_MODE:2 CP=N  zIIP=2"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_cp_mt_mode_statement_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=Y   MT=L  MT_MODE:2 PC=2  zIIP=2"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)

    def test_bad_ziip_mt_mode_value_procview_core(self, good_input_procview_core):
        bad_input = [good_input_procview_core[0]] + \
                    ["CORE STATUS: HD=Y   MT=L  MT_MODE:2 CP=1  zIIP=J"] + \
                    good_input_procview_core[2:]

        with pytest.raises(lpar.LPARException):
            test_lpar = lpar.LPAR()
            test_lpar.parse_d_m_core(bad_input)
