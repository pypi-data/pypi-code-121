from typing import Dict, Union, List, Optional

import numpy as np

import ROOT

from quickstats import semistaticmethod
from quickstats.interface.cppyy.vectorize import as_np_array

class RooAbsPdf:
    @staticmethod
    def extract_sum_pdfs_by_category(pdf:ROOT.RooAbsPdf, poi:Optional[ROOT.RooRealVar]=None):
        pdf_class = pdf.ClassName()
        if pdf_class != "RooSimultaneous":
            raise RuntimeError(f"input pdf must be a RooSimultaneous instance (`{pdf_class}` received)")
        cat = pdf.indexCat()
        n_cat = cat.size()
        result = {}
        for i in range(n_cat):
            cat.setBin(i)
            cat_name = cat.getLabel()
            cat_pdf = pdf.getPdf(cat_name)
            cat_pdf_class = cat_pdf.ClassName()
            if cat_pdf_class != "RooProdPdf":
                raise RuntimeError(f"category pdf must be a RooProdPdf instance (`{cat_pdf_class}` received)")
            target_pdf = [i for i in cat_pdf.pdfList() if i.ClassName() == "RooRealSumPdf" and i != cat_pdf]
            if not target_pdf:
                raise RuntimeError(f"category pdf does not contain a RooRealSumPdf component")
            if len(target_pdf) > 1:
                raise RuntimeError(f"expect only one RooRealSumPdf component from category pdf but {len(target_pdf)} found")
            target_pdf = target_pdf[0]
            if poi is None:
                result[cat_name] = [i for i in pdf.getComponents()]
            else:
                result[cat_name] = [i for i in pdf.getComponents() if i.dependsOn(poi)]
        return result