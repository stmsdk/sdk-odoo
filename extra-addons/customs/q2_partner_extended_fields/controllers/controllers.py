# -*- coding: utf-8 -*-
# from odoo import http


# class Q2ProductExtendedFields(http.Controller):
#     @http.route('/q2_partner_extended_fields/q2_partner_extended_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_partner_extended_fields/q2_partner_extended_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_partner_extended_fields.listing', {
#             'root': '/q2_partner_extended_fields/q2_partner_extended_fields',
#             'objects': http.request.env['q2_partner_extended_fields.q2_partner_extended_fields'].search([]),
#         })

#     @http.route('/q2_partner_extended_fields/q2_partner_extended_fields/objects/<model("q2_partner_extended_fields.q2_partner_extended_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_partner_extended_fields.object', {
#             'object': obj
#         })
