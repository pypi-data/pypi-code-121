from .utils import allow_module_not_found_error
from .utils import get_configuration_context
from importlib import import_module

import pkg_resources
import unittest


try:
    pkg_resources.get_distribution("plone.autoinclude")
    HAS_PLONE_AUTOINCLUDE = True
except pkg_resources.DistributionNotFound:
    HAS_PLONE_AUTOINCLUDE = False
try:
    pkg_resources.get_distribution("z3c.autoinclude")
    HAS_Z3C_AUTOINCLUDE = True
except pkg_resources.DistributionNotFound:
    HAS_Z3C_AUTOINCLUDE = False
if HAS_PLONE_AUTOINCLUDE and HAS_Z3C_AUTOINCLUDE:
    raise ValueError(
        "In the tests at most one of plone.autoinclude and z3c.autoinclude should be available, not both."
    )


class PackageTestCase:
    """Test our interaction with a package.

    You can find most packages in the test-packages directory in the repo.

    This is a base test class for all packages.
    You can inherit from this class and override the variables.

    The base class intentionally does not inherit unittest.TestCase,
    otherwise the test runner tries to run the tests from the base class as well.
    """

    project_name = ""
    # If module name differs from project name, fill this in:
    module_name = ""
    # Accept ModuleNotFound errors for some projects with different module names.
    # This should be same list for all test packages, and should contain all
    # test packages with the old z3c.autoinclude.plugin that have this problem.
    allow_module_not_found = {"example.different"}
    # Does the package use plone.autoinclude (True) or the old z3c.autoinclude (False)?
    # Attribute is only used when we have a different module_name.
    uses_plone_autoinclude = True
    # Is the package expected to work when only z3c.autoinclude is available?
    # It should work when it uses [z3c.autoinclude.plugin] with 'target = plone'.
    standard_z3c_autoinclude = False
    # Which files are included when we load meta.zcml, configure.zcml, overrides.zcml?
    # Make this empty in your test case when the package has no such zcml.
    # When you add a test package, make sure to update test_integration_plone.py
    # and maybe other integration tests as well: add the new package to
    # meta_files, configure_files and overrides_files there.
    meta_files = ["meta.zcml"]
    configure_files = ["configure.zcml"]
    overrides_files = ["overrides.zcml"]
    # Are any features provided when loading meta.zcml?
    features = []

    def import_me(self):
        if self.module_name:
            return import_module(self.module_name)
        return import_module(self.project_name)

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_load_packages(self):
        from plone.autoinclude.loader import load_packages
        from plone.autoinclude import loader

        # Empty the known module names, so projects are loaded again.
        loader._known_module_names = {}
        if self.module_name and not self.uses_plone_autoinclude:
            # Module name differs from project name.
            # Allowing ModuleNotFound in all known ones except our own,
            # should fail, so the user knows something is wrong.
            allowed = self.allow_module_not_found - {self.project_name}
            with allow_module_not_found_error(allowed):
                with self.assertRaises(ModuleNotFoundError):
                    packages = load_packages()

        # User can allow some modules to have ModuleNotFoundErrors.
        with allow_module_not_found_error(self.allow_module_not_found):
            packages = load_packages()
        if self.module_name:
            # Only module names get in the packages list.
            self.assertNotIn(self.project_name, packages.keys())
            if not self.uses_plone_autoinclude:
                # The package uses the old z3c.autoinclude.
                # This means we cannot find any zcml.
                self.assertNotIn(self.module_name, packages.keys())
                return
            self.assertIn(self.module_name, packages.keys())
        else:
            self.assertIn(self.project_name, packages.keys())
        loaded_package = packages[self.module_name or self.project_name]
        imported_package = self.import_me()
        self.assertEqual(loaded_package, imported_package)

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_get_zcml_file_non_existing(self):
        from plone.autoinclude.loader import get_zcml_file

        self.assertIsNone(get_zcml_file(self.project_name, zcml="foo.zcml"))
        if self.module_name:
            self.assertIsNone(get_zcml_file(self.module_name, zcml="foo.zcml"))

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_get_zcml_file_default(self):
        from plone.autoinclude.loader import get_zcml_file

        if self.module_name:
            # The module name differs from the project name,
            # so getting the file by project name will fail.
            filename = get_zcml_file(self.project_name)
            self.assertIsNone(filename)
        filename = get_zcml_file(self.module_name or self.project_name)
        if not self.configure_files:
            self.assertIsNone(filename)
            return
        self.assertIsNotNone(filename)
        with open(filename) as myfile:
            self.assertIn(
                f"This is configure.zcml from {self.project_name}.", myfile.read()
            )

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_load_zcml_file_meta(self):
        from plone.autoinclude.loader import load_zcml_file

        # prepare configuration context
        package = self.import_me()
        context = get_configuration_context(package)
        self.assertEqual(len(context._seen_files), 0)

        load_zcml_file(
            context, self.module_name or self.project_name, package, "meta.zcml"
        )
        for filepath in self.meta_files:
            self.assertIn(context.path(filepath), context._seen_files)
        self.assertEqual(len(context._seen_files), len(self.meta_files))

        # meta.zcml may have a meta:provides option.
        for feature in self.features:
            self.assertTrue(
                context.hasFeature(feature), f"meta:provides feature {feature} missing"
            )
        self.assertEqual(context._features, set(self.features))

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_load_zcml_file_configure(self):
        from plone.autoinclude.loader import load_zcml_file

        # prepare configuration context
        package = self.import_me()
        context = get_configuration_context(package)
        self.assertEqual(context._features, set())

        # Load configure.zcml.
        load_zcml_file(context, self.module_name or self.project_name, package)
        for filepath in self.configure_files:
            self.assertIn(context.path(filepath), context._seen_files)
        self.assertEqual(len(context._seen_files), len(self.configure_files))

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_load_zcml_file_overrides(self):
        from plone.autoinclude.loader import load_zcml_file

        package = self.import_me()
        context = get_configuration_context(package)
        load_zcml_file(
            context,
            self.module_name or self.project_name,
            package,
            "overrides.zcml",
            override=True,
        )
        for filepath in self.overrides_files:
            self.assertIn(context.path(filepath), context._seen_files)
        self.assertEqual(len(context._seen_files), len(self.overrides_files))

    @unittest.skipIf(not HAS_PLONE_AUTOINCLUDE, "plone.autoinclude missing")
    def test_load_zcml_file_non_existing(self):
        from plone.autoinclude.loader import load_zcml_file

        package = self.import_me()
        context = get_configuration_context(package)
        load_zcml_file(
            context,
            self.module_name or self.project_name,
            package,
            zcml="non_existing.zcml",
        )
        self.assertEqual(len(context._seen_files), 0)

    @unittest.skipIf(not HAS_Z3C_AUTOINCLUDE, "z3c.autoinclude missing")
    def test_z3c_plugin_finder(self):
        # Can z3c.autoinclude find all packages that use its entry point in setup.py?
        if not self.standard_z3c_autoinclude:
            self.skipTest("No standard z3c.autoinclude setup.")

        from z3c.autoinclude.plugin import PluginFinder

        # We look for entry points with target plone.
        finder = PluginFinder("plone")
        # And we look for any zcml files.
        info = finder.includableInfo(["meta.zcml", "configure.zcml", "overrides.zcml"])
        # info is a dict. Example key: 'meta.zcml'.  Example value: list of module names.
        modules = []
        for values in info.values():
            modules.extend(values)
        if self.module_name:
            # Module name differs from project name.
            # Only module names get in the modules list.
            self.assertIn(self.module_name, modules)
            self.assertNotIn(self.project_name, modules)
        else:
            self.assertIn(self.project_name, modules)
