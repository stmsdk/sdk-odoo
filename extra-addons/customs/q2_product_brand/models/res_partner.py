from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    q2_brand_id = fields.Many2one('q2_product_brand.product_brand',string='Fabricante')

