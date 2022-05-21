from django.urls import path

from buybackprogram.views import calculate, common, programs, special_taxes, stats

app_name = "buybackprogram"

urlpatterns = [
    path("", common.index, name="index"),
    path("faq", common.faq, name="faq"),
    path("setup", programs.setup, name="setup"),
    path("program_add", programs.program_add, name="program_add"),
    path("location_add", programs.location_add, name="location_add"),
    path("user_settings_edit", common.user_settings_edit, name="user_settings_edit"),
    path(
        "location<int:location_pk>/remove",
        programs.location_remove,
        name="location_remove",
    ),
    path(
        "program/<int:program_pk>/special_taxes",
        special_taxes.program_special_taxes,
        name="program_special_taxes",
    ),
    path(
        "program/<int:program_pk>/edit_item",
        special_taxes.program_edit_item,
        name="program_edit_item",
    ),
    path(
        "program/<int:program_pk>/edit_marketgroup",
        special_taxes.program_edit_marketgroup,
        name="program_edit_marketgroup",
    ),
    path(
        "program/<int:program_pk>/edit",
        programs.program_edit,
        name="program_edit",
    ),
    path(
        "program/<int:program_pk>/remove",
        programs.program_remove,
        name="program_remove",
    ),
    path(
        "program/<int:program_pk>/program_item/<int:item_pk>/remove",
        special_taxes.program_item_remove,
        name="program_item_remove",
    ),
    path(
        "program/<int:program_pk>/remove_all",
        special_taxes.program_item_remove_all,
        name="program_item_remove_all",
    ),
    path(
        "program/<int:program_pk>/calculate",
        calculate.program_calculate,
        name="program_calculate",
    ),
    path("my_stats", stats.my_stats, name="my_stats"),
    path(
        "tracking/<str:contract_title>/",
        stats.contract_details,
        name="contract_details",
    ),
    path("program_stats", stats.program_stats, name="program_stats"),
    path("program_stats_all", stats.program_stats_all, name="program_stats_all"),
    path(
        "item_autocomplete/",
        common.item_autocomplete,
        name="item_autocomplete",
    ),
    path(
        "solarsystem_autocomplete/",
        common.solarsystem_autocomplete,
        name="solarsystem_autocomplete",
    ),
    path(
        "marketgroup_autocomplete/",
        common.marketgroup_autocomplete,
        name="marketgroup_autocomplete",
    ),
]
