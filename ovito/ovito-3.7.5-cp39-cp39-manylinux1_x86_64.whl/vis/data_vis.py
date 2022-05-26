from . import DataVis

# Implement the DataVis.__codegen__ method.
def DataVis__codegen__(self, attributes):
    # Hide all property assignements of the DataVis if it is disabled,
    # because they will not matter anyway in this case.
    if self.enabled == False:
        # Remove all keys from the dictionary except the "enabled" key if it exists.
        enabled_value = attributes.get("enabled")
        attributes.clear()
        if enabled_value:
            attributes["enabled"] = enabled_value
    else:
        # Suppress generation of code assigning the title string.
        if 'title' in attributes:
            del attributes['title']

DataVis.__codegen__ = DataVis__codegen__
