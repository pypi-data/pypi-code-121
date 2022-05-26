from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


appsystem_buttons = [
    PluginMenuButton(
        link='plugins:netbox_app_systems:appsystem_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]


menu_items = (
    PluginMenuItem(
        link='plugins:netbox_app_systems:appsystem_list',
        link_text='App systems',
        # buttons=appsystem_buttons
    ),
)
