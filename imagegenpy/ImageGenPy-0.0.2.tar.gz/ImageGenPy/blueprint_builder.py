from __future__ import annotations
from ImageGenPy.common import *
from ImageGenPy.blueprint import Blueprint
from pprint import pprint
import random

class BlueprintBuilder:
    class InclusionException(Exception):
        pass

    def __init__(
        self, 
        layers: list[str], 
        base_path: str, 
        base_schema: dict={},
        exclusion_table: dict={},
        inclusion_table: dict={},
        sub_traits_z_vals: dict={},
        rarity_table: dict={}
    ) -> None:
        self.base_path = base_path
        self.layers = self.__layers__(layers, base_path, sub_traits_z_vals, rarity_table)
        self.schema = self.__schema__(base_schema)
        self.exclusion_table = exclusion_table
        self.inclusion_table = inclusion_table
        self.rarity_table = rarity_table
        self.__inclusions__()
        self.__exclusions__()

    def __layers__(
        self, 
        layers: list[str], 
        base_path: str, 
        sub_traits_z_vals: dict,
        rarity_table: dict
    ) -> list[Layer]:
        return [
            Layer(
                layers[i], 
                float(i), 
                base_path, 
                sub_trait_z_vals=sub_traits_z_vals,
                rarity_table=rarity_table
            ) for i in range(len(layers))
        ]

    def __schema__(self, base_schema) -> dict:
        schema = base_schema
        attrs = []
        for layer in self.layers:
            attrs.append({"trait_type": layer.name, "value": "none"})
        schema['attributes'] = attrs
        return schema

    def __inclusions__(self):
        #TODO:
        pass

    def __exclusions__(self):
        for (k, v) in self.exclusion_table.items():
            layer = self.get_layer(k)
            for trait_name in v.keys():
                print(trait_name)
                trait = layer.get_trait(trait_name)
                for layer_name in v[trait_name].keys():
                    excluded_layer = self.get_layer(layer_name)
                    excluded_traits = [
                        excluded_layer.get_trait(x) 
                        for x in v[trait_name][layer_name]
                    ]
                    print(excluded_layer, excluded_traits)
                    for layer_excluded_trait in excluded_traits:
                        trait.add_exclusion(layer_excluded_trait)

    def get_layer(self, layer_name: str) -> Layer:
        for layer in self.layers:
            if layer.name == layer_name:
                return layer
        return Layer.none()

    def print_layers(self) -> None:
        for layer in self.layers:
            print(layer)

    def print_schema(self) -> None:
        pprint(self.schema)

    def build_blueprint(self, id: int) -> Blueprint:
        blueprint = self.schema.copy()
        blueprint['name'] += str(id)
        blueprint['tokenID'] = id
        blueprint['image'] += f"{id}.png"
        blueprint['attributes'] = self.choose_attributes()
        return Blueprint(blueprint)

    def choose_attributes(self) -> Attributes:
        attributes: Attributes = []
        for layer in self.layers:
            attribute: Attribute = {
                'trait_type': layer, 
                'value': self.choose_trait(
                    layer, 
                    attributes
                )
            }
            attributes.append(attribute)
        return attributes

    def choose_trait(
        self, 
        layer: Layer, 
        selected_attributes: Attributes
    ) -> Trait:
        selected_traits: Traits = [
            x['value'] for x in selected_attributes 
            if isinstance(x['value'], Trait)
        ]
        traits = self.handle_inclusions(layer, selected_traits)
        weights = [trait.rarity for trait in traits]
        if len(traits) == 0:
            return Trait.none(layer)
        choice: Trait = random.choices(traits, weights=weights)[0]
        excluded = True
        while excluded:
            for attr in selected_attributes: 
                trait: Trait = attr['value'] if isinstance(
                    attr['value'], Trait) else Trait.none(Layer.none()
                )
                #TODO: check this doesn't mess with rarity too much 
                if trait.layer_is_excluded(layer):
                    return Trait.none(layer)
                if choice.is_excluded(trait) or choice.layer_is_excluded(layer):
                    new_choice = self.resolve_conflict(choice, trait)
                    if choice == new_choice:
                        attr['value'] = Trait.none(trait.layer)
                    break
            excluded = False
        return choice.compose_sub_traits()

    def resolve_conflict(self, trait: Trait, other_trait: Trait) -> Trait:
        print(f"[*] Conflict between {trait.name} and {other_trait.name}")
        if trait.rarity < other_trait.rarity:
            ret = trait
        elif other_trait.rarity < trait.rarity:
            ret = Trait.none(trait.layer)
        else:
            ret = random.choices([trait, Trait.none(trait.layer)])[0]
        print(f"Selected {ret.name}")
        return ret
        
    def handle_inclusions(
        self, 
        layer: Layer, 
        selected_traits: Traits
    ) -> Traits:
        inclusions: Traits = []
        included = False
        for trait in selected_traits:
            if layer in trait.inclusions.keys():
                included = True
                if len(inclusions) > 0:
                    inclusions = [
                        trait for trait in inclusions 
                        if trait in trait.inclusions[layer]
                    ]
                else:
                    # I'm so paranoid about fucking deep copies lol
                    inclusions = [trait for trait in trait.inclusions[layer]]

        if included and len(inclusions) == 0: 
            raise self.InclusionException(
                f"""
                Inclusion Error: 
                    Layer: {layer.name}
                    Selected traits: {[trait.name for trait in selected_traits]}
                """
            )
        return inclusions if included else layer.traits
