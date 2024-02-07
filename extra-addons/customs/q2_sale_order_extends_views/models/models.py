# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools
from odoo.tools import float_compare
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo import _

import re
#import wdbb

class q2_sale_order_extends_views(models.Model):
    _inherit = 'sale.order'
    _description = 'q2_sale_order_extends_views.q2_sale_order_extends_views'

    # Campos a incluir en el modelo "sale_order"
    # Check de control es_CB para determinar si la SO es CB
    q2_is_cb = fields.Boolean(default=False,string='R',copy=False, store=True, index=True, tracking=True)
    # Check de control para determinar si está pagada en caso de ser CB
    q2_is_pg = fields.Boolean(default=False,string='P',copy=False, store=True, index=True, tracking=True)

    label_is_cb = fields.Char(compute='_compute_is_cb', string='R', store=False, default='')
    label_is_pg = fields.Char(compute='_compute_is_pg', string='P', store=False, default='')
    # Usuario que lo marca como CB
    q2_user_cb = fields.Many2one('res.users', string='Crea el CB', index=True, store=True)
    # Usuario que realiza el cobro del CB
    q2_user_pg = fields.Many2one('res.users', string='Cobra el CB', index=True, store=True )
    # Campo que define si se muestra o se oculta el CB
    q2_show_r = fields.Boolean(compute='_compute_show_r', default=False, store=False)

    # Computa la 
    def _compute_show_r(self):
        # crearemos una busqueda especifica por orden de pedido "Forzar busqueda por orden de pedido"
        #wdb.set_trace()
        ncb = self.env['ir.config_parameter'].sudo().get_param('q2_sale_order_extends_views.ncb', default=False)
        # Le asignamos el valor booleano
        self.q2_show_r = (ncb == 'true')

    def _compute_is_cb(self):
        for r in self:
            if r.q2_is_cb:
                #wdb.set_trace()
                r.label_is_cb = 'R'
            else:
                r.label_is_cb = ''

    def _compute_is_pg(self):
        for r in self:
            if r.q2_is_cb:
                if r.q2_is_pg:
                    #wdb.set_trace()
                    r.label_is_pg = 'P'
                else:
                    r.label_is_pg = ''
            else:
                r.label_is_pg = ''

    # Chequea si es cb o no
    def check_is_cb(self):
        return self.q2_is_cb == True;        

    # Chequea si es cb o no
    def check_is_cbpg(self):
        return self.q2_is_cb == True and self.q2_is_pg == True;        

    # Metodo que contiene toda la logica del funcionamiento del CB
    # Tenemos que sobreescribir el metodo search para poder filtrar por el valor de ncb
    def set_cbpg_client_order_ref(self,values={}):
        #wdb.set_trace()
        vals = {}
        so = self
        if so:
            self.ensure_one()
            cor_ini = self['client_order_ref']
            if 'client_order_ref' in values.keys():
                cor_ini = values['client_order_ref']
            if cor_ini:
                cor = ' {} '.format(cor_ini.replace(' ','  ').replace('-','  ').replace('_','  ').replace('.','  ').replace(',','  '))
                #Ver si tenemos el CB fuera de una palabra
                rp_lcbpg = "(?i)[\W](CBPG)[\W|$]"  #"(?i)[^a-zA-Z]CB[^a-zA-Z]"
                rp_lpgcb = "(?i)[\W](PGCB)[\W|$]"  #"(?i)[^a-zA-Z]CB[^a-zA-Z]"
                cor = re.sub(rp_lcbpg,'  CB  PG  ',cor)
                cor = re.sub(rp_lpgcb,'  CB  PG  ',cor)

                rp_lcb = "(?i)[\W](CB)[\W|$]"  #"(?i)[^a-zA-Z]CB[^a-zA-Z]"
                rp_nolcb = "(?i)[\W](NOCB)[\W|$]"  #"(?i)[^a-zA-Z]NOCB[^a-zA-Z]"
                rp_lpg = "(?i)[\W](PG)[\W|$]"  #"(?i)[^a-zA-Z]PG[^a-zA-Z]"
                rp_marca = "(?is)\[@X?\]"
                lcb = re.findall(rp_lcb, cor)
                nolcb = re.findall(rp_nolcb, cor)
                lpg = re.findall(rp_lpg, cor)
                marca = ''

                if len(lcb)>0:
                    # Si tiene CB actualizamos el registro
                    vals['q2_is_cb']=True
                    # reemplazamos los valores de client_order_ref
                    marca = '@'               
                    # Eliminamos el texto de CB
                    cor = re.sub(rp_lcb,'',cor)
                    # Eliminamos la marca de CBPG <@>
                    cor = re.sub(rp_marca,'',cor)
                    #wdb.set_trace()
                    msg = _('%s por el operador %s')%('Creado el recibo',self.env.user.name)
                    self.message_post( body = msg)
                    

                if len(nolcb)>0:
                    # Verificamos si ha sido marcada como pagada, 
                    # Si no se ha pagado se puede modificar en caso contrario no se podra modficar
                    if not self.q2_is_pg :
                        # Si tiene CB actualizamos el registro
                        vals['q2_is_cb']=False
                        # Eliminamos el texto de CB
                        cor = re.sub(rp_nolcb,'',cor)
                        # Eliminamos la marca de CBPG <@>
                        cor = re.sub(rp_marca,'',cor)
                        #wdb.set_trace()
                        msg = _('%s por el operador %s')%('Anulado el recibo',self.env.user.name)
                        self.message_post( body = msg)
                    else:
                        if values != {}:
                            #wdb.set_trace()
                            raise ValidationError(
                                (
                                    "No es posible modificar el recibo, debido a que ya esta pagado. Consulte con adminiistración"
                                )
                            )

                if len(lpg)>0:
                    # Si tiene CB actualizamos el registro
                    if self.q2_is_cb or len(lcb)>0:
                        vals['q2_is_pg']=True    
                        marca = '@X'               
                        cor = re.sub(rp_lpg,'',cor)
                        # Eliminamos la marca de CBPG <@>
                        cor = re.sub(rp_marca,'',cor)
                        #wdb.set_trace()
                        msg = _('%s por el operador %s')%('Cobrado el recibo',self.env.user.name)
                        self.message_post( body = msg)
                    else:
                        if values != {}:
                            #wdb.set_trace()
                            raise ValidationError(
                                (
                                    "Antes de abonar este recibo debe de marcarse como CB "
                                )
                            )
                
                if marca is not "": 
                    marca = '[{}]'.format(marca)
                cor = '{} {} '.format(cor.replace('   ',' ').replace('  ',' '),marca)               
                vals["client_order_ref"]=cor
        
        return vals

    def write(self,values):
        #wdb.set_trace()
        vals = self.set_cbpg_client_order_ref(values)
        for k in vals.keys():
            values[k]= vals[k]
        return super(q2_sale_order_extends_views, self).write(values)

    # Metodo que busca todos los CB y los codifica
    def _action_cbpg_update_values(self):
        #wdb.set_trace()
        # Al instalar el modelo inicializacemos el valor de CB y PG en todos los registros de sale_order
        ls_so = self.env['sale.order'].search([('client_order_ref','ilike','%CB%')])
        
        # recorremos todos os registros localizados en la busqueda para actualizar su valor CB y eliminar la etiquueta 
        for so in ls_so:
            # para cada orden llamamos al metodo que ajusta el cbpg
            so.set_cbpg_client_order_ref()

    # Metodo que busca todos los CB y los codifica
    def _action_hide_r(self):
        ncb = self.env['ir.config_parameter'].sudo().set_param('q2_sale_order_extends_views.ncb', True)


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
                domain =    [
                    args or [],
                    ['|', ('name', operator, name), ('partner_id.name', operator, name)]
                ]
                return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return super(q2_sale_order_extends_views, self)._name_search(name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        #wdb.set_trace()
        # Lo primero que haremos es ver en que modo estamos realizando la busqueda con respecto a la vista CB
        domain = args
        # Si esta restringida no mostraremos los CB pagados, y mostraremos todo lo que no sea CB y los CB que aun no han sido pagados
        if self.q2_show_r:
            domain = [('q2_is_cb','!=',True)]
            if len(args)>0:
                domain = [('q2_is_cb','!=',True),args]

        # crearemos una busqueda especifica por orden de pedido "Forzar busqueda por orden de pedido"
        # Si la busqueda es directa por el numero de pedido la mostraremos
        # crearemos una busqueda especifica por producto "Forzar busqueda por orden de pedido"
        # Si la busqueda es directa por producto tambien la mostraremos
        qry = super(q2_sale_order_extends_views, self)._search(domain, offset=offset, limit=limit, order=order,
                                                                count=False, access_rights_uid=access_rights_uid)
        return qry
    
