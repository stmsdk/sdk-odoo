# -*- coding: utf-8 -*-

from odoo import models, fields, api


class q2_purchase_order_extends(models.Model):
    _name = 'q2_purchase_order_extends'
    _description = 'q2_purchase_order_extends'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
