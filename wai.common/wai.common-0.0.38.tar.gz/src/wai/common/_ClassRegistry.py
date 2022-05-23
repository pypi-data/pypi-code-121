from typing import Dict, Set, Type, Optional, Iterator

from .meta import fully_qualified_name
from .meta.code_repr import (
    CodeRepresentable,
    CodeRepresentation,
    code_repr,
    get_import_dict,
    get_code,
    combine_import_dicts
)


class ClassRegistry(CodeRepresentable):
    """
    A registry of classes that can be looked up by name.

    # TODO: Alias conflicts with name/qualname
    """
    def __init__(self, *classes: Type):
        self._name_lookup: Dict[str, Set[str]] = {}
        self._qualname_lookup: Dict[str, Type] = {}
        self._aliases: Dict[str, str] = {}
        self._alias_reverse_lookup: Dict[str, str] = {}

        # Register any initial classes
        for cls in classes:
            self.register(cls)

    def register(self, cls: Type):
        """
        Registers a class with the registry.

        :param cls:     The class to register.
        :return:        The fully-qualified name of the class.
        """
        # Get the short and qualified names of the class
        name: str = cls.__name__
        qualname: str = fully_qualified_name(cls)

        # Abort if already registered
        if qualname in self._qualname_lookup:
            return qualname

        # Initialise the short-name list of necessary
        if name not in self._name_lookup:
            self._name_lookup[name] = set()

        # Add the qualified name to the lookup
        self._name_lookup[name].add(qualname)

        # Add the type to the qualified lookup
        self._qualname_lookup[qualname] = cls

        return qualname

    def is_registered(self, cls: Type) -> bool:
        """
        Checks if the given class is registered.

        :param cls:     The class to check.
        :return:        True if the class is registered,
                        False if not.
        """
        return fully_qualified_name(cls) in self._qualname_lookup

    def registered_classes(self) -> Iterator[Type]:
        """
        Gets an iterator over all registered classes.
        """
        return (value for value in self._qualname_lookup.values())

    def alias(self, cls: Type, alias: str) -> 'ClassRegistry':
        """
        Creates an alias for a class. Automatically registers
        the class if it's not already. Chainable.

        :param cls:         The class to alias.
        :param alias:       The alias to use.
        :raises NameError:  If the alias is already in use, or is empty.
        """
        # Make sure the alias isn't the empty string
        if alias == "":
            raise NameError("Aliases can't be empty")

        # Make sure the alias isn't already in use
        if alias in self._aliases:
            raise NameError(f"Alias '{alias}' already in use")

        # Make sure the class is registered
        qualname = self.register(cls)

        # Save the alias
        self._aliases[alias] = qualname
        self._alias_reverse_lookup[qualname] = alias

        # Return self so as to be chainable
        return self

    def resolve(self, name: str) -> Optional[str]:
        """
        Attempts to resolve names to their fully-qualified equivalent.

        :param name:        The name to resolve (qualified/short/alias).
        :return:            The fully-qualified name, or None if not found.
        :raises NameError:  If the name is an ambiguous short-name.
        """
        # If the name is an alias, dereference it
        if name in self._aliases:
            return self._aliases[name]

        # If the name is qualified, return the class
        if name in self._qualname_lookup:
            return name

        # If the name is a short name, try to resolve it
        if name in self._name_lookup:
            # Get the potential qualified names
            qualnames = self._name_lookup[name]

            # If there's more than one, it's ambiguous
            if len(qualnames) > 1:
                raise NameError(f"Class name '{name}' is ambiguous: {', '.join(qualnames)}")

            for qualname in qualnames:  # Dummy loop to get first (only) item from set
                return qualname

        return None

    def find(self, name: str, *,
             attempt_class_import: bool = False) -> Optional[Type]:
        """
        Tries to find the registered class with the given name.

        :param name:                    The name to find (short or qualified).
        :param attempt_class_import:    Whether to attempt to import the class
                                        if it's not registered.
        :return:                        The class with the given name, or None
                                        if not found.
        :raises NameError:              If the name is an ambiguous short-name.
        """
        # Resolve the name to its fully-qualified counterpart
        qualname = self.resolve(name)

        # If resolution succeeded, return the named class
        if qualname is not None:
            return self._qualname_lookup[qualname]

        # Attempt to import the class if selected
        if attempt_class_import:
            return self.attempt_class_import(name)

        # Class not found
        return None

    def aliases(self) -> Iterator[str]:
        """
        Gets an iterator over the aliases registered with the registry.

        :return:    The iterator of aliases.
        """
        return (str(name) for name in self._aliases.keys())

    def has_alias(self, alias: str) -> bool:
        """
        Whether the registry has an alias with the given name.

        :param alias:   The alias to check for.
        :return:        True if the alias exists, False if not.
        """
        return alias in self._aliases

    def get_alias(self, cls: Type) -> Optional[str]:
        """
        Gets the alias for a class.

        :param cls:     The class to get the alias for.
        :return:        The alias, or None if the class is not aliased.
        """
        # Get the class' fully-qualified name
        qualname = fully_qualified_name(cls)

        return self._alias_reverse_lookup.get(qualname, None)

    def attempt_class_import(self, name: str) -> Optional[Type]:
        """
        Attempts to import the class by name.

        :param name:    The fully-qualified name of the class.
        :return:        The class, or None if it could not
                        be imported.
        """
        # TODO: Implementation
        raise NotImplementedError(ClassRegistry.attempt_class_import.__qualname__)

    def code_repr(self) -> CodeRepresentation:
        # Get the code-representations of all the types that are in the registry
        aliased_types = {}
        unaliased_types = []
        for cls in self._qualname_lookup.values():
            alias = self.get_alias(cls)
            if alias is not None:
                aliased_types[get_code(code_repr(alias))] = code_repr(cls)
            else:
                unaliased_types.append(code_repr(cls))

        # Combine the import dictionaries of the ClassRegistry class and all registered classes
        import_dict = combine_import_dicts(get_import_dict(code_repr(type(self))),
                                           *map(get_import_dict, unaliased_types),
                                           *map(get_import_dict, aliased_types.values()))

        # Create the code representation for just unaliased types (using constructor)
        code = f"ClassRegistry({', '.join(map(get_code, unaliased_types))})"

        # Add the chained calls to 'alias' to add the aliased types
        for alias, code_representation in aliased_types.items():
            code += f".alias({get_code(code_representation)}, {alias})"

        return import_dict, code
