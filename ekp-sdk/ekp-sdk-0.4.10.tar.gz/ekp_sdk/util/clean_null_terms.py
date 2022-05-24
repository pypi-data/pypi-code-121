# https://betterprogramming.pub/how-to-remove-null-none-values-from-a-dictionary-in-python-1bedf1aab5e4
def clean_null_terms(d):
    clean = {}
    for k, v in d.items():
        if isinstance(v, dict):
            nested = clean_null_terms(v)
            if len(nested.keys()) > 0:
                clean[k] = nested
        elif v is not None:
            clean[k] = v
    return clean