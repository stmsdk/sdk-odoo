# -*- coding: utf-8 -*-
# from odoo import http


# class Q2Rma(http.Controller):
#     @http.route('/q2_rma/q2_rma/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_rma/q2_rma/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_rma.listing', {
#             'root': '/q2_rma/q2_rma',
#             'objects': http.request.env['q2_rma.q2_rma'].search([]),
#         })

#     @http.route('/q2_rma/q2_rma/objects/<model("q2_rma.q2_rma"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_rma.object', {
#             'object': obj
#         })
