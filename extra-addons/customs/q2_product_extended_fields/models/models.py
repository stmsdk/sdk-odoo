# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tools.translate import html_translate

#import wdb

class ProductTemplate(models.Model):

    _inherit = "product.template"

    q2_ref_catalog = fields.Char(
        "Referencia de catalogo",
        index=True
    )
    q2_ref_brand_long = fields.Char(
        "Ref. fabricante larga",
        index=True
    )
    q2_ref_brand_short = fields.Char(
        "Ref. fabricante corta",
        index=True
    )
    q2_ref_equivalents = fields.Text(
        "Referencias equivalentes",
        index=True
    )
    q2_ref_originals = fields.Text(
        "Referencias originales",
        index=True
    )
    q2_dimensions = fields.Char(
        "Dimensiones",
        index=False
    )
    q2_models_compatible = fields.Char(
        "Modelos compatibles",
        index=True
    )

    q2_models_compatible_html = fields.Html(
        "Modelos compatibles web",
        sanitize_attributes=False,
        translate=html_translate,
        copy=False,
        index=False
    )
    q2_brand = fields.Many2one('q2_product_brand.product_brand', string='Fabricante')

    """
	@api.model
    def _search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])

        if name :
            args = [
                    '|','|','|','|','|','|','|',
                    ('default_code', operator, name),
                    ('q2_ref_catalog', operator, name),
                    ('q2_ref_brand_long', operator, name),
                    ('q2_ref_brand_short', operator, name),
                    ('q2_ref_equivalents', operator, name),
                    ('q2_ref_originals', operator, name),
                    ('q2_models_compatible', operator, name),
                    ('name', operator, name)
                    ]+ args
            raise ValidationError(args)
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
    
	"""
    