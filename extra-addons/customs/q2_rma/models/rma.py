# -*- coding: utf-8 -*-
"""
# Insercion de valores en celda Type de la tabla  rma_operation
Update rma_operation set type='is_replace' 	where name = 'Replace';
Update rma_operation set type='is_warranty' where name = 'Repair';
Update rma_operation set type='is_refund' 	where name = 'Refund';
SELECT * FROM public.rma_operation ORDER BY id ASC 
"""

from collections import Counter
from email.policy import default
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tests import Form
from odoo import tools
from odoo.tools import float_compare
from odoo import _


import wdb ##wdb.set_trace()

class Rma(models.Model):
    _inherit = "rma"
    
    state_process =fields.Selection(
        [
            ("draft", "Petición"),              # El cliente solicita la devolución o reembolso por garantia
            ("reception", "Recepción"),         # El producto objeto de la devolución o garantia es recepcionado por Soterma
            ("validation", "Validación"),       # Valoramos si la devolución se ajust a los criterios marcados que permiten su devolución o garantía
            ("resolution", "Resolución"),       # Se dicta una resolución tócnica 
            ("negotiation", "Negociación"),     # Se negocia con el cliente la resolucion con el indicamos que es lo que vamos a hacer ,rechazar, reemplazar, reparar o abonar
            ("solution", "Solución"),           # Una vez negociada se procede con la solucion, rearar, reemplazar o abonar o nada si es rechazada           
            ("location", "Destino pieza"),      # Una vez solucionado el rma se             
            ("finished", "Finalización"),       # Una vez se entrega la pieza rechaza o remplazada, o se reembolsa el producto, se da por finalizado el RMA.
        ],
        string="Procesos del RMA", 
        default="draft",
        copy=False,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            # Recepción de RMA (reception)
            ("confirmed", "Confirmed"),
            ("received", "Received"),
            # Validación  (validate)
            ("validation_waiting", "Pendiente de validación técnica"),
            ("validation_internal", "Validacion Interna"),
            ("validation_external", "Validacion Externa"),
            ("validation_supplier", "Validacion Proveedor"),
            # Resolucion técnica (resolution)
            ("resolution_waiting", "Pendiente de resolución"),
            ("resolution_accepted", "Resolución técnica Aceptada"),
            ("resolution_rejected",   "Resolución técnica Rechazada"),            
            # Negociación de solucién al cliente (negotiation)
            ("negotiation_waiting", "Pendiente de negociación"),
            ("negotiation_accepted_to_repair", "Aceptada para reparar"),
            ("negotiation_accepted_to_replace", "Aceptada para reemplazar"),
            ("negotiation_accepted_to_refund", "Aceptada para abonar"),
            ("negotiation_rejected", "Rechazada "),            
            # Solución (solution)
            ("solution_waiting_repair", "Esperando reemplazar/reparar la pieza al cliente"),
            ("solution_repaired", "Reemplazada/reparada la pieza al cliente"),
            ("solution_waiting_replace", "Esperando reemplazar/reparar la pieza al cliente"),
            ("solution_replaced", "Reemplazada/reparada la pieza al cliente"),
            ("solution_waiting_refund", "Esperando reembolso"),
            ("solution_refunded", "Reembolsado"),
            # Destion (location)
            ("waiting_return_to_customer", "Esperando retornar pieza sustituida, reparada o rechazada al cliente"),
            ("returned_to_customer", "Retornada la pieza al cliente"),
            ("in_stock", "Enviada a stock"),
            ("in_scrap", "Enviada a chatarra"),
            ("scrapped", "Chatarreada"),
            # Cierre (finalitation)
            ("finished", "finished"),
            ("locked", "Locked"),
            ("cancelled", "Canceled"),
        ],
        string="Estado del RMA", 
        default="draft",
        copy=False,
        tracking=True,
    )
    # 'sent_to_external','sent_to_supplier','send_to_customer','scrapped'
    # Estado que traza donde se encuentra la pieza en cada momento
    state_product = fields.Selection(
        [
            ("nothing","Sin procesar"),     # Esperando la recepcion una vez se ha confirmado el RMA en action_confirm()
            # Recepción de RMA desde cliente
            ("waiting_reception","Esperando recepción"), # Esperando la recepcion una vez se ha confirmado el RMA en action_confirm()
            ("received","Recibido"), # El producto del RMA ha sido recpcionado
            ("remote","Gestion de RMA no hay recepción"),  # El producto del RMA se queda en las instalaciones del cliente pero se gestion el RMA mediante fotos  y videos
            # Validation
            ("waiting_validation","Esperando valoracion"), # Esperando a que la pieza sea analizada por personal interno
            # Validation interna
            ("waiting_check_internal","Esperando chequeo interno"), # Esperando a que la pieza sea analizada por personal interno
            ("checked_internal","Chequeado por personal interno"),
            # Validation Externa
            ("waiting_send_to_external","Esperando envio al Servicio Externo"), # Esperando el el envio a un externo de la mercancia
            ("sent_to_external","Enviado al Servicio Externo"),
            ("waiting_receive_from_external","Esperando recepción desde el Servicio Externo"),
            ("received_from_external","Recibido desde el Servicio Externo"),
            ("scrapped_from_external","Desechado por el Servicio Externo"),
            # Validation Proveedor
            ("waiting_send_to_supplier","Esperando envio a proveedor"),
            ("sent_to_supplier","Enviado a proveedor"),
            ("waiting_receive_from_supplier","Esperando recepción desde proveedor"),
            ("received_from_supplier","Recibido desde proveedor"),
            ("scrapped_from_supplier","Desechado por el proveedor"),
            # resolution
            ("waiting_resolution", "Pendiente de resolución"),
            # negotiation
            ("waiting_negotiation", "Pendiente de negociación"),
            # Solucion
            # Solucion Reparar
            ("waiting_send_to_repair","Esperando envio a reparar"),
            ("sent_to_repair","Enviado a reparar"),
            ("received_repaired","Recibido reparado"),
            # Solucion Reemplazar
            ("waiting_request_to_replace","Esperando solicitar reemplazo"),
            ("requested_to_replace","Solicitado reemplazo"),
            ("receive_repaired","Recibido remplazo"),
            # Destino
            # Destino Envio de pieza al cliente
            ("waiting_location","Esperando destino"),
            ("waiting_send_to_customer","Esperando envio a cliente"),
            ("sent_to_customer","Retornado a cliente"),
            # Destino Transfereir pieza a stock de almacen
            ("waiting_send_to_stock","Esperando transferencia a stock"),
            ("in_stock","Retornado al stock"),
            ("in_scrap","Enviada a chatarrear"),
            # Destino Envio de pieza a chatarrear
            ("waiting_send_to_scrap","Esperando desechar"),
            ("scrapped","Desechado"),
        ],        
        string="Estado del producto en el proceso de RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )
    # Sobre escribimos loos estados para añadir los de proveedor
    # 'no_purchase','waiting_action_purchase','waiting_send_to_supplier','waiting_response_supplier',
    # 'reject_by_supplier','accepted_waiting_confirm_refund','solution_refunded','','','','','','','','',''
    state_purchase = fields.Selection(
        [
            ("no_purchase", "Sin compra"),                                     
            ("waiting_action_purchase", "En espera"), 
            ("send_to_supplier", "Enviar a proveedor"),
            ("waiting_send_to_supplier", "Esperando devolucion a proveedor"),
            ("waiting_response_supplier", "Esperando respuesta proveedor"),
            ("reject_by_supplier", "Rechazada por el proveedor"),
            ("reject_waiting_return_by_supplier", "Esperando recibir el producto rechazado"),
            ("reject_scrapped_by_supplier", "Desechado por el proveedor"), # si no retiramos la pieza por costes de transporte el proveedor pasara a chatarrearla
            ("reject_returned_by_supplier", "Recibido rechazo proveedor"),
            ("accepted_by_supplier", "Aceptado el reembolso por el prroveedor"),
            ("accepted_waiting_confirm_refund", "Esperando confirmación de reembolso de proveedor"),
            ("accepted_refunded_from_supplier", "Reembolsado por el proveedor"),
        ],
        string="Estado de la gestion del RMA con el proveedor", 
        default="no_purchase",
        copy=False,
        tracking=True,
    )
    #rma_owner_product           :   nothing , costumer , rma , workshop , external , supplier
    rma_owner_product = fields.Selection([
            ("nothing",  "Sin gestionar"),
            ("costumer", "En cliente"),
            ("internal_rma", "En RMA Interno"),
            ("internal_sat", "En SAT Interno"),
            ("internal_scrap", "En Scrap Interno"),
            ("external_sat", "En SAT Externo"),
            ("supplier", "Proveedor"),
        ],        
        string="Tipo de validación del RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )
    
    rma_type_validation = fields.Selection([
            ("nothing",  "Sin gestionar"),
            ("waiting", "En espera"),
            ("internal", "Interna"),
            ("external", "Externa"),
            ("supplier", "Proveedor"),
        ],        
        string="Tipo de validación del RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )
    rma_type_resolution = fields.Selection([
            ("nothing",  "Sin gestionar"),
            ("waiting", "En espera"),
            ("in_progress", "En curso"),
            ("accepted", "Aceptado"),
            ("rejected", "Rechazado"),
        ],        
        string="Resolución técnica del RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )
    rma_type_negotiation = fields.Selection([
            ("nothing",  "Sin gestionar"),
            ("waiting", "En espera"),
            ("in_progress", "En curso"),
            ("accepted", "Aceptada por comercial"),
            ("rejected", "Rechazada por comercial"),            
        ],        
        string="Negociación comercial del RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )
    rma_type_solution = fields.Selection(
        [
            ("nothing",  "Sin gestionar"),
            ("waiting", "En espera"),
            ("repair",  "Aceptado para reparar"),
            ("replace", "Aceptado para sustitucion"),
            ("refund",  "Aceptado para abono"),
            ("rejected", "Rechazado"),
        ],
        string="Solución aportada al RMA", 
        default = 'nothing',
        copy=False,
        tracking=True,
    )
    rma_type_resolution_supplier = fields.Selection(
        [
            ("nothing",  "Sin gestionar"),
            ("waiting",  "En espera"),
            ("accepted", "Aceptado"),
            ("rejected", "Rechazado"),
        ],
        string="Negociación con proveedor del RMA", 
        default = 'nothing',
        copy=False,
        tracking=True,
    )
    rma_type_solution_supplier = fields.Selection(
        [
            ("nothing",  "Sin gestionar"),
            ("waiting", "En espera"),
            ("repair",  "Aceptado para reparar"),
            ("replace", "Aceptado para sustitucion"),
            ("refund",  "Aceptado para abono"),
            ("rejected", "Rechazado"),
        ],
        string="Solución aportada por el proveedor al RMA", 
        default = 'nothing',
        copy=False,
        tracking=True,
    )

    rma_type_final_location = fields.Selection([
            ("nothing",  "Sin asignar"),
            ("costumer", "En cliente"),
            ("stock", "Retornado a stock"),
            ("scrap", "Desechado"),
            ("external_scrap", "Desechado en externo"),
            ("supplier_scrap", "Desechado en proveedor"),
            ("costumer_scrap", "Desechado en cliente"),
        ],        
        string="Tipo de validación del RMA", 
        default="nothing",
        copy=False,
        tracking=True,
    )

    # Exportar a modulo q2 
    #sale_id = fields.Many2one(
    #    comodel_name="sale.order",
    #    readonly=True,
    #    string="Pedido de venta",
    #)
    
    # Las gestiones de RMA pueden ser:
    # > sobre productos recepcionados fisicamente, 
    # > sobre productos que no recepcionamos y cuya gestion se realiza de forma remota o telematica
    # Esta ultima al no recepcionar la pieza no permite que se realicen las operacions que requieren disponer de la pieza en las intalaciones fisicamente

    rma_customer_remote_claim = fields.Boolean(
        string="Reclamación remota del RMA Cliente", 
        default=False,
        copy=False,
        tracking=True,
        )
    rma_supplier_remote_claim = fields.Boolean(
        string="Reclamación remota del RMA Proveedor", 
        default=False,
        copy=False,
        tracking=True,
        )
    rma_external_remote_claim = fields.Boolean(
        string="Reclamación remota del RMA con Servicio Externo", 
        default=False,
        copy=False,
        tracking=True,
        )
    
    rma_received = fields.Boolean(
        string="Recepcionado",
        copy=False,
        default=False,
    )
    
    rma_supplier_delivered_qty = fields.Float(
        string="Delivered qty",
        digits="Product Unit of Measure",
        compute="_compute_delivered_qty",
        store=True,
    )
    rma_supplier_delivered_qty_done = fields.Float(
        string="Delivered qty done",
        digits="Product Unit of Measure",
        compute="_compute_delivered_qty",
        compute_sudo=True,
    )

    # Sale order fields
    origin_sale = fields.Char(
        string="Pedido de venta",
        states={"locked": [("readonly", True)], "cancelled": [("readonly", True)]},
        help="Reference of the sale document that generated this RMA.",
    )
    sale_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Sale group",
    )
    refund_sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Refund SO",
        readonly=True,
        copy=False,
    )
    refund_sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Refund line",
        readonly=True,
        copy=False,
    )
    
    # Purchase order fields
    origin_purchase = fields.Char(
        string="Orden de compra",
        states={"locked": [("readonly", True)], "cancelled": [("readonly", True)]},
        help="Reference of the purchase document that generated this RMA.",
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        readonly=True,
        string="Orden de compra",
    )
    purchase_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Purchase group",
    )
    purchase_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Entrega de compra",
        domain="["
        "    ('state', '=', 'done'),"
        "    ('picking_type_id.code', '=', 'incoming'),"
        "    ('partner_id', 'child_of', purchase_supplier_partner_id),"
        "]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    supplier_reference_purchase = fields.Char(
        string="Ref. del proveedor",
        states={"locked": [("readonly", True)], "cancelled": [("readonly", True)]},
        help="Supplier reference of the purchase document that generated this RMA.",
    )
    purchase_supplier_partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
        string="Proveedor",
    )
    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        readonly=True,
        string="Linea de compraen PO",
    )
    purchase_date_order = fields.Date(
        string="Fecha compra proveedor",
    )
    purchase_receive_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Reception purchase move",
        copy=False,
    )
    purchase_return_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Return purchase move",
        copy=False,
    )
    purchase_return_reject_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Return RMA reject purchase move",
        copy=False,
    )
    refund_purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Refund PO",
        readonly=True,
        copy=False,
    )
    refund_purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        string="Refund line",
        readonly=True,
        copy=False,
    )
    
    # Movimiento de retorno de la pieza al cliente 
    rma_delivery_to_customer_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Movimiento de retorno del RMA al cliente",
        copy=False,
    )
    
    # Id de la orden de venta en Garantia, por regla general a coste 0 pero incluyendo los gastos de gestion de RMA y portes
    replace_sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Garantía SO",
        readonly=True,
        copy=False,
    )
    
    # Movimiento de desachado de pieza a chatarra en tienda
    scrap_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Enviado a desechar",
    )
    
    # Registramos el último movimiento realizado que podremos tomar como origen del siguiente
    last_move_id = fields.Many2one(
        comodel_name="stock.move",
        string="Ultimo movimiento realizado",
    )

    # Hasta aqui exportar a modulo Q2

    # COMPUTE Functions
    # Sobreescribimos la mfuncion de computo de las cantidades entregadas
    # Tenemos que diferenciar las cantidades enviadas a proveedor y que ya no estan en nuestro poder
    # Igualmente una vez son retornadas por el proveedor ya podemos disponer de ella para otro movimiento
    def _compute_delivered_qty(self):
        """Compute 'delivered_qty' and 'delivered_qty_done' fields.
        delivered_qty: represents the quantity delivery or to be
        delivery. For each move in delivery_move_ids the quantity done
        is taken, if it is empty the reserved quantity is taken,
        otherwise the initial demand is taken.
        delivered_qty_done: represents the quantity delivered and done.
        For each 'done' move in delivery_move_ids the quantity done is
        taken. This field is used to control when the RMA cam be set
        to 'delivered' state.
        """
        #wdb.set_trace()

        for r in self:
            delivered_qty = 0.0
            delivered_qty_done = 0.0
            stock_warehouse_id = (
                self.env["stock.warehouse"]
                .search([("company_id", "=", self.order_id.company_id.id)])
                )
            # Obtenemoos el picking_type correspondiente al "RMA pproveedores Salidas"
            #rma_in_type_id = stock_warehouse_id.mapped("rma_in_type_id")
            #rma_out_type_id = stock_warehouse_id.mapped("rma_out_type_id")
            rma_supplier_in_type_id = stock_warehouse_id.mapped("rma_supplier_in_type_id")
            rma_supplier_out_type_id = stock_warehouse_id.mapped("rma_supplier_out_type_id")

            for move in r.delivery_move_ids.filtered(
                lambda r: r.state != "cancel" and not r.scrapped
            ):
                if move.quantity_done:
                    quantity_done = move.product_uom._compute_quantity(
                        move.quantity_done, r.product_uom
                    )
                    if move.picking_type_id not in [rma_supplier_in_type_id,rma_supplier_out_type_id]:
                        if move.state == "done":
                            # Tendremos que diferenciar entre movimientos de salida stock_move.picking_code ='outgoing' y movimientos de entrada  stock_move.picking_code ='incoming'
                            if move.picking_code == "outgoing":
                                delivered_qty_done += quantity_done
                            if move.picking_code == "incoming":
                                delivered_qty_done -= quantity_done
                            delivered_qty += delivered_qty_done
                    else:
                        if move.state == "done":
                            # Tendremos que diferenciar entre movimientos de salida stock_move.picking_code ='outgoing' y movimientos de entrada  stock_move.picking_code ='incoming'
                            if move.picking_code == "outgoing":
                                delivered_qty_done += quantity_done
                            if move.picking_code == "incoming":
                                delivered_qty_done -= quantity_done
                            r.rma_supplier_delivered_qty = delivered_qty_done
                            r.rma_supplier_delivered_qty_done = delivered_qty_done 
                elif move.reserved_availability:
                    delivered_qty += move.product_uom._compute_quantity(
                        move.reserved_availability, r.product_uom
                    )
                elif move.product_uom_qty:
                    delivered_qty += move.product_uom._compute_quantity(
                        move.product_uom_qty, r.product_uom
                    )
            r.delivered_qty = delivered_qty
            r.delivered_qty_done = delivered_qty_done

    # ####################################################################################################################################
    # ####### ACCIONES  ##################################################################################################################
    # ####################################################################################################################################
    # ** CONFIRMATION
    def action_confirm(self):
        #wdb.set_trace()
        res = super(Rma,self).action_confirm()
        self.sudo().write({
                "state_process": "reception",
                "state": "confirmed",
                "state_product": "waiting_reception"
                })
        return res

    # metodo que permite tener un boton con informacion pero sin estar linkado a nada
    def action_view_empty_no_link(self):
        return False

    def action_view_refund_sale(self):
        """Invoked when 'Refund' smart button in rma form view is clicked."""
        #wdb.set_trace()
        self.ensure_one()
        return {
            "name": _("Refund"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "sale.order",
            "views": [(self.env.ref("sale.view_order_form").id, "form")],
            "res_id": self.refund_sale_order_id.id,
        }

    def action_view_refund_purchase(self):
        """Invoked when 'Refund' smart button in rma form view is clicked."""
        #wdb.set_trace()
        self.ensure_one()
        return {
            "name": _("Refund"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "purchase.order",
            "views": [(self.env.ref("purchase.purchase_order_form").id, "form")],
            "res_id": self.refund_purchase_order_id.id,
        }

    # ####################################################################################################################################
    # ####### VISIBLE INFO BUTTON ########################################################################################################
    # ####################################################################################################################################
    # ** RECEPCION(reception) **
    # RMA Remoto                  >   action_view_rma_remote                              > visible_info_button_rma_remote
    visible_info_button_rma_remote = fields.Boolean(
        compute="_compute_visible_info_button_rma_remote",
    )
    def _compute_visible_info_button_rma_remote(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            # attrs="{'invisible': [('rma_customer_remote_claim', '=', False)]}"
            # Veremos el boton de informacion de estado remoto cuando marquemos que es remoto 
            if r.rma_customer_remote_claim:
                visible = True
            r.visible_info_button_rma_remote = visible
    def action_view_rma_remote(self):
        return self.action_view_empty_no_link()

    #> RMA Pte Recibir             >   action_view_rma_waiting_to_receive                  > visible_info_button_rma_waiting_to_receive
    visible_info_button_rma_waiting_to_receive = fields.Boolean(
        compute="_compute_visible_info_button_rma_waiting_to_receive",
    )
    def _compute_visible_info_button_rma_waiting_to_receive(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            #attrs="{'invisible': ['|',('reception_move_id', '=', False),('rma_received', '=', True)]}"
            # Veremos el boton de informacion mientras estemos pendiente de recibir un producto 
            if r.reception_move_id:
                visible = False if r.rma_received else True
            r.visible_info_button_rma_waiting_to_receive = visible
    def action_view_rma_waiting_to_receive(self):
        # llamamos a la funcion de qie hereda
        self.action_view_receipt()

    #> RMA Recibido                >   action_view_rma_received                            > visible_info_button_rma_received
    visible_info_button_rma_received = fields.Boolean(
        compute="_compute_visible_info_button_rma_received",
    )
    def _compute_visible_info_button_rma_received(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            # attrs="{'invisible': [('rma_received', '=', False),('rma_customer_remote_claim', '=', True)]}"
            if r.rma_received:
                visible = True # if not r.rma_customer_remote_claim else False
            r.visible_info_button_rma_received = visible
    def action_view_rma_received(self):
        # llamamos a la funcion de qie hereda
        self.action_view_receipt()

    #> Venta                       >   action_view_sale_order                              > visible_info_button_sale_order  
    visible_info_button_sale_order = fields.Boolean(
        compute="_compute_visible_info_button_sale_order",
    )
    def _compute_visible_info_button_sale_order(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            if r.order_id:
                visible = True
            r.visible_info_button_sale_order = visible
    def action_view_sale_order(self):
        #wdb.set_trace()
        """Esta función devuelve una acción que muestra el pedido de ventas existente.
        de rma dada.
        """
        self.ensure_one()
        # Remove default_picking_id to avoid defaults get
        # https://github.com/odoo/odoo/blob/e4d22d390c8aa8edf757e36704a9e04b2b89f115/
        # addons/stock/models/stock_move.py#L410
        ctx = self.env.context.copy()
        ctx.pop("default_rma_id", False)
        return self.with_context(ctx).order_id.get_formview_action()

    # ** GESTION CON PROVEEDOR **************************************************************************************************************
    #> Compra                      >   action_view_purchase_order                          > visible_info_button_purchase_order
    visible_info_button_purchase_order = fields.Boolean(
        compute="_compute_visible_info_button_purchase_order",
    )
    def _compute_visible_info_button_purchase_order(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            # attrs="{'invisible': [('purchase_id', '=', False)]}"
            if r.purchase_id:
                visible = True
            r.visible_info_button_purchase_order = visible
    def action_view_purchase_order(self):
        #wdb.set_trace()
        """This function returns an action that display existing sales order
        of given rma.
        """
        self.ensure_one()
        # Remove default_picking_id to avoid defaults get
        # https://github.com/odoo/odoo/blob/e4d22d390c8aa8edf757e36704a9e04b2b89f115/
        # addons/stock/models/stock_move.py#L410
        ctx = self.env.context.copy()
        ctx.pop("default_rma_id", False)
        return self.with_context(ctx).purchase_id.get_formview_action()

    # Pte Abono Proveedor         >   action_view_waiting_refund_purchase_to_invoice      > visible_info_button_waiting_refund_purchase_to_invoiced
    visible_info_button_waiting_refund_purchase_to_invoiced = fields.Boolean(
        compute="_compute_visible_info_button_waiting_refund_purchase_to_invoiced",
    )
    def _compute_visible_info_button_waiting_refund_purchase_to_invoiced(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            if r.refund_purchase_order_id:
                visible = (r.state_purchase in ['accepted_waiting_confirm_refund','accepted_by_supplier'])
            r.visible_info_button_waiting_refund_purchase_to_invoiced = visible
    def action_view_waiting_refund_purchase_to_invoice(self):
        return self.action_view_refund_purchase()

    # Abonado por Proveedor       >   action_view_refund_purchase_invoiced                > visible_info_button_refund_purchase_invoiced
    visible_info_button_refund_purchase_invoiced = fields.Boolean(
        compute="_compute_visible_info_button_refund_purchase_invoiced",
    )
    def _compute_visible_info_button_refund_purchase_invoiced(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            if r.refund_purchase_order_id:
                visible = (r.state_purchase == 'accepted_refunded_from_supplier' ) 
            r.visible_info_button_refund_purchase_invoiced = visible
    def action_view_refund_purchase_invoiced(self):
        return self.action_view_refund_purchase()

    # ** SOLUCION / ABONO(solution) **********************************************************************************************************
    # Pte abono Cliente           >   action_view_waiting_refund_sale_to_invoice          > visible_info_button_waiting_refund_sale_to_invoice
    visible_info_button_waiting_refund_sale_to_invoice = fields.Boolean(
        compute="_compute_visible_info_button_waiting_refund_sale_to_invoice",
    )
    def _compute_visible_info_button_waiting_refund_sale_to_invoice(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            if r.refund_purchase_order_id:
                visible = (r.state in ['solution_waiting_refund'])
                #visible = (r.refund_purchase_order_id.invoice_status in ['draft','to invoice']
                    # and r.refund_purchase_order_id.invoice_count == 0 
                #) 
            r.visible_info_button_waiting_refund_sale_to_invoice = visible
    def action_view_waiting_refund_sale_to_invoice(self):
        return self.action_view_refund_sale()

    # Abonado a Cliente           >   action_view_refund_sale_invoiced                    > visible_info_button_refund_sale_invoiced 
    visible_info_button_refund_sale_invoiced = fields.Boolean(
        compute="_compute_visible_info_button_refund_sale_invoiced",
    )
    def _compute_visible_info_button_refund_sale_invoiced(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            if r.refund_sale_order_id:
                visible = (r.state == 'solution_refunded' ) 
            r.visible_info_button_refund_sale_invoiced = visible
    def action_view_refund_sale_invoiced(self):
        return self.action_view_refund_sale()

    # ** DESTINO FINAL PIEZA(location) ***************************************************************************************************
    # Enviado a cliente  (**PTE**)         >   action_view_sent_to_customer                        > visible_info_button_sent_to_customer
    visible_info_button_sent_to_customer = fields.Boolean(
        compute="_compute_visible_info_button_sent_to_customer",
    )
    def _compute_visible_info_button_sent_to_customer(self):
        #wdb.set_trace()
        visible = False
        # **PTE** Hay que ver cuando y como dar visibilidad al boton 
        for r in self:
            r.visible_info_button_sent_to_customer = visible
    def action_view_sent_to_customer(self):
        self.ensure_one()
        return False

    # Desechado                   >   action_view_move_scrap                              > visible_info_button_move_scrap
    visible_info_button_move_scrap = fields.Boolean(
        compute="_compute_visible_info_button_move_scrap",
    )
    def _compute_visible_info_button_move_scrap(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            # attrs="{'invisible': [('scrap_move_id', '=', False)]}"
            if r.scrap_move_id:
                visible = True
            r.visible_info_button_move_scrap = visible
    def action_view_move_scrap(self):
        self.ensure_one()
        #wdb.set_trace()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        scraps = self.env['stock.scrap'].search([('picking_id', '=', self.scrap_move_id.picking_id.id)])
        action['domain'] = [('id', 'in', scraps.ids)]
        action['context'] = dict(self._context, create=False)
        return action

    # ####################################################################################################################################
    # ####### VISBLE RIBBON FINICHED #####################################################################################################
    # ####################################################################################################################################
    # Finalizado reparado
    visible_ribbon_rma_accepted_repair  = fields.Boolean(
        compute="_compute_visible_ribbon_rma_accepted_repair",
    )
    def _compute_visible_ribbon_rma_accepted_repair(self):
        #wdb.set_trace()
        for r in self:
            visible = (r.state_process == "finished" and r.rma_type_solution == 'repair') 
            r.visible_ribbon_rma_accepted_repair = visible
    # Finalizado reemplazado
    visible_ribbon_rma_accepted_replace  = fields.Boolean(
        compute="_compute_visible_ribbon_rma_accepted_replace",
    )
    def _compute_visible_ribbon_rma_accepted_replace(self):
        #wdb.set_trace()
        for r in self:
            visible = (r.state_process == "finished" and r.rma_type_solution == 'replace') 
            r.visible_ribbon_rma_accepted_replace = visible
    # Finalizado abonado
    visible_ribbon_rma_accepted_refund  = fields.Boolean(
        compute="_compute_visible_ribbon_rma_accepted_refund",
    )
    def _compute_visible_ribbon_rma_accepted_refund(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            visible = (r.state_process == "finished" and r.rma_type_solution == 'refund') 
            r.visible_ribbon_rma_accepted_refund = visible
    # Finalizado rechazado
    visible_ribbon_rma_rejected  = fields.Boolean(
        compute="_compute_visible_ribbon_rma_rejected",
    )
    def _compute_visible_ribbon_rma_rejected(self):
        #wdb.set_trace()
        for r in self:
            visible = False
            visible = (r.state_process in ["returned_to_customer","solution_replaced","solution_refunded","finished"]  and r.rma_type_negotiation == "rejected") 
            r.visible_ribbon_rma_rejected = visible

    # ####################################################################################################################################
    # ####### CAN BE #####################################################################################################################
    # ####################################################################################################################################

    # ** RECEPCION(reception) ************************************************************************************************************
    #> Recepcionar RMA                     >  action_receive_rma_costumer                    > can_be_receive_from_costumer                    state_process = ='reception' 
    can_be_receive_from_costumer = fields.Boolean(
        compute="_compute_can_be_receive_from_costumer",
    )
    @api.depends("state",)
    def _compute_can_be_receive_from_costumer(self):
        """
        Compute 
        """ 
        #wdb.set_trace()
        visible = False
        for r in self:
            if self.state_process =='reception' and not r.rma_customer_remote_claim:
                if r.reception_move_id:
                    visible = (r.reception_move_id.picking_id.state == "assigned")
        self.can_be_receive_from_costumer = visible
    def action_receive_rma_costumer(self):
        #wdb.set_trace()
        self.ensure_one()
        self.reception_move_id.picking_id.validate_picking()
        self.sudo().write({
            'rma_owner_product':'internal_rma',
            'rma_type_validation':'waiting',
            'state_process':'validation',
            'state':'validation_waiting',
            'state_product':'received',
            'last_move_id':self.reception_move_id,
        })

    #> Gestión Remota RMA                  >  action_remote_rma_costumer                     > can_be_remote_rma_costumer      
    can_be_remote_rma_costumer = fields.Boolean(
        compute="_compute_can_be_remote_rma_costumer",
    )
    @api.depends("state",)
    def _compute_can_be_remote_rma_costumer(self):
        """
        Compute 
        """ 
        #  #wdb.set_trace()
        visible = False
        for r in self:
            if r.state_process =='reception':
                if not r.rma_customer_remote_claim:
                    visible = True 
        self.can_be_remote_rma_costumer = visible
    def action_remote_rma_costumer(self):
        #  #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            'rma_customer_remote_claim':True,
            'rma_owner_product':'costumer',
            'rma_type_validation':'waiting',
            'state_process':'validation',
            'state':'validation_waiting',
            'state_product':'remote',
        })

    # ** VALIDACION (validation) **********************************************************************************************************
    can_be_validate = fields.Boolean(
        compute="_compute_can_be_validate",
    )
    @api.depends("state",)
    def _compute_can_be_validate(self):
        """
        Compute 
        """ 
        #  #wdb.set_trace()
        visible = False
        for r in self:
            # attrs="{'invisible': [('state_process', '!=', 'validation')]}"
            if r.state_process == 'validation':
                if r.state in ['validation_waiting']:
                    visible = True
        self.can_be_validate = visible

    # Valoración interna                  >  action_internal_validate                     > can_be_validate                               state_process = ='validation' & state = ='validation_waiting'
    # Validacion interna, no requiere de movimiento, aun 
    def action_internal_validate(self):
        #  #wdb.set_trace()
        self.sudo().write({
            'rma_type_validation':'internal', 
            'state':'validation_internal',
            'state_product':'waiting_validation',
        })

    # Valoración externa                  >  action_external_validate                     > can_be_validate                    
    # Se produce un movimiento de la pieza a un proveedor de servicios de verificacion externo
    # De momento no dejamos registrado el movimiento, hacerlo mas adelante
    def action_external_validate(self):
        # Se deveria de generar un picking de envio a una empresa externa que no sea el proveedor para validar el RMA
        # action_send_rma_external(self) # Pendiente de codigo
        #  #wdb.set_trace()
        self.sudo().write({
            'rma_type_validation':'external', 
            'state':'validation_external',
            'state_product':'waiting_validation',
        })

    # Valoración Proveedor                >  action_supplier_validate                     > can_be_validate                    
    # Añadimos la acción de retorno de pieza a proveedor
    def action_supplier_validate(self):
        # Se deveria de generar un picking de envio a una empresa externa que no sea el proveedor para validar el RMA
        # action_send_rma_external(self) # Pendiente de codigo
        #  #wdb.set_trace()
        self.sudo().write({
            'rma_type_validation':'supplier', 
            'state':'validation_supplier',
            'state_product':'waiting_validation',
        })

    # ** Validación INTERNA **************************************************************************************************************
    #  @ Valorar directamente             >  action_validation_direct_internal               > can_be_validation_direct_internal              state = ='validation_external'
    can_be_validation_direct_internal = fields.Boolean(
        compute ="_compute_can_be_validation_direct_internal",
    )
    def _compute_can_be_validation_direct_internal(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #  #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            if r.state == 'validation':
                if r.rma_type_validation == 'internal':
                    if r.state_product == 'waiting_validation':
                        visible = True
            # asignacion
            r.can_be_validation_direct_internal = visible
    def action_validation_direct_internal(self):
        #  #wdb.set_trace()
        self.sudo().write({
            "rma_type_resolution":"waiting",
            'state_process':'resolution', 
            'state':'resolution_waiting',
            'state_product':'waiting_resolution',
        })
    #  @ Enviar a taller                  >  action_validation_delivery_to_internal_test     > can_be_validation_delivery_to_internal_test         state = ='supplier_validate' & state_product = ='waiting_send_to_supplier' & not rma_customer_remote_claim
    can_be_validation_delivery_to_internal_test = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_internal_test",
    )
    @api.depends("state",)
    def _compute_can_be_validation_delivery_to_internal_test(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.state_process == 'validation':
                if r.state in ['validation_internal']:
                    if r.rma_type_validation == 'internal':
                        if r.state_product == 'waiting_validation':
                            visible = True
            # asignacion
            r.can_be_validation_delivery_to_internal_test = visible
    def action_validation_delivery_to_internal_test(self):
        #wdb.set_trace()
        self.sudo().write({
            "rma_owner_product":"internal_sat",
            'state_product':'waiting_check_internal',
        })

    #  @ Recibido desde taller            >  action_validation_received_from_internal_test   > can_be_validation_received_from_internal_test      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
    can_be_validation_received_from_internal_test = fields.Boolean(
        compute ="_compute_can_be_validation_received_from_internal_test",
    )
    @api.depends("state",)
    def _compute_can_be_validation_received_from_internal_test(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.state_product == 'waiting_check_internal':
                visible = True
            # asignacion
            r.can_be_validation_received_from_internal_test = visible
    def action_validation_received_from_internal_test(self):
        #wdb.set_trace()
        self.sudo().write({
            "rma_owner_product":"internal_rma",
            "rma_type_resolution":"waiting",
            'state_process':'resolution', 
            'state':'resolution_waiting',
            'state_product':'waiting_resolution',
        })

    # ** Validación EXTERNO **************************************************************************************************************
    #  @ Gestion Remota Externo           >  action_validation_remote_external            > can_be_validation_remote_external               state = ='validation_external'
    can_be_validation_remote_external = fields.Boolean(
        compute ="_compute_can_be_validation_remote_external",
    )
    @api.depends("state",)
    def _compute_can_be_validation_remote_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.state_process == 'validation':
                if r.state == 'validation_external':
                    if r.state_product == 'waiting_validation':
                        visible = True
            # asignacion
            r.can_be_validation_remote_external = visible
    def action_validation_remote_external(self):
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            "rma_external_remote_claim":True,
            "rma_type_resolution":"waiting",
            'state_process':'resolution',
            "state":"resolution_waiting",
            'state_product':'waiting_resolution',
        })
           
    #  @ Enviar a Externo                 >  action_validation_delivery_to_external       > can_be_validation_delivery_to_external        state = ='validation_external' & state_product = ='waiting_send_to_external' & not rma_customer_remote_claim
    can_be_validation_delivery_to_external = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_external",
    )
    @api.depends("state",)
    def _compute_can_be_validation_delivery_to_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            if r.state_process == 'validation':
                # para poder enviar la pieza debemos etar en posesion de la misma
                if r.rma_owner_product == 'internal_rma':
                    if r.state == 'validation_external':
                        if r.state_product == 'waiting_validation':
                            visible = True
            # asignacion
            r.can_be_validation_delivery_to_external = visible
    def action_validation_delivery_to_external(self):
        """Invoked when 'Return to customer' button in rma form
        view is clicked.
        """
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            "rma_owner_product":"external_sat",
            'state_product':'sent_to_external',
        })


    #  @ Recibido desde Externo           >  action_validation_received_from_external     > can_be_validation_received_from_external      state_product = ='waiting_receive_from_external' & not rma_customer_remote_claim
    can_be_validation_received_from_external = fields.Boolean(
        compute ="_compute_can_be_validation_received_from_external",
    )
    @api.depends("state",)
    def _compute_can_be_validation_received_from_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.rma_owner_product == 'external_sat':
                visible = True
            # asignacion
            r.can_be_validation_received_from_external = visible
    def action_validation_received_from_external(self):
        #wdb.set_trace()
        self.ensure_one()
        # Al ser externo el envio y recepcion es solo a nivel de estado (de momento) 
        self.sudo().write({
            "rma_owner_product":"internal_rma",
            "rma_type_resolution":"waiting",
            "rma_owner_product":"internal_rma",
            'state_process':'resolution',
            "state":"resolution_waiting",
            'state_product':'received_from_external',
        })

    #  @ Desechado en Externo             >  action_validation_send_to_scrap_external     > can_be_validation_send_to_scrap_external      state_product = ='sent_to_external' & not rma_customer_remote_claim
    can_be_validation_send_to_scrap_external = fields.Boolean(
        compute ="_compute_can_be_validation_send_to_scrap_external",
    )
    @api.depends("state",)
    def _compute_can_be_validation_send_to_scrap_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.rma_owner_product == 'external_sat':
                visible = True
            # asignacion
            r.can_be_validation_send_to_scrap_external = visible
    def action_validation_send_to_scrap_external(self):
        #wdb.set_trace()
        self.ensure_one()
        # Al ser externo el envio y recepcion es solo a nivel de estado (de momento) 
        self.sudo().write({
            "rma_type_resolution":"waiting",
            'state_process':'resolution',
            "state":"resolution_waiting",
            'state_product':'scrapped_from_external',
        })

    #  ** Validación PROVEEDOR ***********************************************************************************************************
    #  @ Gestion Remota Proveedor         >  action_validation_remote_supplier            > can_be_validation_remote_supplier               state = ='supplier_validate' 
    can_be_validation_remote_supplier = fields.Boolean(
        compute ="_compute_can_be_validation_remote_supplier",
    )
    @api.depends("state",)
    def _compute_can_be_validation_remote_supplier(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            if r.state_process == 'validation':
                if r.state  == 'validation_supplier':
                    if r.state_product == 'waiting_validation':
                        visible = True
            # asignacion
            r.can_be_validation_remote_supplier = visible
    def action_validation_remote_supplier(self):
        #wdb.set_trace()
        self.ensure_one()
        self.rma_type_resolution
        self.sudo().write({
            "rma_supplier_remote_claim":True,
            'rma_type_resolution':'waiting',
            'state_process':'resolution', 
            "state":"resolution_waiting",            
            'state_product':'waiting_resolution',
            "state_purchase":"waiting_response_supplier"            
        })

    #    Enviar a proveedor               >  action_validation_delivery_to_supplier       > can_be_validation_delivery_to_supplier        state = ='supplier_validate' & state_product = ='waiting_send_to_supplier' & not rma_customer_remote_claim
    can_be_validation_delivery_to_supplier = fields.Boolean(
        compute="_compute_can_be_validation_delivery_to_supplier",
    )
    @api.depends("state",)
    def _compute_can_be_validation_delivery_to_supplier(self):
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.state_process == 'validation':
                if r.rma_owner_product == 'internal_rma':
                    if r.state == 'validation_supplier':
                        if r.state_product == 'waiting_validation':
                            visible = True
                            #if r.purchase_return_move_id:
                            #    visible = (r.purchase_return_move_id.picking_id.state == "assigned")
        self.can_be_validation_delivery_to_supplier = visible
    
    can_be_validation_receive_from_supplier = fields.Boolean(
        compute="_compute_can_be_validation_receive_from_supplier",
    )
    @api.depends("remaining_qty", "state_purchase")
    def _compute_can_be_validation_receive_from_supplier(self):
        """Compute 'can_be_validation_receive_from_supplier'. Nos ayuda a seguiir el flujoo dde trabajo
            En casso de ser positiiivvo nos indica que podemos soliiicitar el reembolso de la compra al proveedor ya sea por garantiia o devolucion.
            Necesita cumpliir las condiiciiones.
            r.remaining_qty > 0
        states:
                "no_purchase",                      # Si el pedido de cliente no tiene compra no tiiene compra no podemos devolver al proveedor
                "waiting_action_purchase",          # Esperando acciion con el proveedor
                "waiting_send_to_supplier",         # Esperando enviarlo al proveedor
                "returned_supplier",                # Enviado al proveedor  
                "waiting_response_supplier",        # Esperando respuesta del proveedor
                "reject_by_supplier",               # Rechazada por el proveedor
                "valid_received_supplier",          # Aceptada por el proveedor
                "accepted_waiting_confirm_refund",  # Esperando la confiirmacion de recepción del abono
                "refunded_from_supplier",           # Aborno realizado por el proveedor
        """
        #wdb.set_trace()
        for r in self:
            r.can_be_validation_receive_from_supplier = (
                #r.purchase_id 
                #and not r.purchase_return_move_id
                r.rma_owner_product == 'internal_rma' 
                #and r.state_purchase in ["waiting_action_purchase"] 
                and (r.state_process in ['validation'])
            )

    def action_validation_delivery_to_supplier(self):
        #wdb.set_trace()
        self.ensure_one()
        
        #self.purchase_return_move_id.picking_id.validate_picking()
        
        #self._ensure_can_be_validation_receive_from_supplier()
        # Force active_id to avoid issues when coming from smart buttons
        # in other models
        # Valores que registraremos si la accion se lleva a cabo
        action = (
            self.env.ref("rma.rma_delivery_wizard_action")
            .with_context(active_id=self.id)
            .read()[0]
        )
        action["context"] = dict(self.env.context)
        action["context"].update(
            active_id=self.id,
            active_ids=self.ids,
            rma_delivery_type="return_supplier",
        )
        action.update(
            name = "Devolver al proveedor",
        )
        return action
    

    #    @ Recibido desde proveedor       >  action_validation_received_from_supplier     > can_be_validation_received_from_supplier      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
    can_be_validation_received_from_supplier = fields.Boolean(
        compute ="_compute_can_be_validation_received_from_supplier",
    )
    def _compute_can_be_validation_received_from_supplier(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.rma_owner_product == 'supplier':
                if r.rma_type_final_location != 'supplier_scrap':
                    visible = True
            # asignacion
            r.can_be_validation_received_from_supplier = visible
    def action_validation_received_from_supplier(self):
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            'rma_owner_product':'internal_rma',
            'state_product':'received_from_supplier',
        })

    #    Desechado en proveedor           >  action_validation_send_to_scrap_supplier     > can_be_validation_send_to_scrap_supplier      state_product = ='sent_to_supplier' & not rma_customer_remote_claim
    can_be_validation_send_to_scrap_supplier = fields.Boolean(
            compute="_compute_can_be_validation_send_to_scrap_supplier",
        )
    @api.depends("state")
    def _compute_can_be_validation_send_to_scrap_supplier(self):
        """Compute ''. 
            Podemos enviar la pieza a stock para su nueva venta
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion
            if r.rma_owner_product == 'supplier':
                if r.rma_type_final_location != 'supplier_scrap':
                    visible = True
        self.can_be_validation_send_to_scrap_supplier = visible
    def action_validation_send_to_scrap_supplier(self):
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            'rma_type_final_location':'supplier_scrap',
            'state_product':'scrapped_from_supplier',
        })

    # ** RESOLUCION(resolution) **********************************************************************************************************
    @api.depends("state",)
    def _compute_can_be_solved(self):
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_resolution == 'waiting':
                visible = True
        return visible
    
    # Reclamacion Aceptada                >  action_resolution_accepted                   > can_be_resolution_accepted                    state_process = ='resolution' 
    can_be_resolution_accepted = fields.Boolean(
        compute="_compute_can_be_resolution_accepted",
    )
    def _compute_can_be_resolution_accepted(self):
        self.can_be_resolution_accepted = self._compute_can_be_solved()
    def action_resolution_accepted(self):
        #wdb.set_trace()
        for r in self:
            # Primeros cambiamos el estado de valizacion como aceptado para que compute todos los campos afectados
            vals = {}
            vals["state"] = "resolution_accepted"
            vals["rma_type_resolution"] = "accepted"
            vals["rma_type_negotiation"] = "waiting"
            vals["state_product"] = "waiting_negotiation"
            #wdb.set_trace()
            r.sudo().write(vals)
            if r.rma_type_validation == "supplier":
                r.action_refund_purchase_confirm()

    # Aceptacion y creacion de abono proveedor
    def action_refund_purchase_confirm(self):
        """
        Hook method
        """
        #wdb.set_trace()
        self.ensure_one()
        for r in self:
            vals = {}
            vals["rma_type_resolution_supplier"] = "accepted"
            vals["rma_type_solution_supplier"] = "refund"
            if r.rma_owner_product == 'supplier':
                vals["rma_type_final_location"] = "supplier_scrap"
            r.sudo().write(vals)

            # de momento tomaremos como que la aceptacion del RMA 
            # por parte del proveedor deriva automaticamente en un abono
            self.create_refund_purchase()
            #if self.refund_purchase_order_id:
            #    self.refund_purchase_order_id.action_confirm()

    # Reclamacion Rechazada               >  action_resolution_rejected                   > can_be_resolution_rejected
    can_be_resolution_rejected = fields.Boolean(
        compute="_compute_can_be_resolution_rejected",
    )
    def _compute_can_be_resolution_rejected(self):
        self.can_be_resolution_rejected = self._compute_can_be_solved()
    def action_resolution_rejected(self):
        #wdb.set_trace()
        for r in self:
            # Primeros cambiamos el estado de valizacion como aceptado para que compute todos los campos afectados
            vals = {}
            vals["state"] = "resolution_rejected"
            vals["rma_type_resolution"] = "rejected"
            vals["rma_type_negotiation"] = "waiting"
            vals["state_product"] = "waiting_negotiation"
            if r.rma_type_validation == "supplier":
                vals["rma_type_resolution_supplier"] = "rejected"
                vals["rma_type_solution_supplier"] = "rejected"
            #wdb.set_trace()
            r.sudo().write(vals)
        
    # ** NEGOCIACION(negotiation) ********************************************************************************************************
    # RMA Aceptado REPARAR                >  action_negotiation_accepted_to_repair        > can_be_negotiation_accepted_to_repair         state_process = ='negotiation' & not rma_customer_remote_claim
    can_be_negotiation_accepted_to_repair = fields.Boolean(
        compute="_compute_can_be_negotiation_accepted_to_repair",
    )
    @api.depends("state")
    def _compute_can_be_negotiation_accepted_to_repair(self):
        # NUEVO ESTADO DE RMA Q2
        """Compute 'can_be_negotiation_accepted_to_repair'. This field controls the visibility
        of 'Replace' button in the rma form
        view and determinates if an rma can be replaced.
        This field is used in:
        rma._compute_can_be_split
        rma._ensure_can_be_negotiation_accepted_to_repair.
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if not r.rma_customer_remote_claim:
                if r.rma_type_negotiation == 'waiting':
                    if r.rma_owner_product not in ['nothing' , 'costumer']:
                        if r.rma_type_final_location =='nothing':
                            visible = True
        self.can_be_negotiation_accepted_to_repair = visible

    def action_negotiation_accepted_to_repair(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "rma_type_negotiation": "accepted",
                "rma_type_solution":"repair",
                "state_process":"solution",
                "state":"negotiation_accepted_to_repair",
                "state_product": "waiting_send_to_repair",
            })

    # RMA Aceptado REEMPLAZAR             >  action_negotiation_accepted_to_replace       > can_be_negotiation_accepted_to_replace        state_process = ='negotiation' 
    can_be_negotiation_accepted_to_replace = fields.Boolean(
        compute="_compute_can_be_negotiation_accepted_to_replace",
    )
    @api.depends("state")
    def _compute_can_be_negotiation_accepted_to_replace(self):
        # SOBRESCRIBE LA FUNCION ORIGINAL DE RMA.PY DE OCA
        """Compute 'can_be_negotiation_accepted_to_replace'. This field controls the visibility
        of 'Replace' button in the rma form
        view and determinates if an rma can be replaced.
        This field is used in:
        rma._compute_can_be_split
        rma._ensure_can_be_negotiation_accepted_to_replace.
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if not r.rma_customer_remote_claim:
                if r.rma_type_negotiation == 'waiting':
                    if r.rma_owner_product not in ['nothing' , 'costumer']:
                        if r.rma_type_final_location =='nothing':
                            visible = True
                        if r.rma_owner_product == 'supplier' and r.rma_type_resolution_supplier =='accepted':
                            visible = True

        self.can_be_negotiation_accepted_to_replace = visible
    def action_negotiation_accepted_to_replace(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "rma_type_negotiation": "accepted",
                "rma_type_solution":"replace",
                "state_process":"solution",
                "state":"negotiation_accepted_to_replace",
            })
        # si entendemos que en el mismo proceso se hace el envio
        # res = super(Rma,self).action_replace()

    # RMA Aceptado ABONAR                 >  action_negotiation_accepted_to_refund        > can_be_negotiation_accepted_to_refund         state_process = ='negotiation' 
    can_be_negotiation_accepted_to_refund = fields.Boolean(
        compute="_compute_can_be_negotiation_accepted_to_refund",
    )
    @api.depends( "state")
    def _compute_can_be_negotiation_accepted_to_refund(self):
        # SOBRESCRIBE LA FUNCION ORIGINAL DE RMA.PY DE OCA
        """Compute 'can_be_refunded'. This field controls the visibility
        of 'Refund' button in the rma form view and determinates if
        an rma can be refunded. It is used in rma.action_refund method.
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_negotiation == 'waiting':
                visible = True
            r.can_be_negotiation_accepted_to_refund = visible

    def action_negotiation_accepted_to_refund(self):
        #wdb.set_trace()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            vals = {}
            vals["rma_type_negotiation"]="accepted"
            vals["rma_type_solution"]="refund"
            vals["state"]="negotiation_accepted_to_refund"
            if not r.rma_customer_remote_claim:
                vals["state_product"]="waiting_location"
                vals["state_process"]="location"
            else:
                vals["state_process"]="finished"
            r.sudo().write(vals)

    # RMA Rechazado                       >  action_negotiation_rejected                  > can_be_negotiation_rejected                   state_process = ='negotiation' 
    can_be_negotiation_rejected = fields.Boolean(
        compute="_compute_can_be_negotiation_rejected",
    )
    @api.depends("state",)
    def _compute_can_be_negotiation_rejected(self):
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_negotiation == 'waiting':
                visible = True
            r.can_be_negotiation_rejected = visible
    def action_negotiation_rejected(self):
        #wdb.set_trace()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            vals = {}
            vals["rma_type_negotiation"]="rejected"
            vals["rma_type_solution"]="rejected"
            vals["state"]="negotiation_rejected"
            if not r.rma_customer_remote_claim:
                vals["state_product"]="waiting_location"
                vals["state_process"]="location"
            else:
                vals["state_process"]="finished"
            r.sudo().write(vals)

    # ** SOLUCION(solucion) **************************************************************************************************************
    # Abono a Cliente                   >  action_solution_refund_to_customer           > can_be_solution_refund_to_customer            state = ='solution_waiting_refund'
    can_be_solution_refund_to_customer = fields.Boolean(
        compute ="_compute_can_be_solution_refund_to_customer",
    )
    def _compute_can_be_solution_refund_to_customer(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_solution == 'refund':
                if r.state == 'solution_waiting_refund':
                    visible = True
            r.can_be_solution_refund_to_customer = visible
    def action_solution_refund_to_customer(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "state_process":"solution",
                "state":"solution_refunded",
            })
    
    # Enviar a reparar                  >  action_solution_delivery_to_repair           > can_be_solution_delivery_to_repair            state = ='solution_waiting_repair'
    can_be_solution_delivery_to_repair = fields.Boolean(
        compute ="_compute_can_be_solution_delivery_to_repair",
    )
    def _compute_can_be_solution_delivery_to_repair(self):
        """Compute ''. 
                Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_solution == 'repair':
                if r.state == 'solution_waiting_repair':
                    visible = True
            r.can_be_solution_delivery_to_repair = visible
    def action_solution_delivery_to_repair(self):
        #wdb.set_trace()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            r.sudo().write({
                "state_product":"sent_to_repair",
            })

    # Recibir reparado                  >  action_solution_receive_repaired             > can_be_solution_receive_repaired              state = ='solution_repaired'
    can_be_solution_receive_repaired = fields.Boolean(
        compute ="_compute_can_be_solution_receive_repaired",
    )
    def _compute_can_be_solution_receive_repaired(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_solution == 'repair':
                if r.state_product == 'sent_to_repair':
                    visible = True
            # asignacion
            r.can_be_solution_receive_repaired = visible
    def action_solution_receive_repaired(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "state_process":"location",
                "state":"solution_repaired",
                "state_product":"waiting_location",
            })

    # Solicitar producto a sustituir    >  action_solution_request_for_replace          > can_be_solution_request_for_replace           state = ='solution_waiting_replace'
    can_be_solution_request_for_replace = fields.Boolean(
        compute ="_compute_can_be_solution_request_for_replace",
    )
    def _compute_can_be_solution_request_for_replace(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_solution == 'replace':
                if r.state == 'negotiation_accepted_to_replace':
                        visible = True
            # asignacion
            r.can_be_solution_request_for_replace = visible
    def action_solution_request_for_replace(self):
        #wdb.set_trace()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            r.sudo().write({
                "state":"solution_waiting_replace",
                "state_product":"waiting_request_to_replace",
            })

    # Recibir producto a sustituir      >  action_solution_receive_for_replace          > can_be_solution_receive_for_replace           state = =''
    can_be_solution_receive_for_replace = fields.Boolean(
        compute ="_compute_can_be_solution_receive_for_replace",
    )
    def _compute_can_be_solution_receive_for_replace(self):
        #wdb.set_trace()
        visible = False
        for r in self:
            if r.rma_type_solution == 'replace':
                if r.state_product == 'waiting_request_to_replace':
                    visible = True
            # asignacion
            r.can_be_solution_receive_for_replace = visible
    def action_solution_receive_for_replace(self):
        #wdb.set_trace()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            r.sudo().write({
                "state_process":"location",
                "state":"solution_replaced",
                "state_product":"waiting_location",
            })

    # ** DESTINO FINAL PIEZA(location) ***************************************************************************************************
    # Enviar al cliente                   >  action_location_delivery_to_customer         > can_be_location_delivery_to_customer          state_process = ='location' & not rma_customer_remote_claim
    can_be_location_delivery_to_customer = fields.Boolean(
            compute="_compute_can_be_location_delivery_to_customer",
        )
    @api.depends("state")
    def _compute_can_be_location_delivery_to_customer(self):
        """Compute 'can_be'. This field controls the visibility
        of 'Replace' button in the rma form
        view and determinates if an rma can be replaced.
        This field is used in:
        rma._compute_can_be_split
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if not r.rma_customer_remote_claim:
                if r.rma_owner_product in ['internal_rma','internal_sat']:
                    if r.state_process == 'location':
                        if r.state_product == 'waiting_location':
                            visible = True
            # asignacion
            r.can_be_location_delivery_to_customer = (r.state=='waiting_return_to_customer')
    def action_location_delivery_to_customer(self):
        #wdb.set_trace()
        self.create_delivery_to_customer()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            vals = {}
            vals["rma_type_final_location"]="costumer"
            vals["rma_owner_product"]="costumer"
            vals["state"]="returned_to_customer"
            vals["state_product"]="sent_to_customer"
            vals["state_process"]="finished"
            r.sudo().write(vals)


    # Enviar a stock                      >  action_location_send_to_stock                > can_be_location_send_to_stock                 state_process = ='location' & not rma_customer_remote_claim
    can_be_location_send_to_stock = fields.Boolean(
            compute="_compute_can_be_location_send_to_stock",
        )
    @api.depends("state")
    def _compute_can_be_location_send_to_stock(self):
        """Compute 'can_be_location_send_to_stock'. 
            Podemos chatarrear la pieza siempre que el cliente este
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if not r.rma_customer_remote_claim:
                if r.rma_owner_product in ['internal_rma','internal_sat']:
                    if r.state_process == 'location':
                        if r.state_product == 'waiting_location':
                            visible = True
            r.can_be_location_send_to_stock = visible
    def action_location_send_to_stock(self):
        #wdb.set_trace()
        #self.create_send_to_stock()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            vals = {}
            vals["rma_type_final_location"]="stock"
            vals["rma_owner_product"]="internal_rma"
            vals["state_product"]="in_stock"
            vals["state"]="in_stock"
            vals["state_process"]="finished"
            r.sudo().write(vals)

    # Enviar a chatarra                   >  action_location_send_to_scrap                > can_be_location_send_to_scrap                 state_process = ='location' & not rma_customer_remote_claim
    can_be_location_send_to_scrap = fields.Boolean(
            compute="_compute_can_be_location_send_to_scrap",
        )
    @api.depends("state")
    def _compute_can_be_location_send_to_scrap(self):
        """Compute 'can_be_location_send_to_scrap'. 
            Podemos enviar la pieza a stock para su nueva venta
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            if not r.rma_customer_remote_claim:
                if r.rma_owner_product in ['internal_rma','internal_sat']:
                    if r.state_process == 'location':
                        if r.state_product == 'waiting_location':
                            visible = True
            r.can_be_location_send_to_scrap = visible
    def action_location_send_to_scrap(self):
        #wdb.set_trace()
        #self.create_send_to_stock()
        for r in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            vals = {}
            vals["rma_type_final_location"]="scrap"
            vals["rma_owner_product"]="internal_scrap"
            vals["state_product"]="in_scrap"
            vals["state"]="in_scrap"
            vals["state_process"]="finished"
            r.sudo().write(vals)
    def create_send_to_scrap(self):
        # Creamos y validamos el movimiento de la pieza a chatarra
        #wdb.set_trace()
        self.ensure_one()
        # Rma Orrgin
        # En los movimientos de RMA solo podremos desechar la pieza en el caso en el que este recepcionada y fisicamente este en nuestro poder
        # Si ha sido recepdionada desde proveedor por un rechazo de RMA, cogeremos esta como ultimo movimiento antes de ser desechado
        mv_scrap = self.purchase_return_reject_move_id
        # En caso de que no haya recepcion de proveedor tomaremos la recepcion del RMA de la pieza 
        if not mv_scrap:
            mv_scrap = self.reception_move_id
        # Verificamos que la pieza ha sido recibida
        if mv_scrap:
            # Registramos el piching que va a ser desechado para posteriores consultas
            self.sudo().write({
                'scrap_move_id' : mv_scrap,
                'state':'finished',        
                'state_process':'finished',        
                'state_product':'scrapped',        
                }
            )
           #wdb.set_trace()
            # Llamamos a la funcion de stock.scrap que gestionara la devolucion del picking
            stock_scrap = self.env['stock.scrap'].sudo().create({
                'name': "SP-{}".format(self.name),
                'origin':self.name,
                'move_id': mv_scrap.id,
                'picking_id': mv_scrap.picking_id.id,
                'product_id': mv_scrap.product_id.id,
                'product_uom_id': mv_scrap.product_uom.id,
                'location_id': mv_scrap.location_dest_id.id,
                'scrap_qty': mv_scrap.product_qty,
            })
            stock_scrap.send_to_scrap(mv_scrap, self.name)

    # ####################################################################################################################################
    # ####################################################################################################################################


    # ####################################################################################################################################
    # ####### Logica de negocio ##########################################################################################################
    # ####################################################################################################################################
    # ACTION Negociacion to solution
    # Crear Abono al cliente
    def create_refund_to_costumer(self):
        """Invoked when 'Refund' button in rma form view is clicked
        and 'rma_refund_action_server' server action is run.
        """
        group_dict = {}
        for r in self.filtered("can_be_refunded"): 
            key = (r.partner_invoice_id.id, r.company_id.id)
            group_dict.setdefault(key, self.env["rma"])
            group_dict[key] |= r
        for rmas in group_dict.values():
            origin =", ".join(rmas.mapped("name"))
            sale_form = Form(
                self.env["sale.order"]
                .sudo()
                .with_context(
                    default_move_type="out_refund",
                    company_id=rmas[0].company_id.id,
                ),
                "sale.view_order_form",
            )
            rmas[0]._prepare_refund_order(sale_form, origin)
            refund = sale_form.save()
            #wdb.set_trace()
            #refund.update(
            #    procurement_group_id = self.sale_group_id.id
            #)

            for rma in rmas:
                # For each iteration the Form is edited, a new invoice line
                # is added and then saved. This is to generate the other
                # lines of the accounting entry and to specify the associated
                # RMA to that new invoice line.
                sale_form = Form(refund)
                with sale_form.order_line.new() as line_form:
                    rma._prepare_refund_order_line(line_form,origin)
                refund = sale_form.save()
               #wdb.set_trace()
                #Datos de seguiimiento de reembolso
                line = refund.order_line.filtered(lambda r: not r.rma_id)
                line.rma_id = rma.id
                rma.sudo().write(
                    {
                        "refund_sale_order_id": refund.id,
                        "refund_sale_order_line_id": line.id,
                        "state": "solution_waiting_refund",
                        "state_process":"solution",
                    }
                )
            refund.with_user(self.env.uid).message_post_with_view(
                "mail.message_origin_link",
                values={"self": refund, "origin": rmas},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
    
    # Envio de pieza al cliente
    def create_delivery_to_customer(self):
        # Validamos el picking de envio a cliente de la pieza rechazada
        #wdb.set_trace()
        self.ensure_one()
        stock_warehouse_id = (
            self.env["stock.warehouse"]
            .search([("company_id", "=", self.order_id.company_id.id)])
            )
        # Obtenemoos el picking_type correspondiente al "RMA pproveedores Salidas"
        rma_out_type_id = stock_warehouse_id.mapped("rma_out_type_id")
        # Obtenemos elmovimiento pendioente de validar para la operacion de salida de RMA a cliente
        moves =  self.delivery_move_ids.filtered(
                        lambda r: r.picking_type_id == rma_out_type_id 
                    )
        for move in moves:
            #wdb.set_trace()
            if move.state == 'assigned':
                if move.picking_id:
                    if self.state == "waiting_return":
                        self.sudo().write({
                            "state":"returned_to_customer",
                            "state_process":"finished"            
                        })
                    elif self.state == "solution_waiting_replace":
                        self.sudo().write({
                            "state":"solution_replaced",
                            "state_process":"finished"            
                        })
                    move.picking_id.validate_picking()

    # La pieza será retornada al cliente
    def create_return(self, scheduled_date, qty, uom):
        #wdb.set_trace()
        # Ponemos el estado en esperando retorno, que pasara a retornado 
        # cuando se confirme la entrega al cliente o mensajero
        self.sudo().write(
            {
                "state": "waiting_return",
            }
        )
        res = super().create_return(scheduled_date, qty, uom)
        #wdb.set_trace()
        return res

    # Crea el envio a chatarrear
    def create_send_to_scrap(self):
        # Creamos y validamos el movimiento de la pieza a chatarra
        #wdb.set_trace()
        self.ensure_one()
        # Rma Orrgin
        # En los movimientos de RMA solo podremos desechar la pieza en el caso en el que este recepcionada y fisicamente este en nuestro poder
        # Si ha sido recepdionada desde proveedor por un rechazo de RMA, cogeremos esta como ultimo movimiento antes de ser desechado
        mv_scrap = self.purchase_return_reject_move_id
        # En caso de que no haya recepcion de proveedor tomaremos la recepcion del RMA de la pieza 
        if not mv_scrap:
            mv_scrap = self.reception_move_id
        # Verificamos que la pieza ha sido recibida
        if mv_scrap:
            # Registramos el piching que va a ser desechado para posteriores consultas
            self.sudo().write({
                'scrap_move_id' : mv_scrap,
                'state':'finished',        
                'state_process':'finished',        
                'state_product':'scrapped',        
                }
            )
           #wdb.set_trace()
            # Llamamos a la funcion de stock.scrap que gestionara la devolucion del picking
            stock_scrap = self.env['stock.scrap'].sudo().create({
                'name': "SP-{}".format(self.name),
                'origin':self.name,
                'move_id': mv_scrap.id,
                'picking_id': mv_scrap.picking_id.id,
                'product_id': mv_scrap.product_id.id,
                'product_uom_id': mv_scrap.product_uom.id,
                'location_id': mv_scrap.location_dest_id.id,
                'scrap_qty': mv_scrap.product_qty,
            })
            stock_scrap.send_to_scrap(mv_scrap, self.name)

    # Metodos complentarios 
    # RETORNO DE RMA A PROVEEDOR PARA SU VALORACION
    # Añadimos la logica de negocio de retorno de pieza a proveedor
    # Returning business methods
    # Retorno o envio de la pieza en devolucion o garantia al proveedor
    def create_delivery_to_supplier(self, scheduled_date=fields.Datetime.now(), qty=None, uom=None):
        """Intended to be invoked by the delivery wizard"""
        #wdb.set_trace()
        # Verifica la configuracion del RMA si hay grupos de devolucion de RMA
        group_returns = self.env.company.rma_return_grouping
        # Verificamos si lo hay y obtenemos el valor
        if "rma_return_grouping" in self.env.context:
            group_returns = self.env.context.get("rma_return_grouping")
        # Verificamos si el producto puede ser retornado al proveedor
        self._ensure_can_be_validation_receive_from_supplier()
        # Verificamos si la cantidad puede ser retornada
        self._ensure_qty_to_return(qty, uom)
        #
        group_dict = {}
        #
        rmas_to_return_supplier = self.filtered("can_be_validation_receive_from_supplier")
        #
        #wdb.set_trace()
        for r in rmas_to_return_supplier:
            #
            # Para buscar el id del proveedor registrado en la ficha de producto
            # r.product_id.seller_ids[0].name  # > esto nos da el res.partner(xxx) 
            key = (
                r.purchase_supplier_partner_id,
                r.company_id.id,
                r.warehouse_id,
            )
            # Creamos la la clave en el diccionario y le asignamos el tipo del valor en este caso sera un objeto 'rma'
            group_dict.setdefault(key, self.env["rma"])
            # Le asignamos un valor de tipo rma a la clave creada 
            group_dict[key] |= r
    
        #
        if group_returns:
            grouped_rmas = group_dict.values()
        else:
            grouped_rmas = rmas_to_return_supplier
        #
        for rmas in grouped_rmas:
            origin =", ".join(rmas.mapped("name"))
            # En esta linea es donde asigna el tipo de operacion
            #wdb.set_trace()
            for rma in rmas:
                rma_out_type = rma.warehouse_id.rma_supplier_out_type_id
                #
                picking_form = Form(
                    rp=self.env["stock.picking"].with_context(
                        default_picking_type_id = rma_out_type.id
                    ),
                    view="stock.view_picking_form",
                )
                #
                rma._prepare_supplier_returning_picking(picking_form, origin)
                #wdb.set_trace()
                picking = picking_form.save()

                #wdb.set_trace()
                with picking_form.move_ids_without_package.new() as move_form:
                    #wdb.set_trace()
                    rma._prepare_supplier_returning_move(move_form, scheduled_date, qty, uom)
                    #rma._prepare_supplier_returning_move(move_form, qty, uom)
                # rma_id is not present in the form view, so we need to get
                # the 'values to save' to add the rma id and use the
                # create method intead of save the form.
                #wdb.set_trace()
                picking_vals = picking_form._values_to_save(all_fields=True)
                move_vals = picking_vals["move_ids_without_package"][-1][2]
                #wdb.set_trace()
                move_vals.update(
                    picking_id=picking.id,
                    rma_id=rma.id,
                    company_id=picking.company_id.id, 
                )
                if "product_qty" in move_vals:
                    move_vals.pop("product_qty")
                move_ids = self.env["stock.move"].sudo().create(move_vals)
                #wdb.set_trace()
                #Asignamos el movimiento de retorno a proveedor
                self.purchase_return_move_id = move_ids.id
                rma.message_post(
                    body=_(
                        'Return: <a href="#" data-oe-model="stock.picking" '
                        'data-oe-id="%d">%s</a> has been created.'
                    )
                    % (picking.id, picking.name)
                )
                picking.move_lines = [(6,0,move_ids.ids)]
            po_id = (self.create_refund_purchase() or None)
            #wdb.set_trace()
            picking.purchase_id = po_id
            #wdb.set_trace()
            picking.action_confirm()
            picking.action_assign()
            picking.message_post_with_view(
                "mail.message_origin_link",
                values={"self": picking, "origin": rmas},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
            # Actualizamos los valores de estado
            after_action_vals = {
                'rma_owner_product':'supplier',
                'rma_type_resolution':'waiting',
                'state_process':'resolution', 
                "state":"resolution_waiting",            
                'state_product':'sent_to_supplier',
                "state_purchase":"waiting_response_supplier",            
            }
            self.sudo().write(after_action_vals)


        return picking
    def _ensure_can_be_validation_receive_from_supplier(self):
        """
        Este método está pensado para ser invocado después de que el usuario haga clic en
        'Reemplazar' o 'Return to customer' button (before the delivery wizard
        is launched) y luego confirme el asistente.

        Este método es invocado por:
        rma.create_return_supplier
        """
        #wdb.set_trace()
        if len(self) == 1:
            if not self.can_be_validation_receive_from_supplier:
                raise ValidationError(_("ThEste RMA no puede realizar una devolución."))
        elif not self.filtered("can_be_validation_receive_from_supplier"):
            raise ValidationError(_("Ninguno de los RMA seleccionados puede realizar una devolución."))

    # recepcion de la pieza rechazada por el proveedor
    def create_return_reject_supplier(self, scheduled_date=fields.Datetime.now(), qty=None, uom=None):
        """Intended to be invoked by the delivery wizard"""
        #wdb.set_trace()
        # Verifica la configuracion del RMA si hay grupos de devolucion de RMA
        group_returns = self.env.company.rma_return_grouping
        # Verificamos si lo hay y obtenemos el valor
        if "rma_return_grouping" in self.env.context:
            group_returns = self.env.context.get("rma_return_grouping")
        # Verificamos si el producto puede ser retornado al proveedor    
        self._ensure_can_be_returned_reject_supplier()
        # Verificamos si la cantidad puede ser retornada
        #self._ensure_qty_to_return(qty, uom)
        # 
        group_dict = {}
        #
        rmas_to_return_reject_supplier = self.filtered("can_be_returned_reject_supplier")
        #
        for r in rmas_to_return_reject_supplier:
            #
            key = (
                r.purchase_supplier_partner_id,
                r.company_id.id,
                r.warehouse_id,
            )
            #
            group_dict.setdefault(key, self.env["rma"])
            #
            group_dict[key] |= r
    
        #
        if group_returns:
            grouped_rmas = group_dict.values()
        else:
            grouped_rmas = rmas_to_return_reject_supplier
        #
        for rmas in grouped_rmas:
            origin =", ".join(rmas.mapped("name"))
            # En esta linea es donde asigna el tipo de operacion
            #wdb.set_trace()
            for rma in rmas:
                rma_in_type = rma.warehouse_id.rma_supplier_in_type_id
                #
                picking_form = Form(
                    rp=self.env["stock.picking"].with_context(
                        default_picking_type_id = rma_in_type.id
                    ),
                    view="stock.view_picking_form",
                )
                #
                rma._prepare_supplier_reject_returning_picking(picking_form, origin)
                #wdb.set_trace()
                picking = picking_form.save()
                
                #wdb.set_trace()
                with picking_form.move_ids_without_package.new() as move_form:
                    #wdb.set_trace()
                    rma._prepare_supplier_reject_returning_move(move_form, scheduled_date, qty, uom)
                    #rma._prepare_supplier_returning_move(move_form, qty, uom)
                # rma_id is not present in the form view, so we need to get
                # the 'values to save' to add the rma id and use the
                # create method intead of save the form.
                #wdb.set_trace()
                picking_vals = picking_form._values_to_save(all_fields=True)
                move_vals = picking_vals["move_ids_without_package"][-1][2]
               #wdb.set_trace()
                move_vals.update(
                    picking_id=picking.id,
                    rma_id=rma.id,
                    company_id=picking.company_id.id, 
                )
                if "product_qty" in move_vals:
                    move_vals.pop("product_qty")
                move_ids = self.env["stock.move"].sudo().create(move_vals)
                #wdb.set_trace()
                #Asignamos el movimiento de retorno a proveedor
                self.purchase_return_reject_move_id = move_ids.id
                self.sudo().write({
                    'last_move_id': self.purchase_return_reject_move_id
                })
                rma.message_post(
                    body=_(
                        'Return: <a href="#" data-oe-model="stock.picking" '
                        'data-oe-id="%d">%s</a> has been created.'
                    )
                    % (picking.id, picking.name)
                )
                picking.move_lines = [(6,0,move_ids.ids)]
            # Cancelamos la order de compra rechazada
            #po_id = (self.create_refund_purchase() or None)
            #picking.purchase_id = po_id
            #wdb.set_trace()
            picking.action_confirm()
            if picking.state != "assigned":
                picking.action_Force_assign()    
            picking.action_assign()
            picking.validate_picking()
            picking.message_post_with_view(
                "mail.message_origin_link",
                values={"self": picking, "origin": rmas},
                subtype_id=self.env.ref("mail.mt_note").id,
            )

            # Actualizamos los valores de estado
            # recepcion de la pieza rechazada por el proveedor
            after_action_vals = {
                'rma_owner_product':'internal_rma',
                'state_product':'received_from_supplier',
                "state_purchase":"reject_returned_by_supplier",            
            }
            self.sudo().write(after_action_vals)

        return picking
    def _ensure_can_be_returned_reject_supplier(self):
        """Este método está pensado para ser invocado después de que el usuario haga clic en
        Botón 'Reemplazar' o 'Devolver al cliente' (antes del asistente de entrega
        se inicia) y después de confirmar el wizard.

        This method is invoked by:
        rma.create_return_supplier
        """
        #wdb.set_trace()
        if len(self) == 1:
            if not self.can_be_returned_reject_supplier:
                raise ValidationError(_("This RMA cannot perform a return."))
        elif not self.filtered("can_be_validation_receive_from_supplier"):
            raise ValidationError(_("None of the selected RMAs can perform a return."))

    # REFUND PURCHASE  
    # ACCION DE REEMBOLSO A PROVEEDOR  
    def create_refund_purchase(self):
        """Invoked when 'Refund' button in rma form view is clicked
        and 'rma_refund_action_server' server action is run.
        """
        # En primer lugar realizamos el picking de salida
        # self.action_return_supplier()  # Esto no funciiona

        group_dict = {}
        # Directamente usaremos el rma del self
        for r in self:
            #wdb.set_trace()
            key = (r.partner_id.id, r.company_id.id)
            group_dict.setdefault(key, self.env["rma"])
            group_dict[key] |= r
        for rmas in group_dict.values():
            origin =", ".join(rmas.mapped("name"))
            #wdb.set_trace()
            purchase_form = Form(
                self.env["purchase.order"]
                .sudo()
                .with_context(
                    default_move_type="out_refund_purchase",
                    company_id=rmas[0].company_id.id,
                ),
                "purchase.purchase_order_form",
            )
            rmas[0]._prepare_refund_purchase_order(purchase_form, origin)
            refund = purchase_form.save()
            #wdb.set_trace()
            for rma in rmas:
                # For each iteration the Form is edited, a new invoice line
                # is added and then saved. This is to generate the other
                # lines of the accounting entry and to specify the associated
                # RMA to that new invoice line.
                purchase_form = Form(refund)
                with purchase_form.order_line.new() as line_form:
                    rma._prepare_refund_purchase_order_line(line_form,origin)
                refund = purchase_form.save()
                #wdb.set_trace()
                #refund.update(
                #    group_id = self.purchase_group_id.id
                #)
                #wdb.set_trace()
                #Datos de seguiimiento de reembolso
                line = refund.order_line.filtered(lambda r: not r.rma_id)
                line.rma_id = rma.id
                # actualizamos los valores del estado
                after_action_vals = {
                        "refund_purchase_order_id": refund.id,
                        "refund_purchase_order_line_id": line.id,
                        "state_purchase": "waiting_confirm_refund",
                        "state_process":"negotiation",
                        "state": "resolution_accepted",
                        "rma_type_resolution":"accepted",
                        "rma_type_negotiation":"in_progress",
                    }
                self.sudo().write(after_action_vals)

            refund.with_user(self.env.uid).message_post_with_view(
                "mail.message_origin_link",
                values={"self": refund, "origin": rmas},
                subtype_id=self.env.ref("mail.mt_note").id,
            )
            #wdb.set_trace()
            # Actualizamos los valores de estado
            # recepcion de la pieza rechazada por el proveedor
            
            return refund
        return None
    def _prepare_refund_order(self, order_form, origin):
        """Hook method for preparing the refund Form.

        This method could be override in order to add new custom field
        values in the refund creation.

        invoked by:
        rma.action_refund
        """
        #wdb.set_trace()
        self.ensure_one()
        order_form.partner_id = (self.order_id.partner_id or None)
        order_form.partner_invoice_id = (self.order_id.partner_invoice_id  or None)
        order_form.partner_shipping_id = (self.order_id.partner_shipping_id  or None)
        order_form.payment_term_id = (self.order_id.payment_term_id or None)
        order_form.rma_refund =True
        order_form.rma_refund_id = (self or None)
        order_form.client_order_ref = 'DEV {} || {}'.format(self.order_id.name,self.order_id.client_order_ref)
    def _prepare_refund_order_line(self, line_form, origin):
        """
        Hook method for preparing a refund line Form.
        This method could be override in order to add new custom field
        values in the refund line creation.
        invoked by:
        rma.action_refund
        """
        #wdb.set_trace()
        self.ensure_one()
        product = self._get_refund_line_product()
        qty, uom = self._get_refund_line_quantity()
        line_form.product_id = product
        line_form.product_uom_qty = qty*-1
        line_form.product_uom = uom
        line_form.price_unit = self._get_refund_line_price_unit()
        line_form.discount = self.sale_line_id.discount
    
    # Preparacion del picking de Envio de la pieza al proveedor para su valoracion
    def _prepare_supplier_returning_picking(self, picking_form, origin=None):
        #wdb.set_trace()
        #Para creamos el movimiento de linea para que no aparezca vacio meve_lines_ids
        picking_form.picking_type_id = self.warehouse_id.rma_supplier_out_type_id
        picking_form.origin = (origin or self.name)
        picking_form.location_id = self.location_id
        picking_form.location_dest_id = self.purchase_receive_move_id.location_id
        picking_form.partner_id = (self.purchase_supplier_partner_id or None)
        #picking_form.group_id = (self.procurement_group_id or None)
        picking_form.sale_id = (self.order_id or None)
    # Si la garantia o devolucion enviada al proveedoor es recibida como rechazada,daremos entrada al rechazo
    def _prepare_supplier_reject_returning_picking(self, picking_form, origin=None):
        #wdb.set_trace()
        #Para creamos el moviimiento de linea para que no aparezca vacio meve_lines_ids
        picking_form.picking_type_id = self.warehouse_id.rma_supplier_in_type_id
        picking_form.origin = (origin or self.name)
        picking_form.location_id = self.purchase_receive_move_id.location_id  # DESDE PROVEEDOR
        picking_form.location_dest_id = self.location_id                        # HASTA RMA/IN
        picking_form.partner_id = (self.purchase_supplier_partner_id or None)
        #picking_form.group_id = (self.procurement_group_id or None)
        picking_form.sale_id = (self.order_id or None)
    def _prepare_supplier_returning_move(self, move_form, scheduled_date=fields.Datetime.now(),quantity=None, uom=None):
        #wdb.set_trace()
        move_form.product_id = self.product_id
        #wdb.set_trace()
        #move_form.group_id =  self.purchase_group_id or None  # error necesita estar en la vista
        move_form.product_uom_qty = quantity or self.product_uom_qty
        move_form.product_uom = uom or self.product_uom
        move_form.date = scheduled_date
        #move_form.origin = self.name
        #move_form.group_id =  self.procurement_group_id or None  # error necesita estar en la vista
        #move_form.warehouse_id = self.warehouse_id
    def _prepare_supplier_reject_returning_move(self, move_form, scheduled_date=fields.Datetime.now(),quantity=None, uom=None):
        #wdb.set_trace()
        move_form.product_id = self.product_id
        #wdb.set_trace()
        move_form.product_uom_qty = quantity or self.product_uom_qty
        move_form.product_uom = uom or self.product_uom
        move_form.date = scheduled_date
        #move_form.origin = self.name
        #move_form.group_id =  self.procurement_group_id or None  # error necesita estar en la vista
        #move_form.warehouse_id = self.warehouse_id
    # Refund business methods
    def _prepare_refund_purchase_order(self, order_form, origin):
        """Hook method for preparing the refund Form.

        This method could be override in order to add new custom field
        values in the refund creation.

        invoked by:
        rma.action_refund
        """
        #wdb.set_trace()
        self.ensure_one()
        order_form.partner_id = (self.purchase_id.partner_id or None)
        order_form.rma_refund =True
        order_form.rma_refund_id = (self or None)
        order_form.partner_ref = 'DEV {} || {} '.format(self.purchase_id.name, self.purchase_id.partner_ref)
    def _prepare_refund_purchase_order_line(self, line_form, origin):
        """Hook method for preparing a refund line Form.
        This method could be override in order to add new custom field
        values in the refund line creation.
        invoked by:
        rma.action_refund
        """
        #wdb.set_trace()
        self.ensure_one()
        product = self._get_refund_purchase_line_product()
        qty, uom = self._get_refund_purchase_line_quantity()
        line_form.product_id = product
        line_form.product_qty = qty*-1
        line_form.product_uom = uom
        line_form.price_unit = self._get_refund_purchase_line_price_unit()
    def _get_refund_purchase_line_product(self):
        """To be overriden in a third module with the proper origin values
        in case a kit is linked with the rma"""
        return self.purchase_order_line_id.product_id
    def _get_refund_purchase_line_quantity(self):
        """To be overriden in a third module with the proper origin values
        in case a kit is linked with the rma"""
        return (self.purchase_order_line_id.product_uom_qty, self.product_uom)
    def _get_refund_purchase_line_price_unit(self):
        """To be overriden in a third module with the proper origin values
        in case a sale order is linked to the original move"""
        return self.purchase_order_line_id.price_unit
    def _get_extra_purchase_refund_line_vals(self):
        """Override to write aditional stuff into the refund line"""
        return {}
    # Extract business methods 
    # Sobreescreibimos este metdo para añadirle el estado de la pieza y del RMA
    def extract_quantity(self, qty, uom):
        res = super(Rma,self).extract_quantity(qty, uom)
        if self.remaining_qty_to_done <= 0:
            if self.state in ['waiting_return_to_customer','solution_waiting_replace']:
                self.state_process = "finished"
        return res



    # ACTION Reception to validation
    """
    def update_received_state_on_reception(self):
        #wdb.set_trace()
        self.sudo().write({
            "rma_received" : True,
            "state": "received",
            "state_product": "received",
            "state_process":"validation",
        })
        self._send_receipt_confirmation_email()


            def action_receive_reject_rma_supplier(self):
        #wdb.set_trace()
        self.ensure_one()
        self.purchase_return_reject_move_id.picking_id.validate_picking()
        self.sudo().write({
            "state_purchase":"reject_returned_by_supplier"            
        })
    """
