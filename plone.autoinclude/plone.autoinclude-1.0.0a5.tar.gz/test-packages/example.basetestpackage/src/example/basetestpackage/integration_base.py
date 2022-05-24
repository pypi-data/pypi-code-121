from .utils import get_configuration_context
from importlib import import_module

import pkg_resources


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


class IntegrationTestCase:
    """Test integration with a project that uses plone.autoinclude to load other packages.

    This is a base test class for all projects.
    You can inherit from this class and override the variables.

    The base class intentionally does not inherit unittest.TestCase,
    otherwise the test runner tries to run the tests from the base class as well.
    """

    project_name = ""
    # In the setup.py entry_point you specify a target, for example "plone".
    target = ""
    # zcml files that we expect to have been loaded.
    # key is project name, value is list of file names within the project
    meta_files = {}
    configure_files = {}
    overrides_files = {}
    # Are any features provided when loading meta.zcml?
    features = []

    def setUp(self):
        """Load meta.zcml

        plone.autoinclude makes sure zcml automatically gets loaded.
        But it can only start doing its work when its own meta.zcml gets loaded.
        So how does that happen?  Do we have a chicken-and-egg problem?

        How it works for Plone 5.2 with buildout and plone.recipe.zope2instance:

        1. When you have a "zcml" option in your plone.recipe.zope2instance part,
           the zcml of the packages in there gets loaded.
        2. Products alphabetically until and including Products.CMFPlone
           get their zcml loaded.
        3. When loading meta.zcml of Products.CMFPlone, z3c.autoinclude gets loaded.
           In example.ploneintegration we replace this by plone.autoinclude.
           Either one makes sure the meta.zcml of packages with
           an autoinclude entry point gets loaded
        4. Same happens when loading configure.zcml of Products.CMFPlone.
        5. Same happens when loading overrides.zcml of Products.CMFPlone.
        6. After this, the rest of the Products get their zcml loaded.

        This is adapted from Maurits' i18n presentation in Ploneconf Arnhem 2012,
        the part about overriding translations:
        https://github.com/mauritsvanrees/maurits.i18ntalk/blob/master/talk.rst#overriding-existing-translations

        In this setUp method, we mimick this.
        We load meta.zcml of example.ploneintegration, and this gets the ball rolling:

        - It loads the meta.zcml of plone.autoinclude.
        - This means the  autoIncludePlugins and autoIncludePluginsOverrides
          directives are available in zcml.
        - This means configure.zcml and overrides.zcml of example.ploneintegration,
          which use these directives, can be loaded without error.

        We do not yet load configure.zcml or overrides.zcml.
        That is done in the tests.
        """
        # prepare configuration context
        package = import_module(self.project_name)
        self.context = get_configuration_context(package)
        self.load_zcml_file("meta.zcml")

    def load_zcml_file(self, zcml="configure.zcml", override=False):
        from plone.autoinclude.loader import load_zcml_file

        load_zcml_file(self.context, self.project_name, zcml=zcml, override=override)

    @property
    def meta_count(self):
        return sum([len(value) for value in self.meta_files.values()])

    @property
    def configure_count(self):
        return sum([len(value) for value in self.configure_files.values()])

    @property
    def overrides_count(self):
        return sum([len(value) for value in self.overrides_files.values()])

    def files_have_been_loaded(self, files):
        for project_name, filenames in files.items():
            package = import_module(project_name)
            package_context = get_configuration_context(package)
            for filename in filenames:
                self.assertIn(package_context.path(filename), self.context._seen_files)

    def test_context(self):
        # Test that the context is still what we expect.
        package = import_module(self.project_name)
        self.assertEqual(package, self.context.package)
        if self.context.basepath is None:
            # Getting the path of a file makes sure the basepath is set.
            self.context.path("configure.zcml")
        # If project name is example.ploneintegration,
        # then ploneintegration must be in the base path.
        self.assertIn(self.project_name.split(".")[-1], self.context.basepath)

    def test_features(self):
        # The various meta.zcml files may have meta:provides options.
        for feature in self.features:
            self.assertTrue(
                self.context.hasFeature(feature),
                f"meta:provides feature {feature} missing",
            )
        self.assertEqual(self.context._features, set(self.features))

    def test_meta(self):
        # The meta files have been loaded in setUp.
        self.assertIn(self.context.path("meta.zcml"), self.context._seen_files)
        self.assertEqual(len(self.context._seen_files), self.meta_count)
        self.files_have_been_loaded(self.meta_files)

    def test_configure(self):
        # Load configure.zcml.
        self.assertNotIn(self.context.path("configure.zcml"), self.context._seen_files)
        self.load_zcml_file()
        self.assertIn(self.context.path("configure.zcml"), self.context._seen_files)
        self.files_have_been_loaded(self.configure_files)
        self.assertEqual(
            len(self.context._seen_files),
            self.meta_count + self.configure_count,
            self.context._seen_files,
        )

    def test_overrides(self):
        # Load overrides.zcml.
        self.assertNotIn(self.context.path("overrides.zcml"), self.context._seen_files)
        self.load_zcml_file(zcml="overrides.zcml", override=True)
        self.assertIn(self.context.path("overrides.zcml"), self.context._seen_files)
        self.files_have_been_loaded(self.overrides_files)
        self.assertEqual(
            len(self.context._seen_files),
            self.meta_count + self.overrides_count,
            self.context._seen_files,
        )

    def test_all_zcml(self):
        # Load configure.zcml and overrides.zcml.
        self.load_zcml_file()
        self.load_zcml_file(zcml="overrides.zcml", override=True)
        self.files_have_been_loaded(self.meta_files)
        self.files_have_been_loaded(self.configure_files)
        self.files_have_been_loaded(self.overrides_files)
        self.assertEqual(
            len(self.context._seen_files),
            self.meta_count + self.configure_count + self.overrides_count,
            self.context._seen_files,
        )
