
def merge_spec_dict(spec, base_spec):
    for key, value in base_spec.items():
        if key not in spec.keys():
            spec[key] = value
        else:
            value_spec = spec.get(key)
            if type(value) != type(value_spec):
                continue
            elif isinstance(value, list):
                to_append = []
                for el in value:
                    if not argument_in_list(el, value_spec):
                        to_append.append(el)
                for el in to_append:
                    value_spec.append(el)
            else:
                merge_spec_dict(value_spec, value)


def argument_in_list(value, list_values):
    for el in list_values:
        if el.get('name', None) == value['name']:
            return True
    return False
