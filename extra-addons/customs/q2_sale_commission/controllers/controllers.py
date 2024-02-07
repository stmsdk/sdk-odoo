# -*- coding: utf-8 -*-
# from odoo import http


# class Q2SaleOrderAgent(http.Controller):
#     @http.route('/q2_sale_order_agent/q2_sale_order_agent/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_sale_order_agent/q2_sale_order_agent/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_sale_order_agent.listing', {
#             'root': '/q2_sale_order_agent/q2_sale_order_agent',
#             'objects': http.request.env['q2_sale_order_agent.q2_sale_order_agent'].search([]),
#         })

#     @http.route('/q2_sale_order_agent/q2_sale_order_agent/objects/<model("q2_sale_order_agent.q2_sale_order_agent"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_sale_order_agent.object', {
#             'object': obj
#         })
