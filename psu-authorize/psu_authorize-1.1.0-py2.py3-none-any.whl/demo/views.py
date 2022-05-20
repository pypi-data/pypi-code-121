from django.shortcuts import render
from psu_base.classes.Log import Log
from psu_base.services import utility_service
from django.conf import settings
from psu_base import _DEFAULTS as base_defaults
log = Log()


def index(request):
    """
    A landing page
    """
    log.trace()

    all_links = []
    for plugin, version in utility_service.get_installed_plugins().items():
        exec(f"from {plugin} import _DEFAULTS as {plugin}_defaults")
        these_links = eval(f"{plugin}_defaults['{plugin.upper()}_ADMIN_LINKS']")
        if these_links:
            all_links.extend(these_links)

    plugins = utility_service.get_installed_plugins()
    base_links = getattr(settings, 'PSU_BASE_ADMIN_LINKS', base_defaults['PSU_BASE_ADMIN_LINKS'])
    log.end()
    return render(
        request, 'landing.html', {'plugins': plugins, 'base_links': base_links, 'all_links': all_links}
    )
