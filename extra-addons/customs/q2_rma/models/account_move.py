# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare

#import wdb #wdb.set_trace()

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        #wdb.set_trace()
        # Verifiamos el tipo de movimiento para ver si se trata de un abono de compra o venta
        # Confirmación de Abono de Venta 
        if self.move_type == 'out_refund':
            # obtenemos el abono de la venta
            so_origin = self.invoice_origin
            if so_origin:
                so = self.env['sale.order'].search([('name','=',so_origin)])
                if so:
                    # Si es un abono de compra, verificamos si la compra tiene rma asociado
                    rma  = so.rma_refund_id
                    if rma:
                        # Si tiene RMA asociado actualizamos los estados 
                        # Damos por finalizado el proceso de RMA
                        rma.sudo().write({
                            "state": "refunded",
                            "state_process": "finished",
                            })

        # Confirmación de Abono de Venta 
        if self.move_type == 'in_refund':
            # obtenemos el abono de compra
            po_origin = self.invoice_origin
            if po_origin:
                po = self.env['purchase.order'].search([('name','=',po_origin)])
                if po:
                    # Si es un abono de compra, verificamos si la compra tiene rma asociado
                    rma  = po.rma_refund_id
                    if rma:
                        # Si tiene RMA asociado actualizamos los estados 
                        rma.sudo().write({
                            "state_purchase": "accepted_refunded",
                            })

        # una vez cambiado los estados lanzamos el post
        return super(AccountMove,self).sudo().action_post()

    def unlink(self):
        rma = self.mapped("invoice_line_ids.rma_id")
        rma.sudo().write({"state": "received"})
        return super().unlink()

    """


    def unlink(self):
        rma = self.mapped("invoice_line_ids.rma_id")
        rma.sudo().write({"state": "received"})
        return super().unlink()
    """

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    rma_id_purchase_refund = fields.Many2one(
        comodel_name="rma",
        string="RMA",
    )
