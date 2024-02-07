# -*- coding: utf-8 -*-
# from odoo import http


# class Q2SaleOrderExtendsViews(http.Controller):
#     @http.route('/q2_sale_order_extends_views/q2_sale_order_extends_views/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_sale_order_extends_views/q2_sale_order_extends_views/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_sale_order_extends_views.listing', {
#             'root': '/q2_sale_order_extends_views/q2_sale_order_extends_views',
#             'objects': http.request.env['q2_sale_order_extends_views.q2_sale_order_extends_views'].search([]),
#         })

#     @http.route('/q2_sale_order_extends_views/q2_sale_order_extends_views/objects/<model("q2_sale_order_extends_views.q2_sale_order_extends_views"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_sale_order_extends_views.object', {
#             'object': obj
#         })

#def my_route(self, named_param, **kw)
#     print named_param
#     print kw.get('another_param')