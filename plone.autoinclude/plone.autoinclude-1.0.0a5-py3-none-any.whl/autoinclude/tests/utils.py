from zope.configuration.config import ConfigurationMachine
from zope.configuration.xmlconfig import registerCommonDirectives


def get_configuration_context(package=None):
    """Get configuration context.

    Various functions take a configuration context as argument.
    From looking at zope.configuration.xmlconfig.file the following seems about right.

    Note: there is a copy of this function in example.basetestpackage.
    The duplication is deliberate: I don't want one package to import code from the other, for now.
    """
    context = ConfigurationMachine()
    registerCommonDirectives(context)
    if package is not None:
        # When you set context.package, context.path(filename) works nicely.
        context.package = package
    return context
