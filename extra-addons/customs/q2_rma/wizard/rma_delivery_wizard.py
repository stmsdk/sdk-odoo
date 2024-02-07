# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import wdb ##wdb.set_trace()
#Q2 RMA_DELIVERY

class RmaReDeliveryWizard(models.TransientModel):
    _inherit = "rma.delivery.wizard"

    type = fields.Selection(
        selection=[
                ("replace", "Replace"), 
                ("return", "Enviar al cliente"),
                ("return_supplier", "Enviar al proveedor"),
                ],
        string="Type",
        required=True,
    )

    @api.model
    def default_get(self, fields_list):
        #wdb.set_trace()
        res = super().default_get(fields_list)
        rma_ids = self.env.context.get("active_ids")
        rma = self.env["rma"].browse(rma_ids)
        warehouse_id = (
            self.env["stock.warehouse"]
            .search([("company_id", "=", rma[0].company_id.id)], limit=1)
            .id
        )
        delivery_type = self.env.context.get("rma_delivery_type")
        product_id = False
        if len(rma) == 1 and delivery_type == "return":
            product_id = rma.product_id.id
        if len(rma) == 1 and delivery_type == "return_supplier":
            product_id = rma.product_id.id
        product_uom_qty = 0.0
        if len(rma) == 1 and rma.remaining_qty > 0.0:
            product_uom_qty = rma.remaining_qty

        res.update({
            'rma_count':len(rma),
            'warehouse_id':warehouse_id,
            'type':delivery_type,
            'product_id':product_id,
            'product_uom_qty':product_uom_qty,
        })
        return res

    def action_deliver(self):
        #wdb.set_trace()
        self.ensure_one()
        rma_ids = self.env.context.get("active_ids")
        rma = self.env["rma"].browse(rma_ids)
        if self.type == "replace":
            rma.sudo().create_replace(
                self.scheduled_date,
                self.warehouse_id,
                self.product_id,
                self.product_uom_qty,
                self.product_uom,
            )
        elif self.type == "return":
            qty = uom = None
            if self.rma_count == 1:
                qty, uom = self.product_uom_qty, self.product_uom
            rma.with_context(
                rma_return_grouping=self.rma_return_grouping
            ).sudo().create_delivery_to_costumer(self.scheduled_date, qty, uom)
        elif self.type == "return_supplier": # iinsertado por moi para gestionar el retorno al proveedor
            qty = uom = None
            if self.rma_count == 1:
                qty, uom = self.product_uom_qty, self.product_uom
            rma.with_context(
                rma_return_grouping=self.rma_return_grouping
            ).sudo().create_delivery_to_supplier(self.scheduled_date, qty, uom)
