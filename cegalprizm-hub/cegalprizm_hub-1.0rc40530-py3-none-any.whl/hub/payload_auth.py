# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from typing import Sequence


class PayloadAuth:

    def __init__(self, required_audiences: Sequence[str] = None, required_app_claims: Sequence[str] = None):
        self._required_audiences = required_audiences
        self._required_app_claims = required_app_claims

    @property
    def required_audiences(self):
        return self._required_audiences

    @property
    def required_app_claims(self):
        return self._required_app_claims
