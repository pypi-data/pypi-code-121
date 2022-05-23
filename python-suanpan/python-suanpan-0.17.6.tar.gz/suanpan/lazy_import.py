import sys
import types
import importlib.util
import importlib.abc


class _LazyModule(types.ModuleType):
    """A subclass of the module type which triggers loading upon attribute access."""

    def __getattribute__(self, attr):
        if attr in ('__name__',):
            return super(_LazyModule, self).__getattribute__(attr)

        print("reload lazy_imported '{}' with attr '{}'".format(self.__name__, attr))
        """Trigger the load of the module and return the attribute."""
        # All module metadata must be garnered from __spec__ in order to avoid
        # using mutated values.
        # Stop triggering this method.
        self.__class__ = types.ModuleType
        # Get the original name to make sure no object substitution occurred
        # in sys.modules.
        original_name = self.__spec__.name
        # Figure out exactly what attributes were mutated between the creation
        # of the module and now.
        attrs_then = self.__spec__.loader_state['__dict__']
        original_type = self.__spec__.loader_state['__class__']
        attrs_now = self.__dict__
        attrs_updated = {}
        for key, value in attrs_now.items():
            # Code that set the attribute may have kept a reference to the
            # assigned object, making identity more important than equality.
            if key not in attrs_then:
                attrs_updated[key] = value
            elif id(attrs_now[key]) != id(attrs_then[key]):
                attrs_updated[key] = value
        self.__spec__.loader.exec_module(self)
        # If exec_module() was used directly there is no guarantee the module
        # object was put into sys.modules.
        if original_name in sys.modules:
            if id(self) != id(sys.modules[original_name]):
                raise ValueError(f"module object for {original_name!r} "
                                 "substituted in sys.modules during a lazy "
                                 "load")
        # Update after loading since that's what would happen in an eager
        # loading situation.
        self.__dict__.update(attrs_updated)
        return getattr(self, attr)

    def __delattr__(self, attr):
        """Trigger the load and then perform the deletion."""
        # To trigger the load and raise an exception if the attribute
        # doesn't exist.
        self.__getattribute__(attr)
        delattr(self, attr)

    def __repr__(self):
        return "<module '{}' from 'lazy_import'>".format(self.__name__)


class LazyLoader(importlib.abc.Loader):
    """A loader that creates a module which defers loading until attribute access."""

    @staticmethod
    def __check_eager_loader(loader):
        if not hasattr(loader, 'exec_module'):
            raise TypeError('loader must define exec_module()')

    @classmethod
    def factory(cls, loader):
        """Construct a callable which returns the eager loader made lazy."""
        cls.__check_eager_loader(loader)
        return lambda *args, **kwargs: cls(loader(*args, **kwargs))

    def __init__(self, loader):
        self.__check_eager_loader(loader)
        self.loader = loader

    def create_module(self, spec):
        return self.loader.create_module(spec)

    def exec_module(self, module):
        """Make the module load lazily."""
        module.__spec__.loader = self.loader
        module.__loader__ = self.loader
        # Don't need to worry about deep-copying as trying to set an attribute
        # on an object would have triggered the load,
        # e.g. ``module.__spec__.loader = None`` would trigger a load from
        # trying to access module.__spec__.
        loader_state = {'__dict__': module.__dict__.copy(), '__class__': module.__class__}
        module.__spec__.loader_state = loader_state
        module.__class__ = _LazyModule


def lazy_import(name):
    try:
        return sys.modules[name]
    except KeyError:
        spec = importlib.util.find_spec(name)
        loader = LazyLoader(spec.loader)
        spec.loader = loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        loader.exec_module(module)
        return module
