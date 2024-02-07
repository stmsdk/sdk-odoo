# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import Counter
from email.policy import default
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tests import Form
from odoo import tools
from odoo.tools import float_compare
from odoo import _

#import wdb

class RmaMoveSendToStockWizard(models.TransientModel):
    _name = "rma_move_send_to_stock_wizard"
    _description = "RMA move_send_to_stock Wizard"

    # partner_id, picking_type_id, location_id, location_dest_id
    # Qbtenemos el picking type de transferencia interna
    def _get_default_picking_type_id(self):
        #wdb.set_trace()
        company_id = self.env.context.get("company_id") or self.env.user.company_id.id
        return (
            self.env["stock.picking.type"]
            .search(
                [
                    ("code", "=", "internal"),
                    ("warehouse_id.company_id", "=", company_id),
                ],
                limit=1,
            )
            .id
        )

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Cliente", required=True
    )

    origin = fields.Char(
        'Source Document', 
        help="Reference of the document"
        )

    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type", default=_get_default_picking_type_id
        )

    picking_type_code = fields.Selection(
        related='picking_type_id.code',
        )

    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        )   

    location_id = fields.Many2one(
        'stock.location', "Source Location",
        required=True,
        )

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        required=True,
        )

    product_id = fields.Many2one(
        comodel_name="product.product",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits="Product Unit of Measure",
    )
    product_uom = fields.Many2one(
        comodel_name="uom.uom",
        string="UoM",
        required=True,
    )
    #procurement_group_id = fields.Many2one(
    #    comodel_name="procurement.group",
    #)

    # Metodos complentarios
    # Añadimos la logica de negocio de retorno de pieza a proveedor
    # Returning business methods
    # Retorno o enio de la pieza en devolucion o garantia al proveedor

    def _create_picking(self):
       #wdb.set_trace()
        return self.env["stock.picking"].sudo().create(
            {
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.location_id.id,
                "location_dest_id": self.location_dest_id.id,
            }
        )

    def _create_moves(self, picking):
        #wdb.set_trace()
        self.ensure_one()
        moveline = {
            "name": self.product_id.name,
            "location_id": self.location_id.id,
            "location_dest_id": self.location_dest_id.id,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom.id,
            "product_uom_qty": self.product_uom_qty,
            "picking_id": picking.id,
            #"location_move": True,
        }
        move = self.env["stock.move"].sudo().create(moveline)
        return move

    def _get_picking_action(self, picking_id):
        #wdb.set_trace()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        form_view = self.env.ref("stock.view_picking_form").id
        action.update(
            {"view_mode": "form", "views": [(form_view, "form")], "res_id": picking_id}
        )
        return action

    def create_transfer_stock(self):
        # Obtenemos el objeto que llama al wizard
       #wdb.set_trace()
        parent = self.env[self.env.context.get('active_model')].search(
                [
                    ("id", "=", self.env.context.get('active_id')),
                ],
                limit=1,
            )
        
        self.ensure_one()
        picking = self._create_picking()
        move = self._create_moves(picking)
        picking.action_confirm()
        picking.action_assign()
        self.picking_id = picking
        if self.picking_id:
            parent.last_move_id = move
            picking.with_context(skip_immediate=True).button_validate()
        return self._get_picking_action(picking.id)



class Rma(models.Model):
    _inherit = 'rma'
    # Envio de la pieza a stock
    def action_view_move_send_to_stock(self):
        """Invoked when a user wants to manually finalize the RMA"""
       #wdb.set_trace()
        self.ensure_one()
        #self._ensure_can_be_returned()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        action = self.env["ir.actions.actions"]._for_xml_id("q2_rma.rma_move_send_to_stock_wizard_action")
        #scraps = self.env['stock.scrap'].search([('picking_id', '=', self.scrap_move_id.picking_id.id)])
        #action['domain'] = [('id', 'in', scraps.ids)]
        #action.with_context(active_id=self.id)
        #action['context'] = dict(self._context, create=False)
        action["context"] = {
            "default_partner_id": self.partner_id.id,
            "default_origin": self.name,
            "default_location_id": self.last_move_id.location_dest_id.id,
            "default_product_id": self.product_id.id,
            "default_product_uom_qty": self.product_uom_qty,
            "default_product_uom": self.product_uom.id,
        }

        #wdb.set_trace()
        return action

