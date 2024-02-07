# -*- coding: utf-8 -*-
{
    'name': "q2_sale_commission",

    'summary': """
        Este módulo extiende las funciones del modulo de OCA Sale Commissions
        Reconocimientos al gran trabajo del equipo de Tecnativa
        # Copyright 2014-2020 Tecnativa - Pedro M. Baeza
        # Copyright 2020 Tecnativa - Manuel Calero

        """,
    'description': """
        Este módulo añade a sales commission la sigioentes funciones
        Regitra en las ordenes de venta los usuarios que ejecutan las diferentes acciones que componen un proceso de venta
        para posteriormente poder fraccionar las comisiones por accion/usuario:
            > Gestor de la cuenta (Comisión asignada al usuario responsable cuenta y de la comunicacion con el cliente)
            > Recuperación de cartera (Comisión asignada al usuario que reactiva un cliente existente sin volumenn de venta)
            > Captacion de cliente (Comision )
            > El usuario que genera el presupuesto
            > El usuario que confirma el presupuesto pasando a pedido
            > El usuario que gestiona la compra si es requerida
        
            Metodos de control de ordenes de venta
            > Control de cancelacion de presupuestos
            > Control de no duplicidad de orden de venta
            > Control de confimacion de orden de compra en caso de ser requerida
            > Control de coste de devoluciones
            
    """,

    'author': "Q2 Quality Query",
    'website': "http://www.q2qualityquery.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # For the full list
    'category': 'sale',
    'version': '0.1',

    # Any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','sales_team','sale_commission','q2_rma'],

    # Always loaded
    'data': [
        'data/data_sale_commission_actions.xml',
        #'data/data_sale_commission_ws_ask_service.xml',
        #'data/data_sale_commission_ws_service_request.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        #'wizard/sale_order_type_wizard_views.xml',
    ],
    # Only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
