# -*- coding: utf-8 -*-
from unicodedata import decimal
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class ResUser(models.Model):
	_inherit = "res.user"

	###################################################################################################
	# PARAMETROS CONFIGURABLES DEL COMERCIAL
	# Porcentaje de ocupacion laboral en venta, a partir del cual se calculan los costes de empresa
	# A los comerciales puros se les aplicara el 100%
	q2_comercial_working_time = fields.Float(default=0.0, editable=True)
	# Margen de operacion mínimo (por debajo de este margen requiere de confirmación y justificacion de la reduccion) se convierte en margen negativo, salvo autorizacion.
	q2_comercial_so_margin_min = fields.Float(default=0.20, editable=True, string='Margen minimo por operacion')
	# Margen de mínimo medio, marca el limite de alerta, a diferencia del anterior este es sobre la media y solo informa de la desviacion.
	q2_comercial_margin_av_min = fields.Float(default=0.25, editable=True, string='Margen minimo medio')
	# Margen bruto total objetivo, el margen bruto a alcanzar para cubrir los costes de empresa
	q2_comercial_margin_amount_target = fields.Monetary(default=0, string='Margen total bruto objetivo')
	# Coste de empresa del comercial, a descontar del importe total de comisiones para ajustar el importe mensual
	q2_comercial_cost_amount = fields.Monetary(default=0, string='Total coste empresa')
	# Total pagos realizados a cuenta
	q2_comercial_payments_amount = fields.Monetary(default=0, string='Total pagos realizados a cuenta')
	
	###################################################################################################
	# ESTADISTICAS SOBRE ORDENES DE CLIENTES ASIGNADOS
	# Notiene porque coincidir el numero de ordenes de colientes asignados con las de ordenes atendidas
	# Ordenes abiertas
	q2_so_open = fields.Integer(default=0, string='Nº ordenes abiertas')
	# Ordenes vendidas
	q2_so_sales = fields.Integer(default=0, string='Nº ordenes cerradas')
	# Ordenes devueltas
	q2_so_rma = fields.Integer(default=0, string='Nº ordenes devueltas')
	# Ordenes perdidas
	q2_so_loss = fields.Integer(default=0, string='Nº ordenes perdidas')
	# Importe operaciones abiertas
	q2_so_amount_open = fields.Monetary(default=0, string='Importe ordenes abiertas')
	# Importe operaciones cerradas
	q2_so_amount_sales = fields.Monetary(default=0, string='Importe ordenes vendidas')
	# Importe operaciones devueltas
	q2_so_amount_rma = fields.Monetary(default=0, string='Importe ordenes devueltas')
	# Importe operaciones perdidas
	q2_so_amount_loss = fields.Monetary(default=0, string='Importe ordenes perdidas')
	# Fecha de ultimo calculo de ventas
	q2_so_calculate_last_update = fields.Datetime(
        string="Last Stage Update", default=fields.Datetime.now
    )

	###################################################################################################
	# DESGLOSE DE MARGENES PARCIALES BRUTOS
	# Ordenes presupuestadas 
	q2_so_budget_open = fields.Integer(default=0, string='Nº ordenes abiertas')
	# Comision bruta por ordenes presupuestadas
	q2_so_budget_open_profit_amount = fields.Monetary(default=0, string='Margen total bruto presupuestado')
	
	# Ordenes confimadas  
	q2_so_sales = fields.Integer(default=0, string='Nº ordenes confirmadas')
	# Comision bruta por ordenes confirmadas
	q2_so_sales_profit_amount = fields.Monetary(default=0, string='Margen total bruto por ordenes confirmadas')

	# Ordenes de compra asociadas a la venta confimadas (Incluye el pedido al proveedor y el registro en odoo con su precio y nº de albaran si fuese posible) 
	q2_so_purchase = fields.Integer(default=0, string='Nº ordenes de compra gestionadas')
	# Margen total bruto por ordenes de compra gestionadas
	q2_so_purchase_profit_amount = fields.Monetary(default=0, string='Margen total bruto por ordenes de compra gestionadas')

	# Ordenes Consultas respondidas
	q2_so_ask = fields.Integer(default=0, string='Nº Consultas resueltas')
	# Margen total bruto por ordenes de compra gestionadas
	q2_so_ask_profit_amount = fields.Monetary(default=0, string='Margen total bruto por consultas resueltas')

	# Devoluciones realizadas que afectan a las comisiones del comercial
	q2_so_rma = fields.Integer(default=0, string='Nº ordenes devueltas')
	# Perdida total bruto por ordenes devueltas
	q2_so_rma_loss_amount = fields.Monetary(default=0, string='Perdida total bruto por ordenes devueltas')

	# Comision por gestion de cartera (comisión de aquellos clientes asignados )
	q2_so_partner_manager_profit_amount = fields.Monetary(default=0, string='Margen total bruto por gestion de clientes')
	# Comision por captacion de cartera (comisión de aquellos clientes nuevos captados )
	q2_so_partner_owner_profit_amount = fields.Monetary(default=0, string='Margen total bruto por clientes captados')


	###################################################################################################
	# CALCULO DE MARGENES Y COMISIONES
	# Ratio Margen Medio de Ventas => (PV-PC)/PV = Margen % 
	q2_so_margin_trade_ratio = fields.Float(default=0, string='Ratio Margen medio de ventas')
	# Margen total bruto base generado sobre ordenes confirmadas de la cartera asignada
	q2_so_margin_total_amount = fields.Monetary(default=0, string='Margen total bruto generado')
	# Importe total por comisiones acumuladas para el comercial
	q2_comercial_profit_amount = fields.Monetary(default=0, string='Total devengado por comisiones acumuladas')
	# Ratio de cumplimiento del objetivo
	q2_comercial_ratio_target = fields.Float(default=0, editable=True, string='Ratio de cumplimiento de objetivo')

	#funcion que podremos llamar desde fuera en la que se le pasa la orden de venta y se calculan todas las estadísticas
	def calculate_statics(self, so):
		pass

	#funcion que podremos llamar desde fuera en la que se le pasa la orden de venta y se calculan todas las estadísticas
	def recalculate_statics(self, so):
		pass
