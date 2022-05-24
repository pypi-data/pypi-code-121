from contextlib import contextmanager
from zope.configuration.config import ConfigurationMachine
from zope.configuration.xmlconfig import registerCommonDirectives


def get_configuration_context(package=None):
    """Get configuration context.

    Various functions take a configuration context as argument.
    From looking at zope.configuration.xmlconfig.file the following seems about right.

    Note: this is a copy of a function in plone.autoinclude.tests.utils.
    The duplication is deliberate: I don't want one package to import code from the other, for now.
    """
    context = ConfigurationMachine()
    registerCommonDirectives(context)
    if package is not None:
        # When you set context.package, context.path(filename) works nicely.
        context.package = package
    return context


@contextmanager
def allow_module_not_found_error(allowed):
    from plone.autoinclude import loader

    # save original settings
    orig_all = loader.ALLOW_MODULE_NOT_FOUND_ALL
    orig_set = loader.ALLOW_MODULE_NOT_FOUND_SET
    # Temporarily allow module not found error for only the
    # packages in the allowed set.
    loader.ALLOW_MODULE_NOT_FOUND_ALL = False
    loader.ALLOW_MODULE_NOT_FOUND_SET = allowed
    # breakpoint()
    try:
        yield
    finally:
        # restore
        loader.ALLOW_MODULE_NOT_FOUND_ALL = orig_all
        loader.ALLOW_MODULE_NOT_FOUND_SET = orig_set
