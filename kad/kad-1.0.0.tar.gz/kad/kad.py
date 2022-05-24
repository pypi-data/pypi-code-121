def to_kad(dictionary):
    kad = Kad()
    for key in dictionary.keys():
        setattr(kad, key, dictionary[key])
    return kad

class Kad:
    def __init__(self):
        return;
