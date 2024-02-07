# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
#import wdb

class StockPicking(models.Model):
    _inherit = "stock.picking"

    # esta funcion intenta localizar el articulo que se demanda para poder realizar el picking
    def action_assign_forced(self):
        # Si se para aqui es por que no asigna y espera un movimiento que tiene que realizar o forzar
        #wdb.set_trace()
        pass

