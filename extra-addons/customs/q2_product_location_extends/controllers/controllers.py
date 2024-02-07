# -*- coding: utf-8 -*-
# from odoo import http


# class Q2ProductLocationExtends(http.Controller):
#     @http.route('/q2_product_location_extends/q2_product_location_extends/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_product_location_extends/q2_product_location_extends/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_product_location_extends.listing', {
#             'root': '/q2_product_location_extends/q2_product_location_extends',
#             'objects': http.request.env['q2_product_location_extends.q2_product_location_extends'].search([]),
#         })

#     @http.route('/q2_product_location_extends/q2_product_location_extends/objects/<model("q2_product_location_extends.q2_product_location_extends"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_product_location_extends.object', {
#             'object': obj
#         })
