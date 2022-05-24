from __future__ import annotations
from ImageGenPy.common import *
import random
import os

class Layer:
    def __init__(
        self, 
        name: str, 
        z: float, 
        base_path: str, 
        composed=False,
        composed_trait: Trait=None,
        sub_trait_z_vals: dict={},
        rarity_table: dict={}
    ) -> None:
        self.name: str = name
        self.z: float = z
        self.path = f"{base_path}/{self.name}"
        self.traits: Traits
        self.sub_trait_z_vals = sub_trait_z_vals

        if not composed:
            self.traits = self.__traits__(self.path, rarity_table)
        elif composed_trait:
            self.traits = [composed_trait]
        else: 
            raise Exception("Composed layer must contain at least one trait")

    @staticmethod
    def none() -> Layer:
        return Layer("none", -1, "")

    def __str__(self) -> str:
        msg = f"{self.name}"
        for trait in self.traits:
            msg = msg + trait.__repr__(0)
        return msg

    def __repr__(self) -> str:
        return self.name

    def __traits__(self, path: str, rarity_table: dict) -> Traits:
        #TODO: lookup colour schemes etc???
        traits: Traits = []
        if path == "/none":
            return traits
        for name in os.listdir(path):
            if name == '.DS_Store':
                continue
            if "none" in name:
                traits.append(
                    Trait.none(self, rarity_table.get(name, 100))
                )
            fp = os.path.join(path, name)
            if os.path.isdir(fp):
                sub_traits = self.__traits__(fp, rarity_table)
                traits.append(
                    Trait(
                        name, 
                        fp, 
                        self, 
                        rarity_table.get(name, 100), 
                        [], 
                        sub_traits, 
                        sub_trait_z_vals=self.sub_trait_z_vals
                    )
                )
            else:
                traits.append(
                    Trait(
                        name.split(".")[0], 
                        fp, 
                        self, 
                        rarity_table.get(name.split(".")[0], 100), 
                        [], 
                        [], 
                        sub_trait_z_vals=self.sub_trait_z_vals
                    )
                )
        return traits    
    
    def get_trait(self, trait_name: str) -> Trait:
        if trait_name == 'all':
            return Trait("all", "", self)
        elif ":" in trait_name:
            print("[*] composed")
            trait_name = trait_name.split(":")[0]
        for trait in self.traits:
            if trait.name == trait_name:
                return trait
        error_msg = f"{trait_name} not found in {self.name}"
        raise LookupError(error_msg)


