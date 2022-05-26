# -*- coding: utf-8 -*-
{
  'name': "sm_report_data",

  'summary': """
     Module to generate reports xlsx and be able to send it via mail. 
  """,

  'description': """
  The module allows establishing a periodicity to generate and send a report automatically.
  """,

  'author': "Som Mobilitat",
  'website': "http://www.sommobilitat.coop",

  # Categories can be used to filter modules in modules listing
  # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
  # for the full list
  'category': 'Reports',
  'version': '12.0.0.0.6',

  # any module necessary for this one to work correctly
  'depends': ['base','vertical_carsharing','report_xlsx'],

  # always loaded
  'data': [
    'security/ir.model.access.csv',
    'views/views.xml',
    'views/templates.xml',
    'views/views_report_configuration.xml',
  ],
  # only loaded in demonstration mode
  'demo': [],
}
