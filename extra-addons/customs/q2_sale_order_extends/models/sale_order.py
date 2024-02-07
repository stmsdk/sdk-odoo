# -*- coding: utf-8 -*-
from email.policy import default
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo import tools
from odoo.tools import float_compare


#import wdb ##wdb.set_trace().set_trace()

class q2_sale_order_extends(models.Model):
    _inherit = "sale.order"
    #wdb.set_trace()

    """
    status
            T   Taller > Preparar
            F   Directo Fabrica > Facturar
            I   Recepcionado > Preparar 
            P   Preparado > Entregar
            O   Entregado > Facturar
            F   Facturado > Fin
            D   Devolucion > Facturar
            G   Garantia > Preparar/Facturar

    picking_type_id	name
            1	    Receipts
            2	    Delivery Orders
            3	    Empaquetar
            5	    Internal Transfers
            6	    SEST Producción Entrada
            7	    SEST Producción Salida
            8	    SEST  Producción
            9   	Recepciones de RMA
            10	    Órdenes de entrega de RMA
            11  	Dropship
    """
    
    # Marcaremos los estados del pedido { 'directo','pendiente','preparado','entregado','devuelto','facturado'}
    # q2_sale_status_times = fields.datetime(string='Estado',  default= tools.datetime.now)
    q2_sale_status = fields.Selection(selection=[
        ('pendiente', 'PENDIENTE'),
        ('taller', 'SERVICIO TALLER'),
        ('comprar', 'PTE. COMPRA'),
        ('directo', 'ENVIO DIRECTO'),
        ('retirar', 'RETIRAR'),
        ('recepcionar', 'RECEPCIONAR'),
        ('preparar', 'PREPARAR'),
        ('entregar', 'ENTREGAR'),
        ('facturar', 'FACTURAR'),
        ('facturado', 'FACTURADO'), 
        ('no_facturar', 'NO FACTURAR'),
        ('devolver', 'DEVOLVER'),
        ('devuelto', 'DEVUELTO'),
        ('dev_rechazada', 'DEV. RECHAZADO'),
        ('rma_garantia', 'RMA GARANTIA'),
        ('rma_rechazada', 'RMA RECHAZADO'),
        ], 
        store=True,
        copy=False,
        default='',
        compute='checked_action',
        string='Estado Pedido')

    q2_sale_delivery = fields.Boolean(string='Entregado',default=False, store=True, copy=False)
    
    q2_sale_invoiced = fields.Boolean(string='Facturado',default=False, store=True, copy=False)

    #   Ampliamos la busqueda añadiendo la busqueda desde metodo incluyendo la busqueda por orden de linea
    #   <field name="name" string="Order" 
    #       filter_domain="['|','|','|',
    #           ('name', 'ilike', self),
    #           ('client_order_ref', 'ilike', self),
    #           ('partner_id', 'child_of', self),
    #           ('order_line', 'ilike', self)
    #       ]"
    #   />

    """
    # No funciona he probado varrios arreglos y da fallo cuando le añades una clausula
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        #wdb.set_trace()
        search_default_my_quotation = self.env.context['search_default_my_quotation']
        # Chequeamos si la busqueda proviene de sale_order
        if search_default_my_quotation == 1:
            if operator == 'ilike' and not (name or '').strip():
                domain = []
            elif operator in ('ilike', 'like', '=', '=like', '=ilike'):
                domain = expression.AND([
                    args or [],
                    ['|', ('name', operator, name), ('partner_id.name', operator, name)]
                ])
                return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return super(SaleOrder, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def _search(self, args, offset, limit, order='', count=True):
        search_default_my_quotation = self.env.context['search_default_my_quotation']
        domain = []
        # Chequeamos si la busqueda proviene de sale_order
        if search_default_my_quotation == 1:
            if len(args)>0:
                #wdb.set_trace()
                for a in args:
                    if type(a) is list or type(a) is tuple:
                        if a[0]=='name':
                            domain.append('|')
                            domain.append(['order_line', 'ilike', a[2]])
                        domain.append(a)
                    else:
                        domain.append(a)
            else:
                domain = args
        else:
            domain = args
        #wdb.set_trace()
        return super(q2_sale_order_extends, self)._search(args, offset, limit, order,count)
    """

    def _action_confirm(self):
        #wdb.set_trace()
        res = super(q2_sale_order_extends, self)._action_confirm()
        for obj in self:
            obj.checked_action()
        return res

    @api.depends('state', 'invoice_status','order_line.qty_delivered')
    def checked_action(self):
        #wdb.set_trace()
        #  1. Si no es una fabricacion verificamos:
        #  2. si tiene compra
        #       2.1. Si tiene envio directo 
        #       2.2. Si es una compra a recepcionar
        #  3. Si es un producto almacenado 
        for obj in self:
            mo = self.env['mrp.production'].search([('sale_id','=',obj.id)])
            po = self.env['purchase.order'].search([('origin','=',obj.name),('state','=','draft')])
            sp_assigned = self.env['stock.picking'].search([('sale_id','=',obj.id),('state','=','assigned')]) 
            if mo:
                obj.q2_sale_status = 'taller'
            
            elif po:
                obj.q2_sale_status = 'comprar'
        
            elif sp_assigned:
                if sp_assigned[0].picking_type_id == 11:
                    obj.q2_sale_status = 'directo'
                elif sp_assigned[0].picking_type_id == 1:
                    obj.q2_sale_status = 'recepcionar'
                elif sp_assigned[0].picking_type_id == 2:
                    obj.q2_sale_status = 'entregar'
                elif sp_assigned[0].picking_type_id == 3:
                    obj.q2_sale_status = 'preparar'
        
        #if self[0].invoice_status == 'invoiced':
        #    self.q2_sale_status = 'facturado'

        return

    def checked_production(self):
        #wdb.set_trace()
        for obj in self:
            obj.production()
            obj.q2_sale_status = 'preparar'
        return 

    def production(self):
        #wdb.set_trace()
        mo = self.env['mrp.production'].search([('sale_id','=',self.id)])
        if mo:
            return mo.button_mark_done()        
        return

    def checked_dropship(self):
        #wdb.set_trace()
        for obj in self:
            obj.dropship()
            obj.q2_sale_status = 'facturar'
        return

    def dropship(self):
        #wdb.set_trace()
        ds = self.env['stock.picking'].search([('sale_id','=',self.id),('state','=','assigned'),('picking_type_id','=',11)])
        if ds:
            return ds.validate_picking()
        return 

    def checked_receips(self):
        #wdb.set_trace()
        for obj in self:
            pin = obj.receips()
            tint = obj.receips_transfer_stock()
            obj.q2_sale_status = 'preparar'
        return 

    def receips(self):
        #wdb.set_trace()
        # Buscamos el picking de entrada
        pin = self.env['stock.picking'].search([('sale_id','=',self.id),('state','=','assigned'),('picking_type_id','=',1)])
        if pin:
            return pin.validate_picking()
        return 

    def receips_transfer_stock(self):
        #wdb.set_trace()
        tint = self.env['stock.picking'].search([('sale_id','=',self.id),('state','=','assigned'),('picking_type_id','=',5)])
        if tint:
            return tint.validate_picking()
        return 

    def checked_picking(self):
        #wdb.set_trace()
        for obj in self:
            obj.picking()
            obj.q2_sale_status = 'entregar'
        return 

    def picking(self):
        #wdb.set_trace()
        pick = self.env['stock.picking'].search([('sale_id','=',self.id),('state','=','assigned'),('picking_type_id','=',3)])
        if pick:
            return pick.validate_picking()
        return 

    def checked_delivery(self):
        #wdb.set_trace()
        # Solo cambiaremos de estado si  es usuario administrador
        for obj in self:
            obj.delivery()
            obj.q2_sale_status = 'facturar'
        return 

    def delivery(self):
        #wdb.set_trace()
        # Solo cambiaremos de estado si  es usuario administrador
        self.q2_sale_delivery =  not self.q2_sale_delivery
        pick = self.env['stock.picking'].search([('sale_id','=',self.id),('state','=','assigned'),('picking_type_id','=',2)])
        if pick:
            return pick.validate_picking()
        return 

    def checked_invoiced(self):
        #wdb.set_trace()
        # Solo cambiaremos de estado si  es usuario administrador
        #self.q2_sale_invoiced =  not self.q2_sale_invoiced
        #self.q2_sale_status = 'facturado'
        #self.q2_sale_status_times = tools.datetime.now
        return 

