from pathlib import PosixPath

import uproot
import numpy as np

from tdub.config import AVOID_IN_CLF
from tdub.frames import iterative_selection, drop_avoid
from tdub.frames import apply_weight_trrw, apply_weight_tptrw, apply_weight_inverse
from tdub.data import selection_branches

test_file_root = PosixPath(__file__).parent / "test_data"


def test_exclude_avoids():
    files = [
        str(test_file_root / "testfile1.root"),
        str(test_file_root / "testfile2.root"),
        str(test_file_root / "testfile3.root"),
    ]
    df = iterative_selection(files, "(reg1j1b == True)", exclude_avoids=True)
    cols = set(df.columns)
    avoid = set(AVOID_IN_CLF)
    assert len(cols & avoid) == 0

    df = iterative_selection(
        files,
        "(reg1j1b == True)",
        exclude_avoids=True,
        keep_category="kinematics",
    )
    cols = set(df.columns)
    avoid = set(AVOID_IN_CLF)
    assert len(cols & avoid) == 0


def test_drop_avoid():
    files = [
        str(test_file_root / "testfile1.root"),
        str(test_file_root / "testfile2.root"),
        str(test_file_root / "testfile3.root"),
    ]
    df = iterative_selection(files, "(reg1j1b == True)")
    df.drop_avoid()
    avoid = set(AVOID_IN_CLF)
    cols = set(df.columns)
    assert len(cols & avoid) == 0


def test_drop_jet2():
    files = [
        str(test_file_root / "testfile1.root"),
        str(test_file_root / "testfile3.root"),
    ]
    df = iterative_selection(files, "(OS == True)")
    j2s = [col for col in df.columns if "jet2" in col]
    df.drop_jet2()
    for j in j2s:
        assert j not in df.columns


def test_selection_augmented():
    files = [
        str(test_file_root / "testfile1.root"),
        str(test_file_root / "testfile3.root"),
    ]
    df = iterative_selection(
        files, "(OS == True) & (reg1j1b == True) & (mass_lep1jet1 < 155)"
    )
    sel_vars = set(selection_branches(df.selection_used))
    manual = {"OS", "reg1j1b", "mass_lep1jet1"}
    assert sel_vars == manual
    assert (
        df.selection_used == "(OS == True) & (reg1j1b == True) & (mass_lep1jet1 < 155)"
    )


def test_selection_strings():
    files = [
        str(test_file_root / "testfile1.root"),
        str(test_file_root / "testfile3.root"),
    ]
    root_sel1 = "OS == 1 && reg2j2b == 1 && mass_lep1jet1 < 155"
    nume_sel1 = "(OS == 1) & (reg2j2b == 1) & (mass_lep1jet1 < 155)"
    root_sel2 = "OS == true && reg2j2b == true && mass_lep1jet1 < 155"
    nume_sel2 = "(OS == True) & (reg2j2b == True) & (mass_lep1jet1 < 155)"
    df_r_sel1 = iterative_selection(files, root_sel1)
    df_r_sel2 = iterative_selection(files, root_sel2)
    df_n_sel1 = iterative_selection(files, nume_sel1)
    df_n_sel2 = iterative_selection(files, nume_sel2)
    assert df_r_sel1.equals(df_r_sel2)
    assert df_r_sel1.equals(df_n_sel1)
    assert df_r_sel1.equals(df_n_sel2)


def test_apply_weight_tptrw():
    f = test_file_root / "testfile4.root"
    t = uproot.open(f).get("WtLoop_nominal")
    w1 = t.arrays(["weight_nominal"], library="np")["weight_nominal"]
    w2 = t.arrays(["weight_sys_pileup_DOWN"], library="np")["weight_sys_pileup_DOWN"]
    wr = t.arrays(["weight_tptrw_tool"], library="np")["weight_tptrw_tool"]
    r1 = w1 * wr
    r2 = w2 * wr
    df = t.arrays(library="pd")
    apply_weight_tptrw(df)
    rr1 = df["weight_nominal"].to_numpy()
    rr2 = df["weight_sys_pileup_DOWN"].to_numpy()
    assert np.allclose(r1, rr1)
    assert np.allclose(r2, rr2)


def test_apply_weight_trrw():
    f = test_file_root / "testfile4.root"
    t = uproot.open(f).get("WtLoop_nominal")
    w1 = t.arrays(["weight_nominal"], library="np")["weight_nominal"]
    w2 = t.arrays(["weight_sys_pileup_DOWN"], library="np")["weight_sys_pileup_DOWN"]
    wr = t.arrays(["weight_trrw_tool"], library="np")["weight_trrw_tool"]
    r1 = w1 * wr
    r2 = w2 * wr
    df = t.arrays(library="pd")
    apply_weight_trrw(df)
    rr1 = df["weight_nominal"].to_numpy()
    rr2 = df["weight_sys_pileup_DOWN"].to_numpy()
    assert np.allclose(r1, rr1)
    assert np.allclose(r2, rr2)
