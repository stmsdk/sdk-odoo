# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tools.translate import html_translate

#import wdb #wdb.set_trace()

class ProductTemplate(models.Model):

    _inherit = "product.template"


    q2_product_default_location = fields.Char(
        "Ubicación preferente",
        index=True
    )

    #q2_product_default_location = fields.Char('Ubi', related='product_id.q2_product_default_location', store=True)
    q2_product_stock_ubi_qty = fields.Char('stock_ubi_qty', compute="_compute_get_stock_qty" ) #related='product_id.q2_product_default_location', store=True)
    q2_product_stock_qty = fields.Float('stock_qty', compute="_compute_get_stock_qty")

    def _compute_get_stock_qty(self):
        # first execute the query
        #wdb.set_trace()
        for r in self:
            if r.id:
                data = ''
                onhand = 0.0
                pid = r.id
                query = """
                    select ubi, und from public.stm_stock_a02_a10_full_location where product_tmpl_id = %s 
                """ 
                prm = (pid,)   

                self._cr.execute(query, prm)
                # fetc rows
                result = self._cr.fetchall()
                for c in result:
                    if c[1]>0:
                        #wdb.set_trace()
                        onhand += c[1]
                    data += c[0] + "["+ str(c[1]) +"] "
                r.q2_product_stock_ubi_qty = data      
                r.q2_product_stock_qty = onhand  
          


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #q2_product_default_location = fields.Char('Ubi', related='product_id.q2_product_default_location', store=True)
    q2_product_default_location = fields.Char('Ubi', compute="_compute_get_last_product_location" ) #related='product_id.q2_product_default_location', store=True)

    @api.depends('product_id')
    def _compute_get_last_product_location(self):
        # first execute the query
        self.q2_product_default_location = '' # en caso de no tener linias iniciamos el valor
        #wdb.set_trace()
        if self.product_id:
            data = ''
            for sol in self:
                p = sol.product_id 
                if p.id:
                    pid = p.id
                    query = """
                        select  
                            sl.name
                        from stock_move as sm
                            inner join stock_location as sl on sl.id=sm.location_dest_id 
                        where sm.product_id = %s
                            and sl.corridor in ('A02','A10') and state ='done' order by sm.id desc
                        limit 1
                        """ 
                    prm = (pid,)   

                    self._cr.execute(query, prm)
                    # fetc rows
                    data = self._cr.fetchone()
                    if data:
                        data = data[0]
                        sol.q2_product_default_location = data       

class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    q2_product_default_location = fields.Char('Ubi', related='product_id.q2_product_default_location', store=True)
