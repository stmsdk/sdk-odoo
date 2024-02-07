# -*- coding: utf-8 -*-
# from odoo import http


# class Q2PartnerFilterCreate(http.Controller):
#     @http.route('/q2_partner_filter_create/q2_partner_filter_create/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/q2_partner_filter_create/q2_partner_filter_create/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('q2_partner_filter_create.listing', {
#             'root': '/q2_partner_filter_create/q2_partner_filter_create',
#             'objects': http.request.env['q2_partner_filter_create.q2_partner_filter_create'].search([]),
#         })

#     @http.route('/q2_partner_filter_create/q2_partner_filter_create/objects/<model("q2_partner_filter_create.q2_partner_filter_create"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('q2_partner_filter_create.object', {
#             'object': obj
#         })
