# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RmaOperation(models.Model):
    _inherit = "rma.operation"

    type = fields.Selection([
        #('is_replace','Reemplazar'),
        ('is_warranty','Garantía'),
        ('is_refund','Devolucion'),
    ],
    default = None,
    copy=False,
    )
