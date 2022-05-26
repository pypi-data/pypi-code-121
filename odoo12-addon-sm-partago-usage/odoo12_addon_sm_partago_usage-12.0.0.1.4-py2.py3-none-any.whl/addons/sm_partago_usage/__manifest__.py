# -*- coding: utf-8 -*-
{
    'name': "sm_partago_usage",

    'summary': """
        Module to manage reservations from booking app""",

    'author': "Som Mobilitat",
    'website': "https://www.sommobilitat.coop",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'vertical-carsharing',
    'version': '12.0.0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['base','vertical_carsharing','sm_carsharing_structure'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/views_cron.xml',
        'views/views_reservation_compute.xml',
        'views/views_edit_reservation_compute_wizard.xml',
        'views/views_wizards.xml',
        'views/views_members.xml'
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
