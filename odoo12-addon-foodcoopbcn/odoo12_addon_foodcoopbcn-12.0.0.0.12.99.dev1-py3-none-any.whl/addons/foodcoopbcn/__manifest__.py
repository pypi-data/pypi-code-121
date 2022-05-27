{
    'name': "Odoo customizations for FoodCoopBCN",
    'version': '12.0.0.0.12',
    'depends': ['easy_my_coop_es','beesdoo_product'],
    'author': "Coopdevs Treball SCCL",
    'website': 'https://coopdevs.org',
    'category': "Cooperative management",
    'description': """
    Odoo customizations for FoodCoopBCN.
    """,
    "license": "AGPL-3",
    'data': [
        "data/ir_default.xml",
        "data/report_paperformat.xml",
        "data/templates.xml",
        # "views/become_cooperator_view.xml",
        "views/subscription_request_view.xml",
        "report/layout.xml",
        "report/same_product_label.xml",
        "report/product_label.xml",
        "report/product_reports.xml",
    ],
}
