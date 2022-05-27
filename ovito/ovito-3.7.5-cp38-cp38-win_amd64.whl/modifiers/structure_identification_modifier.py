from . import StructureIdentificationModifier

# Implement the StructureIdentificationModifier.__codegen__ method.
def StructureIdentificationModifier__codegen__(self, attributes):
    if "structures" in attributes and hasattr(self, "Type"):
        list = attributes["structures"]
        for idx, item in enumerate(list):
            if item[0] == '[':
                parts = item.partition(']')
                scalar_val = int(parts[0][1:])
                enum_val = self.Type(scalar_val)
                list[idx] = f"[{type(self).__name__}.{enum_val}]{parts[2]}"
StructureIdentificationModifier.__codegen__ = StructureIdentificationModifier__codegen__