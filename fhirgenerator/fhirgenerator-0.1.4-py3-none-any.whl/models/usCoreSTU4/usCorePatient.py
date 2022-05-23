# -*- coding: utf-8 -*-
"""
Profile: http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
Release: STU4
Version: 4.0.0
"""

import typing

from pydantic import validator, Field

from fhir.resources.patient import Patient
from fhir.resources import fhirtypes


class USCorePatient(Patient):
    '''Defines constraints and extensions on the patient resource for the minimal set of data to query and retrieve patient demographic information.'''

    gender: fhirtypes.Code = Field(
        ...,
        alias="gender",
        title="male | female | other | unknown",
        description=(
            "Administrative Gender - the gender that the patient is considered to "
            "have for administration and record keeping purposes."
        ),
        # if property is element of this resource.
        element_property=True,
        # note: Enum values can be used in validation,
        # but use in your own responsibilities, read official FHIR documentation.
        enum_values=["male", "female", "other", "unknown"],
    )

    identifier: typing.List[fhirtypes.IdentifierType] = Field(
        ...,
        alias="identifier",
        title="An identifier for this patient",
        description=None,
        # if property is element of this resource.
        element_property=True,
    )

    name: typing.List[fhirtypes.HumanNameType] = Field(
        ...,
        alias="name",
        title="A name associated with the patient",
        description="A name associated with the individual.",
        # if property is element of this resource.
        element_property=True,
    )

    @validator('identifier')
    def check_identifier(cls, identifiers):
        '''Identifier 1..*, Identifier.system 1..1, Identifier.value 1..1'''
        for identifier in identifiers:
            if identifier.system is None and identifier.value is None:
                raise ValueError('system and value are required')
            elif identifier.system is None:
                raise ValueError('system is required')
            elif identifier.value is None:
                raise ValueError('value is required')
        return identifiers

    @validator('telecom')
    def check_telecom(cls, telecoms):
        '''telecom 0..*, telecom.system 1..1, telecom.value 1..1'''
        for telecom in telecoms:
            if telecom.system is None and telecom.value is None:
                raise ValueError('system and value are required')
            elif telecom.system is None:
                raise ValueError('system is required')
            elif telecom.value is None:
                raise ValueError('value is required')
        return telecoms
