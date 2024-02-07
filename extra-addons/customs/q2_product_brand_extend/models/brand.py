# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_brand(models.Model):
    _inherit = 'q2_product_brand.product_brand'

    q2_partner_id= fields.Many2one('res.partner', string='Proveedor pref.')

