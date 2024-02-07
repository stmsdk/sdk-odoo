from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from datetime import date
from datetime import timedelta
import re
#import wdb

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'q2_sale_commision.purchase_order'

    partner_ref = fields.Char(tracking=True)

    # Tenemos que buscar donde se realiza la actualizacion del precio en la orden de compra para actualizar los precios de la orden de venta y quien lo hace
    # puchase_price en sale_order_line garda el precio y tendriamos que reclacular el margen de la venta en cuastion asi como el recalclo de los margenes totales en SO

    def button_confirm(self):
        #wdb.set_trace()
        if self.origin:
            domain = [('name','=',self.origin)]
            so = self.env['sale.order'].search(domain)
        if so:
            vals = {}
            vals['q2_user_confirm_purchase'] = self.env.uid
            so.write(vals)
            res = super(PurchaseOrder, self).button_confirm()
            return res

    def get_total_cost_and_user_purchase(self):
        #wdb.set_trace()
        po_no_cost = False          # No tiene un coste objetivo
        po_total_cost = 0           # Coste de la compra
        po_user_close = None        # Usuario que cierra la compra
        po_usr_close_date = None    # Fecha hora del cierre de la compra
        # Tomaremos como usuario de cierre aquel que realice la ultima operación en el proceso e compra
        # Si tiene compra revisamos los logs para ver quien realiza lo movimientos 
        ls_msg_po = self.env['mail.message'].search([('model','=','purchase.order'),('res_id','=',self.id)])

        for msg_po in ls_msg_po:
            # DENTRO DEL LOG TRACKING DE LA COMPRA OBTENEMOS LOS CAMBIOS REALIZADOS
            # Buscamos si es una apertura de compra que encontraremos en el body  
            body = msg_po.body
            ptrn_po_open = "Pedido de compra creado"
            re_po_open = re.search(ptrn_po_open, body , re.IGNORECASE)
            # verificamos el resultado 
            if re_po_open:
                #wdb.set_trace()
                qry_user = self.env['res.users'].search([('partner_id','=',msg_po.author_id.id)])
                if qry_user:
                    po_user_close = qry_user.id 
                    po_usr_close_date = msg_po.create_date
            else:
                #wdb.set_trace()
                # Si no es el pedido de compra verificamo el resto de acciones
                msg_tracking_value = self.env['mail.tracking.value'].search([('mail_message_id','=',msg_po.id)])
                # verifico si hay resultado
                #Si se ha modificado la referencia del proveedor para el registro del albaran
                
                if msg_tracking_value:
                    for mtv in msg_tracking_value:
                        # Si hay resultado vemos que tipo de mensaje se ha realizado
                        if mtv.field_desc == 'Base imponible':
                            # Es un cambio de precio
                            po_usr_close = mtv.create_uid
                            po_usr_close_date = mtv.create_date                                   
                        if mtv.field_desc == 'Referencia de proveedor':
                            if po_usr_close_date:
                                if po_usr_close_date < mtv.create_date:
                                    po_usr_close = mtv.create_uid 
                                    po_usr_close_date = mtv.create_date                                   
                            else:
                                    po_usr_close = mtv.create_uid 
                                    po_usr_close_date = mtv.create_date                                   

                        if mtv.field_desc == 'Estado' and mtv.new_value_char == 'Pedido de compra':
                            # Si es un cambio del estado del pedido verificamos si es un pedido de compra confirmado 
                            if po_usr_close_date:
                                if po_usr_close_date < mtv.create_date:
                                    po_usr_close = mtv.create_uid 
                                    po_usr_close_date = mtv.create_date                                   
                            else:
                                    po_usr_close = mtv.create_uid 
                                    po_usr_close_date = mtv.create_date                                   


                            # Obtenemos todas las lineas de compra
                            po_ln = self.env['purchase.order.line'].search([('order_id','=',self.id),('state','in',['purchase','sent'])])
                            # obtenmos por cada linea de compra los datos que necesitamos para averiguar los costes
                            po_total_cost = 0.0
    
                            #wdb.set_trace()
                            for pol in po_ln:
                                # verficamos los precios de compra
                                # Si el precio es 0 tomaremos el precio de
                                if pol.price_unit > 0:
                                    po_total_cost += pol.price_unit
                                else:
                                    po_no_cost = True
        
        #wdb.set_trace()
        return po_no_cost,po_total_cost, po_user_close, po_usr_close_date 

