import os, imp, sys, inspect

from . import io_lib
from ..models.tests import TestGroup, AlphaTest, test, TestCategories
import importlib
from inspect import getmembers, isfunction, isclass
from .py_lib import reload_modules

from ..models.logger import AlphaLogger
from typing import List

from core import core

LOG = core.get_logger("tests")

CATEGORIES = {}


def get_tests_auto(
    tests_modules: List[str],
    name: str = None,
    names: List[str] = [],
    group: str = None,
    groups: List[str] = [],
    category: str = None,
    categories: List[str] = [],
    file_path: str = None,
    run: bool = False,
    resume: bool = False,
    coverage: str = None,
) -> TestCategories:
    """Get the TestCategories class, containings all required tests.

    Args:
        tests_modules (List[str]): list of test modules path
        tests_modules (List[str]): list of test modules path
        name (str, optional): the name of the test to select. Defaults to None.
        group (str, optional): the name of the group to select. Defaults to None.
        category (str, optional): the name of the category to select. Defaults to None.

    Returns:
        TestCategories: [description]
    """
    global CATEGORIES

    categories = categories if categories is not None else []
    groups = groups if groups is not None else []
    names = names if names is not None else []

    if category is not None:
        categories.append(category)
    if group is not None:
        groups.append(group)
    if name is not None:
        names.append(name)
    categories = [x.strip() for x in categories]
    groups = [x.strip() for x in groups]
    names = [x.strip() for x in names]

    if len(categories) == 0 and len(groups) == 0 and len(names) == 0:
        LOG.info("Requested execution of all tests")
    else:
        LOG.info(
            f"Requested execution of tests:\n - categories: {', '.join(categories)}\n - groups: {', '.join(groups)}\n - names: {', '.join(names)}"
        )

    test_categories = TestCategories()

    for tests_module in tests_modules:
        try:
            module = importlib.import_module(tests_module)
        except Exception as ex:
            LOG.error(f"Cannot load test module <{tests_module}>", ex=ex)
            continue

        class_list = []
        for o in getmembers(module):
            is_class = isclass(o[1])
            if not is_class:
                continue
            is_test = (
                issubclass(o[1], AlphaTest)
                and (not hasattr(o[1], "_test") or o[1]._test)
                and not o[1] == AlphaTest
            )
            if not is_test:
                continue
            class_list.append(o)

        LOG.info(
            f'Loaded test module <{tests_module}> with test groups: {", ".join([x[0] for x in class_list])}'
        )

        for el in class_list:
            test_group = TestGroup(el[0], el[1], coverage=coverage is not None)

            if len(categories) != 0 and test_group.category not in categories:
                continue
            if len(groups) != 0 and test_group.name not in groups:
                continue

            if LOG is not None:
                LOG.debug(f"Found function group <{test_group.name}>")

            test_group.get_from_database()
            if run and len(names) == 0:
                test_group.test_all()
            elif run:
                test_group.test_all(names)

            test_categories.add_test_group(test_group)

    if file_path is not None:
        test_categories.to_junit(file_path)

    if resume:
        test_categories.resume()

    if coverage is not None:
        coverages = {}
        for category_name, category in test_categories.categories.items():
            for group_name, group in category.groups.items():
                for test_name, test in group.tests.items():
                    if (
                        test_name in test.coverages
                        and test.coverages[test_name] is not None
                    ):
                        coverages[
                            f"{category_name}-{group_name}-{test_name}"
                        ] = test.coverages[test_name]
        io_lib.archive_object(coverages, coverage)
    return test_categories


def execute_all_tests_auto(directory, output=True, refresh=True, name=None):
    return operate_all_tests_auto(
        directory, output=output, refresh=refresh, name=name, action="execute"
    )


def save_all_tests_auto(directory, output=True, refresh=True, name=None):
    return operate_all_tests_auto(
        directory, output=output, refresh=refresh, name=name, action="save"
    )


def operate_all_tests_auto(
    directory,
    output=True,
    refresh=True,
    name=None,
    action="execute",
    group=None,
    import_path=None,
):
    if refresh:
        reload_modules(os.getcwd())

    test_categories = get_tests_auto(directory, group=group, import_path=import_path)

    if action == "execute":
        tests_groups.test_all()
        return tests_groups.print(output=output)
    elif action == "save":
        tests_groups.save_all()
