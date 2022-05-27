#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
import climetlab as cml
from climetlab import Dataset
import cf2cdm


from .utils import (
    Parser,
    ReprMixin,
    handle_cropping_area,
    build_multi_request
)




class GlofasForecast(Dataset, ReprMixin):
    """_summary_

    :param system_version: _description_
    :type system_version: _type_
    :param product_type: _description_
    :type product_type: _type_
    :param model: _description_
    :type model: _type_
    :param variable: _description_
    :type variable: _type_
    :param period: _description_
    :type period: _type_
    :param leadtime_hour: _description_
    :type leadtime_hour: _type_
    :param area: _description_, defaults to None
    :type area: _type_, optional
    :param lat: _description_, defaults to None
    :type lat: _type_, optional
    :param lon: _description_, defaults to None
    :type lon: _type_, optional
    :param split_on: _description_, defaults to None
    :type split_on: _type_, optional
    :param threads: _description_, defaults to None
    :type threads: _type_, optional
    :param merger: _description_, defaults to False
    :type merger: bool, optional
        """
        
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

    temporal_range = [2019, date.today().year]

    def __init__(
        self,
        system_version,
        product_type,
        model,
        variable,
        period,
        leadtime_hour,
        area=None,
        lat=None,
        lon=None,
        split_on=None,
        threads=None,
        merger=False
    ):
        """Constructor method
        """


        if threads is not None:
            cml.sources.SETTINGS.set("number-of-download-threads", threads)

        self.parser = Parser(self.temporal_range)

        years, months, days = self.parser.period(period)

        leadtime_hour = self.parser.leadtime(leadtime_hour, 24)

        self.request = {
            "system_version": system_version,
            "hydrological_model": model,
            "product_type": product_type,
            "variable": variable,
            "year": years,
            "month": months,
            "day": days,
            "leadtime_hour": leadtime_hour,
            "format": "grib",
        }

        handle_cropping_area(self.request, area, lat, lon)

        if split_on is not None:
            sources, output_names = build_multi_request(self.request, split_on, dataset ='cems-glofas-forecast')
            self.output_names = output_names
            self.source = cml.load_source("multi", sources, merger=merger)
            
        else:
            self.output_names = None
            self.source = cml.load_source("cds", "cems-glofas-forecast", **self.request)
            

    def to_xarray(self):
        ds = self.source.to_xarray().isel(surface=0, drop=True)
        return cf2cdm.translate_coords(ds, cf2cdm.CDS)

