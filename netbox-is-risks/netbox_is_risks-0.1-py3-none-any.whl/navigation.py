from extras.plugins import PluginMenuItem
from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

risk_buttons = [
    PluginMenuButton(
        link='plugins:risks:risk_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]
risk_rel_buttons = [
    PluginMenuButton(
        link='plugins:risks:riskrelation_add',
        title='Add',
        icon_class='mdi mdi-plus-thick',
        color=ButtonColorChoices.GREEN
    )
]

menu_items = (
    PluginMenuItem(
        link='plugins:risks:risk_list',
        link_text='Risks',
        buttons=risk_buttons
    ),
    PluginMenuItem(
        link='plugins:risks:riskrelation_list',
        link_text='Risk Relations',
        buttons=risk_rel_buttons
    ),
)
