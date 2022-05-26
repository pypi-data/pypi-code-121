import pytest

import pathlib

import uproot

from tdub.data import (
    SampleInfo,
    Region,
    avoids_for,
    branches_from,
    categorize_branches,
    features_for,
    selection_for,
    selection_branches,
    selection_as_numexpr,
    selection_as_root,
)

from tdub.config import (
    FEATURESET_1j1b,
    FEATURESET_2j1b,
    FEATURESET_2j2b,
    SELECTION_1j1b,
    SELECTION_2j1b,
    SELECTION_2j2b,
    AVOID_IN_CLF_1j1b,
    AVOID_IN_CLF_2j1b,
    AVOID_IN_CLF_2j2b,
)


def test_sample_info():
    s1 = "ttbar_410472_AFII_MC16d_nominal.root"
    s2 = "ttbar_410472_AFII_MC16e_EG_SCALE_ALL__1up"
    s3 = "tW_DS_410657_FS_MC16d_EG_RESOLUTION_ALL__1down"
    s4 = "Diboson_364255_FS_MC16e_nominal.root"
    s5 = "Data17_data17_Data_Data_nominal.root"
    s6 = "MCNP_Zjets_364137_FS_MC16a_nominal.root"
    s7 = "tW_DR_410648_AFII_MC16d_nominal.bdtresp.npy"

    si1 = SampleInfo(s1)
    si2 = SampleInfo(s2)
    si3 = SampleInfo(s3)
    si4 = SampleInfo(s4)
    si5 = SampleInfo(s5)
    si6 = SampleInfo(s6)
    si7 = SampleInfo(s7)

    assert si1.phy_process == "ttbar"
    assert si1.dsid == 410472
    assert si1.sim_type == "AFII"
    assert si1.campaign == "MC16d"
    assert si1.tree == "nominal"

    assert si2.phy_process == "ttbar"
    assert si2.dsid == 410472
    assert si2.sim_type == "AFII"
    assert si2.campaign == "MC16e"
    assert si2.tree == "EG_SCALE_ALL__1up"

    assert si3.phy_process == "tW_DS"
    assert si3.dsid == 410657
    assert si3.sim_type == "FS"
    assert si3.campaign == "MC16d"
    assert si3.tree == "EG_RESOLUTION_ALL__1down"

    assert si4.phy_process == "Diboson"
    assert si4.dsid == 364255
    assert si4.sim_type == "FS"
    assert si4.campaign == "MC16e"
    assert si4.tree == "nominal"

    assert si5.phy_process == "Data"
    assert si5.dsid == 0
    assert si5.sim_type == "Data"
    assert si5.campaign == "Data"
    assert si5.tree == "nominal"

    assert si6.phy_process == "MCNP"
    assert si6.dsid == 364137
    assert si6.sim_type == "FS"
    assert si6.campaign == "MC16a"
    assert si6.tree == "nominal"

    assert si7.phy_process == "tW_DR"
    assert si7.dsid == 410648
    assert si7.sim_type == "AFII"
    assert si7.campaign == "MC16d"
    assert si7.tree == "nominal"


def test_bad_sample_info():
    bad = "tW_DR_410_bad"
    with pytest.raises(ValueError) as err:
        SampleInfo(bad)
    assert str(err.value) == "tW_DR_410_bad cannot be parsed by SampleInfo regex"


def test_Region_from_str():
    assert Region.from_str("2j2b") == Region.r2j2b
    assert Region.from_str("1j1b") == Region.r1j1b
    assert Region.from_str("2j1b") == Region.r2j1b

    assert Region.from_str("r2j2b") == Region.r2j2b
    assert Region.from_str("r1j1b") == Region.r1j1b
    assert Region.from_str("r2j1b") == Region.r2j1b

    assert Region.from_str("reg2j2b") == Region.r2j2b
    assert Region.from_str("reg1j1b") == Region.r1j1b
    assert Region.from_str("reg2j1b") == Region.r2j1b


def test_features_for():
    assert features_for("reg2j1b") == FEATURESET_2j1b
    assert features_for("2j2b") == FEATURESET_2j2b
    assert features_for(Region.r1j1b) == FEATURESET_1j1b
    assert features_for("r2j1b") == FEATURESET_2j1b
    assert features_for(Region.r2j2b) == FEATURESET_2j2b
    assert features_for("reg1j1b") == FEATURESET_1j1b
    assert features_for("1j1b") == FEATURESET_1j1b


