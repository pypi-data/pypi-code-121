from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.utils.translation import gettext_lazy as _
from allianceauth import hooks
from . import urls


class IndyDash(MenuItemHook):
    def __init__(self):

        MenuItemHook.__init__(self,
                              "Industry Structures",
                              'fas fa-hammer fa-fw',
                              'indydash:view',
                              navactive=['indydash:'])

    def render(self, request):
        if request.user.has_perm('indydash.view_dash'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return IndyDash()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'indydash', r'^indy/')
