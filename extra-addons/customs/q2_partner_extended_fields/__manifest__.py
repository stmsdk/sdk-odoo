# -*- coding: utf-8 -*-
{
    'name': "q2_partner_extended_fields",

    'summary': """
        Módulo que extiende los campos y funcionalidad del módulo de contactos
        """,

    'description': """
        Añade al módulo de contactos id extra para migraciones de otros sistemas.
		Tambien hace visible el id incremental y unico actual en el campo ref (ventas>referencia)
		Amplia la busqueda por defecto a estos dos campos para que se pueda buscar por ellos en lso M2O y M2M
		Al crear un contacto le asigna un id automaticamente de forma incremental
		Generamos las cuentas de compra y gastos de forma automatica  y se las asignamos al guardar el 
    """,

    'author': "Q2 QualityQuery",
    'website': "http://www.q2consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Others',
    'version': '14.0.1.0',
    "application": False,
    "installable": True,
    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/report.xml',
    ],
}
