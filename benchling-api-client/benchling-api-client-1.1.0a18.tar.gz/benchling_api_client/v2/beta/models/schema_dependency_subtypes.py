from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SchemaDependencySubtypes(Enums.KnownString):
    AA_SEQUENCE = "aa_sequence"
    DNA_SEQUENCE = "dna_sequence"
    CUSTOM_ENTITY = "custom_entity"
    MIXTURE = "mixture"
    DNA_OLIGO = "dna_oligo"
    RNA_OLIGO = "rna_oligo"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SchemaDependencySubtypes":
        if not isinstance(val, str):
            raise ValueError(f"Value of SchemaDependencySubtypes must be a string (encountered: {val})")
        newcls = Enum("SchemaDependencySubtypes", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SchemaDependencySubtypes, getattr(newcls, "_UNKNOWN"))
