# -*- coding: utf-8 -*-
{
    'name': "q2_sale_order_extends_views",

    'summary': """
        Módulo que extiende las vistas de las ordenes de compra, principalmente para las albaranes no facturables y pedidos sin recepcion.
    """,

    'description': """
        Módulo que extiende las vistas de las ordenes de compra, principalmente para las albaranes no facturables y pedidos sin recepcion.
    """,

    'author': "Q2 Solutions",
    'website': "www.q2solutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'data/ir_config_parameter_data.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    # scripts de configuracion, donde analizaremos las so para inicializar los valores de CB y PG y añadiremos el parametro de control de vista  en la instalacion
    "post_init_hook": "post_init_hook",
}
