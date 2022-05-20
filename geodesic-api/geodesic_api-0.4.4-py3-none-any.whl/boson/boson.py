from geodesic.bases import APIObject
from geodesic.descriptors import StringDescr, BoolDescr, ListDescr, DictDescr, IntDescr, BaseDescr


class BosonConfig(APIObject):
    """BosonConfig Provider Configuration

    This tells Boson how it should access the underlying data.
    """
    provider_name = StringDescr(doc="the name of the provider this Boson uses")
    url = StringDescr(doc="the url of the service this refers to (if any)")
    thread_safe = BoolDescr(doc="is this particular provider implementation thread safe")
    pass_headers = ListDescr(doc="list of headers that this provider should pass to backend")
    max_page_size = IntDescr(doc="the max number of records this provider can page through")
    properties = DictDescr(doc="additional provider-specific properties")
    credential = StringDescr(doc="credential needed to access this dataset")


class BosonDescr(BaseDescr):
    """A Boson Provider Config

    __get__ returns a BosonConfig object
    __set__ sets from a dictionary or BosonConfig, coercing to a BosonConfig if needed
        and stores internally to the APIObject dict
    """
    def _get(self, obj: object, objtype=None) -> dict:
        # Try to get the private attribute by name (e.g. '_boson_config')
        b = getattr(obj, self.private_name, None)
        if b is not None:
            # Return it if it exists
            return b

        try:
            b = self._get_object(obj)
            if isinstance(b, dict):
                b = BosonConfig(**b)
            setattr(obj, self.private_name, b)
        except KeyError:
            if self.default is None:
                self._attribute_error(objtype)
            return self.default
        return b

    def _set(self, obj: object, value: object) -> None:
        # Reset the private attribute (e.g. "_boson_config") to None
        setattr(obj, self.private_name, None)

        if isinstance(value, (BosonConfig, dict)):
            self._set_object(obj, BosonConfig(**value))
        else:
            raise ValueError(f"invalid value type {type(value)}")

    def _validate(self, obj: object, value: object) -> None:
        if not isinstance(value, (BosonConfig, dict)):
            raise ValueError(f"'{self.public_name}' must be a BosonConfig or a dict")

        try:
            BosonConfig(**value)
        except Exception as e:
            raise ValueError("boson config is invalid") from e
