def test_modules():
    import importlib
    assert importlib.util.find_spec("lhcb_ftcalib")  is not None
    assert importlib.util.find_spec("iminuit")       is not None
    assert importlib.util.find_spec("numpy")         is not None
    assert importlib.util.find_spec("pandas")        is not None
    assert importlib.util.find_spec("flake8")        is not None
    assert importlib.util.find_spec("scipy")         is not None
    assert importlib.util.find_spec("numba")         is not None
    assert importlib.util.find_spec("matplotlib")    is not None


import os
import pytest
import itertools
import iminuit
import pandas as pd
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt

import lhcb_ftcalib as ft


class FakeMinimizer:
    def __init__(self, cov):
        self.covariance = cov


def test_syntax():
    from flake8.api import legacy as flake8
    style_guide = flake8.get_style_guide(ignore=["E221", "E402", "E501", "E251", "E203", "E201",
                                                 "E202", "E241", "E272", "E127", "E222", "E226",
                                                 "E722", "W503", "W291", "E265", "E266", "E303",
                                                 "E302", "E305", "E261"])
    pyfiles = ["Tagger.py", "TaggingData.py", "TaggerCollection.py", "link_functions.py",
               "PolynomialCalibration.py", "NSplineCalibration.py", "BSplineCalibration.py",
               "plotting.py", "printing.py", "apply_tagger.py", "combination.py",
               "save_calibration.py", "__main__.py", "resolution_model.py"]

    pyfiles = [ "src/lhcb_ftcalib/" + py for py in pyfiles]
    report = style_guide.check_files(pyfiles)
    repF = report.get_statistics("F")
    repE = report.get_statistics("E")
    for rep in repF:
        print(rep)
    for rep in repE:
        print(rep)
    assert repF == []
    assert repE == []