class StockPicking(models.Model):
    _inherit = "stock.picking"
    # Metodo que asigna al picking automaticamente las cantidades demandadas como realizasdas y procesa el movimiento
    def validate_picking(self):
        #wdb.set_trace()
        """Set quantities automatically and validate the pickings."""
        for picking in self:
            picking.action_assign()
            for move in picking.move_lines.filtered(
                lambda m: m.state not in ["done", "cancel"]
            ):
                rounding = move.product_id.uom_id.rounding
                if (
                    float_compare(
                        move.quantity_done,
                        move.product_qty,
                        precision_rounding=rounding,
                    )
                    < 0 # == -1
                ):
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
            picking.with_context(skip_immediate=True).button_validate()
        return True

    def _check_entire_pack(self):
        #wdb.set_trace()
        # Sobreescribimos el metodo create
        res = super(StockPicking,self)._check_entire_pack()
        for picking in self:
            if picking.state == 'assigned':
                # Dropship
                if picking.picking_type_id.id == 11:
                    picking.sale_id.update({'q2_sale_status':'directo'})
                # Compra
                if picking.picking_type_id.id == 1:
                    picking.sale_id.update({'q2_sale_status':'recepcionar'})
                # Preparar
                if picking.picking_type_id.id == 3:
                    picking.sale_id.update({'q2_sale_status':'preparar'})
                # Entregar
                if picking.picking_type_id.id == 2:
                    picking.sale_id.update({'q2_sale_status':'entregar'})

        return res

    #def _show_cancel_wizard(self):
    #    #wdb.set_trace()
    #    res = super(q2_sale_order_extends, self)._show_cancel_wizard()
    #    for obj in self:
    #        pick = self.env['stock.picking'].search([('sale_id','=',obj.id),('state','=','done'),('picking_type_id','=',2)])
    #        if pick:
    #            obj.with_context({'disable_cancel_warning':False})
    #    return res

