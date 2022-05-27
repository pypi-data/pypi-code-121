import datetime

import numpy as np
import rnx

def test_obs():

    # Read the data.
    obs = rnx.read("data/example_rinex.05o")

    # Check metadata.
    assert obs.system == 'M'
    assert obs.program == "XXRINEXO V9.9"
    assert obs.author == "AIUB"
    assert obs.created == "24-MAR-01 14:43"
    assert obs.marker == "A 9080"
    assert obs.observer == "BILL SMITH"
    assert obs.agency == "ABC INSTITUTE"
    assert obs.rec_number == "X1234A123"
    assert obs.rec_type == "XX"
    assert obs.rec_version == "ZZZ"
    assert obs.ant_number == "234"
    assert obs.ant_type == "YY"
    assert (obs.pos == [4375274.0, 587466.0, 4589095.0]).all()
    assert obs.tz_approx == 1.0
    assert obs.ant_height == 0.9030
    assert obs.ant_east_ecc == 0.0
    assert obs.ant_north_ecc == 0.0
    assert obs.ts_bow == datetime.datetime(2005, 3, 20)
    assert obs.len == 6

    # Check arrays.
    assert (obs.types == ["P1", "L1", "L2", "P2", "L5"]).all()

    assert obs.t[0] == (datetime.datetime(2005, 3, 24, 13, 10, 36, 2) -
            obs.ts_bow).total_seconds() + 3e-10
    assert obs.t[1] == (datetime.datetime(2005, 3, 24, 13, 10, 54) -
            obs.ts_bow).total_seconds()
    assert obs.t[2] == (datetime.datetime(2005, 3, 24, 13, 11, 48) -
            obs.ts_bow).total_seconds()
    assert obs.t[3] == (datetime.datetime(2005, 3, 24, 13, 12, 6) -
            obs.ts_bow).total_seconds()
    assert obs.t[4] == (datetime.datetime(2005, 3, 24, 13, 14, 12) -
            obs.ts_bow).total_seconds()
    assert obs.t[5] == (datetime.datetime(2005, 3, 24, 13, 14, 48) -
            obs.ts_bow).total_seconds()

    assert obs.T_os[0] == -0.123456789
    assert obs.T_os[1] == -0.123456789
    assert obs.T_os[2] == -0.123456789
    assert obs.T_os[3] == -0.123456987
    assert obs.T_os[4] == -0.123456012
    assert obs.T_os[5] == -0.123456234

    assert (obs.sys == ['E', 'G', 'G', 'G', 'G', 'R', 'R']).all()
    assert (obs.prns == [11, 6, 9, 12, 16, 21, 22]).all()
    assert (obs.svs == ['E11', 'G06', 'G09', 'G12', 'G16', 'R21', 'R22']).all()
    assert obs.sv_ind['E11'] == 0
    assert obs.sv_ind['G06'] == 1
    assert obs.sv_ind['G09'] == 2
    assert obs.sv_ind['G12'] == 3
    assert obs.sv_ind['G16'] == 4
    assert obs.sv_ind['R21'] == 5
    assert obs.sv_ind['R22'] == 6
    assert obs.n_E == [0]
    assert (obs.n_G == [1, 2, 3, 4]).all()
    assert (obs.n_R == [5, 6]).all()
    assert len(obs.n_S) == 0

    P1 = np.array([
        [0.0,20607600.189,20891534.648,23629347.915,0.0,0.0,0.0],
        [0.0,20611072.689,20886075.667,23619095.450,0.0,21345678.576,
            22123456.789],
        [0.0,20621643.727,20869878.790,23588424.398,21110991.756,0.0,0.0],
        [0.0,20625218.088,20864539.693,23578228.338,21112589.384,0.0,0.0],
        [0.0,20650944.902,20828010.354,23507272.372,21124965.133,0.0,0.0],
        [0.0,20658519.895,20817844.743,23487131.045,21128884.159,0.0,0.0]])
    L1 = np.array([
        [0.324, -0.430, -0.120, 0.300, 0.0, 0.0, 0.0],
        [65432.123, 18247.789, -28688.027, -53875.632, 0.0, 12345.567,
            23456.789],
        [0.0, 73797.462, -113803.187, -215050.557, 16119.980, 0.0, 0.0],
        [0.0, 92581.207, -141858.836, -268624.234, 24515.877, 0.0, 0.0],
        [0.0, 227775.130, -333820.093, -212616.150, 89551.302, 0.0, 0.0],
        [0.0, 267583.678, -387242.571, -318463.297, 110143.144, 0.0, 0.0]])
    L2 = np.array([
        [0.0, 0.394, -0.358, -0.353, 0.0, 0.0, 0.0],
        [0.0, 14219.770, -22354.535, -41981.375, 0.0, 0.0, 0.0],
        [0.0, 57505.177, -88677.926, -167571.734, 12560.510, 0.0, 0.0],
        [0.0, 72141.846, -110539.435, -209317.284, 19102.763, 0.0, 0.0],
        [0.0, 177487.651, -260119.395, -165674.789, 69779.626, 0.0, 0.0],
        [0.0, 208507.262, -301747.229, -248152.728, 85825.185, 0.0, 0.0]])
    P2 = np.array([
        [0.0, 20607605.848, 20891541.292, 23629364.158, 0.0, 0.0, 0.0],
        [0.0, 20611078.410, 20886082.101, 23619112.008, 0.0, 0.0, 0.0],
        [0.0, 20621649.276, 20869884.938, 23588439.570, 21110998.441, 0.0, 0.0],
        [0.0, 20625223.795, 20864545.943, 23578244.398, 21112596.187, 0.0, 0.0],
        [0.0, 20650950.363, 20828017.129, 23507288.421, 21124972.275, 0.0, 0.0],
        [0.0, 20658525.869, 20817851.322, 23487146.149, 21128890.776, 0.0,
            0.0]])
    L5 = np.array([
        [0.178, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [48861.586, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
    obs.P1[np.isnan(obs.P1)] = 0.0
    obs.L1[np.isnan(obs.L1)] = 0.0
    obs.L2[np.isnan(obs.L2)] = 0.0
    obs.P2[np.isnan(obs.P2)] = 0.0
    obs.L5[np.isnan(obs.L5)] = 0.0
    assert (obs.P1 == P1).all()
    assert (obs.L1 == L1).all()
    assert (obs.L2 == L2).all()
    assert (obs.P2 == P2).all()
    assert (obs.L5 == L5).all()

    is_vis = (P1 + L1 + L2 + P2 + L5 != 0)
    assert (obs.is_vis == is_vis).all()

    vis_prn = np.zeros((6, 7))
    vis_prn[is_vis[:, 0], 0] = 11
    vis_prn[is_vis[:, 1], 1] = 6
    vis_prn[is_vis[:, 2], 2] = 9
    vis_prn[is_vis[:, 3], 3] = 12
    vis_prn[is_vis[:, 4], 4] = 16
    vis_prn[is_vis[:, 5], 5] = 21
    vis_prn[is_vis[:, 6], 6] = 22
    obs.vis_prn[np.isnan(obs.vis_prn)] = 0.0
    assert (obs.vis_prn == vis_prn).all()

    wf1 = np.array([
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1]])
    wf2 = np.array([
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 2, 2, 1, 1, 1],
        [1, 1, 2, 2, 2, 1, 1],
        [1, 1, 2, 2, 2, 1, 1],
        [1, 1, 2, 2, 2, 1, 1],
        [1, 1, 2, 2, 2, 1, 1]])
    assert (obs.wf1 == wf1).all()
    assert (obs.wf2 == wf2).all()

    assert obs.t_events[0] == (datetime.datetime(2005, 3, 24, 13, 10, 50) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[1] == (datetime.datetime(2005, 3, 24, 13, 11, 0) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[2] == (datetime.datetime(2005, 3, 24, 13, 11, 48) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[3] == (datetime.datetime(2005, 3, 24, 13, 13, 1,
            234567) - obs.ts_bow).total_seconds() + 8e-10
    assert obs.t_events[4] == (datetime.datetime(2005, 3, 24, 13, 13, 1,
            234567) - obs.ts_bow).total_seconds() + 8e-10
    assert obs.t_events[5] == (datetime.datetime(2005, 3, 24, 13, 14, 12) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[6] == (datetime.datetime(2005, 3, 24, 13, 14, 12) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[7] == (datetime.datetime(2005, 3, 24, 13, 14, 12) -
            obs.ts_bow).total_seconds()
    assert obs.t_events[8] == (datetime.datetime(2005, 3, 24, 13, 14, 48) -
            obs.ts_bow).total_seconds()
    assert (obs.events == [4, 2, 3, 5, 4, 4, 6, 4, 4]).all()

    P1_LLI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]])
    assert (obs.P1_LLI == P1_LLI).all()
    L1_LLI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 0]])
    assert (obs.L1_LLI == L1_LLI).all()
    L2_LLI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 5, 0, 0],
        [0, 3, 2, 2, 4, 0, 0]])
    assert (obs.L2_LLI == L2_LLI).all()
    P2_LLI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 4, 0, 0],
        [0, 0, 0, 0, 4, 0, 0]])
    assert (obs.P2_LLI == P2_LLI).all()
    L5_LLI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]])
    assert (obs.L5_LLI == L5_LLI).all()

    P1_SSI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]])
    assert (obs.P1_SSI == P1_SSI).all()
    L1_SSI = np.array([
        [8, 9, 9, 8, 0, 0, 0],
        [5, 9, 9, 8, 0, 5, 5],
        [0, 7, 8, 6, 7, 0, 0],
        [0, 7, 8, 7, 6, 0, 0],
        [0, 7, 6, 7, 6, 0, 0],
        [0, 7, 6, 7, 7, 0, 0]])
    assert (obs.L1_SSI == L1_SSI).all()
    L2_SSI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 4, 5, 4, 3, 0, 0],
        [0, 4, 5, 5, 4, 0, 0],
        [0, 4, 5, 4, 5, 0, 0]])
    assert (obs.L2_SSI == L2_SSI).all()
    P2_SSI = np.array([
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]])
    assert (obs.P2_SSI == P2_SSI).all()
    L5_SSI = np.array([
        [7, 0, 0, 0, 0, 0, 0],
        [7, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0]])
    assert (obs.L5_SSI == L5_SSI).all()

    assert obs.C1_LLI is None


