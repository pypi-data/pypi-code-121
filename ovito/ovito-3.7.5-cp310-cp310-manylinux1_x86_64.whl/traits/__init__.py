import traits.api

__all__ = ['OvitoObjectTrait', 'ColorTrait']

# A parameter traits that has an instance of a OvitoObject-derived class as value.
class OvitoObjectTrait(traits.api.Instance):
    """A trait type whose value is an instance of a class from the OVITO package."""
    def __init__(self, klass, **params):
        """
        :param klass: The object class type to instantiate.
        :param params: All other keyword parameters are forwarded to the constructor of the object class.
        """
        params['_load_user_defaults_in_gui'] = True # Use user defaults to initialize object parameters when running in the GUI environment.
        super().__init__(klass, kw=params)

# A parameter trait whose value is a RGB tuple with values from 0 to 1.
# The default value is (1.0, 1.0, 1.0).
class ColorTrait(traits.api.BaseTuple):
    """A trait type whose value is a tuple with three floats that represent the RGB values of a color."""
    def __init__(self, default=(1.0, 1.0, 1.0), **metadata):
        """
        :param default: The initial color value to be assigned to the parameter trait.
        """
        super().__init__(default, **metadata)
