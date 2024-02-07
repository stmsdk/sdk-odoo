# -*- coding: utf-8 -*-
# from odoo import http


# class Q2PurchaseOrderExtends(http.Controller):
#     @http.route('/q2_purchase_order_extends/q2_purchase_order_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_purchase_order_extends/q2_purchase_order_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_purchase_order_extends.listing', {
#             'root': '/q2_purchase_order_extends/q2_purchase_order_extends',
#             'objects': http.request.env['q2_purchase_order_extends.q2_purchase_order_extends'].search([]),
#         })

#     @http.route('/q2_purchase_order_extends/q2_purchase_order_extends/objects/<model("q2_purchase_order_extends.q2_purchase_order_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_purchase_order_extends.object', {
#             'object': obj
#         })