class Trait:
    def __init__(
        self, 
        name: str,
        path: str,
        layer: Layer,
        rarity: int=100, 
        colour_schemes: list[str]=[],
        sub_traits: list[Trait]=[],
        expanded=False,
        sub_trait_z_vals: dict={}
    ) -> None:
        self.name: str = name
        self.rarity: int = rarity
        self.colour_schemes: list[str] = colour_schemes
        self.sub_traits: Traits = sub_traits
        self.exclusions: dict[Layer, Traits] = {}
        # Trait can only be combined with items in inclusions, unless empty
        self.inclusions: dict[Layer, Traits] = {}
        self.path: str = path
        self.sub_trait_z_vals: dict = sub_trait_z_vals
        if not expanded:
            self.layer = layer
        else:
            layer_name = path.split('/')[-2]
            z = self.sub_trait_z_vals.get(layer_name, 0)
            self.layer = Layer(
                layer_name,
                z,
                "/".join(path.split("/")[ :-1]), 
                composed=True,
                composed_trait=self
            )

    def __sub_trait_exclusions__(self) -> None:
        for sub_trait in self.sub_traits:
            for (_, v) in self.exclusions.items():
                sub_trait.add_exclusions(v)
            sub_trait.__sub_trait_exclusions__()


    @staticmethod
    def none(layer: Layer, rarity: int=100) -> Trait:
        return Trait("None", "./", layer)

    def __str__(self) -> str:
        return f"{self.name}: {self.rarity}" 

    def __repr__(self, level=-1) -> str:
        if level == -1:
            return self.name
        branch = "├──"
        trunk = "│\t"
        current_branch = branch
        for _ in range(level):
            current_branch = trunk + current_branch
        msg = f"\n{current_branch}{self.__str__()}"
        for sub_trait in self.sub_traits:
            msg = msg + sub_trait.__repr__(level + 1)
        return msg

    def compose_sub_traits(self) -> Trait:
        if not self.has_sub_traits():
            return self
        elif self.is_leaf_only():
            traits = self.sub_traits
            weights = [trait.rarity for trait in traits]
            try:
                choice = random.choices(traits, weights)[0]
            except ValueError as e:
                print(traits)
                print(weights)
                print(self.name)
                raise e
            return choice
        else:
            selected_sub_traits = []
            for sub_trait in self.sub_traits:
                selected_sub_traits.append(sub_trait.compose_sub_traits())
            composed_trait_paths = ":".join(
                [sub_trait.path for sub_trait in selected_sub_traits]
            )
            composed_trait_name = ":".join(
                [sub_trait.name for sub_trait in selected_sub_traits]
            )
            composed_trait_name = f"{self.name}:[{composed_trait_name}]"
            composed_trait = Trait(
                composed_trait_name, 
                composed_trait_paths, 
                self.layer,
                self.rarity,
                self.colour_schemes,
                sub_trait_z_vals=self.sub_trait_z_vals
            )
            for (_, v) in self.inclusions.items():
                composed_trait.add_inclusions(v)
            for (_, v) in self.exclusions.items():
                composed_trait.add_exclusions(v)
            return composed_trait

    def expand_composed_sub_traits(self) -> Traits:
        if not self.is_composed_trait():
            raise TypeError("Non-composed trait cannot be expanded")
        else:
            split_names = self.name.split(':')
            top_level_name = split_names[0]
            sub_trait_names = ":".join(split_names[1:]).strip('[]').split(':')
            top_level_trait = self.layer.get_trait(
                top_level_name
            )
            sub_trait_paths = self.path.split(':')
            sub_traits = []
            assert len(sub_trait_names) == len(sub_trait_paths)
            for i in range(len(sub_trait_names)):
                name = sub_trait_names[i]
                path = sub_trait_paths[i]
                trait = Trait(
                    name,
                    path,
                    Layer.none(),
                    expanded=True,
                    sub_trait_z_vals=self.sub_trait_z_vals
                )
                sub_traits.append(trait)
            return sub_traits

    def is_composed_trait(self) -> bool:
        return ":" in self.name

    def __set_sub_trait_path(self, sub_trait: Trait) -> None:
        sub_trait.set_path(f"{self.path}/{sub_trait.name}")

    def set_path(self, path: str) -> None:
        self.path = path

    def add_exclusion(self, other_trait: Trait) -> None:
        # print(f"[*] adding exclusion: {other_trait.name} to {self.name}")
        if not self.is_excluded(other_trait) \
           and not self.is_included(other_trait):
            other_layer = other_trait.layer
            self.exclusions[other_layer] = self.exclusions.get(
                other_layer, 
                []
            )
            self.exclusions[other_layer].append(other_trait)
            try:
                other_trait.exclusions[self.layer].append(self)
            except KeyError:
                other_trait.exclusions[self.layer] = [self]
            self.__sub_trait_exclusions__()

    def add_inclusion(self, other_trait: Trait) -> None:
        if not self.is_excluded(other_trait) \
           and not self.is_included(other_trait):
            other_layer = other_trait.layer
            self.inclusions[other_layer] = self.inclusions.get(
                other_layer, 
                []
            )
            self.inclusions[other_layer].append(other_trait)
            try:
                other_trait.inclusions[self.layer].append(self)
            except KeyError:
                other_trait.inclusions[self.layer] = [self]

    def add_exclusions(self, other_traits: Traits) -> None:
        for other_trait in other_traits:
            self.add_exclusion(other_trait)
    
    def add_inclusions(self, other_traits: Traits) -> None:
        for other_trait in other_traits:
            self.add_inclusion(other_trait)

    def add_sub_trait(self, other_trait: Trait) -> None:
        self.sub_traits.append(other_trait)
        other_trait.exclusions = self.exclusions #TODO: copy or reference?
        print(f"[*] {self.exclusions}")
        self.__set_sub_trait_path(other_trait)
    
    def has_sub_traits(self) -> bool:
        return len(self.sub_traits) > 0

    def is_leaf_only(self) -> bool:
        for sub_trait in self.sub_traits:
            if sub_trait.has_sub_traits():
                return False
        return self.has_sub_traits()

    def has_inclusions(self) -> bool:
        return len(self.inclusions) > 0

    def has_exclusions(self) -> bool:
        return len(self.exclusions) > 0

    def is_excluded(self, other_trait: Trait) -> bool:
        return self in other_trait.exclusions.get(self.layer, [])

    def is_included(self, other_trait: Trait) -> bool:
        return self in other_trait.inclusions.get(self.layer, [])

    def is_none(self) -> bool:
        return self == Trait.none(self.layer)

    def exclude_layer(self, layer: Layer) -> None:
        self.exclusions[layer] = [Trait("all", "all", layer)]

    def layer_is_excluded(self, layer: Layer) -> bool:
        return "all" in [
            exclusion.name for exclusion in self.exclusions.get(layer, [])
        ]