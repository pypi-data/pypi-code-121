from mfire.settings import get_logger

# Logging
LOGGER = get_logger(name="base_selector.mod", bind="base_selector")


class BaseSelector:
    """ BaseSelector qui doit renvoyer une clé de template
    """

    def compute(self, reduction: dict) -> str:
        """ génération du dictionnaire de choix, recherche dans la matrice
        du texte de synthèse pour détermier la clé du template
        en fonction du paramètre
        """

        key = None

        return key
