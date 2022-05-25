from . import urls
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook
from .models import BlacklistFilter


class LogMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Pilot Log',
                              'fas fa-address-book fa-fw',
                              'blacklist:note_board',
                              navactive=['blacklist:note_board'])

    def render(self, request):
        if request.user.has_perm('blacklist.view_eve_notes') or request.user.has_perm('blacklist.view_basic_eve_notes'):
            return MenuItemHook.render(self, request)
        return ''


class BlacklistMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Blacklist',
                              'fas fa-ban fa-fw',
                              'blacklist:blacklist',
                              navactive=['blacklist:blacklist'])

    def render(self, request):
        if request.user.has_perm('blacklist.view_eve_blacklist'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return LogMenu()


@hooks.register('menu_item_hook')
def register_menu():
    return BlacklistMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'blacklist', r'^blacklist/')


@hooks.register("secure_group_filters")
def filters():
    return [BlacklistFilter]
