

class MissingKeyComponent(Exception):
    pass

class Key:
    def __init__(self,
                 pattern,
                 **kwargs):
        self._pattern = pattern
        self._kwargs = kwargs

    def get_str(self):
        return self._pattern.format(**self._kwargs)

    def get_temporal_key(self):
        if 'temporal_key' in self._kwargs:
            return self._kwargs['temporal_key']
        else:
            raise MissingKeyComponent("missing temporal_key in Key")

    def get_spatial_key(self):
        if 'temporal_key' in self._kwargs:
            return self._kwargs['spatial_key']
        else:
            raise MissingKeyComponent("missing spatial_key in Key")



