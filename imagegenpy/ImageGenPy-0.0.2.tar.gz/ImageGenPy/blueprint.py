from __future__ import annotations
from ImageGenPy.common import *
from pprint import pprint 
import re


class Blueprint(dict):
    def print(self):
        pprint(self)

    def fingerprint(self) -> str:
        try:
            for attr in self['attributes']:
                print(attr)
            return "".join(
                sorted(
                    [
                        attr['value'].name for attr in self['attributes'] 
                        if attr['trait_type'].name != 'BG'
                    ]
                )
            )
        except KeyError:
            return ""

    def to_dict(self) -> dict:
        d = self.copy()
        d['attributes'] = []
        for attribute in self['attributes']:
            d['attributes'].append(
                {
                    'trait_type': attribute['trait_type'].name,
                    'value': attribute['value'].name
                }
            )
        return d

    def expand_subtraits(self) -> Blueprint:
        d = self.copy()
        d['attributes'] = []
        for attribute in self['attributes']:
            if attribute['value'].is_composed_trait():
                for trait in attribute['value'].expand_composed_sub_traits():
                    d['attributes'].append(
                        {"trait_type": trait.layer, "value": trait}
                    )
            else:
                d['attributes'].append(attribute)
        return Blueprint(d)

    def get_attribute(self, layer_name: str) -> Attribute:
        for attribute in self['attributes']:
            if attribute['trait_type'].name == layer_name:
                return attribute
        raise Exception("attribute not found")

    def get_attribute_colour(self, layer_name: str) -> Union[str, None]:
        #TODO: use regex
        attr = self.get_attribute(layer_name)
        name: str = attr['value'].name
        search_str: str = 'color(' if 'color(' in name.lower() else 'skin('
        i = name.lower().find(search_str) + len(search_str) 
        if i < 0:
            return None
        return name[i].upper()

    def change_attribute_colour(self, layer_name: str, new_colour: str) -> None:
        #TODO: handle is_composed()
        #TODO: use regex for all 
        print(f"new_colour: {new_colour}")
        attr = self.get_attribute(layer_name)
        # print(f"attr: {attr['value'].name}")
        try:
            if self.get_attribute_colour(layer_name) == new_colour:
                # print("same same")
                return
        except IndexError:
            pass
        else:
            old_name: str = attr['value'].name
            search_str: str 
            if 'color(' in old_name.lower():
                search_str = 'color('
            elif 'color-(' in old_name.lower():
                search_str = 'color-('
            elif 'skin(' in old_name.lower():
                search_str = 'skin('
            elif 'skin-(' in old_name.lower():
                search_str = 'skin-('
            elif new_colour.isnumeric():
                if len(new_colour) < 2:
                    new_colour = '0' + new_colour
                new_name = re.sub(r"\d+", new_colour, old_name)
            else:
                # print("[*] FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF-")
                return
            if not new_colour.isnumeric():
                i = old_name.lower().find(search_str) + len(search_str) 
                # print(old_name[i])
                new_name = old_name[ :i] + new_colour + old_name[i+1: ]
            # print(f"new_name: {new_name}")
            layer: Layer = \
                attr['trait_type'] \
                    if isinstance(attr['trait_type'], Layer) \
                    else Layer.none()
            if layer == Layer.none():
                return
            attr['value'] = layer.get_trait(new_name) 
