''' mi_models.py
A module to that makes calles to the Infor ION API simple. This module
contains dataclasses that represents data objects from the Api.

Author: Kim Timothy Engh
Email: kim.timothy.engh@epiroc.com
Licence: GPLv3 '''

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class Base:
    def __iter__(self):
        return iter(asdict(self).items())


@dataclass
class Endpoint(Base):
    name: str
    host: str
    port: int
    usr: str
    pwd: str = field(default='')

    def __repr__(s):
        return f'Endpoint(name={s.name}, host={s.host}, port={s.port}, usr={s.usr}, pwd={"*" * len(s.pwd)})'


@dataclass
class MiRecords(Base):
    program: str
    transaction: str
    metadata: List[Dict] = field(repr=False)
    records: List[Dict] = field(repr=False)


@dataclass
class MiPrograms(Base):
    records: List[str]


@dataclass
class MiFieldMetadata(Base):
    name: str
    description: str
    fieldtype: str
    length: int
    mandatory: str


@dataclass
class MiTransactionMetadata(Base):
    program: str
    transaction: str
    description: str
    multi: str
    inputs: List[MiFieldMetadata] = field(repr=False)
    outputs: List[MiFieldMetadata] = field(repr=False)


@dataclass
class MiProgramMetadata(Base):
    program: str
    description: str
    version: str
    transactions: List[Optional[MiTransactionMetadata]] = field(repr=False)


@dataclass
class MiError:
    code: str
    description: str
