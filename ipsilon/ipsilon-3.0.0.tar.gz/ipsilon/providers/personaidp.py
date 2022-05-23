# Copyright (C) 2014 Ipsilon project Contributors, for license see COPYING

from __future__ import absolute_import

from ipsilon.providers.common import ProviderBase, ProviderInstaller


class IdpProvider(ProviderBase):
    retired = True

    def __init__(self, *pargs):
        super(IdpProvider, self).__init__('persona', 'Persona (RETIRED)',
                                          'persona', *pargs)
        self.description = """
RETIRED Provided Persona authentication infrastructure. """

        self.new_config(
            self.name,
        )

    def register(self, root, site):
        pass

    def on_enable(self):
        self.disable()

    def get_tree(self, site):
        raise NotImplementedError("No tree available for Persona")

    def on_disable(self):
        pass

    def get_client_display_name(self, clientid):
        return clientid

    def consent_to_display(self, consentdata):
        return []


class Installer(ProviderInstaller):

    def __init__(self, *pargs):
        super(Installer, self).__init__()
        self.name = 'persona'
        self.pargs = pargs

    def install_args(self, group):
        pass

    def configure(self, opts, changes):
        pass
