# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

## ERRORES POSIBLES AL DESINSTALAR E INSTALAR DE NUEVO
## INDICES DUPLICADOS
"""
__exception__
IntegrityError: duplicate key value violates unique constraint "stock_picking_name_uniq"
DETAIL:  Key (name, company_id)=(SEAG0/RMA/IN/00003, 1) already exists.
"""

from odoo import SUPERUSER_ID, _, api, fields, models

import wdb ##wdb.set_trace()


class SaleOrderTypeWizard(models.TransientModel):
    _name = "q2_sale_order.type_wizard"
    
    # is_refund is_replace is_warranty
    # def create_and_open_rma_replace(self):
    #    #wdb.set_trace()
    #    self.env.context = dict(self.env.context)
    #    self.env.context.update( { 'rma_operation_type': 'is_replace' } )
    #    self.create_and_open_rma()
    

    def action_is_sale(self):
        #wdb.set_trace()
        self.env.context = dict(self.env.context)
        # self.env.context.update( { 'q2_sale_operation_type': 'sale' } )

    def action_is_service(self):
        #wdb.set_trace()
        self.env.context = dict(self.env.context)
        # self.env.context.update( { 'q2_sale_operation_type': 'service' } )



        

