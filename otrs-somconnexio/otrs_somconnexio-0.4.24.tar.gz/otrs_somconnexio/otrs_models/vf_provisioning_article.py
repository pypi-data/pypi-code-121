# coding: utf-8
from otrs_somconnexio.otrs_models.abstract_article import AbstractArticle


class VfProvisioningArticle(AbstractArticle):
    def __init__(self, provisioning_ticket):
        self.subject = "Aprovisionament del tiquet de Vodafone {}".format(provisioning_ticket["ticket"])
        self.body = self._body_from_dict(provisioning_ticket)

    def _body_from_dict(self, dct):
        body = ""

        for field in sorted(dct):
            value = dct[field]
            if value:
                body = u"{}{}: {}\n".format(body, field, value)

        return body
