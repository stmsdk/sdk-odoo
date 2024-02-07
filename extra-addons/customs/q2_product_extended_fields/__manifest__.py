# -*- coding: utf-8 -*-
{
    'name': "q2_product_extended_fields",

    'summary': """
        Módulo que extiende los campos de la ficha producto
        """,

    'description': """
        Módulo que extiende los campos de la ficha producto
        Añadiendo
            - Referencia catálogo
            - Referencias equivalentes
            - Referencias originales
            - Marcas y modelos compatibles
            - Ancho
            - Alto
            - Largo
            - Peso             
    """,

    'author': "Q2 QualityQuery",
    'website': "http://www.q2consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Others',
    'version': '14.0.2.0',
    "application": False,
    "installable": True,
    # any module necessary for this one to work correctly
    'depends': ["website_sale",'product','q2_product_brand','sale','purchase'],

    # always loaded
    'data': [
        "templates/assets.xml",
        'views/templates.xml',
        'views/website_sale_template.xml',
    ],
}
