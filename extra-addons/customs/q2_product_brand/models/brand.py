# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_brand(models.Model):
    _name = 'q2_product_brand.product_brand'
    _description = 'Módulo de gestion de marcas de productos'
    # Por defecto en los usa el campo name para mostrarlo en todos los many2one, pero cuando no hay campo name como en este caso 
    # Tenemos que declarar que campo tiene que cojer o se mostrara el id
    _rec_name = 'q2_name_brand'
    
    q2_name_brand = fields.Char(string="Marca")
    q2_name_maker = fields.Char(string="Fabricante")
    q2_code = fields.Char(string="Código")
    q2_image = fields.Image()
    q2_supplier_base_discount = fields.Float(string="Descuento base sobre PVP", default=50.00)
    #q2_partner_ids= fields.One2many(comodel_name='res.partner', inverse_name='q2_brand_id', string='Proveedores')
    # un partner preferente por fabricante
    q2_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor preferente",
        copy=False,
        tracking=True,
    )

    """
    # Otra forma es sobreescribiendo el metodo name_get que es el que usaremos en este caso
    @api.depends('q2_name_brand', 'q2_code')
    def name_get(self):
        result = []
        for r in self:
            if r.q2_code: 
                if r.q2_name_brand:
                    name = '{}-{}'.format(r.q2_code,r.q2_name_brand)
                    result.append((r.id, name))
        return result
    """