from typing import Optional, Dict, List
import uuid

def template_DSCB(observable:"ROOT.RooRealVar", weight:Optional[str]=None, n_bins:Optional[int]=None,
                  tree:Optional["ROOT.TTree"]=None, hist:Optional["ROOT.TH1"]=None):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    
    if n_bins is None:
        n_bins = observable.numBins()
    vmin = observable.getMin()
    vmax = observable.getMax()
    name = observable.GetName()
    
    mask = 1*(tree is not None) + 2*(hist is not None)
    if mask not in [1, 2]:
        raise RuntimeError("either a tree or a histogram must be provided to setup model parameter templates")
    # case a tree is given
    if mask == 1:
        h_name = uuid.uuid4().hex
        hist = ROOT.TH1D(h_name, h_name, n_bins, vmin, vmax)
        if weight is not None:
            tree.Draw(f"{name} >> {h_name}", weight)
        else:
            tree.Draw(f"{name} >> {h_name}")
    # evaluate shape properties
    hist_max             = hist.GetMaximum()
    hist_bin_pos_max     = hist.GetMaximumBin()
    hist_pos_max         = hist.GetBinCenter(hist_bin_pos_max)
    hist_pos_FWHM_low    = hist.GetBinCenter(hist.FindFirstBinAbove(0.5 * hist_max))
    hist_pos_FWHM_high   = hist.GetBinCenter(hist.FindLastBinAbove(0.5 * hist_max))
    hist_sigma_effective = (hist_pos_FWHM_high - hist_pos_FWHM_low) / 2.355;
    # free memory
    if mask == 1:
        hist.Delete()
    parameters = {
        'muCBNom': ROOT.RooRealVar("muCBNom", "mean of CB", hist_pos_max, hist_pos_FWHM_low, hist_pos_FWHM_high),
        'sigmaCBNom': ROOT.RooRealVar("sigmaCBNom", "sigma of CB", hist_sigma_effective, 0., 5 * hist_sigma_effective),
        'alphaCBLo': ROOT.RooRealVar("alphaCBLo", "alpha of CB", 1, 0., 5.),
        'nCBLo': ROOT.RooRealVar("nCBLo", "n of CB", 10, 0., 200.),
        'alphaCBHi': ROOT.RooRealVar("alphaCBHi", "alpha of CB", 1, 0., 5.),
        'nCBHi': ROOT.RooRealVar("nCBHi", "n of CB", 10, 0., 200.)
    }
    return parameters

def template_ExpGaussExp(observable:"ROOT.RooRealVar", weight:Optional[str]=None,
                         tree:Optional["ROOT.TTree"]=None, hist:Optional["ROOT.TH1"]=None):
    parameters = {
        "EGE_mean": ROOT.RooRealVar("EGE_mean", "mean of EGE", 124.5, 123., 126.),
        "EGE_sigma": ROOT.RooRealVar("EGE_sigma", "sigma of EGE", 2.5, 0.5, 8.0),
        "EGE_kLo": ROOT.RooRealVar("EGE_kLo", "kLow of EGE", 2.5, 0.01, 10.0),
        "EGE_kHi": ROOT.RooRealVar("EGE_kHi", "kHigh of EGE", 2.4, 0.01, 10.0)
    }
    return parameters

def template_Bukin(observable:"ROOT.RooRealVar", weight:Optional[str]=None,
                   tree:Optional["ROOT.TTree"]=None, hist:Optional["ROOT.TH1"]=None):
    parameters = {
        "Bukin_Xp": ROOT.RooRealVar("Bukin_Xp", "peak position", 124.5, 123., 126.),
        "Bukin_sigp": ROOT.RooRealVar("Bukin_sigp", "peak width as FWHM divided by 2*sqrt(2*log(2))=2.35",
                                      0.5, 0.01, 2.0),
        "Bukin_xi": ROOT.RooRealVar("Bukin_xi", "peak asymmetry", 0.0, -1, 1),
        "Bukin_rho1": ROOT.RooRealVar("Bukin_rho1", "left tail", -0.1, -1.0, 0.0),
        "Bukin_rho2": ROOT.RooRealVar("Bukin_rho2", "right tail", 0.0, 0.0, 1.0)
    }
    return parameters

def template_Exp(observable:"ROOT.RooRealVar", weight:Optional[str]=None,
                 tree:Optional["ROOT.TTree"]=None, hist:Optional["ROOT.TH1"]=None):
    parameters = {
        "Exp_c": ROOT.RooRealVar("Exp_c", "Exp_c", 1, -10, 10)
    }
    return parameters

template_maps = {
    'DSCB': template_DSCB,
    'RooTwoSidedCBShape': template_DSCB,
    'ExpGaussExp': template_ExpGaussExp,
    'RooExpGaussExpShape': template_ExpGaussExp,
    'Bukin': template_Bukin,
    'RooBukinPdf': template_Bukin,
    'Exp': template_Exp,
    'RooExponential': template_Exp
}


def get_param_templates(model:str):
    if model not in template_maps:
        raise RuntimeError(f"no default parameter templates found for the model \"{model}\"")
    return template_maps[model]