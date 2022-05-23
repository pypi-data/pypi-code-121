import pytest
import rsrfile
from datetime import datetime


@pytest.yield_fixture
def opened_file():
    fileobj = rsrfile.open(r'./tests/data/cons_acase.RSR', 'r')
    try:
        yield fileobj
    finally:
        fileobj.close()

def test_MCSSummary(opened_file):
    mcs_summary = opened_file.MCSSummary
    assert mcs_summary.DateTime == datetime(2022, 5, 13, 8, 18, 4) 
    assert mcs_summary.InputFormat==1
    assert mcs_summary.AcaseType==33
    assert mcs_summary.AcaseSpec1_rsat==3040518
    assert mcs_summary.AcaseSpec1_rsatexe==3040518
    assert mcs_summary.AcaseSpec1_rsmisc==3040518
    assert mcs_summary.AcaseSpec1_rsuit==3040518
    assert mcs_summary.AcaseSpec1_rsmcs==3040518
    assert mcs_summary.AcaseSpec2==144
    assert mcs_summary.BCSetUsed==0
    assert mcs_summary.CalcType==4
    assert mcs_summary.Time==0.0
    assert mcs_summary.CutOffType==1
    assert mcs_summary.AbsCutOff==9.9999998245167e-14
    assert mcs_summary.RelCutOff==0.0
    assert mcs_summary.Approx==1
    assert mcs_summary.IncludeCCF==65535
    assert mcs_summary.NegationHandling==1
    assert mcs_summary.SaveCutoff==0.0
    assert mcs_summary.MaxSaveModMCS==10000000
    assert mcs_summary.MaxSavedDemodMCS==10000000
    assert mcs_summary.Events==39444
    assert mcs_summary.BEEvents==5538
    assert mcs_summary.CCFEvents==8497
    assert mcs_summary.Gates==25409
    assert mcs_summary.PrimaryEvents==14035
    assert mcs_summary.ModEvents==39510
    assert mcs_summary.ModBEEvents==5508
    assert mcs_summary.ModCCFEvents==8427
    assert mcs_summary.ModGates==23631
    assert mcs_summary.ModPrimaryEvents==8883
    assert mcs_summary.Modules==1944
    assert mcs_summary.ModChildren==6996
    assert mcs_summary.MCSMod==1845
    assert mcs_summary.MCSDemod==2356
    assert mcs_summary.MCSModSaved==1845
    assert mcs_summary.MCSDemodSaved==2356
    assert mcs_summary.QBestApprox==1.1728675476161502e-09
    assert mcs_summary.WBestApprow==0.0
    assert mcs_summary.TruncErrorMod==2.8210024895924094e-05
    assert mcs_summary.TruncErrorDemod==6.237134986155586e-11
    assert mcs_summary.TruncErrorTot==2.8210087267273956e-05
    assert mcs_summary.UsedCutoffDemod==9.9999998245167e-14
    assert mcs_summary.UsedCutoffMod==9.9999998245167e-14
    assert mcs_summary.RunTimeTot==488.147
    assert mcs_summary.RunTimeMCS==482.537

def test_UNCSummary(opened_file):
    unc_summary = opened_file.UNCSummary
    assert unc_summary.DateTime == datetime(2022, 5, 13, 8, 18, 38)
    assert unc_summary.CalcType==4
    assert unc_summary.Time==0.0
    assert unc_summary.AbsCutOff==0.0
    assert unc_summary.Simulations==99999
    assert unc_summary.SimType==2
    assert unc_summary.Seed==12345
    assert unc_summary.RngType==2
    assert unc_summary.Mean==1.1222901192322351e-09
    assert unc_summary.Median==7.240581801859939e-10
    assert unc_summary.f5th==2.2864226573306478e-10
    assert unc_summary.f95th==3.0865799139934854e-09
    assert unc_summary.RunTimeTot==34.111

def test_TimeDepSummary(opened_file):
    pass

def test_unc_cdf_pdf(opened_file):
    #assert  opened_file.unc_pdf[2] == (0.0, 4.981830252434798e-11) 
    assert  opened_file.unc_cdf[2] == (0.0, 4.981830252434798e-11)

