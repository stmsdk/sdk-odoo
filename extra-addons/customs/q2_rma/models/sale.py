
# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
import wdb

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Marca la so como contenedora de devolucion siempre que se devuelva algun producto de la orden
    q2_with_rma = fields.Boolean(
        string='La Orden contiene devolución',
    )

    # Marcamos True cuando el documento es una orden de abono por devolucion
    q2_is_rma = fields.Boolean(
        string='Es una devolución',
    )

    rma_refund_id = fields.Many2one(
        comodel_name="rma",
        string="Abono/Cliente",
    )

    rma_refund= fields.Boolean(
        string='Abonado',
    )

    rma_refund_count= fields.Integer(
        string='Abonos',
    )


    visible_button_create_rma = fields.Boolean(
        compute="_compute_visible_button_create_rma"
    )

    def _compute_visible_button_create_rma(self):
        #wdb.set_trace()
        visible = False
        group_id = self.procurement_group_id.id
        # Verificamos que este confirmado el pedido y que tenga picking
        # Solo haremos este filtro si queremos mostrar el boton solo cuando quedan articulos entregados que no hayan sido gestionados por RMA
        #wdb.set_trace()
        #if self.rma_ids:
        #    if self.rma_ids < 1:
        #        visible=False
        #elif group_id:

        if group_id:
            # Obtenemos el id del stock_picking_type out_type_id desde stock warehouse
            sw = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)])
            # controlamos que tengamos resultados
            if sw:
                #asignamos el valor de out_type_id que es el correspondiente a las operaciones de salida a cliente
                out_type_id = sw['out_type_id'].id
                sp = self.env['stock.picking'].search([
                    ('group_id', '=', self.procurement_group_id.id),
                    '|',
                    ('picking_type_id', '=', out_type_id),
                    ('picking_type_id', '=', 11), # Dropship pero hay que buscar la formula de hacerlo dinamico, esto daria fallos en otra instalación
                ])
                for p in sp:
                    if p['state']=='done':
                        visible=True

        self.visible_button_create_rma = visible

    def action_cancel(self):
        """
        sobreescribimos la accion ed cancelar
        para incluir la cancelacion de la propuesta de abono a cliente

        """
        #wdb.set_trace()
        res = super().action_cancel()
 
        for order in self:
            if order.rma_refund:
                #OObtenemoos el rma a partir del id
                rma = order.rma_refund_id
                # actualizamos los campos para que no haga referenciia a la orden cancelada
                rma.update({
                    "refund_sale_order_id" : None ,
                    "refund_sale_order_line_id" : None ,
                    "state" : "received",
                    })

                order.update({
                    "rma_refund_id" : None,
                    "rma_refund" : False,
                    "rma_refund_count" : 0,
                    })
        return res

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
                rma.update({
                    "state" : "waiting_refund",
                    "state_process" : "invoicing",
                    })
        res = super().action_confirm()
        return res

    def action_view_rma_refund(self):
        #wdb.set_trace()
        self.ensure_one()
        action = self.sudo().env.ref("rma.rma_action").read()[0]
        #rma = self.rma_ids
        rma = self.rma_refund_id
        if len(rma) == 1:
            action.update(
                res_id = rma.id,
                view_mode = "form",
                views = [],
            )
        #else:
        #    action["domain"] = [("id", "in", rma.ids)]
        # reset context to show all related rma without default filters
        action["context"] = {}
        return action


