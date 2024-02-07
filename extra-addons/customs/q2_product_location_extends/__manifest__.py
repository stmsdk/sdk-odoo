# -*- coding: utf-8 -*-
{
    'name': "q2_product_location_extends",

    'summary': """
        Este modulo nos permite mostrar la ubicacion por defecto de un producto 
        obtenida de la ultima ubicacion asignada.
        Tambien mostrara la ubicacion el pedido / albaran
        Muestra la ubicacion del producto en la busqueda de productos en el modo kanban
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Q2 Quality Query Solutions",
    'website': "http://www.q2s.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '14.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ["website_sale",'product','q2_product_brand','sale','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
