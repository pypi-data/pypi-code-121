# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.protect.rule.base_rule import BaseRule

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class Ssrf(BaseRule):
    """
    Ssrf Protection rule
    Currently in BETA.
    """

    RULE_NAME = "ssrf"

    def is_postfilter(self):
        return False

    def build_sample(self, evaluation, url, **kwargs):
        sample = self.build_base_sample(evaluation)
        if url is not None:
            sample.ssrf.url = url
        return sample

    def sample_dtm_to_json(self, sample):
        return {"url": sample.ssrf.url}
