# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Viene con una adaptacion del modulo de Notes de odoo

{
    'name': 'q2_workshop',
    'version': '1.0',
    'category': 'Sales',
    'description': "Aplicacion de seguimiento de ordenes de servicio taller",
    'website': 'https://www.q2q.com',
    'summary': 'Permite seguir los trabajos de taller de  forma grafica',
    'sequence': 260,
    'depends': [
        'sale','q2_sale_order_extends'
    ],
    'data': [
        'data/workshop_data.xml',
        'security/workshop_security.xml',
        'security/ir.model.access.csv',
        #'data/mail_activity_data.xml',
        #'data/res_users_data.xml',
        'views/workshop_views.xml',
        'views/menu.xml',
        'views/sale_views.xml',
        #'views/note_templates.xml',
    ],
    'demo': [
        #'data/workshop_demo.xml',
    ],
    'qweb': [
        #'static/src/xml/systray.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
