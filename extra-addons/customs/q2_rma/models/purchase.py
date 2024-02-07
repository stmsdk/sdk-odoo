
# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_round
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

#import wdb

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    rma_refund_id = fields.Many2one(
        comodel_name="rma",
        string="Abono Provedor",
    )

    rma_refund= fields.Boolean(
        string='Abonado',
    )

    rma_refund_count= fields.Integer(
        string='Abonos',
    )

    def action_cancel(self):
        """
        sobreescribimos la accion ed cancelar
        para incluir la cancelacion de la propuesta de abono a cliente

        """
        #wdb.set_trace()
 
        for order in self:
            if order.rma_refund:
                #OObtenemoos el rma a partir del id
                rma = order.rma_refund_id
                state_purchase = "waiting_action_purchase"
                if rma.state_purchase == "reject_by_supplier":
                    state_purchase = "reject_return_by_supplier"

                # actualizamos los campos para que no haga referenciia a la orden cancelada
                rma.update({
                    #"refund_purchase_order_id" : None ,
                    #"refund_purchase_order_line_id" : None ,
                    "state_purchase" : state_purchase,
                    })

                #order.update({
                #    "rma_refund" : False,
                #    "rma_refund_count" : 0,
                #    })
                order.button_cancel()

    # Sobreescribimos la funcion button_confirm para evitar que nos realice un doble movimiento (evitamos el movimiento de entrada)
    def button_confirm(self):
        #wdb.set_trace()
        if not self.rma_refund:
            res= super(PurchaseOrder,self).button_confirm()
            return res
        else:
            for order in self:
                if order.state not in ['draft', 'sent']:
                    continue
                order._add_supplier_to_product()
                # Deal with double validation process
                if self.rma_refund:
                    order.button_approve()
                elif order._approval_allowed():
                    order.sudo().write({'state': 'to approve'})
                if order.partner_id not in order.message_partner_ids:
                    order.message_subscribe([order.partner_id.id])
            return True

    # No es valido interviniendo en button approve, porque duplica el movimiento
    def button_approve(self, force=False):
        #wdb.set_trace()
        if self.rma_refund:
            #self = self.filtered(lambda order: order._approval_allowed())
            self.sudo().write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
            self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
            return {}
        else:
            result = super(PurchaseOrder, self).button_approve(force=force)
            self._create_picking()
            return result

    def action_confirm(self):
        """
        sobreescribimos la accion ed cancelar
        para incluir la cancelacion de la propuesta de abono a cliente
        """
        #wdb.set_trace()
        for order in self:
            if order.rma_refund:
                #OObtenemoos el rma a partir del id
                rma = order.rma_refund_id
                # actualizamos los campos para que no haga referenciia a la orden cancelada
                rma.sudo().update({
                    "state_purchase" : "accepted_waiting_confirm_refund",
                    })

                #wdb.set_trace\(\)
                order.sudo().button_confirm()

    def action_view_rma_refund(self):
        #wdb.set_trace()
        self.ensure_one()
        action = self.sudo().env.ref("rma.rma_action").read()[0]
        rma = self.rma_refund_id
        if len(rma) == 1:
            #action.sudo().update(
            #    res_id = rma.id,
            #    view_mode = "form",
            #    views = [],
            #)
            action.sudo().update({
                'res_id': rma.id,
                'view_mode' : "form",
                'views' : [],
            })
        #else:
        #    action["domain"] = [("id", "in", rma.ids)]
        # reset context to show all related rma without default filters
        action["context"] = {}
        return action

    def _create_or_update_picking(self):
        #wdb.set_trace()
        res = super()._create_or_update_picking()
        for line in self:
            if line.product_id and line.product_id.type in ('product', 'consu'):
                # Prevent decreasing below received quantity
                if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
                    raise UserError(_('You cannot decrease the ordered quantity below the received quantity.\n'
                                      'Create a return first.'))

                if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
                    # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                    # inviting the user to create a refund.
                    line.invoice_lines[0].move_id.activity_schedule(
                        'mail.mail_activity_data_warning',
                        note=_('The quantities on your purchase order indicate less than billed. You should ask for a refund.'))

                # If the user increased quantity of existing line or created a new line
                #wdb.set_trace()
                pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit', 'customer'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.order_id._prepare_picking()
                    picking = self.env['stock.picking'].sudo().create(res)

                moves = line._create_stock_moves(picking)
                moves.sudo()._action_confirm()._action_assign()
        return res

    # Prepara el la factura de devoluciono a proveedor para que se realice la factuura
    # La confirmacion de pedido de abono a factura se realiza en account_move > action_post borramos esta sobreescritura
    """
    def action_create_invoice(self):
        #wdb.set_trace()
        #self.ensure_one()
        # Si ya hemos iniciado su facturación, no procederemos con otra factura para evitar duplicidad
        for order in self:
            if order.state not in  ['cancel']:
                if not order.rma_refund or order.invoice_count>0:
                    raise ValidationError(
                        _(
                            "Hay una factura en curso, conrme o concele la actual factura "
                        )
                    )
        # Si no esta ya creada la factura lanzamos la accion de crear
        return super(PurchaseOrder,self).action_create_invoice()
    """