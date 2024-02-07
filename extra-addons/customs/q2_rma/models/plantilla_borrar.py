
class Plantilla:

    """ @values
    rma_received                :   True , False
    rma_customer_remote_claim   :   True , False    
    rma_supplier_remote_claim   :   True , False    
    rma_external_remote_claim   :   True , False    

    state_process               :   draft , reception , validation , resolution , negotiation , solution , location , finished  

    state              reception:   confirmed , received , remoto
                      validation:   validation_waiting , validation_internal , validation_external , validation_supplier   
                      resolution:   resolution_waiting, resolution_accepted , resolution_rejected
                     negotiation:   negotiation_waiting , negotiation_accepted_to_repair , negotiation_accepted_to_replace , negotiation_accepted_to_refund , negotiation_rejected 
                        solution:   solution_waiting_repair , solution_repaired , solution_waiting_replace , solution_replaced , solution_waiting_refund , solution_refunded ,  ,  ,  ,  , 
                        location:   waiting_return_to_customer , returned_to_customer, in_stock, in_scrap
                        close:   

    state_product      reception:   nothing , waiting_reception , received , remote
                      validation:   waiting_validation,
             validation_internal:   waiting_check_internal , checked_internal
             validation_external:   waiting_send_to_external , sent_to_external , waiting_receive_from_external , received_from_external , scrapped_from_external
             validation_supplier:   waiting_send_to_supplier , sent_to_supplier , waiting_receive_from_supplier , received_from_supplier , scrapped_from_supplier
                      resolution:   waiting_resolution,
                     negotiation:   waiting_negotiation,
                 solution_repair:   waiting_send_to_repair , sent_to_repair , received_repaired 
                solution_replace:   waiting_request_to_replace , requested_to_replace , receive_repaired
                        location:   waiting_location,
              location_to_client:   waiting_send_to_customer , sent_to_customer 
               location_to_stock:   waiting_send_to_stock , in_stock
               location_to_scrap:   waiting_send_to_scrap, scrapped

    state_purchase              :   no_purchase , waiting_action_purchase, waiting_send_to_supplier , waiting_response_supplier , 
                                    waiting_return_from_supplier ,returned_from_supplier , scrapped_from_supplier ,  
                                    waiting_confirm_refund , refunded_from_supplier , 

    rma_owner_product           :   nothing , costumer , internal,  internal_rma , internal_sat , external_sat , supplier, scrap
    rma_type_validation         :   nothing , waiting , internal , external , supplier
    rma_type_resolution         :   nothing , waiting , accepted , rejected
    rma_type_negotiation        :   nothing , waiting , accepted , rejected
    rma_type_solution           :   nothing , waiting , repair , replace , refund , discount , rejected
    rma_type_resolution_supplier:   nothing , waiting , accepted , rejected 
    rma_type_solution_supplier  :   nothing , waiting , repair , replace , refund , rejected
    rma_type_final_location     :   nothing , costumer , stock ,  scrap , external_scrap , supplier_scrap
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
    # Recepcionar RMA                     >  action_receive_rma_client                    > can_be_receive_from_costumer                    state_process = ='reception' 
    # Gestión Remota RMA                  >  action_remote_rma_client                     > can_be_receive_from_costumer      
    # ** VALIDACION(validation) **********************************************************************************************************
    # Valoración interna                  >  action_internal_validate                     > can_be_validate                               state_process = ='validation' & state = ='validation_waiting'
    # Valoración externa                  >  action_external_validate                     > can_be_validate                    
    # Valoración Proveedor                >  action_supplier_validate                     > can_be_validate                    
    # ** Validación INTERNA **************************************************************************************************************
    #  @ Valorar directamente             >  action_validation_direct_internal               > can_be_validation_direct_internal              state = ='validation_external'
    #    Enviar a taller                  >  action_validation_delivery_to_internal_test     > can_be_validation_delivery_to_internal_test         state = ='supplier_validate' & state_product = ='waiting_send_to_supplier' & not rma_customer_remote_claim
    #    Recibido desde taller            >  action_validation_received_from_internal_test   > can_be_validation_received_from_internal_test      state_product = ='waiting_receive_from_supplier' & not rma_customer_remote_claim
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
    # ** SOLUCION(solution) **************************************************************************************************************
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
    # _validation_direct_internal 
    can_be_validation_direct_internal = fields.Boolean(
        compute ="_compute_can_be_validation_direct_internal",
    )
    def _compute_can_be_validation_direct_internal(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            if r.state == 'validation':
                if r.state_product == 'waiting_validation':
                    visible = True
            # asignacion
            r._can_be_validation_direct_internal = visible
    def action_validation_direct_internal(self):
        return False
    # _validation_delivery_to_internal_test
    can_be_validation_delivery_to_internal_test = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_internal_test",
    )
    def _compute_can_be_validation_delivery_to_internal_test(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        #wdb.set_trace()
        visible = False
        for r in self:
            # condicio que habilita la funcion
            if r.state == 'validation':
                if r.state_product == 'waiting_validation':
                    visible = True
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
            #wdb.set_trace()
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
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_remote_external = visible
    def action_validation_remote_external(self):
        return False
            
    # Enviar a Externo                >  action_validation_delivery_to_external       > can_be_validation_delivery_to_external        state = ='validation_external' & state_product = ='waiting_send_to_external' & not rma_customer_remote_claim
    can_be_validation_delivery_to_external = fields.Boolean(
        compute ="_compute_can_be_validation_delivery_to_external ",
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
        compute ="_compute_can_be_validation_received_from_external  ",
    )
    def _compute_can_be_validation_received_from_external(self):
        """Compute ''. 
            Controla la visibilidad del boton "Enviar a taller"
        """
        #wdb.set_trace()
        visible = False
        for r in self:
            #wdb.set_trace()
            # condicio que habilita la funcion

            # asignacion
            r._can_be_validation_received_from_external = visible
    def action_validation_received_from_external(self):
        return False

    # Desechado en Externo            >  action_validation_send_to_scrap_external     > can_be_validation_send_to_scrap_external      state_product = ='sent_to_external' & not rma_customer_remote_claim
    can_be_validation_send_to_scrap_external = fields.Boolean(
        compute ="_compute_can_be_validation_send_to_scrap_external   ",
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
        compute ="_compute_can_be_validation_remote_supplier   ",
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
        compute ="_compute_can_be_validation_received_from_supplier   ",
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
        compute ="_compute_can_be_solution_refund_to_customer   ",
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
        compute ="_compute_can_be_solution_delivery_to_repair   ",
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
        compute ="_compute_can_be_solution_receive_repaired   ",
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
        compute ="_compute_can_be_solution_request_for_replace   ",
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
        compute ="_compute_can_be_solution_receive_for_replace   ",
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
                and (r.rma_type_resolution in ['rejected'])
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
                "rma_type_negotiation":"rejected",
            })
    def action_negotiation_accepted_refund(self):
        #wdb.set_trace()
        for order in self:
            # Posteriormente lo pasamos a la aceptación del comercial para que complete la devolución
            order.sudo().write({
                "state": "accepted",
                "state_process":"negotiation",
                "rma_type_negotiation":"accepted",
            })

    def action_remote_rma_client(self):
        #wdb.set_trace()
        self.ensure_one()
        self.sudo().write({
            'rma_customer_remote_claim':True,
            'state_process':'validation',
            'state':'validation_waiting'
            'state_product':'remote'
        })


#######
# FUNCIONES DE FORZADO DE SALIDA RESERVA DE PIEZA
#######

    def action_repair_end(self):
        if any(r.show_check_availability for r in self):
            raise UserError(_("Some related stock moves are not available."))
        # I can not everything has been reserved.
        self._force_qty_done_in_repair_lines()
        for repair in self:
            operation_moves = repair.mapped("operations.move_id")
            if operation_moves:
                consumed_lines = operation_moves.mapped("move_line_ids")
                produced_lines = repair.move_id.move_line_ids
                operation_moves |= repair.move_id
                produced_lines.write({"consume_line_ids": [(6, 0, consumed_lines.ids)]})

        self.move_id._set_quantity_done(self.move_id.product_uom_qty)
        self.move_id._action_done()
        for move in self.mapped("operations.move_id"):
            move._set_quantity_done(move.product_uom_qty)
            move._action_done()
        return super().action_repair_end()

    def _force_qty_done_in_repair_lines(self):
        for operation in self.mapped("operations"):
            for move in operation.stock_move_ids:
                if move.state not in ["confirmed", "waiting", "partially_available"]:
                    continue
                product_qty = move.product_uom._compute_quantity(
                    operation.product_uom_qty,
                    move.product_id.uom_id,
                    rounding_method="HALF-UP",
                )
                available_quantity = self.env["stock.quant"]._get_available_quantity(
                    move.product_id,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._update_reserved_quantity(
                    product_qty - move.reserved_availability,
                    available_quantity,
                    move.location_id,
                    lot_id=operation.lot_id,
                    strict=False,
                )
                move._set_quantity_done(operation.product_uom_qty)
                if operation.lot_id:
                    move.move_line_ids.lot_id = operation.lot_id