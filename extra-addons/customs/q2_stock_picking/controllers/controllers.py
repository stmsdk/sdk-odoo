# -*- coding: utf-8 -*-
# from odoo import http


# class Q2StockPicking(http.Controller):
#     @http.route('/q2_stock_picking/q2_stock_picking/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_stock_picking/q2_stock_picking/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_stock_picking.listing', {
#             'root': '/q2_stock_picking/q2_stock_picking',
#             'objects': http.request.env['q2_stock_picking.q2_stock_picking'].search([]),
#         })

#     @http.route('/q2_stock_picking/q2_stock_picking/objects/<model("q2_stock_picking.q2_stock_picking"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_stock_picking.object', {
#             'object': obj
#         })
