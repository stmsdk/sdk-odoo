
# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
#import wdb

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rma_id = fields.Many2one(
        comodel_name="rma",
        string="RMA",
    )
    refund_origin = fields.Char(string='Refund', readonly=True, tracking=True,
        help="The document(s) that generated the RMA.")