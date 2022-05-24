from typing import Union, Dict
import xarray as xr
from mfire.localisation.localisation_manager import Localisation


class ComponentInterface:
    @property
    def log_ids(self):
        """Permet de recupérer des infos pour le logging"""

    def get_template_key(self):
        """ Permet d'avoir la clé pour le template"""

    def get_template_type(self):
        """Permet d'avoir le type de template"""

    def get_production_datetime(self):
        """
        Permet d'avoir la date de production
        """

    def get_periods_name(self):
        """
        Permet d'avoir le nom des périodes
        """

    def get_areas_name(self):
        """
        Permet d'avoir le nom des zones
        """

    def merge_area(self):
        """
        Permet de merger des areas
        """

    def get_critical_value(self):
        """
        Permet d'avoir les valeurs critiques
        """

    def get_risk_name(self):
        """
        Permet d'avoir le nom du risque.
        """


class ComponentHandlerLocalisation(ComponentInterface):
    """
    Classe permettant de faire dialoguer le resultat de la localisaiton et les modules
    de generation de commentaires.
    Cette classe est à l'interface entre les deux et permet d'aisément de faire passer
    l'info.
    Ainsi les modules de textes n'ont pas à savoir où sont les infos.
    """

    def __init__(self, localisation_handler: Localisation):
        """Init a component Handler based on localisation objetc

        Args:
            localisation_handler (Localisation): The localisation object
        """
        self.localisation_handler = localisation_handler
        self.unique_table = self.localisation_handler.get_unique_table()

    @property
    def log_ids(self) -> Dict[str, str]:
        return {
            "production_id": self.localisation_handler.component.production_id,
            "production_name": self.localisation_handler.component.production_name,
            "component_id": self.localisation_handler.component.id,
            "component_name": self.localisation_handler.component.name,
            "hazard_id": self.localisation_handler.component.hazard,
            "hazard_name": self.localisation_handler.component.hazard_name,
            "geo_id": self.localisation_handler.geo_id,
        }

    def get_template_key(self) -> str:
        return self.localisation_handler.get_unique_name()

    def get_production_datetime(self):
        return self.localisation_handler.component.production_datetime

    def get_periods_name(self) -> list:
        return list(self.unique_table.period.values.tolist())

    def get_areas_name(self) -> list:
        return list(self.unique_table.areaName.values)

    def get_areas_id(self) -> list:
        return list(self.unique_table.id.values.tolist())

    def merge_area(self, da: Union[xr.DataArray, list]) -> xr.DataArray:
        """Merge areas in a dataarray. If a list is given, it uses
        a list of ids to select from self.unique_table

        Args:
            da (Union[xr.DataArray, list]): Areas dataarray

        Returns:
            xr.DataArray: Merged dataarray
        """
        if isinstance(da, list):
            # case of given da is a list
            return self.merge_area(self.unique_table.sel(id=da))
        return self.localisation_handler.summarized_handler.merge_zones(da)

    def modify_template(self, areaIds: list):
        self.localisation_handler.summarized_handler.update_uniqueTable(areaIds)
        self.unique_table = self.localisation_handler.get_unique_table()

    def get_unique_table(self) -> xr.DataArray:
        return self.unique_table

    def get_critical_value(self) -> dict:
        return self.localisation_handler.get_critical_values()

    def get_risk_name(self) -> str:
        return self.localisation_handler.component.hazard_name

    def get_template_type(self, risk_level=None) -> str:
        """
        This function enable to know which kind of template we should use.
        It is (currently) based only on the variable found at a given level.

        Returns:
            str: [description]
        """
        template_type = self.localisation_handler.get_level_type(risk_level)
        return template_type

    @classmethod
    def open(cls, repo: str):
        """Open a componentHandler based on localisation.
        To do so, use a savedLocalisation Object

        Args:
            repo (str): path for instansiating the localisation object

        Returns:
            cls: The componentHandler initialized
        """
        return cls(Localisation.load(repo=repo))


if __name__ == "__main__":
    compo_handler = ComponentHandlerLocalisation.open(
        repo="/scratch/labia/chabotv/tmp/test_save/"
    )
    print(compo_handler.get_template_key())
    print(compo_handler.get_production_datetime())
    print(compo_handler.get_periods_name())
    print(compo_handler.get_areas_name())
    print(compo_handler.get_areas_id())
    print(compo_handler.get_risk_name())
    print(compo_handler.get_level_type())
    dout = compo_handler.merge_area(compo_handler.unique_table)
    print(dout.areaName)
    IDS = compo_handler.get_areas_id()
    dout2 = compo_handler.merge_area(IDS)
    print(dout2.areaName)
    print(compo_handler.get_critical_value())
