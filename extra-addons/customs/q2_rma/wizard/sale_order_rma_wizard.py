# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

## ERRORES POSIBLES AL DESINSTALAR E INSTALAR DE NUEVO
## INDICES DUPLICADOS
"""
__exception__
IntegrityError: duplicate key value violates unique constraint "stock_picking_name_uniq"
DETAIL:  Key (name, company_id)=(SEAG0/RMA/IN/00003, 1) already exists.
"""

from odoo import SUPERUSER_ID, _, api, fields, models

import wdb ##wdb.set_trace()


class SaleOrderRmaWizard(models.TransientModel):
    _inherit = "sale.order.rma.wizard"
    # is_refund is_replace is_warranty
    # def create_and_open_rma_replace(self):
    #    #wdb.set_trace()
    #    self.env.context = dict(self.env.context)
    #    self.env.context.update( { 'rma_operation_type': 'is_replace' } )
    #    self.create_and_open_rma()

    def create_and_open_rma_warranty(self):
        #wdb.set_trace()
        self.env.context = dict(self.env.context)
        self.env.context.update( { 'rma_operation_type': 'is_warranty' } )
        self.create_and_open_rma()

    def create_and_open_rma_refund(self):
        #wdb.set_trace()
        self.env.context = dict(self.env.context)
        self.env.context.update( { 'rma_operation_type': 'is_refund' } )
        self.create_and_open_rma()

    def create_and_open_rma(self):
        #wdb.set_trace()
        self.ensure_one()
        rma = self.create_rma()
        if not rma:
            return
        for rec in rma:
            rec.action_confirm()
            rec.sudo().write({
                "state_process": "reception",
            })

        action = self.sudo().env.ref("rma.rma_action").read()[0]
        if len(rma) > 1:
            action["domain"] = [("id", "in", rma.ids)]
        elif rma:
            action.update(
                res_id=rma.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        return action


class SaleOrderLineRmaWizard(models.TransientModel):
    _inherit = "sale.order.line.rma.wizard"

    def _prepare_rma_values(self):
        # Q2 RMA WIZAR
        #wdb.set_trace()
        self.ensure_one()
        #wdb.set_trace()
        """It will be used as a reference for the components"""
        res = super()._prepare_rma_values()
        partner_shipping = (
            self.wizard_id.partner_shipping_id or self.order_id.partner_shipping_id
        )
        description = (self.description or "") + (
            self.wizard_id.custom_description or ""
        )
        # Asignamos el tipo de operacion al RMA
        rma_operation_type = self.env.context.get('rma_operation_type')
        op = self.env['rma.operation'].search([('type','=',rma_operation_type)])
        operation_id = None
        if op:
            operation_id = op.id

        #Obtenemos las PO associadas a esta venta, pueden ser varias por lo que las trataremos individualmente
        pos = self.env["purchase.order"].search([("origin","=",self.order_id.name),("state","not in",["draft","cancel"])])
        #recorremos todas las PO en busca de la compra para este producto
    
        #wdb.set_trace()
        if pos:
            # Asignamos los datos de compra al RMA
            purchase_id = None
            origin_purchase = None
            purchase_date_order = None
            supplier_reference_purchase = None
            purchase_order_line_id = None        
            #purchase_supplier_partner_id = None
            for po in pos:
                #Obtenemos la linea de po referente al producto
                if po:
                    #line = refund.order_line.filtered(lambda r: not r.rma_id)
                    # Buscamos si hy una compra dentro de las PO para ese producto
                    # Filtramos dentro de las lineas de compra el producto sobre el que hacemos el RMA
                    pol = po.order_line.filtered(lambda r:  r.product_id.id == self.product_id.id )
                    #pol = self.env["purchase.order.line"].search([("order_id","=",po.id),("product_id","=",self.product_id.id)]) 
                    if pol:
                        #sale_id = (self.order_id.id or None)
                        sale_group_id = (self.order_id.procurement_group_id.id or None)
                        purchase_group_id = (po.group_id.id or None)
                        purchase_id = (po.id or None)
                        origin_purchase = (po.name or None)
                        purchase_date_order = (po.date_order or None)
                        purchase_supplier_partner_id = (po.partner_id.id or None)
                        supplier_reference_purchase = (po.partner_ref or None)
                        purchase_order_line_id = (pol.id or None)
                        #pk = po.picking_ids.search([('origin','=',origin_purchase),('state', '=', 'done'),('picking_type_id.code', '=', 'incoming'),('partner_id', 'child_of', purchase_supplier_partner_id),])
                        pk = po.picking_ids.search([('origin','=',origin_purchase),('picking_type_id.code', '=', 'incoming'),('partner_id', 'child_of', purchase_supplier_partner_id),])
                        purchase_picking_id = None
                        if pk:
                            purchase_picking_id = (pk[0].id or None)
                            sm = self.env["stock.move"].search([("picking_id","=",purchase_picking_id )])
                            purchase_receive_move_id = (sm[0].id or None )
                        #wdb.set_trace()
                        # return{
                        res.update({
                            #"sale_id":sale_id,
                            "partner_id": self.order_id.partner_id.id,
                            "partner_invoice_id": self.order_id.partner_invoice_id.id,
                            "partner_shipping_id": partner_shipping.id,
                            "origin": self.order_id.name,
                            "company_id": self.order_id.company_id.id,
                            "location_id": self.wizard_id.location_id.id,
                            "order_id": self.order_id.id,
                            "picking_id": self.picking_id.id,
                            "move_id": self.move_id.id,
                            "product_id": self.product_id.id,
                            "product_uom_qty": self.quantity,
                            "product_uom": self.uom_id.id,
                            "operation_id":operation_id,
                            "description": description,
                            "origin_sale" :self.order_id.name,
                            "sale_group_id" : sale_group_id,
                            "purchase_id" :purchase_id,
                            "origin_purchase" :origin_purchase,
                            "purchase_group_id" : purchase_group_id,
                            "purchase_date_order":purchase_date_order,
                            "supplier_reference_purchase":supplier_reference_purchase,
                            "purchase_order_line_id":purchase_order_line_id,
                            "purchase_supplier_partner_id":purchase_supplier_partner_id,
                            "purchase_picking_id":purchase_picking_id,
                            "purchase_receive_move_id": purchase_receive_move_id,
                            "state_purchase":"waiting_action_purchase",
                        })
                        #Cuando encuentre una linea de compra paara este produucto me salgo
                        #wdb.set_trace()
                        return res
                        #return {
        else:
            #wdb.set_trace()
            # self.product_id.seller_ids[0].name  # > esto nos da el res.partner(xxx)
            purchase_supplier_partner_id = (self.product_id.seller_ids[0].name.id or None)

        res.update({
            "partner_id": self.order_id.partner_id.id,
            "partner_invoice_id": self.order_id.partner_invoice_id.id,
            "partner_shipping_id": partner_shipping.id,
            "origin": self.order_id.name,
            "company_id": self.order_id.company_id.id,
            "location_id": self.wizard_id.location_id.id,
            "order_id": self.order_id.id,
            "picking_id": self.picking_id.id,
            "move_id": self.move_id.id,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "product_uom": self.uom_id.id,
            "operation_id":operation_id,
            "description": description,
            "purchase_supplier_partner_id":purchase_supplier_partner_id,
        })
        #wdb.set_trace()
        return res

            # hasta aqui llevar a modulo
            # devolvemos los valores actualizados
        

