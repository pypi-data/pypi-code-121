# Copyright 2008-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""See :doc:`/specs/gfks`.

"""

from lino.api import ad


class Plugin(ad.Plugin):

    """Base class for this plugin."""

    needs_plugins = ['lino.modlib.system', 'django.contrib.contenttypes']
    # needs_plugins = ['django.contrib.contenttypes']
    # avoid Exception: Tried to install lino_welfare.modlib.system where
    # lino.modlib.system (needed_by=lino.modlib.gfks (needed_by=lino.modlib.memo
    # (needed_by=lino_react.react (media_name=react)))) is already installed.


    # def setup_reports_menu(config, site, user_type, m):
    #     hook = site.plugins.system
    #     m = m.add_menu(hook.app_label, hook.verbose_name)
    #     m.add_action(site.modules.gfks.BrokenGFKs)

    def setup_config_menu(config, site, user_type, m):
        hook = site.plugins.system
        m = m.add_menu(hook.app_label, hook.verbose_name)
        m.add_action(site.modules.gfks.HelpTexts)

    def setup_explorer_menu(config, site, user_type, m):
        hook = site.plugins.system
        m = m.add_menu(hook.app_label, hook.verbose_name)
        m.add_action(site.modules.gfks.ContentTypes)
