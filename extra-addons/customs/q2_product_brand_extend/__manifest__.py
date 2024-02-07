# -*- coding: utf-8 -*-
{
    'name': "q2_product_brand_extend",

    'summary': """
        Agregamos la seleccion de proveedores para un fabricante""",

    'description': """
        Módulo de fabricantes para los productos
    """,

    'author': "Q2 Consulting",
    'website': "http://www.q2consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Others',
    'version': '14.0.2.0',
    "application": False,
    "installable": True,   

    # any module necessary for this one to work correctly
    'depends': ['base','q2_product_brand'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
}
