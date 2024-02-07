# Archivo de instalacion
# En este archivo incluiremos todos los cambios que se tengan que hacer para que 
# el modulo se ejecte con normalidad

# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api
import re
#import wdb #wdb.set_trace()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # En la instalacion incluiremos un registro de configuracion, ncb

    def init_cbpg_values():
        #wdb.set_trace()
        # Al instalar el modelo inicializacemos el valor de CB y PG en todos los registros de sale_order
        ls_so = env['sale.order'].search([('client_order_ref','ilike','%CB%')])
        
        # recorremos todos os registros localizados en la busqueda para actualizar su valor CB y eliminar la etiquueta 
        for so in ls_so:
            # para cada orden llamamos al metodo que ajusta el cbpg
            vals = {} #so.set_cbpg_client_order_ref({},True)
            so.sudo().write(vals)

    # Iniciamos el metodo que ajusta los valores
    init_cbpg_values()  