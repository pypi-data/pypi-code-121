from __future__ import annotations
from typing import Union
from typing_extensions import TypeAlias
from ImageGenPy.layer import Layer, Trait
from ImageGenPy.blueprint import Blueprint
from ImageGenPy.blueprint_builder import BlueprintBuilder
import random

Traits: TypeAlias = list[Trait]
Layers: TypeAlias = list[Layer]
# Attribute needs a better type alias, 
# or it should just be a class that inherits dict
Attribute: TypeAlias = dict[str, Union[Layer, Trait]]
Attributes: TypeAlias = list[Attribute]