def test_nav():
    nav = rnx.read("data/example_rinex.99n")

    assert nav.program == "XXRINEXN V2.10"
    assert nav.author == "AIUB"
    assert nav.created == "3-SEP-99 15:22"

    assert (nav.ion_alpha ==
            [0.1676e-07, 0.2235e-07, -0.1192e-06, -0.1192e-06]).all()
    assert (nav.ion_beta ==
            [0.1208e+06, 0.1310e+06, -0.1310e+06, -0.1966e+06]).all()
    assert nav.UTC_A0 == 0.133179128170e-6
    assert nav.UTC_A1 == 0.107469588780e-12
    assert nav.UTC_t_ot == 552960
    assert nav.UTC_WN_t == 1025
    assert nav.UTC_Dt_LS == 13
    assert nav.ts_bow == datetime.datetime(1999, 8, 29)

    assert nav.t_oc[0] == (datetime.datetime(1999, 9, 2, 17, 51, 44) -
            nav.ts_bow).total_seconds()
    assert nav.t_oc[1] == (datetime.datetime(1999, 9, 2, 19, 0, 0, 200000) -
            nav.ts_bow).total_seconds()


    eph = nav.ephs[0, 0]
    assert eph.prn == 6
    assert eph.t_oc == nav.t_oc[0]
    assert eph.a_f0     == -0.839701388031e-03
    assert eph.a_f1     == -0.165982783074e-10
    assert eph.a_f2     == 0.000000000001e+00

    assert eph.IODE     == 0.910000000000e+02
    assert eph.C_rs     == 0.934062500000e+02
    assert eph.Delta_n  == 0.116040547840e-08
    assert eph.M_0      == 0.162092304801e+00

    assert eph.C_uc     == 0.484101474285e-05
    assert eph.e        == 0.626740418375e-02
    assert eph.C_us     == 0.652112066746e-05
    assert eph.sqrtA    == 0.515365489006e+04

    assert eph.t_oe     == 0.409904000000e+06
    assert eph.C_ic     == -0.242143869400e-07
    assert eph.Omega_0  == 0.329237003460e+00
    assert eph.C_is     == -0.596046447754e-07

    assert eph.i_0      == 0.111541663136e+01
    assert eph.C_rc     == 0.326593750000e+03
    assert eph.omega    == 0.206958726335e+01
    assert eph.DOmega   == -0.638312302555e-08

    assert eph.Di       == 0.307155651409e-09
    assert eph.cL2      == 0.000000000002e+00
    assert eph.WN       == 0.102500000000e+04
    assert eph.pL2      == 0.000000000003e+00

    assert eph.acc      == 0.000000000004e+00
    assert eph.health   == 5.000000000000e+00
    assert eph.T_GD     == 0.000000000006e+00
    assert eph.IODC     == 0.910000000000e+02

    assert eph.t_sv     == 0.406800000000e+06
    assert eph.T_fit    == 0.000000000007e+00*3600


    eph = nav.ephs[1, 1]
    assert eph.prn == 13
    assert eph.t_oc == nav.t_oc[1]
    assert eph.a_f0     == 0.490025617182e-03
    assert eph.a_f1     == 0.204636307899e-11
    assert eph.a_f2     == 0.000000000008e+00

    assert eph.IODE     == 0.133000000000e+03
    assert eph.C_rs     == -0.963125000000e+02
    assert eph.Delta_n  == 0.146970407622e-08
    assert eph.M_0      == 0.292961152146e+01

    assert eph.C_uc     == -0.498816370964e-05
    assert eph.e        == 0.200239347760e-02
    assert eph.C_us     == 0.928156077862e-05
    assert eph.sqrtA    == 0.515328476143e+04

    assert eph.t_oe     == 0.414000000000e+06
    assert eph.C_ic     == -0.279396772385e-07
    assert eph.Omega_0  == 0.243031939942e+01
    assert eph.C_is     == -0.558793544769e-07

    assert eph.i_0      == 0.110192796930e+01
    assert eph.C_rc     == 0.271187500000e+03
    assert eph.omega    == -0.232757915425e+01
    assert eph.DOmega   == -0.619632953057e-08

    assert eph.Di       == -0.785747015231e-11
    assert eph.cL2      == 0.000000000009e+00
    assert eph.WN       == 0.102500000000e+04
    assert eph.pL2      == 0.000000000001e+00

    assert eph.acc      == 0.000000000002e+00
    assert eph.health   == 3.000000000000e+00
    assert eph.T_GD     == 0.000000000004e+00
    assert eph.IODC     == 0.389000000000e+03

    assert eph.t_sv     == 0.410400000000e+06
    assert eph.T_fit    == 0.000000000005e+00*3600
