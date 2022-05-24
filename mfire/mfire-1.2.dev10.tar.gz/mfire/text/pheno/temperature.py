"""
@package lib.text.pheno.temperature

Temperature text module
"""

# Standard packages

# Third parties packages
import xarray as xr

# Own package
from mfire.data.aggregator import Aggregator
from mfire.utils.unit_converter import convert_dataarray
from mfire.composite.events import EventComposite
from mfire.text.pheno.pheno import Pheno
from mfire.utils.my_profile import logwrap
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="text.temperature.mod", bind="text.temperature")


class TemperatureGeneric(Pheno):
    def __init__(self, geos, temperature, *args, **kwargs):
        super().__init__(geos, *args, **kwargs)
        self.temperature = temperature
        self.units = kwargs.get("units", {"temperature": "°C"})
        self._values = None

    @property
    def values(self):
        if isinstance(self._values, xr.Dataset):
            return self._values
        values_list = []
        for field in self.temperature:
            # A corriger
            temp_kwargs = {"field": field, "geos": self.geos}
            element_event = EventComposite(**temp_kwargs)
            element_event.compute()
            agg_handler = Aggregator(element_event.field, mask=element_event.mask)
            mini_da = convert_dataarray(
                agg_handler.compute("min"), self.units["temperature"]
            )
            maxi_da = convert_dataarray(
                agg_handler.compute("max"), self.units["temperature"]
            )
            values_list += [xr.Dataset({"mini": mini_da, "maxi": maxi_da})]
        self._values = xr.merge(values_list)
        return self._values

    @logwrap(logger=LOGGER)
    def generate(self):
        try:
            mini = int(self.values["mini"].values.round().min())
            maxi = int(self.values["maxi"].values.round().max())
            text = f"Température : mini={mini}°C, maxi={maxi}°C"
        except BaseException:
            text = "Température : données non disponibles"
        return text
