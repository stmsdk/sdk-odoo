# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare
#import wdb

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    def send_to_scrap(self, move, origin):
        #wdb.set_trace()
        self.ensure_one()
        # Pasamos los valores necesarios para realizar el desechado stock.scrap

        if self.product_id.type != 'product':
            #wdb.set_trace()
            return self.do_scrap()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        #wdb.set_trace()
        available_qty = sum(self.env['stock.quant']._gather(self.product_id,
                                                            self.location_id,
                                                            self.lot_id,
                                                            self.package_id,
                                                            self.owner_id,
                                                            strict=True).mapped('quantity'))
        scrap_qty = self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id)
        if float_compare(available_qty, scrap_qty, precision_digits=precision) >= 0:
            #wdb.set_trace()
            return self.do_scrap()

        else:
            #wdb.set_trace()
            ctx = dict(self.env.context)
            ctx.update({
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_scrap_id': self.id,
                'default_quantity': scrap_qty,
                'default_product_uom_name': self.product_id.uom_name
            })
            # Actualizamos move objeto del desecho poniendo en true el campo scrapped

            return {
                'name': self.product_id.display_name + _(': Insufficient Quantity To Scrap'),
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
