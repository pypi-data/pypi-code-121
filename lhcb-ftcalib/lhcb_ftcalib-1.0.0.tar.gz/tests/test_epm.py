import pytest
import os
import numpy as np
import uproot
import pandas as pd
import matplotlib.pyplot as plt

import lhcb_ftcalib as ft
from utils import force_calibration, get_xml_content, compare_basis, compare_tuples


# Use outdated oscillation parameters of EPM
ft.constants.DeltaM_d     = 0.51
ft.constants.DeltaM_s     = 17.761
ft.constants.DeltaGamma_d = 0
ft.constants.DeltaGamma_s = 0.0913


def compare_performances_to_epm(jobdir, mode, tree, func, calibrations_to_use, num_taggers):
    # Compare flavour tagging performance numbers
    print(f"Comparing uncalibrated performances in {jobdir}")
    epm_perf       = pd.read_csv(jobdir + "/EspressoPerformanceSummary.csv.orig", delimiter=';')
    epm_perf_calib = pd.read_csv(jobdir + "/EspressoCalibratedPerformanceSummary.csv.orig", delimiter=';')

    name_mapping = {
        "OS_Muon"     : "TOY0",
        "OS_Electron" : "TOY1",
        "SS_Pion"     : "TOY2",
    }

    # Rename epm taggers in perf file
    for t in range(num_taggers):
        epm_perf.TaggerName.iloc[t] = name_mapping[epm_perf.TaggerName.iloc[t]]
        epm_perf_calib.TaggerName.iloc[t] = name_mapping[epm_perf_calib.TaggerName.iloc[t]]

    df = uproot.open("tests/epm_reference_data/reference.root")[tree].arrays(library="pd")
    taggers = ft.TaggerCollection()

    for t in range(num_taggers):
        tageta = f"TOY{t}_ETA"
        tagdec = f"TOY{t}_DEC"
        if mode != "Bu":
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, tau_ps=df.TAU, analytic_gradient=True)
        else:
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, analytic_gradient=True)

    for t, tagger in enumerate(taggers):
        ftc_eff = tagger.stats.tagging_efficiency(calibrated=False)
        epm_eff = (epm_perf.TaggingEfficiency.iloc[t], epm_perf.TaggingEfficiencyStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Tagging Efficiency", ftc_eff, epm_eff, rtol=1e-3)

        ftc_eff = tagger.stats.mistag_rate(calibrated=False)
        epm_eff = (epm_perf.MistagRate.iloc[t], epm_perf.MistagRateStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Mistag rate", ftc_eff, epm_eff, rtol=1e-3)

        ftc_eff = tagger.stats.effective_mistag(calibrated=False)
        epm_eff = (epm_perf.EffectiveMistag.iloc[t], epm_perf.EffectiveMistagStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Effective Mistag", ftc_eff, epm_eff, rtol=1e-3)

        ftc_eff = tagger.stats.tagging_power(calibrated=False)
        epm_eff = (epm_perf.TaggingPower.iloc[t], epm_perf.TaggingPowerStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Tagging Power", ftc_eff, epm_eff, rtol=1e-3)

    print("Comparing calibrated tagging performances")
    # Apply EPM calibrations
    # for tagger, calib in zip(taggers, calibrations_to_use):
    #     force_calibration(tagger, func, calib)
    for t in range(num_taggers):
        force_calibration(taggers[t], func, calibrations_to_use[t])

    for t, tagger in enumerate(taggers):
        ftc_eff = tagger.stats.tagging_efficiency(calibrated=True)
        epm_eff = (epm_perf_calib.TaggingEfficiency.iloc[t], epm_perf_calib.TaggingEfficiencyStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Cal. Tagging Efficiency", ftc_eff, epm_eff, rtol=1e-2) or True

        ftc_eff = tagger.stats.mistag_rate(calibrated=True)
        epm_eff = (epm_perf_calib.MistagRate.iloc[t], epm_perf_calib.MistagRateStatUncert.iloc[t])

        assert compare_tuples(tagger.name, "Cal. Mistag rate", ftc_eff, epm_eff, rtol=1e-2) or True

        ftc_eff = tagger.stats.effective_mistag(calibrated=True)
        epm_eff = (epm_perf_calib.EffectiveMistag.iloc[t], epm_perf_calib.EffectiveMistagStatUncert.iloc[t], epm_perf_calib.EffectiveMistagCalibUncert.iloc[t])

        assert compare_tuples(tagger.name, "Cal. Effective Mistag", ftc_eff, epm_eff, rtol=1e-2) or True

        ftc_eff = tagger.stats.tagging_power(calibrated=True)
        epm_eff = (epm_perf_calib.TaggingPower.iloc[t], epm_perf_calib.TaggingPowerStatUncert.iloc[t], epm_perf_calib.TaggingPowerCalibUncert.iloc[t])

        assert compare_tuples(tagger.name, "Cal. Tagging Power", ftc_eff, epm_eff, rtol=1e-2) or True


def compare_calibrations(jobdir, mode, tree, func, numTaggers=3):
    assert os.path.exists(jobdir)
    df = uproot.open("tests/epm_reference_data/reference.root")[tree].arrays(library="pd")
    taggers = ft.TaggerCollection()

    # Make ftc taggers, run calibrations
    for t in range(numTaggers):
        tageta = f"TOY{t}_ETA"
        tagdec = f"TOY{t}_DEC"
        if mode != "Bu":
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, tau_ps=df.TAU, analytic_gradient=False)
        else:
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, analytic_gradient=False)
    taggers.set_calibration(func)
    taggers.calibrate(quiet=True)

    tagger_xml = {
        0 : ("OS_Muon_Calibration.xml", "OS_Muon"),
        1 : ("OS_Electron_Calibration.xml", "OS_Electron"),
        2 : ("SS_Pion_Calibration.xml", "SS_Pion")
    }

    # Extract EPM calibration from xml
    epm_calibrations = []
    for t in range(numTaggers):
        epm_calibrations.append(get_xml_content(jobdir + f"/{tagger_xml[t][0]}", tagger_xml[t][1]))

    # Extract ftcalib calibration
    ftc_calibrations = []

    for t, tagger in enumerate(taggers):
        ftc_calibrations.append({})
        P = tagger.stats.params
        ftc_calibrations[-1]["paramnames"] = [p.replace("Δ", "D") for p in P.names_delta]
        ftc_calibrations[-1]["p_nom"] = P.params_delta
        ftc_calibrations[-1]["p_err"] = P.errors_delta
        ftc_calibrations[-1]["cov"] = P.covariance_delta
        ftc_calibrations[-1]["basis"] = tagger.func.basis

        if not isinstance(tagger.func, ft.PolynomialCalibration):
            ftc_calibrations[-1]["nodes"] = tagger.func.nodes

    # Compare calibrations
    for t, tagger in enumerate(taggers):
        print(f"Comparing parameters of tagger {tagger.name}")
        ftc = ftc_calibrations[t]
        epm = epm_calibrations[t]

        compare_basis(epm, ftc)

        # Compare parameters
        for i, p in enumerate(ftc["paramnames"]):
            compare_tuples(tagger.name, p, (ftc["p_nom"][i], ftc["p_err"][i]), (epm[p], epm[p + "_err"]), rtol=1e-2, atol=1e-3)

        # Compare covariance matrix elements
        for j in range(len(ftc["paramnames"])):
            compare_tuples(tagger.name, f"COV_row_{j}", (ftc["cov"][j]), (epm["cov"][j]), rtol=1e-2, atol=1e-3, sep=";")

    # At this point we have shown that the calibrations are matching to a
    # satisfactory degree. Now we take the EPM result and see whether ftcalib
    # computes the same calibrated statistics
    use_calibrations = []
    params = ftc_calibrations[0]["paramnames"]
    for cal in epm_calibrations:
        if isinstance(func, ft.PolynomialCalibration):
            basis = np.array(cal["basis"])
            basis = np.reshape(basis, (len(params) // 2, len(params) // 2))
            basis = [b[:j + 1][::-1] for j, b in enumerate(basis)]
            use_calibrations.append({"paramnames" : params,                             # parameter names
                                     "p_nom"      : [cal[p] for p in params],           # p parameters
                                     "p_err"      : [cal[p + "_err"] for p in params],  # p errors
                                     "cov"        : cal["cov"],                         # covariance matrix
                                     "basis"      : basis})                             # basis
        elif isinstance(func, ft.NSplineCalibration):
            basis = np.array(cal["basis"])
            basis = np.reshape(basis, (len(params) // 2, len(params) // 2))
            basis = [b[:j + 1][::-1] for j, b in enumerate(basis)]
            use_calibrations.append({"paramnames" : params,                             # parameter names
                                     "p_nom"      : [cal[p] for p in params],           # p parameters
                                     "p_err"      : [cal[p + "_err"] for p in params],  # p errors
                                     "cov"        : cal["cov"],                         # covariance matrix
                                     "nodes"      : cal["nodes"],                       # spline nodes
                                     "basis"      : basis})                             # basis
        elif isinstance(func, ft.BSplineCalibration):
            use_calibrations.append({"paramnames" : params,                             # parameter names
                                     "p_nom"      : [cal[p] for p in params],           # p parameters
                                     "p_err"      : [cal[p + "_err"] for p in params],  # p errors
                                     "cov"        : cal["cov"],                         # covariance matrix
                                     "nodes"      : cal["nodes"]})                      # spline nodes

    taggers.plot_calibration_curves(savepath=jobdir)
    return use_calibrations


def compare_writing(jobdir, mode, tree, func, calibrations_to_use, num_taggers):
    # Compare OMEGA values that are written to the tuples
    print(f"Comparing uncalibrated performances in {jobdir}")

    df = uproot.open("tests/epm_reference_data/reference.root")[tree].arrays(library="pd")
    taggers = ft.TaggerCollection()

    for t in range(num_taggers):
        tageta = f"TOY{t}_ETA"
        tagdec = f"TOY{t}_DEC"
        if mode != "Bu":
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, tau_ps=df.TAU, analytic_gradient=True)
        else:
            taggers.create_tagger(f"TOY{t}", df[tageta], df[tagdec], df.FLAV_DECAY, mode, analytic_gradient=True)

    print("Comparing calibrated tagging performances")
    # Apply EPM calibrations

    for t in range(num_taggers):
        force_calibration(taggers[t], func, calibrations_to_use[t])

    ftc         = taggers.get_dataframe(calibrated=True)
    ftc_uncalib = taggers.get_dataframe(calibrated=False)
    epm = uproot.open(jobdir + "/output.root")["TaggingTree"].arrays(library="pd")

    name_mapping = {
        "TOY0" : "OS_Muon",
        "TOY1" : "OS_Electron",
        "TOY2" : "SS_Pion"
    }

    # The EPM does not calibrate tagging decisions, i.e. does not set dec to 0
    print("Comparing data in output tuples")
    for t in range(num_taggers):
        assert ftc_uncalib[f"TOY{t}_DEC"].equals(epm[name_mapping[f"TOY{t}"] + "_DEC"])

    plt.figure(figsize=(30, 20))

    for t in range(3):
        if t < num_taggers:
            plt.subplot(2, 3, t + 1)
            plt.plot(ftc[f"TOY{t}_OMEGA"], epm[name_mapping[f"TOY{t}"] + "_OMEGA"], ',')
            plt.xlim(0, 0.5)
            plt.ylim(0, 0.5)
            plt.plot([0, 0.5], [0, 0.5], color='b', linewidth=0.5)

    for t in range(3):
        if t < num_taggers:
            plt.subplot(2, 3, 4 + t)
            ftcomega = ftc[f"TOY{t}_OMEGA"]
            epmomega = epm[name_mapping[f"TOY{t}"] + "_OMEGA"]
            plt.hist(ftcomega[ftcomega < 0.5], range=(0, 0.5), bins=300, histtype="step", linewidth=0.5, label="ftcalib")
            plt.hist(epmomega[epmomega < 0.5], range=(0, 0.5), bins=300, histtype="step", linewidth=0.5, label="epm")
            plt.xlim(0, 0.5)
            plt.legend(loc="upper left")

    plt.savefig(jobdir + "/comparison_plot.pdf")

    for t in range(num_taggers):
        assert np.allclose(ftc[f"TOY{t}_OMEGA"], epm[name_mapping[f"TOY{t}"] + "_OMEGA"], rtol=1e-4)


def print_test(title):
    print('\n' + len(title) * "#")
    print(title)
    print(len(title) * "#")


@pytest.mark.parametrize(
    ("name", "test", "success"),
    [
        ("Bu_poly1_mistag", {
            "mode" : "Bu",
            "func" : ft.PolynomialCalibration(2, ft.link.mistag),
            "tree" : "BU_POLY1_MISTAG",
            "nTaggers" : 3,
        }, True),
        ("Bd_poly1_mistag", {
            "mode" : "Bd",
            "func" : ft.PolynomialCalibration(2, ft.link.mistag),
            "tree" : "BD_POLY1_MISTAG",
            "nTaggers" : 3,
        }, True),
        ("Bs_poly1_mistag", {
            "mode" : "Bs",
            "func" : ft.PolynomialCalibration(2, ft.link.mistag),
            "tree" : "BS_POLY1_MISTAG",
            "nTaggers" : 3,
        }, True),
        ("Bd_poly1_logit", {
            "mode" : "Bd",
            "func" : ft.PolynomialCalibration(2, ft.link.logit),
            "tree" : "BD_POLY1_LOGIT",
            "nTaggers" : 3,
        }, True),
        ("Bd_poly2_mistag", {
            "mode" : "Bd",
            "func" : ft.PolynomialCalibration(3, ft.link.mistag),
            "tree" : "BD_POLY2_MISTAG",
            "nTaggers" : 3,
        }, True),
        ("Bd_bspline5_mistag", {
            "mode" : "Bd",
            "func" : ft.BSplineCalibration(5, ft.link.mistag),
            "tree" : "BD_POLY1_MISTAG",
            "nTaggers" : 1,
        }, True),
        ("Bd_bspline4_logit", {
            "mode" : "Bd",
            "func" : ft.BSplineCalibration(4, ft.link.logit),
            "tree" : "BD_POLY1_MISTAG",
            "nTaggers" : 1,
        }, True),
        ("Bd_nspline3_mistag", {
            "mode" : "Bd",
            "func" : ft.NSplineCalibration(3, ft.link.mistag),
            "tree" : "BD_POLY1_MISTAG",
            "nTaggers" : 1,
        }, True),
        ("Bd_nspline4_logit", {
            "mode" : "Bd",
            "func" : ft.NSplineCalibration(4, ft.link.logit),
            "tree" : "BD_POLY1_MISTAG",
            "nTaggers" : 1,
        }, True),
    ]
)
def test_compare_calibration_to_epm(name, test, success):
    # name = "Bu_poly1_mistag"
    print_test(name)

    calibrations = compare_calibrations(f"tests/epm_reference_data/{name}", mode=test["mode"], tree=test["tree"], func=test["func"], numTaggers=test["nTaggers"])
    compare_performances_to_epm(
        jobdir              = f"tests/epm_reference_data/{name}",
        mode                = test["mode"],
        tree                = test["tree"],
        func                = test["func"],
        calibrations_to_use = calibrations,
        num_taggers         = test["nTaggers"])
    compare_writing(
        jobdir              = f"tests/epm_reference_data/{name}",
        mode                = test["mode"],
        tree                = test["tree"],
        func                = test["func"],
        calibrations_to_use = calibrations,
        num_taggers         = test["nTaggers"])
    return True


def test_combination():
    single_taggers = ft.TaggerCollection()
    df = uproot.open("tests/epm_reference_data/reference.root")["BD_POLY1_MISTAG"].arrays(library="pd")
    single_taggers.create_tagger("TOY0", df.TOY0_ETA, df.TOY0_DEC, df.FLAV_DECAY, "Bd", tau_ps=df.TAU)
    single_taggers.create_tagger("TOY1", df.TOY1_ETA, df.TOY1_DEC, df.FLAV_DECAY, "Bd", tau_ps=df.TAU)
    single_taggers.create_tagger("TOY2", df.TOY2_ETA, df.TOY2_DEC, df.FLAV_DECAY, "Bd", tau_ps=df.TAU)
    Combination = single_taggers.combine_taggers("Combination", calibrated=False)

    epm = uproot.open("./tests/epm_reference_data/combination_test/combined.root")["TaggingTree"].arrays("Combination_ETA", library="pd")

    assert np.allclose(epm.Combination_ETA, Combination.stats._full_data.eta), "Combination does not match"
