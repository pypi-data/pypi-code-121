# coding: utf-8
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class CoverageArticle(AbstractArticle):
    """
    This entity gets created from a CoverageTicket.
    """
    dynamic_fields_names = (
        "tipusVia", "nomVia", "numero", "bloc", "portal", "pis", "escala", "porta",
        "poblacioServei", "provinciaServei", "codiProvinciaServei", "CPservei", "altresCobertura",
        "coberturaADSL", "coberturaFibraMM", "coberturaFibraVdf", "coberturaFibraOrange", "IDhogar"
    )
    subject = "Sol·licitud cobertura"

    def __init__(self, ticket):
        self.ticket = ticket
        self.body = self._body()

    def _body(self):
        body = ""
        for df_name in self.dynamic_fields_names:
            df_value = getattr(self.ticket, df_name)
            if df_value:
                body = u"{}{}: {}\n".format(body, df_name, df_value)
        return body
