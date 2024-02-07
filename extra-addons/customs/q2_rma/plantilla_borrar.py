import wdb
from collections import Counter
from email.policy import default
from odoo.exceptions import ValidationError
from odoo import models, fields, api
from odoo.tests import Form
from odoo import tools
from odoo.tools import float_compare
from odoo import _

class Plantilla:

    """ @values
    rma_received                :   True , False
    rma_customer_remote_claim   :   True , False    
    rma_supplier_remote_claim   :   True , False    
    rma_external_remote_claim   :   True , False    

    state_process               :   draft , reception , validation , resolution , negotiation , solution , location , finished  
    state              reception:   confirmed , received
                      validation:   validation_waiting , validation_internal , validation_external , validation_supplier   
                      resolution:   resolution_accepted , resolution_rejected
                     negotiation:   negotiation_waiting , negotiation_accepted_to_repair , negotiation_accepted_to_replace , negotiation_accepted_to_refund , negotiation_rejected 
                        solution:   solution_waiting_repair , solution_repaired , solution_waiting_replace , solution_replaced , solution_waiting_refund , solution_refunded ,  ,  ,  ,  , 
                        location:   waiting_return_to_customer , returned_to_customer
                        close:   
    state_product      reception:   nothing , waiting_reception , received , remote
             validation_internal:   waiting_check_internal , checked_internal
             validation_external:   waiting_send_to_external , sent_to_external , waiting_receive_from_external , received_from_external , scrapped_from_external
             validation_supplier:   waiting_send_to_supplier , sent_to_supplier , waiting_receive_from_supplier , received_from_supplier , scrapped_from_supplier
                 solution_repair:   waiting_send_to_repair , sent_to_repair , received_repaired 
                solution_replace:   waiting_request_to_replace , requested_to_replace , receive_repaired
            location_to_costumer:   waiting_send_to_customer , sent_to_customer 
               location_to_stock:   waiting_send_to_stock , in_stock
               location_to_scrap:   waiting_send_to_scrap, scrapped
    state_purchase              :   no_purchase , waiting_action_purchase , send_to_supplier , waiting_send_to_supplier , waiting_response_supplier , 
                                    reject_by_supplier , reject_waiting_return_by_supplier , reject_scrapped_by_supplier , reject_returned_by_supplier , 
                                    accepted_by_supplier , accepted_waiting_confirm_refund , accepted_refunded_from_supplier , 
    rma_resolution_result       :   nothing , waiting , in_progress , accepted , rejected
    rma_negotiation_result      :   nothing , waiting , in_progress , accepted , rejected
    rma_type_solution           :   nothing , waiting , accepted_repair , accepted_replace , accepted_refund , rejected
    rma_type_resolution_supplier:   nothing , waiting , accepted , rejected 
    rma_type_solution_supplier  :   nothing , waiting , accepted_repair , accepted_replace , accepted_refund , rejected
    """
    """
        self.sudo().write({
            'state_process':'', 
            'state':'',
            'state_product':'',
        })
    
    """
    # ####################################################################################################################################
    # ####### VISIBLE INFO BUTTON ########################################################################################################
    # ####################################################################################################################################
    
    # ** RECEPCION(reception) ************************************************************************************************************
    # RMA Remoto                  >   action_view_rma_remote                              > visible_info_button_rma_remote
    # RMA Pte Recibir             >   action_view_rma_waiting_to_receive                  > visible_info_button_rma_waiting_to_receive
    # RMA Recibido                >   action_view_rma_received                            > visible_info_button_rma_received
    # Venta                       >   action_view_sale_order                              > visible_info_button_sale_order  
    # ** GESTION CON PROVEEDOR ***********************************************************************************************************
    # Compra                      >   action_view_purchase_order                          > visible_info_button_purchase_order
    # Pte Abono Proveedor         >   action_view_waiting_refund_purchase_to_invoice      > visible_info_button_waiting_refund_purchase_to_invoice
    # Abonado por Proveedor       >   action_view_refund_purchase_invoiced                > visible_info_button_refund_purchase_invoiced
    # ** SOLUCION / ABONO(solution) ******************************************************************************************************
    # Pte abono Cliente           >   action_view_waiting_refund_sale_to_invoice          > visible_info_button_waiting_refund_sale_to_invoice
    # Abonado a Cliente           >   action_view_refund_sale_invoiced                    > visible_info_button_refund_sale_invoiced 
    # ** DESTINO FINAL PIEZA(location) ***************************************************************************************************
    # Enviado a cliente           >   action_view_sent_to_customer                        > visible_info_button_sent_to_customer
    # Desechado                   >   action_view_move_scrap                              > visible_info_button_move_scrap

    # ####################################################################################################################################
    # ####### CAN BE #####################################################################################################################
    # ####################################################################################################################################

    # ** RECEPCION(reception) ************************************************************************************************************
    # Recepcionar RMA                     >  action_receive_rma_costumer                    > can_be_receive_from_costumer                    state_process = ='reception' 
    # Gestión Remota RMA                  >  action_remote_rma_costumer                     > can_be_receive_from_costumer      
    # ** VALIDACION(validation) **********************************************************************************************************
    # Valoración interna                  >  action_internal_validate                     > can_be_validate                               state_process = ='validation' & state = ='validation_waiting'
    # Valoración externa                  >  action_external_validate                     > can_be_validate                    
    # Valoración Proveedor                >  action_supplier_validate                     > can_be_validate                    
    # ** Validación INTERNA **************************************************************************************************************
    #  @ Enviar a taller                  >  action_validation_delivery_to_internal_test     > can_be_validation_delivery_to_internal_test         state = ='supplier_validate' & state_product = ='waiting_send_to_supplier' & not rma_customer_remote_claim
    #  @ Recibido desde taller            >  action_validation_received_from_internal_test   > can_be_validation_received_from_internal_test      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
    # ** Validación EXTERNO **************************************************************************************************************
    #  @ Gestion Remota Externo           >  action_validation_remote_external            > can_be_validation_remote_external               state = ='validation_external'
    #  @ Enviar a Externo                 >  action_validation_delivery_to_external       > can_be_validation_delivery_to_external        state = ='validation_external' & state_product = ='waiting_send_to_external' & not rma_customer_remote_claim
    #  @ Recibido desde Externo           >  action_validation_received_from_external     > can_be_validation_received_from_external      state_product = ='waiting_receive_from_external' & not rma_customer_remote_claim
    #  @ Desechado en Externo             >  action_validation_send_to_scrap_external     > can_be_validation_send_to_scrap_external      state_product = ='sent_to_external' & not rma_customer_remote_claim
    # ** Validación PROVEEDOR ************************************************************************************************************
    #  @ Gestion Remota Proveedor         >  action_validation_remote_supplier            > can_be_validation_remote_supplier               state = ='supplier_validate' 
    #    Enviar a proveedor               >  action_validation_delivery_to_supplier       > can_be_validation_delivery_to_supplier        state = ='supplier_validate' & state_product = ='waiting_send_to_supplier' & not rma_customer_remote_claim
    #    @ Recibido desde proveedor       >  action_validation_received_from_supplier     > can_be_validation_received_from_supplier      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
    #    Desechado en proveedor           >  action_validation_send_to_scrap_supplier     > can_be_validation_send_to_scrap_supplier      state_product = ='sent_to_supplier' & not rma_customer_remote_claim
    # ** RESOLUCION(resolution) **********************************************************************************************************
    # Reclamacion Aceptada                >  action_resolution_accepted                   > can_be_resolution_accepted                    state_process = ='resolution' 
    # Reclamacion Rechazada               >  action_resolution_rejected                   > can_be_resolution_rejected
    # ** NEGOCIACION(negotiation) ********************************************************************************************************
    # RMA Aceptado REPARAR                >  action_negotiation_accepted_to_repair        > can_be_negotiation_accepted_to_repair         state_process = ='negotiation' & not rma_customer_remote_claim
    # RMA Aceptado REEMPLAZAR             >  action_negotiation_accepted_to_replace       > can_be_negotiation_accepted_to_replace        state_process = ='negotiation' 
    # RMA Aceptado ABONAR                 >  action_negotiation_accepted_to_refund        > can_be_negotiation_accepted_to_refund         state_process = ='negotiation' 
    # RMA Rechazado                       >  action_negotiation_rejected                  > can_be_negotiation_rejected                   state_process = ='negotiation' 
    # ** SOLUCION(solucion) **************************************************************************************************************
    # @ Abono a Cliente                   >  action_solution_refund_to_customer           > can_be_solution_refund_to_customer            state = ='solution_waiting_refund'
    # @ Enviar a reparar                  >  action_solution_delivery_to_repair           > can_be_solution_delivery_to_repair            state = ='solution_waiting_repair'
    # @ Recibir reparado                  >  action_solution_receive_repaired             > can_be_solution_receive_repaired              state = ='solution_repaired'
    # @ Solicitar producto a sustituir    >  action_solution_request_for_replace          > can_be_solution_request_for_replace           state = ='solution_waiting_replace'
    # @ Recibir producto a sustituir      >  action_solution_receive_for_replace          > can_be_solution_receive_for_replace           state = =''
    # ** DESTINO FINAL PIEZA(location) ***************************************************************************************************
    # Enviar al cliente                   >  action_location_delivery_to_customer         > can_be_location_delivery_to_customer          state_process = ='location' & not rma_customer_remote_claim
    # Enviar a stock                      >  action_location_send_to_stock                > can_be_location_send_to_stock                 state_process = ='location' & not rma_customer_remote_claim
    # Enviar a chatarra                   >  action_location_send_to_scrap                > can_be_location_send_to_scrap                 state_process = ='location' & not rma_customer_remote_claim

    # ####################################################################################################################################
    # ####################################################################################################################################



    ## VALIDATION INTERNAL
    # _validation_delivery_to_internal_test
    can_be_validation_delivery_to_internal_test = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_internal_test",
    )
    def _compute_can_be_validation_delivery_to_internal_test(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_delivery_to_internal_test = visible
    def action_validation_delivery_to_internal_test(self):
        return False

    # _validation_received_from_internal_test
    can_be_validation_received_from_internal_test = fields.Boolean(
        compute ="_compute_can_be_validation_received_from_internal_test",
    )
    def _compute_can_be_validation_received_from_internal_test(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_traceee()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_received_from_internal_test = visible
    def action_validation_received_from_internal_test(self):
        return False

    # Gestion Remota Externo          >  action_validation_remote_external            > can_be_validation_remote_external               state = ='validation_external'
    can_be_validation_remote_external = fields.Boolean(
        compute ="_compute_can_be_validation_remote_external",
    )
    def _compute_can_be_validation_remote_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_traceeeeeeeeeeeeeee()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_remote_external = visible
    def action_validation_remote_external(self):
        return False
            
    # Enviar a Externo                >  action_validation_delivery_to_external       > can_be_validation_delivery_to_external        state = ='validation_external' & state_product = ='waiting_send_to_external' & not rma_customer_remote_claim
    can_be_validation_delivery_to_external = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_external",
    )
    def _compute_can_be_validation_delivery_to_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_delivery_to_external = visible
    def action_validation_delivery_to_external(self):
        return False

    # Recibido desde Externo          >  action_validation_received_from_external     > can_be_validation_received_from_external      state_product = ='waiting_receive_from_external' & not rma_customer_remote_claim
    can_be_validation_received_from_external = fields.Boolean(
        compute ="_compute_can_be_validation_received_from_external",
    )
    def _compute_can_be_validation_received_from_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_tracee()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_received_from_external = visible
    def action_validation_received_from_external(self):
        return False

    # Desechado en Externo            >  action_validation_send_to_scrap_external     > can_be_validation_send_to_scrap_external      state_product = ='sent_to_external' & not rma_customer_remote_claim
    can_be_validation_send_to_scrap_external = fields.Boolean(
        compute ="_compute_can_be_validation_send_to_scrap_external",
    )
    def _compute_can_be_validation_send_to_scrap_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_send_to_scrap_external = visible
    def action_validation_send_to_scrap_external(self):
        return False

    # Gestion Remota Proveedor        >  action_validation_remote_supplier            > can_be_validation_remote_supplier               state = ='supplier_validate' 
    can_be_validation_remote_supplier = fields.Boolean(
        compute ="_compute_can_be_validation_remote_supplier",
    )
    def _compute_can_be_validation_remote_supplier(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_remote_supplier = visible
    def action_validation_remote_supplier(self):
        return False
    
    # Recibido desde proveedor      >  action_validation_received_from_supplier     > can_be_validation_received_from_supplier      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
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

            # asignacion
            r._can_be_validation_received_from_supplier = visible
    def action_validation_received_from_supplier(self):
        return False
    
    #** SOLUCION(solucion) **
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
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_solution_refund_to_customer = visible
    def action_solution_refund_to_customer(self):
        return False
    
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
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_solution_delivery_to_repair = visible
    def action_solution_delivery_to_repair(self):
        return False

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
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_solution_receive_repaired = visible
    def action_solution_receive_repaired(self):
        return False

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
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_solution_request_for_replace = visible
    def action_solution_request_for_replace(self):
        return False

    # Recibir producto a sustituir      >  action_solution_receive_for_replace          > can_be_solution_receive_for_replace           state = =''
    can_be_solution_receive_for_replace = fields.Boolean(
        compute ="_compute_can_be_solution_receive_for_replace",
    )
    def _compute_can_be_solution_receive_for_replace(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_solution_receive_for_replace = visible
    def action_solution_receive_for_replace(self):
        return False


    # SIN USO ###############################################################
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
                r.purchase_id 
                and not r.purchase_return_move_id
                and r.state_purchase in ["waiting_action_purchase"] 
                and (r.state_process in ['validation'])
            )




    can_be_returned_reject_supplier = fields.Boolean(
        compute="_compute_can_be_returned_reject_supplier",
    )
    @api.depends("remaining_qty", "state_purchase")
    def _compute_can_be_returned_reject_supplier(self):
        """
        """
        #wdb.set_trace()
        for r in self:
            r.can_be_returned_reject_supplier = (
                r.purchase_id  
                and r.purchase_return_move_id.picking_id.state == "done"
                and r.state_purchase in ["reject_by_supplier"] 
            )

    can_be_validate_replaced = fields.Boolean(
            compute="_compute_can_be_validate_replaced",
        )
    @api.depends("state")
    def _compute_can_be_validate_replaced(self):
        """
        """
        for r in self:
            r.can_be_validate_replaced = (r.state=='solution_waiting_replace')

    can_be_validate_repair = fields.Boolean(
            compute="_compute_can_be_validate_repair",
        )
    @api.depends("state")
    def _compute_can_be_validate_repair(self):
        """
        """
        for r in self:
            r.can_be_validate_repair = (r.state=='solution_waiting_repair')

    can_be_receive_reject_rma_supplier = fields.Boolean(
        compute="_compute_can_be_receive_reject_rma_supplier",
    )
    @api.depends("state",)
    def _compute_can_be_receive_reject_rma_supplier(self):
        #wdb.set_trace()
        visible = False
        for record in self:
            if record.purchase_return_reject_move_id:
                visible = (record.purchase_return_reject_move_id.picking_id.state == "assigned")
        self.can_be_receive_reject_rma_supplier = visible

    can_be_refunded_purchase = fields.Boolean(
        compute="_compute_can_be_refunded_purchase",
    )
    @api.depends("remaining_qty", "state_purchase")
    def _compute_can_be_refunded_purchase(self):
        """Compute '_compute_can_be_refunded_purchase'. This field controls the visibility
        of the 'Return to customer' button in the rma form
        view and determinates if an rma can be returned to the customer.
        This field is used in:
        rma.can_be_refunded_purchase.
        """
        #wdb.set_trace()
        for r in self:
            r.can_be_refunded_purchase = (
                r.purchase_id                 
                and (r.state_process in ['validation'])
            )

    @api.depends("remaining_qty", "state")
    def _compute_can_be_returned(self):
        """Compute 'can_be_returned'. This field controls the visibility
        of the 'Return to customer' button in the rma form
        view and determinates if an rma can be returned to the customer.
        This field is used in:
        rma._compute_can_be_split
        rma._ensure_can_be_returned.
        """
        #wdb.set_trace()
        for r in self:
            r.can_be_returned = (
                r.rma_received 
                and (r.rma_resolution_result in ['rejected'])
                and r.remaining_qty > 0
                and (r.state_process in ['negotiation'])
                and (r.state not in ['solution_waiting_replace'])
            )


    # ACCIONES SIN USO

    def action_trade_validate_reject(self):
        #wdb.set_trace()
        for order in self:
            order.sudo().write({
                "state": "negotiation_rejected",
                "state_process":"negotiation",
                "rma_negotiation_result":"rejected",
            })
    def action_negotiation_accepted_refund(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "state": "accepted",
                "state_process":"negotiation",
                "rma_negotiation_result":"accepted",
            })

    def action_remote_rma_costumer(self):
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            'rma_customer_remote_claim':True,
            'state_process':'validation',
            'state':'validation_waiting'
            'state_product':'remote'
        })