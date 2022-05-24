"""
This module handle temporal localisation
"""
import numpy as np
import xarray as xr
from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="temporal_localisation.mod", bind="temporal_localisation")

xr.set_options(keep_attrs=True)


class TemporalLocalisation:
    """
        Class used to perform temporal localisation
        The assumption are the following :
            - The table is relatively small (a few area and less than 70 timesteps).
    """

    def __init__(
        self, da, time_dimension="valid_time", area_dimension="id", trim_period=True
    ):
        """
        Initialize the table for temporal localisation

        Args:
            da ([dataArray]): The dataArray we need to summarize
            time_dimension (str, optional): The name of the time_dimension.
                Defaults to 'step'.
            area_dimension (str, optional): The name of the dimension for areas.
                Defaults to 'area'.
            trim_period (bool, optional): Do we exclude bounds if there is no risk.
                Defaults to True.
        """
        self.table = da
        self.time_dimension = time_dimension
        self.area_dimension = area_dimension
        self.trim_period = trim_period

        tmp = self.table.sum(self.area_dimension)
        start_p = (
            tmp.where(tmp > 0)
            .dropna(self.time_dimension)[self.time_dimension][0]
            .values
        )
        end_p = (
            tmp.where(tmp > 0)
            .dropna(self.time_dimension)[self.time_dimension][-1]
            .values
        )

        self.table_shorten = self.table.sel(
            {self.time_dimension: slice(start_p, end_p)}
        )

    def update(self, trim_period=True):
        """
        Update informaiton on trimming.
        Args:
            trim_period (bool, optional): Do we need to summarized only
                the period with risk? Defaults to True.
        """
        self.trim_period = trim_period

    def new_division(self, delta_h=3) -> xr.DataArray:
        """
        Effectue la division en prenant en compte que chaque periode
        doit être au moins de delta_h.

        Args:
            delta_h : durée (en heure) minimale de périodes
        """
        if self.trim_period:
            table = self.table_shorten
        else:
            table = self.table

        # On va avoir différents cas en fonction de la taille
        # Si la taille est petite, on aura qu'un seul tableau
        # Si la taille est plus importante sans excéder les 9h
        #   on pourra avoir deux colonnes
        # Si la taille est encore plus grande, on aura 3 colonnes
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        delta = max_time - min_time
        nb_hour = int(delta / np.timedelta64(1, "h")) + 1
        bounds = None
        if nb_hour >= 3 * delta_h:
            # Si le nombre d'heure est supérieur à 9 on peut avoir trois colonnes
            bounds = self.three_bounds(delta_h=delta_h)
        elif nb_hour >= 2 * delta_h:
            bounds = self.two_bounds_bourrin(delta_h=delta_h)
        summary = []
        if bounds is None:
            summary.append(self.get_period_summary(table))
        elif len(bounds) == 1:
            tab1_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(bounds[0], "h")
                    )
                }
            )
            tab2_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[0] + 1, "h"), max_time
                    )
                }
            )
            summary.append(self.get_period_summary(tab1_f))
            summary.append(self.get_period_summary(tab2_f))
        elif len(bounds) == 2:
            tab1_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(bounds[0], "h")
                    )
                }
            )
            tab2_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[0] + 1, "h"),
                        min_time + np.timedelta64(bounds[1], "h"),
                    )
                }
            )
            tab3_f = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(bounds[1] + 1, "h"), max_time
                    )
                }
            )
            summary.append(self.get_period_summary(tab1_f))
            summary.append(self.get_period_summary(tab2_f))
            summary.append(self.get_period_summary(tab3_f))
        else:
            LOGGER.error("Not implemented yet")
            raise ValueError("We can not have more than two bounds.")

        dout = xr.merge(summary)
        return dout["elt"]

    def two_bounds_bourrin(self, delta_h):
        """
        Looking at bounds for division.
        We make the hypothesis that the information is summarized
        by the maxi risk over the period.
        The methodology is very crude : we look at each possibility and take the best.
        However, due to de problem size it seems we can afford it.

        This function divide in 3 periods (with 2 bounds)
        To Do : implement limit case (when there is only one or two steps)
        Returns:
            [list]: the bounds

        History :
          Adding to int : Enable the input table to be a boolean table.
        """
        if self.trim_period:
            table = self.table_shorten.astype(int)
        else:
            table = self.table.astype(int)

        # Retourne la période la premiere échéance avec un delta de 3H
        # On va maintenant fonctionner non pas en indice mais en horaire.
        #
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        nb_hour = int((max_time - min_time) / np.timedelta64(1, "h"))
        error_min = table.size
        selected_bounds = None
        # On va boucler sur les heures
        # Globalement on va tester de min_time + 2 à max_time -2 si on peut être
        # sur la tranche qui change.

        for x in range(delta_h - 1, nb_hour - (delta_h - 1)):
            tab1 = table.sel(
                {
                    self.time_dimension: slice(
                        min_time, min_time + np.timedelta64(x, "h")
                    )
                }
            )
            tab1max = tab1.max(self.time_dimension)
            tab2 = table.sel(
                {
                    self.time_dimension: slice(
                        min_time + np.timedelta64(x + 1, "h"), max_time
                    )
                }
            )
            tab2max = tab2.max(self.time_dimension)
            error = ((tab1 - tab1max) ** 2).sum() + ((tab2 - tab2max) ** 2).sum()
            if error < error_min:
                error_min = error
                selected_bounds = [x]
        return selected_bounds

    def three_bounds(self, delta_h):
        if self.trim_period:
            table = self.table_shorten.astype(int)
        else:
            table = self.table.astype(int)

        # Retourne la période la premiere échéance avec un delta de 3H
        # On va maintenant fonctionner non pas en indice mais en horaire.
        #
        min_time = table[self.time_dimension].min()
        max_time = table[self.time_dimension].max()
        nb_hour = int((max_time - min_time) / np.timedelta64(1, "h"))
        error_min = table.size
        selected_bounds = None
        # On va boucler sur les heures
        # Globalement on va tester de min_time + 2 à max_time -2 si on peut être
        # sur la tranche qui change.

        for x in range(delta_h - 1, nb_hour - (2 * delta_h - 1)):
            for y in range(x + delta_h, nb_hour - delta_h + 1):

                tab1 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time, min_time + np.timedelta64(x, "h")
                        )
                    }
                )
                tab1max = tab1.max(self.time_dimension)
                tab2 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time + np.timedelta64(x + 1, "h"),
                            min_time + np.timedelta64(y, "h"),
                        )
                    }
                )
                tab2max = tab2.max(self.time_dimension)
                tab3 = table.sel(
                    {
                        self.time_dimension: slice(
                            min_time + np.timedelta64(y + 1, "h"), max_time
                        )
                    }
                )
                tab3max = tab3.max(self.time_dimension)
                error = (
                    ((tab1 - tab1max) ** 2).sum()
                    + ((tab2 - tab2max) ** 2).sum()
                    + ((tab3 - tab3max) ** 2).sum()
                )
                if error < error_min:
                    error_min = error
                    selected_bounds = [x, y]
        return selected_bounds

    def get_period_summary(self, table):
        """
        Summarize information for the period.
        Take the maximum over the period as the value
        Take the period bounds to rename the period

        Args:
            table (DataArray): The dataArray to summarize.
                Should have self.time_dimension as dimension

        Returns:
            [Dataset]: The summarized table
        """
        res = xr.Dataset()
        value = table.max(self.time_dimension).astype(np.float)
        period_objet = table[self.time_dimension]
        p_name = (
            period_objet[0].dt.strftime("%Y%m%dT%H").values
            + "_to_"
            + period_objet[-1].dt.strftime("%Y%m%dT%H").values
        )
        LOGGER.debug(f"period_name is {p_name}")
        res["elt"] = value
        res = res.expand_dims("period").assign_coords(period=[p_name])
        return res


if __name__ == "__main__":
    import datetime as dt
    import numpy.random as npr
    import xarray as xr

    # On fixe la seed afin d'avoir une reproductibilité des résultats.
    npr.seed(0)
    din = xr.Dataset()
    din.coords["valid_time"] = [
        dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(40)
    ]
    din.coords["id"] = ["A" + str(i) for i in range(4)]
    din["elt"] = (("valid_time", "id"), npr.binomial(1, 0.1, (40, 4)))
    Thandler = TemporalLocalisation(din["elt"])
    dout = Thandler.new_division()
    print(dout)
    dout = Thandler.new_division(delta_h=5)
    print(dout)

    npr.seed(0)
    nb_time = 8
    din = xr.Dataset()
    din.coords["valid_time"] = [
        dt.datetime(2019, 1, 1) + dt.timedelta(hours=i) for i in range(nb_time)
    ]
    din.coords["id"] = ["A" + str(i) for i in range(4)]
    din["elt"] = (("valid_time", "id"), npr.binomial(1, 0.2, (nb_time, 4)))
    Thandler = TemporalLocalisation(din["elt"])
    dout = Thandler.new_division()
