from __future__ import annotations
from ImageGenPy.common import *
from ImageGenPy.blueprint_builder import BlueprintBuilder
import random
from PIL import Image

class ImageBuilder:
    def __init__(
        self, 
        base_output_path: str, 
        base_input_path: str,
        layers: list[str], 
        base_schema: dict,
        exclusion_table: dict={},
        inclusion_table: dict={},
        sub_traits_z_vals: dict={},
        rarity_table: dict={}
    ) -> None:
        self.base_output_path = base_output_path
        self.blueprint_builder = BlueprintBuilder(
            layers, 
            base_input_path, 
            base_schema,
            exclusion_table=exclusion_table,
            inclusion_table=inclusion_table,
            sub_traits_z_vals=sub_traits_z_vals,
            rarity_table=rarity_table
        )
    
    def build_image(
        self, 
        id: int=-1, 
        bp: Blueprint=Blueprint({})
    ) -> None:
        if bp == Blueprint({}) and id >= 0:
            bp = self.blueprint_builder.build_blueprint(id)
        elif id < 0 and bp != None:
            id = bp['tokenID']
        else:
            # For testing
            id = random.randint(1, 10_000)
            bp = self.blueprint_builder.build_blueprint(id)
        attributes = sorted(
            bp.expand_subtraits()['attributes'], 
            key=lambda x: x['trait_type'].z
        )
        layers = []
        for attribute in attributes:
            layer = attribute['trait_type']
            v = attribute['value']
            if v.name.lower() == "none":
                continue
            else:
                # print(layer.name)
                layers.append(Image.open(v.path))
        if layers == []:
            return
        else:
            composite = Image.new("RGBA", layers[0].size)
            for layer in layers:
                composite = Image.alpha_composite(composite, layer)
            print(f"Saving image: {self.base_output_path}/img/{id}.png")
            composite.save(f"{self.base_output_path}/img/{id}.png")

    def find_layer(
        self, 
        attributes: Attributes, 
        layer: Layer
    ) -> Attribute:
        for attribute in attributes:
            if attribute['trait_type'].name == layer.name:
                return attribute 
        return {}





