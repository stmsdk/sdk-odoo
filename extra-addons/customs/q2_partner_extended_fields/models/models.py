# -*- coding: utf-8 -*-
from unicodedata import decimal
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class ResPartner(models.Model):
	_inherit = "res.partner"
 
	q2_partner_id = fields.Char(
        "ID",
        index=True,
    )
	q2_rmh_id = fields.Char(
        "RMH ID",
        index=True,
    )
	"""
	q2_ratio = fields.Float(
		string='Ratio', 
		required=False, 
		default=0.00,
	)
	"""
	# rmh_id
	# ref
	"""
	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100,name_get_uid=None):
		if args is None:
			args = args or []	
			recs = self.search([('partner_gid', operator, name)] + args, limit=limit)
			if recs.ids:
				return recs.name_get()

		return super(ResPartner, self).name_search(name=name, args=args,
												operator=operator,
												limit=limit)


	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		#Ampliamos la busqueda por defecto al campo de id_erp y de referencia
		args = args or []
		recs = self.search([('partner_gid', operator, name)] + args, limit=limit)
		if not recs.ids:
			return super(ResPartner, self).name_search(name=name, args=args,
													   operator=operator,
													   limit=limit)
		return recs.name_get()
	"""
