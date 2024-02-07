# -*- coding: utf-8 -*-
# from odoo import http


# class Q2ProductBrand(http.Controller):
#     @http.route('/q2_product_brand/q2_product_brand/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_product_brand/q2_product_brand/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_product_brand.listing', {
#             'root': '/q2_product_brand/q2_product_brand',
#             'objects': http.request.env['q2_product_brand.q2_product_brand'].search([]),
#         })

#     @http.route('/q2_product_brand/q2_product_brand/objects/<model("q2_product_brand.q2_product_brand"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_product_brand.object', {
#             'object': obj
#         })