def test_avoids_for():
    assert avoids_for("reg1j1b") == AVOID_IN_CLF_1j1b
    assert avoids_for("r1j1b") == AVOID_IN_CLF_1j1b
    assert avoids_for("1j1b") == AVOID_IN_CLF_1j1b
    assert avoids_for(Region.r1j1b) == AVOID_IN_CLF_1j1b
    assert avoids_for("reg2j1b") == AVOID_IN_CLF_2j1b
    assert avoids_for("r2j1b") == AVOID_IN_CLF_2j1b
    assert avoids_for("2j1b") == AVOID_IN_CLF_2j1b
    assert avoids_for(Region.r2j1b) == AVOID_IN_CLF_2j1b
    assert avoids_for("reg2j2b") == AVOID_IN_CLF_2j2b
    assert avoids_for("r2j2b") == AVOID_IN_CLF_2j2b
    assert avoids_for("2j2b") == AVOID_IN_CLF_2j2b
    assert avoids_for(Region.r2j2b) == AVOID_IN_CLF_2j2b


def test_branches_from():
    f1 = uproot.open("tests/test_data/testfile1.root")
    f2 = "tests/test_data/testfile1.root"
    f3 = ["tests/test_data/testfile1.root"]
    b1 = sorted(branches_from(f1))
    b2 = sorted(branches_from(f2))
    b3 = sorted(branches_from(f3))
    assert b1 == b2
    assert b2 == b3
    f4 = pathlib.PosixPath(f2)
    b4 = sorted(branches_from(f4, ignore_weights=True))
    b5 = sorted(branches_from(f2, ignore_weights=True))
    assert b4 == b5
    assert all(["weight_" not in b for b in b5])


def test_categorize_branches():
    branches = [
        "pT_lep1",
        "pT_lep2",
        "weight_nominal",
        "weight_sys_jvt",
        "reg2j2b",
        "reg1j1b",
        "OS",
        "elmu",
    ]
    cb = categorize_branches(branches)
    assert cb["meta"] == sorted(["OS", "reg1j1b", "reg2j2b", "elmu"], key=str.lower)
    assert cb["kinematics"] == sorted(["pT_lep1", "pT_lep2"], key=str.lower)
    assert cb["weights"] == sorted(["weight_nominal", "weight_sys_jvt"], key=str.lower)

    cb = categorize_branches(branches_from("tests/test_data/testfile1.root"))
    assert "reg2j1b" in cb["meta"]
    assert "pT_lep1" not in cb["meta"]
    assert "pT_lep1" not in cb["weights"]
    assert "pT_lep2" in cb["kinematics"]

    from pathlib import PosixPath

    cb = categorize_branches(branches_from(PosixPath("tests/test_data/testfile2.root")))
    assert "reg2j1b" in cb["meta"]
    assert "pT_lep1" not in cb["meta"]
    assert "pT_lep1" not in cb["weights"]
    assert "pT_lep2" in cb["kinematics"]


def test_selection_for():
    assert selection_for("reg2j1b") == SELECTION_2j1b
    assert selection_for("2j2b") == SELECTION_2j2b
    assert selection_for(Region.r1j1b) == SELECTION_1j1b
    assert selection_for("r2j1b") == SELECTION_2j1b
    assert selection_for(Region.r2j2b) == SELECTION_2j2b
    assert selection_for("reg1j1b") == SELECTION_1j1b
    assert selection_for("1j1b") == SELECTION_1j1b


def test_selection_as_numexpr():
    sel = "reg1j1b == true && OS == true && mass_lep1jet1 < 155"
    newsel = selection_as_numexpr(sel)
    assert newsel == "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"
    sel = "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"
    newsel = selection_as_numexpr(sel)
    assert newsel == "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"


def test_selection_as_root():
    sel = "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"
    newsel = selection_as_root(sel)
    assert "(reg1j1b == true) && (OS == true) && (mass_lep1jet1 < 155)"
    sel = "(reg1j1b == true) && (OS == true) && (mass_lep1jet1 < 155)"
    newsel = selection_as_root(
        "(reg1j1b == true) && (OS == true) && (mass_lep1jet1 < 155)"
    )
    assert newsel == "(reg1j1b == true) && (OS == true) && (mass_lep1jet1 < 155)"


def test_selection_branches():
    sel = "(reg1j1b == True) & (OS == True) & (mass_lep1jet1 < 155)"
    varsin = set(("reg1j1b", "OS", "mass_lep1jet1"))
    assert selection_branches(sel) == varsin
    sel = "reg1j1b == true && OS == true && mass_lep1jet1 < 155"
    varsin = set(("reg1j1b", "OS", "mass_lep1jet1"))
    assert selection_branches(sel) == varsin
