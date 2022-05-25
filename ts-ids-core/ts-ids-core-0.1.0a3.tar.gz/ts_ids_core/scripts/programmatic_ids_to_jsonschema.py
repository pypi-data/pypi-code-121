import inspect
import json
import pathlib
from importlib import import_module
from textwrap import dedent
from types import ModuleType
from typing import List, Optional, Type

import click

from ts_ids_core.annotations import DictStrAny
from ts_ids_core.base.ids_element import IdsElement
from ts_ids_core.schema import IdsSchema


@click.command(help="Export an 'IdsElement' class to JSON Schema.")
@click.option(
    "--ids-location",
    "-i",
    type=str,
    help=dedent(
        """
        The 'location' of the IDS class to export to JSON Schema. This may be...
        
        1. ...an import-able module, e.g. 'my_ids_package.my_subpackage', in which case 
        the `IdsSchema` subclass in the module is exported. If no `IdsSchema` subclass
        is found export the module's `IdsElement` if there's exactly one in the module.
        
        2. ...an import-able module and `IdsElement` subclass, e.g.
        'my_ids_package.my_subpackage.MyIds'.
        
        WARNING: The specified Python module will be imported, so it should have no
        consequential side effects. 
        """
    ),
)
@click.option(
    "--out",
    "-o",
    default=None,
    help=dedent(
        """
        The path to write the JSON Schema file to. This must be the name of a file, 
        not a directory.
        """
    ),
    show_default=True,
    type=click.Path(
        file_okay=True, dir_okay=False, writable=True, path_type=pathlib.Path
    ),
)
def write_jsonschema_ids(
    ids_location: str, out: pathlib.Path
) -> None:  # pragma: no cover
    """
    See documentation by running
    ``python -m ts_ids_core.scripts.programmatic_ids_to_jsonschema --help``.
    """
    schema = convert_programmatic_ids_to_jsonschema(ids_location)

    if out is None:
        print(json.dumps(schema, indent=2))  # noqa: T001
        return
    if out.suffix != ".json":
        raise click.UsageError(
            f"The 'out' argument should be a JSON file, but got a file with "
            f"extension '{out.suffix}'."
        )
    # Create the parent directory if it's missing.
    out.parent.mkdir(exist_ok=True, parents=True)
    with out.open("w") as fp:
        json.dump(schema, fp, indent=2)


def get_module_classes(
    module: ModuleType, *, name: Optional[str] = None, base_class: Optional[Type] = None
) -> List[Type]:
    """
    Return the classes defined in a Python module.

    :param module:
        The module to return the classes of.
    :param name:
        If ``name`` is not ``None``, return only classes with this name.
    :param base_class:
        If ``base_class`` is not ``None``, return only classes derived from ``base_class``.
    :return:
        The Python classes, as described above.
    """
    names_and_classes = inspect.getmembers(
        module, predicate=lambda member: inspect.isclass(member)
    )
    classes = [class_ for _, class_ in names_and_classes]

    # Filter out imported members
    # https://stackoverflow.com/a/24994871
    non_imported_classes = [
        class_ for class_ in classes if class_.__module__ == module.__name__
    ]

    filtered_classes = non_imported_classes
    if name is not None:
        filtered_classes = filter(
            lambda class_: class_.__name__ == name, filtered_classes
        )

    if base_class is not None:
        filtered_classes = filter(
            lambda class_: issubclass(class_, base_class), filtered_classes
        )

    return list(filtered_classes)


def convert_programmatic_ids_to_jsonschema(ids_location: str) -> DictStrAny:
    """
    Generate the JSON Schema of the import-able Python object.

    :param ids_location:
        The 'location' of the IDS class to export to JSON Schema. This may be...

        1. ...an import-able module, e.g. ``my_ids_package.my_subpackage``, in which case
        the :class:`ts_ids_core.schema.IdsSchema` subclass in the module is exported. If
        no :class:`ts_ids_core.schema.IdsSchema` subclass is found export the module's
        :class:`ts_ids_core.base.ids_element.IdsElement` if there's exactly one in the
        module.

        2. ...an import-able module and :class:`ts_ids_core.base.ids_element.IdsElement`
        subclass, e.g. ``my_ids_package.my_subpackage.MyIds``.

        WARNING: The specified Python module will be imported, so it should have no
        consequential side effects.
    :return:
        The JSON schema as a Python dictionary.
    """
    if ids_location == "":
        raise ValueError("An empty string is not a valid module and/or IDS class.")

    try:
        module = import_module(ids_location)
    except ModuleNotFoundError:
        # user passed in module and class name, e.g. "my_package.my_subpackage.MyClass"
        *module_name_components, ids_class_name = ids_location.split(".")
        module_name = ".".join(module_name_components)
        try:
            module = import_module(module_name)
        except (ModuleNotFoundError, ValueError) as exc:
            # ValueError is raised if `ids_location` contains a top-level package name
            # only, e.g. "requests", such that `module_name_components` is an empty string.
            raise ModuleNotFoundError(
                f"Failed to import '{ids_location}' and '{module_name}'. Are they in "
                f"the system path?"
            ) from exc
        ids_classes = get_module_classes(
            module, name=ids_class_name, base_class=IdsElement
        )
        if len(ids_classes) == 0:
            raise ValueError(
                f"No IdsElement class named {ids_class_name} found in module '{module_name}'."
            )
        if len(ids_classes) > 1:
            raise ValueError(
                f"Multiple IDS classes named {ids_class_name} were found in "
                f"module '{module_name}'. Please use unique class names."
            )
    else:
        # look for the IdsSchema child class in that module
        ids_classes = get_module_classes(module, base_class=IdsElement)
        if len(ids_classes) == 0:
            raise ValueError(f"No IdsElement classes found in module '{ids_location}'.")
        elif len(ids_classes) > 1:
            ids_classes = get_module_classes(module, base_class=IdsSchema)
            if len(ids_classes) == 0:
                raise ValueError(f"No IDS class found in module, '{module.__name__}'.")
            if len(ids_classes) > 1:
                raise ValueError(
                    "Multiple IdsSchema classes found. Please specify which one to "
                    "generate jsonschema from."
                )

    return ids_classes[0].schema()


if __name__ == "__main__":
    write_jsonschema_ids()
