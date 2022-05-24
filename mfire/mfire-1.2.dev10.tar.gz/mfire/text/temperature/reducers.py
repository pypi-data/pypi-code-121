from mfire.settings import get_logger
from mfire.text.base import BaseReducer

from mfire.composite import WeatherComposite

# Logging
LOGGER = get_logger(name="temperature_reducer.mod", bind="temperature_reducer")


class TemperatureReducer(BaseReducer):
    """ Classe Reducer pour le module temperature.

    La méthode "compute" ici prend en entrée un "WeatherComposite" contenant
    exactement un "field" "temperature".

    Le résumé en sortie a la structure suivante:
    self.summary = {
        "general": {
            "start": <Datetime: date de début>,
            "stop": <Datetime: date de fin>,
            "temperature": {
                "units": <str: unités>,
                "mini": {
                    "low": <float: valeur basse des minimales>,
                    "high": <float: valeur haute des minimales>,
                },
                "maxi": {
                    "low": <float: valeur basse des maximales>,
                    "high": <float: valeur haute des maximales>,
                }
            }
        },
        "meta": {
            "production_datetime": <Datetime: date de début de production>,
        }
    }
    """

    def add_general_bloc(self) -> None:
        """ Méthode qui permet d'ajouter le bloc "general" au self.summary.

        Ce bloc "general" concerne toute la période et toutes les zones et permet
        de calculer les minimales et maximales.
        """
        pass

    def add_metadata(self) -> None:
        """ Méthode qui ajoute au summary les metadata d'intérêt.
        """
        pass

    def compute(self, compo: WeatherComposite, metadata: dict = None) -> dict:
        super().compute(compo=compo)
        self.add_general_bloc()
        self.add_metadata()
        return self.summary