def test_init_Bu():
    """ Check Tagger init values """
    name = "test1"
    df = pd.DataFrame({
        "eta"      : [0.2, 0.3, 0.4, 0.25],
        "dec"      : [-1, 0, 1, 1],
        "B_ID"     : [-521, 0, 521, 521],
        "tau"      : [0.01, 0.02, 0.03, 0.02],
        "tau_err"  : [0.003, 0.002, 0.001, 0.006],
        "weight"   : [0.3, 0.2, 0.7, 0.1],
        "selected" : [True, True, True, False]
    })
    df.dec = df.dec.astype(np.int32)
    mode = "Bu"
    tagged = df.dec != 0
    tagged_sel = tagged & df.selected
    decay_flav = pd.Series(df.B_ID // 521, dtype=np.int32)
    prod_flav = pd.Series(decay_flav.copy(deep=True), dtype=np.int32)

    t = ft.Tagger(name      = name,
                  eta_data  = df.eta,
                  dec_data  = df.dec,
                  B_ID      = df.B_ID,
                  mode      = mode,
                  tau_ps    = df.tau,
                  tauerr_ps = df.tau_err,
                  weight    = df.weight,
                  selection = df.selected)

    t_full = t.stats._full_data
    t_tag  = t.stats._tagdata

    assert t.name == name
    assert t.mode == mode

    # Compare full datasets
    assert isinstance(t.stats, ft.TaggingData)
    assert np.allclose(t_full.eta, df.eta)
    assert np.allclose(t_full.dec, df.dec)
    assert np.allclose(t_full.decay_flav, decay_flav)
    assert np.allclose(t_full.selected, df.selected)
    assert np.allclose(t_full.tau, df.tau)
    assert np.allclose(t_full.tau_err, df.tau_err)
    assert np.allclose(t_full.weight, df.weight)
    assert np.allclose(t_full.overflow, df.eta > 0.5)
    assert np.allclose(t_full.underflow, df.eta < 0)
    assert np.allclose(t_full.tagged, tagged)
    assert np.allclose(t_full.tagged_sel, tagged_sel)

    # Compare tagged datasets
    assert np.allclose(t_tag.eta, df.eta[tagged_sel])
    assert np.allclose(t_tag.dec, df.dec[tagged_sel])
    assert np.allclose(t_tag.decay_flav, decay_flav[tagged_sel])
    assert np.allclose(t_tag.prod_flav, prod_flav[tagged_sel])
    assert np.allclose(t_tag.selected, df.selected[tagged_sel])
    assert np.allclose(t_tag.tau, df.tau[tagged_sel])
    assert np.allclose(t_tag.tau_err, df.tau_err[tagged_sel])
    assert np.allclose(t_tag.weight, df.weight[tagged_sel])
    assert np.allclose(t_tag.overflow, df.eta[tagged_sel] > 0.5)
    assert np.allclose(t_tag.underflow, df.eta[tagged_sel] < 0)
    assert np.allclose(t_tag.tagged, tagged[tagged_sel])
    assert np.allclose(t_tag.tagged_sel, tagged[tagged_sel])
    assert np.allclose(t_tag.correct_tags, prod_flav[tagged_sel] == df.dec[tagged_sel])
    assert np.allclose(t_tag.wrong_tags, prod_flav[tagged_sel] != df.dec[tagged_sel])

    # Test metadata
    assert not t.stats._is_calibrated
    assert t.stats._absID == 521

    # Test oscillation parameters
    assert t.DeltaM is None
    assert t.DeltaGamma is None
    assert t.Aprod == 0

    # Test default calibration
    assert isinstance(t.func, ft.PolynomialCalibration)
    assert t.func.npar == 2
    assert t.func.link == ft.link_functions.mistag
    assert np.isclose(t.stats.avg_eta, np.average(df.eta[tagged_sel], weights=df.weight[tagged_sel]))

    # Test (some) statistics
    assert t.stats.N == len(df)
    assert t.stats.Ns == df.selected.sum()
    assert t.stats.Nt == tagged.sum()
    assert t.stats.Nts == tagged_sel.sum()
    assert t.stats.Nw == df.weight.sum()
    assert t.stats.Nwt == df.weight[tagged].sum()

    # Test Minimizer
    assert isinstance(t.minimizer, iminuit.Minuit)
    assert t.minimizer.errordef == iminuit.Minuit.LIKELIHOOD


def test_init_Bd():
    """ Check Tagger init values """
    name = "test2"
    df = pd.DataFrame({
        "eta"      : [0.2, 0.3, 0.4, 0.25],
        "dec"      : [-1, 0, 1, 1],
        "B_ID"     : [-521, 0, 521, 521],
        "tau"      : [0.01, 0.02, 0.03, 0.02],
        "tau_err"  : [0.003, 0.002, 0.001, 0.006],
        "weight"   : [0.3, 0.2, 0.7, 0.1],
        "selected" : [True, True, True, False]
    })
    df.dec = df.dec.astype(np.int32)
    mode = "Bd"
    tagged = df.dec != 0
    tagged_sel = tagged & df.selected
    decay_flav = pd.Series(df.B_ID // 521, dtype=np.int32)
    prod_flav = pd.Series(decay_flav.copy(deep=True), dtype=np.int32)

    t = ft.Tagger(name      = name,
                  eta_data  = df.eta,
                  dec_data  = df.dec,
                  B_ID      = df.B_ID,
                  mode      = mode,
                  tau_ps    = df.tau,
                  tauerr_ps = df.tau_err,
                  weight    = df.weight,
                  selection = df.selected)

    t_full = t.stats._full_data
    t_tag  = t.stats._tagdata

    assert t.name == name
    assert t.mode == mode

    # Compare full datasets
    assert isinstance(t.stats, ft.TaggingData)
    assert np.allclose(t_full.eta, df.eta)
    assert np.allclose(t_full.dec, df.dec)
    assert np.allclose(t_full.decay_flav, decay_flav)
    assert np.allclose(t_full.selected, df.selected)
    assert np.allclose(t_full.tau, df.tau)
    assert np.allclose(t_full.tau_err, df.tau_err)
    assert np.allclose(t_full.weight, df.weight)
    assert np.allclose(t_full.overflow, df.eta > 0.5)
    assert np.allclose(t_full.underflow, df.eta < 0)
    assert np.allclose(t_full.tagged, tagged)
    assert np.allclose(t_full.tagged_sel, tagged_sel)

    # Compare tagged datasets
    assert np.allclose(t_tag.eta, df.eta[tagged_sel])
    assert np.allclose(t_tag.dec, df.dec[tagged_sel])
    assert np.allclose(t_tag.decay_flav, decay_flav[tagged_sel])
    assert np.allclose(t_tag.prod_flav, prod_flav[tagged_sel])
    assert np.allclose(t_tag.selected, df.selected[tagged_sel])
    assert np.allclose(t_tag.tau, df.tau[tagged_sel])
    assert np.allclose(t_tag.tau_err, df.tau_err[tagged_sel])
    assert np.allclose(t_tag.weight, df.weight[tagged_sel])
    assert np.allclose(t_tag.overflow, df.eta[tagged_sel] > 0.5)
    assert np.allclose(t_tag.underflow, df.eta[tagged_sel] < 0)
    assert np.allclose(t_tag.tagged, tagged[tagged_sel])
    assert np.allclose(t_tag.tagged_sel, tagged[tagged_sel])
    assert np.allclose(t_tag.correct_tags, prod_flav[tagged_sel] == df.dec[tagged_sel])
    assert np.allclose(t_tag.wrong_tags, prod_flav[tagged_sel] != df.dec[tagged_sel])

    # Test metadata
    assert not t.stats._is_calibrated
    assert t.stats._absID == 521

    # Test oscillation parameters
    assert t.DeltaM == ft.constants.DeltaM_d
    assert t.DeltaGamma == ft.constants.DeltaGamma_d
    assert t.Aprod == 0

    # Test default calibration
    assert isinstance(t.func, ft.PolynomialCalibration)
    assert t.func.npar == 2
    assert t.func.link == ft.link_functions.mistag
    assert np.isclose(t.stats.avg_eta, np.average(df.eta[tagged_sel], weights=df.weight[tagged_sel]))

    # Test (some) statistics
    assert t.stats.N == len(df)
    assert t.stats.Ns == df.selected.sum()
    assert t.stats.Nt == tagged.sum()
    assert t.stats.Nts == tagged_sel.sum()
    assert t.stats.Nw == df.weight.sum()
    assert t.stats.Nwt == df.weight[tagged].sum()

    # Test Minimizer
    assert isinstance(t.minimizer, iminuit.Minuit)
    assert t.minimizer.errordef == iminuit.Minuit.LIKELIHOOD


def test_init_Bs():
    """ Check Tagger init values """
    name = "test2"
    df = pd.DataFrame({
        "eta"      : [0.2, 0.3, 0.4, 0.25],
        "dec"      : [-1, 0, 1, 1],
        "B_ID"     : [-521, 0, 521, 521],
        "tau"      : [0.01, 0.02, 0.03, 0.02],
        "tau_err"  : [0.003, 0.002, 0.001, 0.006],
        "weight"   : [0.3, 0.2, 0.7, 0.1],
        "selected" : [True, True, True, False]
    })
    df.dec = df.dec.astype(np.int32)
    mode = "Bs"
    tagged = df.dec != 0
    tagged_sel = tagged & df.selected
    decay_flav = pd.Series(df.B_ID // 521, dtype=np.int32)
    prod_flav = pd.Series(decay_flav.copy(deep=True), dtype=np.int32)

    t = ft.Tagger(name      = name,
                  eta_data  = df.eta,
                  dec_data  = df.dec,
                  B_ID      = df.B_ID,
                  mode      = mode,
                  tau_ps    = df.tau,
                  tauerr_ps = df.tau_err,
                  weight    = df.weight,
                  selection = df.selected)

    t_full = t.stats._full_data
    t_tag  = t.stats._tagdata

    assert t.name == name
    assert t.mode == mode

    # Compare full datasets
    assert isinstance(t.stats, ft.TaggingData)
    assert np.allclose(t_full.eta, df.eta)
    assert np.allclose(t_full.dec, df.dec)
    assert np.allclose(t_full.decay_flav, decay_flav)
    assert np.allclose(t_full.selected, df.selected)
    assert np.allclose(t_full.tau, df.tau)
    assert np.allclose(t_full.tau_err, df.tau_err)
    assert np.allclose(t_full.weight, df.weight)
    assert np.allclose(t_full.overflow, df.eta > 0.5)
    assert np.allclose(t_full.underflow, df.eta < 0)
    assert np.allclose(t_full.tagged, tagged)
    assert np.allclose(t_full.tagged_sel, tagged_sel)

    # Compare tagged datasets
    assert np.allclose(t_tag.eta, df.eta[tagged_sel])
    assert np.allclose(t_tag.dec, df.dec[tagged_sel])
    assert np.allclose(t_tag.decay_flav, decay_flav[tagged_sel])
    assert np.allclose(t_tag.prod_flav, prod_flav[tagged_sel])
    assert np.allclose(t_tag.selected, df.selected[tagged_sel])
    assert np.allclose(t_tag.tau, df.tau[tagged_sel])
    assert np.allclose(t_tag.tau_err, df.tau_err[tagged_sel])
    assert np.allclose(t_tag.weight, df.weight[tagged_sel])
    assert np.allclose(t_tag.overflow, df.eta[tagged_sel] > 0.5)
    assert np.allclose(t_tag.underflow, df.eta[tagged_sel] < 0)
    assert np.allclose(t_tag.tagged, tagged[tagged_sel])
    assert np.allclose(t_tag.tagged_sel, tagged[tagged_sel])
    assert np.allclose(t_tag.correct_tags, prod_flav[tagged_sel] == df.dec[tagged_sel])
    assert np.allclose(t_tag.wrong_tags, prod_flav[tagged_sel] != df.dec[tagged_sel])

    # Test metadata
    assert not t.stats._is_calibrated
    assert t.stats._absID == 521

    # Test oscillation parameters
    assert t.DeltaM == ft.constants.DeltaM_s
    assert t.DeltaGamma == ft.constants.DeltaGamma_s
    assert t.Aprod == 0

    # Test default calibration
    assert isinstance(t.func, ft.PolynomialCalibration)
    assert t.func.npar == 2
    assert t.func.link == ft.link_functions.mistag
    assert np.isclose(t.stats.avg_eta, np.average(df.eta[tagged_sel], weights=df.weight[tagged_sel]))

    # Test (some) statistics
    assert t.stats.N == len(df)
    assert t.stats.Ns == df.selected.sum()
    assert t.stats.Nt == tagged.sum()
    assert t.stats.Nts == tagged_sel.sum()
    assert t.stats.Nw == df.weight.sum()
    assert t.stats.Nwt == df.weight[tagged].sum()

    # Test Minimizer
    assert isinstance(t.minimizer, iminuit.Minuit)
    assert t.minimizer.errordef == iminuit.Minuit.LIKELIHOOD


def test_memory_addresses_Tagger():
    """ Test whether all dataframes are properly copied and memory cannot be externally corrupted """
    size = 100
    df = pd.DataFrame({
        "eta"    : np.random.uniform(0, 1, size),
        "dec"    : np.random.randint(-1, 2, size),
        "B_ID"   : 521 * np.random.randint(-1, 2, size),
        "tau"    : np.random.uniform(0, 1, size),
        "tauerr" : np.random.uniform(0, 1, size),
        "weight" : np.random.uniform(0, 1, size)
    })
    mode = "Bd"

    t = ft.Tagger(name      = "test",
                  eta_data  = df.eta,
                  dec_data  = df.dec,
                  B_ID      = df.B_ID,
                  mode      = mode,
                  tau_ps    = df.tau,
                  tauerr_ps = df.tauerr,
                  weight    = df.weight)

    # Test if TaggingData dataframe member can be retrieved as reference
    reference = t.stats._tagdata
    assert reference is t.stats._tagdata


def test_init_list_types():
    # Check whether Tagger initializes with different kinds of lists and if the
    # tagging data of all initialized taggers is identical afterwards

    df = pd.DataFrame({
        "eta"    : [0.2, 0.3, 0.4],
        "dec"    : [-1, 0, 1],
        "B_ID"   : [-521, 0, -521],
        "weight" : [0.3, 0.2, 0.7],
        "tau"    : [0.01, 0.02, 0.03],  # Very small decay times -> no oscillation for this test
        "tauerr" : [0.01, 0.02, 0.03],
    })
    df.B_ID = df.B_ID.astype(np.int32)
    dftagged = df[df.dec != 0].copy()
    dftagged.reset_index(drop=True, inplace=True)
    mode = "Bd"
    name = "test1"

    def values_are_stored(tagger):
        fulldata = tagger.stats._full_data
        tagdata  = tagger.stats._tagdata
        assert fulldata.eta.equals(df.eta)
        assert fulldata.dec.equals(df.dec)
        assert fulldata.decay_flav.equals(df.B_ID // 521)
        assert fulldata.tagged.equals(df.dec != 0)
        assert fulldata.weight.equals(df.weight)

        assert tagdata.eta.equals(dftagged.eta)
        assert tagdata.dec.equals(dftagged.dec)
        assert tagdata.decay_flav.equals(dftagged.B_ID // 521)
        assert tagdata.prod_flav.equals(dftagged.B_ID // 521)
        assert tagdata.weight.equals(dftagged.weight)

    # Test whether tagger data is matching
    def data_match(taggers):
        for t1, t2 in itertools.combinations(taggers, 2):
            assert t1.stats._tagdata.equals(t2.stats._tagdata)
            assert t1.stats._full_data.equals(t2.stats._full_data)

    def same_values(taggers):
        for t1, t2 in itertools.combinations(taggers, 2):
            assert id(t1) != id(t2)
            assert id(t1.stats) != id(t2.stats)  # Would be mysterious
            assert np.isclose(t1.stats.avg_eta, t2.stats.avg_eta)
            assert np.isclose(t1.stats.N,       t2.stats.N)
            assert np.isclose(t1.stats.Ns,      t2.stats.Ns)
            assert np.isclose(t1.stats.Nt,      t2.stats.Nt)
            assert np.isclose(t1.stats.Nts,     t2.stats.Nts)
            assert np.isclose(t1.stats.Nw,      t2.stats.Nw)
            assert np.isclose(t1.stats.Neff,    t2.stats.Neff)
            assert np.isclose(t1.stats.Nwt,     t2.stats.Nwt)
            assert np.isclose(t1.stats.Nws,     t2.stats.Nws)
            assert np.isclose(t1.stats.Nwts,    t2.stats.Nwts)
    try:
        t_list = ft.Tagger(name      = name,
                           eta_data  = list(df.eta),
                           dec_data  = list(df.dec),
                           B_ID      = list(df.B_ID),
                           tau_ps    = list(df.tau),
                           tauerr_ps = list(df.tauerr),
                           mode      = mode,
                           weight    = list(df.weight))
    except Exception as e:
        pytest.fail("List init failed")
        print(e.message)

    try:
        t_array = ft.Tagger(name      = name,
                            eta_data  = np.array(df.eta),
                            dec_data  = np.array(df.dec),
                            B_ID      = np.array(df.B_ID),
                            tau_ps    = np.array(df.tau),
                            tauerr_ps = np.array(df.tauerr),
                            mode      = mode,
                            weight    = np.array(df.weight))
    except Exception as e:
        pytest.fail("Array init failed")
        print(e.message)

    try:
        t_df = ft.Tagger(name      = name,
                         eta_data  = df.eta,
                         dec_data  = df.dec,
                         B_ID      = df.B_ID,
                         tau_ps    = df.tau,
                         tauerr_ps = df.tauerr,
                         mode      = mode,
                         weight    = df.weight)
    except Exception as e:
        pytest.fail("DataFrame init failed")
        print(e.message)

    # Test whether tagger data is pandas series and whether it is the same in all cases
    values_are_stored(t_list)
    values_are_stored(t_array)
    values_are_stored(t_df)
    data_match([t_list, t_array, t_df])
    same_values([t_list, t_array, t_df])


def TagDataEquals(d1, d2):
    if d1 is None and d2 is None:
        return True
    equal = True
    equal &= d1._full_data.equals(d2._full_data)
    equal &= d1._tagdata.equals(d2._tagdata)

    equal &= d1.N     == d2.N
    equal &= d1.Nt    == d2.Nt
    equal &= d1.Nw    == d2.Nw
    equal &= d1.Neff  == d2.Neff
    equal &= d1.Nwt   == d2.Nwt
    equal &= d1.Ns    == d2.Ns
    equal &= d1.Nts   == d2.Nts
    equal &= d1.Nws   == d2.Nws
    equal &= d1.Neffs == d2.Neffs
    equal &= d1.Nwts  == d2.Nwts
    return equal


def test_tagdata_equality():
    """ Test equality operator """
    td_ref = ft.TaggingData(eta_data  = [0.2, 0.1, 0.5],
                            dec_data  = [1, -1, 0],
                            ID        = [521, -521, 0],
                            tau       = None,
                            tauerr    = None,
                            weights   = [0.1, 0.2, 0.3],
                            selection = [True, True, True])

    td_clone      = deepcopy(td_ref)
    td_clone_fake = deepcopy(td_ref)

    assert id(td_clone) != id(td_ref)
    assert id(td_clone) != id(td_clone_fake)

    td_clone_fake._full_data.loc[1, "eta"] *= 1.001

    assert TagDataEquals(td_ref, td_clone)
    assert not TagDataEquals(td_ref, td_clone_fake)


def test_tagdata_values():
    """ Test whether tagging statistics are determined as expected """
    dec_true     = pd.Series([1, 0, -1, 1, -1, 0, 0, 1, 0, -1], dtype=np.int32)
    eta_true     = pd.Series([0.1, 0.2, 0.3, 0.4, 0.3, 0.4, 0.2, 0.2, 0.3, 0.05])
    absid        = 521
    ID_true      = pd.Series(absid * np.array([1, 1, 1, -1, -1, 1, -1, 1, 1, -1]), dtype=np.int32)
    decay_flav   = ID_true // absid
    prod_flav    = decay_flav.copy()
    selection    = pd.Series([True, True, True, True, False, False, True, False, True, False])
    weights_true = pd.Series([0.3, 0.8, 0.2, 0.7, 1.2, 1.6, 0.2, 0.1, 0.7, 1.0])
    tag          = dec_true != 0
    tag_sel      = tag & selection

    td = ft.TaggingData(eta_data = eta_true,
                        dec_data = dec_true,
                        ID       = ID_true,
                        tau      = None,
                        tauerr   = None,
                        weights  = weights_true,
                        selection = selection)

    # Basic data
    assert np.allclose(td._full_data.eta, eta_true)
    assert np.allclose(td._full_data.dec, dec_true)
    assert np.allclose(td._full_data.decay_flav, ID_true // absid)
    assert np.allclose(td._full_data.selected, selection)
    assert np.allclose(td._tagdata.weight, weights_true[tag_sel])

    # Basic memory safety (make sure data has been copied)
    assert id(td._full_data.eta)        != id(eta_true)
    assert id(td._full_data.dec)        != id(dec_true)
    assert id(td._full_data.decay_flav) != id(decay_flav)
    assert id(td._full_data.weight)     != id(weights_true)

    # overflow flags
    assert all(~td._full_data.overflow)
    assert all(~td._full_data.underflow)

    # Higher level data
    assert np.allclose(td._full_data.tagged, tag)
    assert np.allclose(td._tagdata.weight, weights_true[tag_sel])
    assert np.allclose(td._full_data.tagged_sel, tag_sel)
    assert np.allclose(td._tagdata.dec, dec_true[tag_sel])
    assert np.allclose(td._tagdata.decay_flav, decay_flav[tag_sel])
    assert np.allclose(td._tagdata.prod_flav, prod_flav[tag_sel])
    assert np.allclose(td._tagdata.eta, eta_true[tag_sel])
    assert np.isclose(td.avg_eta, np.average(eta_true[tag_sel], weights=weights_true[tag_sel]))

    # Yields
    assert td.N  == len(eta_true)
    assert td.Ns == selection.sum()
    assert td.Nt == tag.sum()
    assert td.Nts == tag_sel.sum()
    assert np.isclose(td.Nw, np.sum(weights_true))
    assert np.isclose(td.Nwt, np.sum(weights_true[tag]))
    assert np.isclose(td.Nws, np.sum(weights_true[selection]))
    assert np.isclose(td.Nwts, np.sum(weights_true[tag_sel]))
    assert np.isclose(td.Neff, np.sum(weights_true) ** 2 / np.sum(weights_true**2))
    assert np.isclose(td.Neffs, np.sum(weights_true[selection]) ** 2 / np.sum(weights_true[selection]**2))

    # tag decision correctness
    correct = dec_true[tag_sel] == prod_flav[tag_sel]
    wrong   = ~correct
    assert np.allclose(td._tagdata.correct_tags, correct[tag_sel])
    assert np.allclose(td._tagdata.wrong_tags, wrong[tag_sel])


def test_link_function_evaluation():
    """ Test link function derivatives numerically """
    mistag   = ft.link.mistag
    logit    = ft.link.logit
    rlogit   = ft.link.rlogit
    probit   = ft.link.probit
    rprobit  = ft.link.rprobit
    cauchit  = ft.link.cauchit
    rcauchit = ft.link.rcauchit

    x = np.linspace(-5, 5, 10000)

    def derivative_test(func):
        link  = func.L(x)
        dlink = func.DL(x)

        dlink_num = (link[2:] - link[:-2]) / (20 / 10000)

        plt.figure(figsize=(8, 6))
        plt.title(func.__name__)
        plt.plot(x, link)
        plt.plot(x, dlink)
        plt.plot(x[1:-1], dlink_num)

        if not os.path.exists("tests/testplots"):
            os.mkdir("tests/testplots")
        plt.savefig("tests/testplots/" + func.__name__ + "_D.pdf")

        if func.__name__ == "mistag":
            return
        assert np.max(np.abs(dlink[1:-1] - dlink_num)) < 0.001

    def inverse_test(func):
        link = func.L(x)
        linkInv = func.InvL(x)

        plt.figure(figsize=(8, 6))
        plt.title(func.__name__)
        plt.plot([-10, 10], [-10, 10], 'k--')
        plt.plot(x, link)
        plt.plot(x, linkInv)
        plt.xlim(-5, 5)
        plt.ylim(-5, 5)
        plt.savefig("tests/" + func.__name__ + "_Inv.pdf")

    derivative_test(mistag)
    derivative_test(logit)
    derivative_test(rlogit)
    derivative_test(probit)
    derivative_test(rprobit)
    derivative_test(cauchit)
    derivative_test(rcauchit)

    inverse_test(mistag)
    inverse_test(logit)
    inverse_test(rlogit)
    inverse_test(probit)
    inverse_test(rprobit)
    inverse_test(cauchit)
    inverse_test(rcauchit)


def test_link_function_inverse():
    # F(F^-1(x)) == F^-1(F(x)) == id(x)
    eta = np.random.normal(loc=0.25, scale=0.05, size=10000)
    eta[eta < 0] = 0
    eta[eta >= 0.5] = 0.4999
    for link in ft.link_functions.link_function.__subclasses__():
        assert np.allclose(eta, link.L(link.InvL(eta)))
        assert np.allclose(eta, link.InvL(link.L(eta)))


def test_link_function_addresses():
    # Link function must not return a reference, or equivalently: data passed
    # to a link function must be a copy, otherwise link function permanently
    # modifies data (The reference mistag) and then chaos happens
    def check_link(FCN, data):
        print("Testing", FCN.__name__, "with", data.__class__)
        reference = data.copy()

        linked = FCN.L(data)
        assert id(linked) != id(data), f"{FCN.__name__}::L steals ownership"
        assert np.array_equal(reference, np.array(data)), f"{FCN.__name__}::L modifies passed data"

        linked2 = FCN.DL(data)
        assert id(linked2) != id(data), f"{FCN.__name__}::DL steals ownership"
        assert np.array_equal(reference, np.array(data)), f"{FCN.__name__}::DL modifies passed data"

        linked3 = FCN.InvL(data)
        assert id(linked3) != id(data), f"{FCN.__name__}::InvL steals ownership"
        assert np.array_equal(reference, np.array(data)), f"{FCN.__name__}::InvL modifies passed data"

        linked4 = FCN.DInvL(data)
        assert id(linked4) != id(data), f"{FCN.__name__}::DInvL steals ownership"
        assert np.array_equal(reference, np.array(data)), f"{FCN.__name__}::DInvL modifies passed data"

    data_pd = pd.DataFrame({"eta" : np.linspace(0.1, 0.4, 100)})
    data_pdseries = pd.Series(np.linspace(0.1, 0.4, 100))
    data_np = np.linspace(0.1, 0.4, 100)

    for data in [data_pd, data_pdseries, data_np]:
        for LINK in ft.link.link_function.__subclasses__():
            check_link(LINK, data)


def test_convolution_at():
    # Test fast convolution algorithm for compliance to scipy.signal.convolve
    np.random.seed(3098750432)
    from scipy import signal

    for i in range(1000):
        arr1 = np.random.randint(-10, 10, np.random.randint(1, 128, 1))
        arr2 = np.random.randint(-10, 10, np.random.randint(1, 128, 1))

        reference = signal.convolve(arr1, arr2, mode="same")
        values    = np.array([ft.resolution_model.convolution_at(arr1, arr2, j) for j in range(len(arr1))])

        assert np.array_equal(reference, values)


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    import sys
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def test_Tagger_frees_memory():
    # Test whether del causes memory to be freed
    N = 100000
    df = pd.DataFrame({
        "eta"    : np.random.uniform(0, 0.5, N),
        "dec"    : np.random.choice([-1, 0, 1], N),
        "B_ID"   : np.random.choice([-521, 0, 521], N),
        "tau"    : np.random.uniform(0, 0.01, N),
        "tauerr" : np.random.uniform(0, 0.001, N),
        "weight" : np.random.uniform(0, 1, N)
    })

    t = ft.Tagger(name      = "test",
                  eta_data  = df.eta,
                  dec_data  = df.dec,
                  B_ID      = df.B_ID,
                  mode      = "Bd",
                  tau_ps    = df.tau,
                  tauerr_ps = df.tauerr,
                  weight    = df.weight)

    taggersize = get_size(t)  # sys.getsizeof(t)
    print("Tagsize in mem", taggersize)

    t.destroy()

    taggersize = get_size(t)  # sys.getsizeof(t)
    print("Tagsize after in mem", taggersize)

    # Some couple of thousand bytes from tagger attributes are not destroyed
    assert taggersize < 10000


def test_TaggerCollection_frees_memory():
    # Test whether del causes memory to be freed
    N = 100000
    df = pd.DataFrame({
        "eta"    : np.random.uniform(0, 0.5, N),
        "dec"    : np.random.choice([-1, 0, 1], N),
        "B_ID"   : np.random.choice([-521, 0, 521], N),
        "tau"    : np.random.uniform(0, 0.01, N),
        "tauerr" : np.random.uniform(0, 0.001, N),
        "weight" : np.random.uniform(0, 1, N)
    })

    tc = ft.TaggerCollection()
    tc.create_tagger(name      = "test1",
                     eta_data  = df.eta,
                     dec_data  = df.dec,
                     B_ID      = df.B_ID,
                     mode      = "Bd",
                     tau_ps    = df.tau,
                     tauerr_ps = df.tauerr,
                     weight    = df.weight)
    tc.create_tagger(name      = "test2",
                     eta_data  = df.eta,
                     dec_data  = df.dec,
                     B_ID      = df.B_ID,
                     mode      = "Bd",
                     tau_ps    = df.tau,
                     tauerr_ps = df.tauerr,
                     weight    = df.weight)

    taggersize = get_size(tc)  # sys.getsizeof(t)
    print("Tagsize in mem", taggersize)

    tc.destroy()

    taggersize = get_size(tc)  # sys.getsizeof(t)
    print("Tagsize after in mem", taggersize)

    # Some couple of thousand bytes from tagger attributes are not destroyed
    assert taggersize < 10000, taggersize


def test_combination():
    from lhcb_ftcalib.combination import combine_taggers

    decs = []
    for d1 in [-1, 1, 0]:
        for d2 in [-1, 1, 0]:
            for d3 in [-1, 1, 0]:
                decs.append(np.array([d1, d2, d3]))

    omegas = []
    for w1 in [0.4, 0.2, 0.5]:
        for w2 in [0.2, 0.4, 0.5]:
            for w3 in [0.4, 0.5, 0.2]:
                omegas.append(np.array([w1, w2, w3]))

    assert len(decs) == len(omegas)
    cdec, comega = combine_taggers(decs, omegas)

    print(np.array(decs))
    print(np.array(omegas))
    print(cdec)
    print(comega)
    assert len(cdec) == len(comega)
    assert len(cdec) == len(decs)

    for i in range(len(cdec)):
        # Do values make sense
        assert cdec[i] in [1, -1, 0]
        assert comega[i] >= 0 and comega[i] <= 0.5


# Calibration function tests
def test_calibfunction_usage():
    eta = np.random.normal(loc=0.25, scale=0.05, size=10000)
    eta[eta < 0] = 0
    eta[eta >= 0.5] = 0.4999
    etaref = eta.copy()
    dec = np.random.choice([-1, 1], size=10000)
    decref = dec.copy()

    assert id(eta) != id(etaref)
    assert id(dec) != id(decref)

    for functype in ft.CalibrationFunction.CalibrationFunction.__subclasses__():
        print(functype.__name__)
        for link in ft.link_functions.link_function.__subclasses__():
            for deg in range(0, 10):
                if functype is ft.PolynomialCalibration:
                    if deg < 2:
                        with pytest.raises(AssertionError):
                            func = functype(deg, link)
                        continue
                    else:
                        func = functype(deg, link)

                    assert func.npar == deg
                    assert func.link == link
                    params = (2 * func.npar) * [0]

                    func.init_basis(eta)
                    assert np.array_equal(eta, etaref)

                    result = func.eval(params, eta, dec)
                    assert id(result) != id(eta)
                    assert id(result) != id(dec)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    result = func.eval_averaged(params, eta)
                    assert id(result) != id(eta)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    result = func.eval_plotting(params, eta, dec)
                    assert id(result) != id(eta)
                    assert id(result) != id(dec)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    for p in range(2 * func.npar):
                        result = func.derivative(0, params, eta, dec)
                        assert id(result) != id(eta)
                        assert id(result) != id(dec)
                        assert np.array_equal(eta, etaref)
                        assert np.array_equal(dec, decref)
                elif functype == ft.NSplineCalibration:
                    func = functype(deg, link)

                    assert func.npar == deg + 2
                    assert func.link == link
                    params = (2 * func.npar) * [0]

                    func.init_basis(eta)
                    assert np.array_equal(eta, etaref)

                    result = func.eval(params, eta, dec)
                    assert id(result) != id(eta)
                    assert id(result) != id(dec)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    result = func.eval_averaged(params, eta)
                    assert id(result) != id(eta)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    result = func.eval_plotting(params, eta, dec)
                    assert id(result) != id(eta)
                    assert id(result) != id(dec)
                    assert np.array_equal(eta, etaref)
                    assert np.array_equal(dec, decref)

                    # for p in range(2 * func.npar):
                    #     result = func.derivative(0, params, eta, dec)
                    #     assert id(result) != id(eta)
                    #     assert id(result) != id(dec)
                    #     assert np.array_equal(eta, etaref)
                    #     assert np.array_equal(dec, decref)
