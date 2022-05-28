from cvee.utils.misc import is_list_of


def build_from_cfg(cfg, registry):
    """Build a instance from config dict.

    Args:
        cfg (dict): Config dict. It should contain the key `type`.
        registry (Registry): The registry containing the `type`.

    Return:
        obj: The constructed object.
    """
    if not isinstance(cfg, dict):
        raise TypeError(f"cfg should be dict, but got {type(cfg)}")
    if "type" not in cfg:
        raise KeyError(f"cfg should contain the key `type`, but got {cfg}")
    if not isinstance(registry, Registry):
        raise TypeError(f"registry should be Registry, but got {type(registry)}")

    args = cfg.copy()
    obj_type = args.pop("type")
    if isinstance(obj_type, str):
        obj_cls = registry.get(obj_type)
        if obj_cls is None:
            raise KeyError(f"Key {obj_type} is not in registry {registry.name}")
    else:
        raise TypeError(f"obj_type should be str, but got {type(obj_type)}")

    try:
        return obj_cls(**args)
    except Exception as e:
        raise type(e)(f"{obj_cls.__name__}: {e}")


class Registry:
    """The registry maps string to object.

    Example:
        >>> MODELS = Registry('models')
        >>> @MODELS.register()
        >>> class ResNet:
        >>>     pass
        >>> res_net = MODELS.get('ResNet')
        >>> model = MODELS.build({'type': 'ResNet'})

    Args:
        name (str): Registry name.
        build_func (func, optional): A function to build an instance
            from the registry based on a single dict argument.

    """

    # pylint: disable=R1710

    def __init__(self, name, build_func=None):
        self._name = name
        self._obj_map = {}

        if build_func is None:
            self.build_func = build_from_cfg
        else:
            self.build_func = build_func

    def _do_register(self, names, obj, force=False):
        if isinstance(names, str):
            names = [names]
        if not is_list_of(names, str):
            raise TypeError("Names should be a list of str")
        for name in names:
            if not force and name in self._obj_map:
                raise KeyError(f"{name} is registered in registry {self._name}")
            self._obj_map[name] = obj

    def register(self, obj=None, name=None, force=False):
        """Register an object.

        A object will be registered with its `obj.__name__` or a custom name.
        It can be called as a decorator or a function.

        Example:
            >>> @MODELS.register()
            >>> class ResNet:
            >>>     pass
            >>> # or call it as a function and use a custom name.
            >>> MODELS.register(ResNet, name='res_net')

        Args:
            obj (obj, optional): Obejct to be registered. Keep it as None
                when used as a decorator.
            name (str or list[str], optional): Some names mapped to the object.
                If not specifed, the `obj.__name__` will be used.
            force (bool, optional): Whether to override an existing mapping
                with the same name. Default: False.
        """
        if obj is None:
            # as a decorator
            def deco(func_or_class):
                obj_name = func_or_class.__name__ if name is None else name
                self._do_register(obj_name, func_or_class, force)
                return func_or_class

            return deco

        # as a function
        obj_name = obj.__name__ if name is None else name
        self._do_register(obj_name, obj, force)

    def get(self, name):
        """Return an object if it's registered, else None."""
        ret = self._obj_map.get(name)
        return ret

    def build(self, *args, **kwargs):
        """Build an object from the registry based on args."""
        return self.build_func(*args, **kwargs, registry=self)

    @property
    def name(self):
        """Get registry name"""
        return self._name

    def __len__(self):
        return len(self._obj_map)

    def __getitem__(self, name):
        ret = self._obj_map.get(name)
        if ret is None:
            raise KeyError(f"Key {name} is not in registry {self._name}")
        return ret

    def __setitem__(self, name, obj):
        self._do_register(name, obj)

    def __contains__(self, name):
        return name in self._obj_map

    def __repr__(self):
        fmt_str = f"Registry: {self._name} Items: {self._obj_map.items()}"
        return fmt_str
