# -*- coding: utf-8 -*-
{
    'name': "q2_sale_order_extends",

    'summary': """
        Incluiremos varios campos de control para marcar rapidamente los pedidos entregados y los pedidos facturados
        """,

    'description': """
        Check de pedido entregado y de pedido facturado
    """,

    'author': "Q2 Solutions",
    'website': "http://q2s.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '14.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
