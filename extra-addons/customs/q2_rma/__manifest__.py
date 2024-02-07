# -*- coding: utf-8 -*-
{
    'name': "q2_rma",

    'summary': """
        Modulo que agiliza la devolución de los productos y realiza seguimiento de los mismos
    """,

    'description': """
        Modulo que agiliza la devolución de los productos y realiza seguimiento de los mismos
    """,

    'author': "Q2 Solutions",
    'website': "http://q2s.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','rma','rma_sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/rma_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/rma_delivery_views.xml',
        'views/sale_order_rma_wizard_views.xml',
        'wizard/rma_move_send_to_stock_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "post_init_hook": "post_init_hook",
}
