# -*- coding: utf-8 -*-
{
    'name': "q2_partner_filter_create",

    'summary': """
        Modulo que permite crear clientes sin que se dupliquen, al filtrar por el nombre, teléfono, correo electrónico y cif
        Al dar de alta verifica que no existe ningún partner con algunos de estos criterios y si es así lo crea creando tambien su cuanta analitica

        """,

    'description': """
                Modulo que permite crear clientes sin que se dupliquen, al filtrar por el nombre, teléfono, correo electrónico y cif
        Al dar de alta verifica que no existe ningún partner con algunos de estos criterios y si es así lo crea creando tambien su cuanta analitica
    """,

    'author': "Q2 Consulting",
    'website': "http://www.q2consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Contacts',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
