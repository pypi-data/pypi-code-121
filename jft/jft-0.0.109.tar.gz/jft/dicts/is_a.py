from jft.dict.is_a import f as is_dict
f = lambda x: all([is_dict(i) for i in x]) if isinstance(x, list) else False
t = lambda: all([not f(0), f([]), not f(['ab','cd']), f([{'a':0},{'b':1}])])