#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import climetlab as cml
from climetlab import Dataset
import cf2cdm


from .utils import Parser, ReprMixin, handle_cropping_area

class GlofasSeasonal(Dataset, ReprMixin):
    name = None
    home_page = "-"
    licence = "-"
    documentation = "-"
    citation = "-"
    request = "-"


    terms_of_use = (
        "By downloading data from this dataset, you agree to the terms and conditions defined at "
        "https://github.com/ecmwf-lab/climetlab_cems_flood/LICENSE"
        "If you do not agree with such terms, do not download the data. "
    )

    temporal_range = [2021, date.today().year]

    def __init__(self, system_version, model, variable, period, leadtime, area = None, lat = None, lon = None):

        self.parser = Parser(self.temporal_range)

        years, months, _ = self.parser.period(period)

        leadtime_hour = self.parser.leadtime(leadtime, 24)

        self.request = {
            "system_version": system_version,
            "hydrological_model": model,
            "variable": variable,
            "year": years,
            "month": months,
            "leadtime_hour": leadtime_hour,
            "format": "grib",
        }

        handle_cropping_area(self.request, area, lat, lon)

        self.source = cml.load_source("cds", "cems-glofas-seasonal", **self.request)



    def to_xarray(self):
        ds = self.source.to_xarray().isel(surface=0,drop=True)
        return cf2cdm.translate_coords(ds, cf2cdm.CDS)