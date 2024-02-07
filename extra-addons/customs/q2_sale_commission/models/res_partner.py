# -*- coding: utf-8 -*-
from unicodedata import decimal
from odoo.exceptions import ValidationError
from odoo import models, fields, api


class ResPartner(models.Model):
	_inherit = "res.partner"

	# OBJETIVOS DE VENTAS
	# Ventas objetivo
	q2_so_amount_target = fields.Monetary(default=0, string='Objetivo de ventas año actual')
	# Desviacion objetivo
	q2_so_desviation_target = fields.Integer(default=0, string='Desviacion de ventas objetivo')

	# Marcaremos si es agente externo
	# Diferenciaremos entre agente (personal externo que facilita el contacto) y comercial (personal interno que gestiona al cliente)
	# Tendremos en cuenta que sale_commision ya se contempla los agentes y los comerciales
	# q2_account_manager = fields.Many2one(
        'res.users', string='Comercial asignado', index=True, tracking=2, default=None,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
	),)
	# Ordenes abiertas 
	q2_so_open = fields.Integer(default=0, string='Nº ordenes abiertas')
	# Ordenes vendidas
	q2_so_closed = fields.Integer(default=0, string='Nº ordenes cerradas')
	# Ordenes devueltas
	q2_so_rma = fields.Integer(default=0, string='Nº ordenes devueltas')
	# Ordenes perdidas
	q2_so_loss = fields.Integer(default=0, string='Nº ordenes perdidas')
	# Importe operaciones abiertas
	q2_so_amount_open = fields.Monetary(default=0, string='Importe ordenes abiertas')
	# Importe operaciones vendidas
	q2_so_amount_closed = fields.Monetary(default=0, string='Importe ordenes cerradas')
	# Importe operaciones devueltas
	q2_so_amount_rma = fields.Monetary(default=0, string='Importe ordenes devueltas')
	# Importe operaciones perdidas
	q2_so_amount_loss = fields.Monetary(default=0, string='Importe ordenes perdidas')
	# Vantas ultimo año
	q2_so_amount_last_year = fields.Monetary(default=0, string='Ventas año anterior')
	# Desviacion ultimo año
	q2_so_loss = fields.Integer(default=0, string='Nº ordenes perdidas')

	#funcion que podremos llamar desde fuera en la que se le pasa la orden de venta y se calculan todas las estadísticas
	def calculate_statics(self, so):
		pass

	#funcion que podremos llamar desde fuera en la que se le pasa la orden de venta y se calculan todas las estadísticas
	def recalculate_statics(self, so):
		pass

	def calculate_desviation_target(self, so):
		pass

