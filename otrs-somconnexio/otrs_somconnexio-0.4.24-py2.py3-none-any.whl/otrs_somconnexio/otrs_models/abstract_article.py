# coding: utf-8
from pyotrs.lib import Article


class AbstractArticle:

    subject = ""
    body = ""
    # Parameter to mark notes field red and available only for personnel
    isVisibleForCustomer = "1"

    def call(self):
        article_params = {
            "Subject": self.subject,
            "Body": self.body,
            "ContentType": "text/plain; charset=utf8",
            "IsVisibleForCustomer": self.isVisibleForCustomer,
        }

        return Article(article_params)
