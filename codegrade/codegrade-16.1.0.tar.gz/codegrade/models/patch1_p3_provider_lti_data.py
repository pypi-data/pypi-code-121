"""The module that defines the ``Patch1P3ProviderLTIData`` model.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

import typing as t
from dataclasses import dataclass, field

import cg_request_args as rqa
from cg_maybe import Maybe, Nothing
from cg_maybe.utils import maybe_from_nullable

from ..utils import to_dict


@dataclass
class Patch1P3ProviderLTIData:
    """Input data required for the `LTI::Patch1P3Provider` operation."""

    #: The new iss.
    iss: Maybe["str"] = Nothing
    #: The new client id.
    client_id: Maybe["str"] = Nothing
    #: The new authentication token url.
    auth_token_url: Maybe["str"] = Nothing
    #: The new authentication login url.
    auth_login_url: Maybe["str"] = Nothing
    #: The new key set url.
    key_set_url: Maybe["str"] = Nothing
    #: The new OAuth2 audience.
    auth_audience: Maybe["str"] = Nothing
    #: Should this provider be finalized.
    finalize: Maybe["bool"] = Nothing

    raw_data: t.Optional[t.Dict[str, t.Any]] = field(init=False, repr=False)

    data_parser: t.ClassVar = rqa.Lazy(
        lambda: rqa.FixedMapping(
            rqa.OptionalArgument(
                "iss",
                rqa.SimpleValue.str,
                doc="The new iss.",
            ),
            rqa.OptionalArgument(
                "client_id",
                rqa.SimpleValue.str,
                doc="The new client id.",
            ),
            rqa.OptionalArgument(
                "auth_token_url",
                rqa.SimpleValue.str,
                doc="The new authentication token url.",
            ),
            rqa.OptionalArgument(
                "auth_login_url",
                rqa.SimpleValue.str,
                doc="The new authentication login url.",
            ),
            rqa.OptionalArgument(
                "key_set_url",
                rqa.SimpleValue.str,
                doc="The new key set url.",
            ),
            rqa.OptionalArgument(
                "auth_audience",
                rqa.SimpleValue.str,
                doc="The new OAuth2 audience.",
            ),
            rqa.OptionalArgument(
                "finalize",
                rqa.SimpleValue.bool,
                doc="Should this provider be finalized.",
            ),
        ).use_readable_describe(True)
    )

    def __post_init__(self) -> None:
        getattr(super(), "__post_init__", lambda: None)()
        self.iss = maybe_from_nullable(self.iss)
        self.client_id = maybe_from_nullable(self.client_id)
        self.auth_token_url = maybe_from_nullable(self.auth_token_url)
        self.auth_login_url = maybe_from_nullable(self.auth_login_url)
        self.key_set_url = maybe_from_nullable(self.key_set_url)
        self.auth_audience = maybe_from_nullable(self.auth_audience)
        self.finalize = maybe_from_nullable(self.finalize)

    def to_dict(self) -> t.Dict[str, t.Any]:
        res: t.Dict[str, t.Any] = {}
        if self.iss.is_just:
            res["iss"] = to_dict(self.iss.value)
        if self.client_id.is_just:
            res["client_id"] = to_dict(self.client_id.value)
        if self.auth_token_url.is_just:
            res["auth_token_url"] = to_dict(self.auth_token_url.value)
        if self.auth_login_url.is_just:
            res["auth_login_url"] = to_dict(self.auth_login_url.value)
        if self.key_set_url.is_just:
            res["key_set_url"] = to_dict(self.key_set_url.value)
        if self.auth_audience.is_just:
            res["auth_audience"] = to_dict(self.auth_audience.value)
        if self.finalize.is_just:
            res["finalize"] = to_dict(self.finalize.value)
        return res

    @classmethod
    def from_dict(
        cls: t.Type["Patch1P3ProviderLTIData"], d: t.Dict[str, t.Any]
    ) -> "Patch1P3ProviderLTIData":
        parsed = cls.data_parser.try_parse(d)

        res = cls(
            iss=parsed.iss,
            client_id=parsed.client_id,
            auth_token_url=parsed.auth_token_url,
            auth_login_url=parsed.auth_login_url,
            key_set_url=parsed.key_set_url,
            auth_audience=parsed.auth_audience,
            finalize=parsed.finalize,
        )
        res.raw_data = d
        return res
