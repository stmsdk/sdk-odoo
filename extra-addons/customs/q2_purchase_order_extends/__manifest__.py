# -*- coding: utf-8 -*-
{
    'name': "q2_purchase_order_extends",

    'summary': """
        Extension personalizada para Soterma del módulo de compra
    """,
    'description': """
        Extension personalizada para Soterma del módulo de compra
    """,

    'author': "Q2 Solutions",
    'website': "http://www.q2solutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
