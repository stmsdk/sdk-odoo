# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime
from datetime import date
from datetime import timedelta
import re
import pytz
#import wdb #wdb.set_trace()

class q2_WorkshopService(models.Model):
    _inherit = 'sale.order'
    _description = 'Extensión de campos dentro de sale para la gestion de flujos de procesos del servicio técnico'
    """
    q2_ws_status_items = [
        ('waitin'  ,'EED Recepción'),           #'En espera de recepcionar la pieza'
        ('waitcom'  ,'EED Acción comercial'),   #'En espera de accion comercial'
        ('waitcfm'  ,'EED Confirmación'),       #'En espera de confirmacién'
        ('waitmt'   ,'EED Material'),           #'En espera de material'
        ('stin'     ,'ST Entrada'),             #'Entrada al servicio técnico'
        ('stwait'   ,'ST En espera'),           #'En espera de turno en taller'
        ('strun'    ,'ST En proceso'),          #'En ejecución'
        ('stout'    ,'ST Salida'),              #'Salida de taller'
        ('stend'    ,'ST Finalizado'),          #'Finalizado'
        ]
    """
    def _get_items_selection_ws_status(self):
       #wdb.set_trace()
        qry_items = self.env['q2_workshop.stage'].search([('active','=',True)])
        choise = []
        if qry_items:
            for qi in qry_items:
                obj = self.env['q2_workshop.stage'].browse(qi.id)
                choise.append((str(obj.code), str(obj.name)))
        return choise

    q2_ws_status = fields.Selection(selection= _get_items_selection_ws_status,
        string="Estado Taller" ,
        default="",
        copy=False,
        tracking=True,
    )
    q2_is_ws = fields.Boolean(
        string="Es servicio taller",
        copy=False,
        default=False,
    )

    q2_ws_id = fields.Many2one(
        comodel_name="q2_workshop",
        string="Orden de taller",
    )



    #     value2 = fields.Float(compute="_value_pc", store=True)
    #     description = fields.Text()
    #
    #     @api.depends('value' #wdb.set_trace)
    #     def _value_pc(self):
    #         for record in self:
    #             record.value2 = float(record.value) / 100

    #@api.onchange('q2_is_ws')
    def checked_is_ws(self):
       #wdb.set_trace()
        # Eliminamos la etiqueta de taller antes de incluirla por si se ha metido anteriormente ya sea manual o por boton
        str_del_taller =""
        if  self.client_order_ref:
            pattern = re.compile("TALLER", re.IGNORECASE)
            str_del_taller = pattern.sub("", self.client_order_ref)
        if not self.q2_is_ws:
            #wdb.set_trace()
            # Si es Taller incluimos la etiqueta Taller
            client_order_ref = "TALLER {}".format(str_del_taller)
            ws_status = 'waitcom'
            self.sudo().write({
                "client_order_ref" : client_order_ref,
                "q2_is_ws" : True,
                "q2_ws_status" : ws_status,
            })
            self.create_update('waitcom')  
        else:
            #wdb.set_trace()
            client_order_ref = str_del_taller
            ws_status = ''
            # Actualizamos el valor
            self.sudo().write({
                "client_order_ref" : client_order_ref,
                "q2_is_ws" : False,
                "q2_ws_status" : ws_status,
            })

    # Accions de visualizacion
    def action_view_workshop(self):
        #wdb.set_trace()
        """This function returns an action that display existing workshop order
        of given sale.
        """
        self.ensure_one()
        # Remove default_picking_id to avoid defaults get
        # https://github.com/odoo/odoo/blob/e4d22d390c8aa8edf757e36704a9e04b2b89f115/
        # addons/stock/models/stock_move.py#L410
        ctx = self.env.context.copy()
        #ctx.pop("default_rma_id", False)
        if self.q2_ws_id:
            return self.with_context(ctx).q2_ws_id.get_formview_action()
        return

    # Confirmación del pedido inicial por el cliente
    # Le daremos entrada en el taller siguiendo las indicaciones del comercial previa comunicacion con el cliente
    def action_confirm(self):
        #wdb.set_trace()
        res = super(q2_WorkshopService, self).action_confirm()
        #wdb.set_trace()
        if self.q2_is_ws:
            self.action_st_in()         
        return res
    # Cuando desde el taller se determina que la verificacion ha descubierto un incidente mayor del presupuestado
    def action_eed_commercial(self):
        #wdb.set_trace()
        self.create_update('waitcom')   

    # accion comercial realizada
    def action_eed_commercial_done(self):
        #wdb.set_trace()
        self.action_eed_customer() 

    # Se lo comunicarña al comercial para que contacte con el cliente y le informe y adapte el ppto
    def action_eed_customer(self):
        #wdb.set_trace()
        self.create_update('waitcfm')

    # accion comercial realizada
    def action_eed_customer_done(self):
        #wdb.set_trace()
        if self.state in ['draft']:
            self.action_confirm()
        else:
            self.action_st_in()

    # Entrada en taller
    def action_st_in(self):
        #wdb.set_trace()
        self.create_update('stin')
    
    #def create(self,vals):
        #wdb.set_trace()
        #res = super(q2_WorkshopService, self).create(vals)
        #if self.q2_is_ws:
        #    res.create_update('waitcom')
        #return res

    def create_update(self,stage_code=None):
        #wdb.set_trace()
        if stage_code:
            self.sudo().write({
                "q2_ws_status" : stage_code,
            })
        # Verificamos si ya esta dado de alta el servicio en pantalla taller
        st = self.env['q2_workshop'].search([('origin','=',self.name)])
        # Obtenemos la etapa en la que se encuentra
        stage = self.env['q2_workshop.stage'].search([('code','=',stage_code)])
        # Si no existe lo creamos
        if not st:
            vals = {
                'name':'{} >> {}'.format(self.partner_id.name, self.client_order_ref),
                'user_id':self.user_id.id,
                'origin':self.name,
                'sale_id':self._origin.id,
                'stage_id': stage.id,
            }
           #wdb.set_trace()
            # Creamos la rden de taller
            new_st = self.env['q2_workshop'].sudo().create(vals)
            # le asignamos la nueva orden de taller a la venta
            self.sudo().write({
                'q2_ws_id':new_st.id
            })
        else:
            # Si existe lo actualizamos el stage de taller
            for s in st:
                # Verificamos si laventa tiene orden de taller
                # Si no tiene Orden de taller se la asignamos
                if not self.q2_ws_id:
                    self.sudo().write({
                        'q2_ws_id':s.id
                    })
                # Actualizamos el stage de la orden de taller
                vals = {
                    'stage_id': stage.id,
                }
                s.sudo().write(vals)       
    