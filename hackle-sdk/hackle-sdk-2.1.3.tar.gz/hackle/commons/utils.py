from hackle.commons import validator


def filter_properties(properties):
    return dict((k ,v) for k,v in properties.items() if validator.is_property_valid(k, v))
