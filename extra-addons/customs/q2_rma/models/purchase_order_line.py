from odoo import _
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.float_utils import float_compare, float_round
from odoo import fields, models
from odoo import _
#import wdb

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    rma_id = fields.Many2one(
        comodel_name="rma",
        string="RMA",
    )
    refund_origin = fields.Char(string='Refund', readonly=True, tracking=True,
    help="The document(s) that generated the RMA.")
    
    def _create_or_update_picking(self):
        #wdb.set_trace()
        if self.env.context.get('not_create_or_update_picking'):
            return
        return super()._create_or_update_picking()

    def _prepare_stock_moves(self, picking):
        #wdb.set_trace()
        is_return = self.product_qty < 0
        self_not_update = self.with_context(not_create_or_update_picking=True)
        if is_return:
            self_not_update.product_qty *= -1
        res = super()._prepare_stock_moves(picking)
        if is_return:
            self_not_update.product_qty *= -1
            for item in res:
                if self.env.context.get('reverse_picking'):
                    item['picking_id'] = self.env.context['reverse_picking']
                item.sudo().update({
                    'to_refund': True,
                    'location_id': item['location_id'],
                    'location_dest_id': item['location_dest_id']})
        return res

    def _create_stock_moves(self, picking):
        # Tenemos que ver que tipo de operacion estamos haciendo
        # Si es una devolucion/garantia quue enviamos a un proveedor
        # Tendremos que asignarle el tipo de operacion correspondiiente a picking_type_id = stock_warehouse_id.rma_supplier_out_type_id.id  
        # Rma Proveedor Salidas que corresponde al movimiento RMA/SGA0 -> Proveedor
        # La localización la obtendremos del  stock_warehouse_id.rma_loc_id.id 
        # todo esto los sacaremos de:
        # stock_warehouse_id = (
        #     self.env["stock.warehouse"]
        #     .search([("company_id", "=", sale.company_id.id)])
        # )
        # rma_supplier_out_type_id = stock_warehouse_id.mapped("rma_supplier_out_type_id")
        # rma_loc_id = stock_warehouse_id.mapped("rma_loc_id")
        #wdb.set_trace()
        # obtenemos el stock_warehouse para despues mapear los campos quue necesitaamos
        rma = self.order_id.rma_refund_id
        if rma:
            rma_purchase = rma.refund_purchase_order_id
            if rma_purchase: 
                
                #picking = rma_purchase.picking_ids
                stock_warehouse_id = (
                    self.env["stock.warehouse"]
                    .search([("company_id", "=", self.order_id.company_id.id)])
                    )
                # Obtenemoos el picking_type correspondiente al "RMA pproveedores Salidas"
                rma_supplier_out_type_id = stock_warehouse_id.mapped("rma_supplier_out_type_id")
                # Obtenemoos la ubicacion del RMA desde donde vamos  dar salida al producto en el envio al proveedor RMA/SEAG0
                rma_loc_id = stock_warehouse_id.mapped("rma_loc_id")
                rma_loc_dest_id = rma.purchase_receive_move_id.location_id
                if any([li.product_qty < 0 for li in self]): 
                    #and not (self.order_id.rma_refund_id and not self.order_id.rma_refund):
                    #wdb.set_trace()
                    reverse = picking.sudo().copy({
                        'move_lines': [],
                        'picking_type_id': rma_supplier_out_type_id.id,
                        'state': 'draft',
                        'origin': _('Return of %s') % rma_purchase.name,
                        'location_id': rma_loc_id.id,
                        'location_dest_id': rma_loc_dest_id.id})
                    self = self.with_context(reverse_picking = reverse.id)
                    #wdb.set_trace()
        return super()._create_stock_moves(picking) 

    # Sobreescribimos el metodo computado de cantidad a facturar para poder filtrar los abonos generados en RMA
    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'qty_received', 'product_uom_qty', 'order_id.state')
    def _compute_qty_invoiced(self):
        #wdb.set_trace()
        for line in self:
            # compute qty_invoiced
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.move_type == 'in_invoice':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
                    elif inv_line.move_id.move_type == 'in_refund':
                        qty -= inv_line.product_uom_id._compute_quantity(inv_line.quantity, line.product_uom)
            line.qty_invoiced = qty

            # compute qty_to_invoice
            for po in self.order_id:
                if po.rma_refund:
                    line.qty_to_invoice = line.product_qty
                elif line.order_id.state in ['purchase', 'done']:
                    if line.product_id.purchase_method == 'purchase':
                        line.qty_to_invoice = line.product_qty - line.qty_invoiced
                    else:
                        line.qty_to_invoice = line.qty_received - line.qty_invoiced
                else:
                    line.qty_to_invoice = 0

    """
    def _create_stock_moves(self, picking):
        #wdb.set_trace()
        if picking:
            if not self.order_id.rma_refund_id.refund_purchase_order_id:
                picking = self.order_id.rma_refund_id.purchase_id.picking_ids
            if any([li.product_qty < 0 for li in self]): 
                #and not (self.order_id.rma_refund_id and not self.order_id.rma_refund):
                #wdb.set_trace()
                reverse = picking.copy({
                    'move_lines': [],
                    'picking_type_id': (
                        picking.picking_type_id.return_picking_type_id.id
                        or picking.picking_type_id.id
                    ),
                    'state': 'draft',
                    'origin': _('Return of %s') % picking.origin,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id})
                self = self.with_context(reverse_picking=reverse.id)
        return super()._create_stock_moves(picking) 
    """