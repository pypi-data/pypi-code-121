from typing import Any, cast, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BenchlingAppManifestSecurity")


@attr.s(auto_attribs=True, repr=False)
class BenchlingAppManifestSecurity:
    """  """

    _public_key: Union[Unset, str] = UNSET

    def __repr__(self):
        fields = []
        fields.append("public_key={}".format(repr(self._public_key)))
        return "BenchlingAppManifestSecurity({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        public_key = self._public_key

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if public_key is not UNSET:
            field_dict["public_key"] = public_key

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_public_key() -> Union[Unset, str]:
            public_key = d.pop("public_key")
            return public_key

        public_key = get_public_key() if "public_key" in d else cast(Union[Unset, str], UNSET)

        benchling_app_manifest_security = cls(
            public_key=public_key,
        )

        return benchling_app_manifest_security

    @property
    def public_key(self) -> str:
        """Public key used to encrypt secure_text values. The value is constrained:
        * value must be a public key PEM certificate
        * key type (kty) must be RSA
        * algorithm must be RSAES_OAEP_SHA_256
        * key size must be 2048 bits, with exponent=65537
        * key usage (use) must not be "signing". It can be either unspecified, or "encrypt/decrypt" """
        if isinstance(self._public_key, Unset):
            raise NotPresentError(self, "public_key")
        return self._public_key

    @public_key.setter
    def public_key(self, value: str) -> None:
        self._public_key = value

    @public_key.deleter
    def public_key(self) -> None:
        self._public_key = UNSET
