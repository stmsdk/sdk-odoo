# -*- coding: utf-8 -*-
"""
        Este módulo incorpora en la ficha de usurio y partnes,campos computados que calculan los ratios de venta y devolucion
        Regitra en las ordenes de compra:
            > El usuario que genera el presupuesto
            > El usuario que cierra el presupuesto, entendiendo por cierre los pasos de confirmacion de presupuesto y de compra a proveedor si fuese necesario, asi como el pedido externo al proveedor
            > En cada movimiento de la orden de venta se actualizaran los valores necesarios para el cálculo decmisiones.

            Metodos de control de ordenes de venta
            > Control de cancelacion de presupuestos
            > Control de no duplicidad de orden de venta
            > Control de confimacion de orden de compra en caso de ser requerida
"""


from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, date, timedelta
import re
import pytz
import time
import wdb #wdb.set_trace()

# Tabla de sintomas
class WorkshopTestService(models.Model):
    _name = 'q2_ws_test'
    name = fields.Char(string='Pruebas a realizar')

class WorkshopAskService(models.Model):
    _name = 'q2_ws_ask_service'
    name = fields.Char(string='Sintomas de la averia')

# Tabla de servicios solicitados
class WorkshopServiceRequest(models.Model):
    _name = 'q2_ws_service_request'
    name = fields.Char(string='Servicio de taller')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'q2_sale_commision.sale_order'

    # ######################################################
    # TOMA DE RAZON ########################################
    # ######################################################
    # Con esta opcion solo los usuarios que esten dentro del equipo de ventas podran realizar un pedido
    # El resto de usuarios podran tomar razones a los cliente que llamen 
    # Las razones capturadas quedaran pendiente de ser atendida por algun usuario del equipo comercial
    # Añadimos un nuevo item al estado del pedido que es el estado de toma de razón
    # De la misma forma una entrada de taller solo sera recepcionada por el mostrador y seran los comerciales los que hablen con el cliente pongan precios  
    # Diferenciaremos entre dos tipos de razones RAZON DE VENTA y RAZON DE TALLER
    
    # Un usuario que no sea comercial no podra desarrollar la venta pero si tomar razones
    # LAS RAZONES podran ser:
    # ('reason', 'Razón')               Razon para realizar el presupuesto
    # ('reason_contact', 'Contactar')   Razón para que el comercial llame al cliente
    # ('reason_confirm', 'Confirmado')  Razón de confirmacion de presupuesto para que el comercial proceda con el pedido y cierre de la venta
    # ('reason_reject', 'Rechazado')    Razón de pedido rechazado para que el comercial proceda con su cancelación o llame al cliente para determinar la causa de la misma

    state = fields.Selection(selection_add=[
                                        ('reason', 'Razón'),
                                        ('reason_contact', 'Contactar'),
                                        ('reason_confirm', 'Confirmado'),
                                        ('reason_reject', 'Rechazado'),
                                        ])
    q2_sale_type = fields.Selection([
                                       ('none', 'Sin seleccionar'),
                                       ('product', 'Producto'),
                                       ('service', 'Servicio'),
                                    ] 
                                    , default='none' 
                                    , string="Tipo de operacion")
    
    # Campos de gestion de visibilidad
    q2_is_salesman = fields.Boolean( compute = '_compute_is_salesman')
        
    def _compute_is_salesman(self):
        # este campo nos gestiona la visidad de los campos que deben de aparecer cuando el usuario es comercial y lo oculta si no lo es
        #wdb.set_trace()
        self.q2_is_salesman = self._check_is_salesman()
    
    def check_is_salesman(self):
        self._check_is_salesman()

    def _check_is_salesman(self, user=None):
        check = False
        if user == None:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
            # Obtenemos el crm team
            equipo_venta_uid = 1
            sales_team = self.env['crm.team'].browse(equipo_venta_uid)
            if sales_team:
                if user in sales_team.member_ids:
                    check = True
        #wdb.set_trace()
        return check

    def _check_is_sales_team_manager(self):
        wdb.set_trace()
        check = False
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        # Obtenemos el crm team
        equipo_venta_uid = 1
        sales_team = self.env['crm.team'].browse(equipo_venta_uid)
        if sales_team:
            if user in sales_team.user_id:
                check = True
        return check

    def _check_is_user_owner(self):
        #wdb.set_trace()
        check = False
        user_owner = (True if self.q2_user_salesman_owner.id == self.env.uid else False)
        if user_owner: 
            check=True
        if self._check_is_sales_team_manager():
            check=True
        return check 
    
    q2_is_sales_team_manager = fields.Boolean(compute = '_compute_is_sales_team_manager')
    # Verificamos si el usuario pertenece al equipo de venta
    def _compute_is_sales_team_manager(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        #wdb.set_trace()
        self.q2_is_sales_team_manager = self._check_is_sales_team_manager()

    # Razon para venta de producto
    q2_is_reason = fields.Boolean(string = "Es razón" , default=True)
    # Espacio donde escribir la razon
    q2_reason_note = fields.Char(string="Razon", default='' )

    q2_visible_take_reason = fields.Boolean(default=False, compute = '_compute_visible_take_reason')
    def _compute_visible_take_reason(self):
        # Verificamos que
        #wdb.set_trace() 
        visible = False
        if self.q2_is_salesman:
            if self.q2_sale_type != 'none':
                if self.q2_is_reason:
                    visible = True
        self.q2_visible_take_reason = visible

    q2_visible_operator_reason = fields.Boolean(default=False, compute = '_compute_visible_operator_reason')
    def _compute_visible_operator_reason(self):
        # Verificamos que
        # q2_visible_operator_reason
        #wdb.set_trace()
        visible = False
        if not self._check_is_user_owner():
            if self.q2_sale_type != 'none':
                if not self.q2_is_reason:
                    visible = True
        self.q2_visible_operator_reason = visible

    # DETALLE DE RAZON
    # Tipo de Vehiculo (Turismos, Motos, Comerciales, Autobuses, Industriales, Maquinarias, otros )
    q2_vehiculo_type = fields.Selection([
                                       ('turismo', 'Turismo'),
                                       ('moto', 'Moto'),
                                       ('comercial', 'Comercial'),
                                       ('autobus', 'Autobús'),
                                       ('industrial', 'Industrial'),
                                       ('maquinaria', 'Maquinaria'),
                                       ('generador', 'Generador'),
                                       ('otro', 'Otro'),
                                       ] 
                                       , string = 'Tipo de Vehículo' 
                                       , default='otro' )
    # Marca/Modelo/ año/ Motor / Cilindrada
    q2_vehiculo_model = fields.Char(string="Marca / Modelo", default='' )
    # Solo Distribucion ####################################
    # Matricula 
    q2_vehiculo_matricula = fields.Char(string="Matricula", default='' )
    # Bastidor
    q2_vehiculo_bastidor = fields.Char(string="Nº Bastidor", default='' )
    #  Producto
    # Referencia OE / PRV
    q2_product_ref = fields.Char(string="Referencia OE", default='' )
    # Solo Taller ##########################################
    # Presupuestar antes de actuar (reparar fabricar)
    q2_ppto_required = fields.Boolean(string='Requiere presupuesto', default=False)   
    # Solo verificar (Si se marca no se hara nada de reparacion o fabricacion, solo verificacion)     
    q2_only_test = fields.Boolean(string='Solo probar', default=False)   
    #  Producto para para la razón 
    q2_products_types_ids = fields.Many2many(
        comodel_name="product.category",
        relation="rel_sale_order_reason_products_types",
        column1="sale_order_id",
        column2="category_id",
        string="Razon para los productos",
    )
    # Sintomas:
    q2_ws_ask_service = fields.Selection([
                                        ('none', 'Sin identificar'),
                                        ('sin_sintomas', 'No se aprecian sintomas'),
                                        ('con_fuga', 'Con fugas'),
                                        ('se_calienta', 'El motor se calienta'),
                                    ]
                                    , default='none' )
    # Preguntas para determinar la causa de la incidencia         
    q2_ws_service_request = fields.Selection([
                                        ('none', 'Sin seleccionar'),
                                        ('verificar','Verificar'),
                                        ('limpieza','Limpieza/Baqueteado'),
                                        ('reparar','Reparar'),
                                        ('soldar','Soldar'),
                                        ('tub_rep','Tubería reparacion'),
                                        ('tub_eng','Tubería engatillado'),
                                        ('camb_bp','Cambio de Bloque/Panal'),
                                        ('fab_dep','Fabricar deposito'),
                                        ('fab_enfriador','Fabricar enfriador'),
                                        ('fab_muestra','Fabricar sobre muestra'),
                                        ('fap','Limpieza Filtro Particula'),
                                        ('limp_circuito_refri','Limpieza circuito térmico'),
                                        ('limp_circuito_clima','Limpieza circuito climatización'),
                                        ('carga','Carga'),
                                    ]
                                    , default='none' )

    # ################################################################################
    # campos de calculo de margenes y comisiones 
    # ################################################################################
    # Coste no definido, o aproximado, iremos a 5% del valor de PVP o en su defecto ???
    q2_po_no_cost = fields.Boolean(string='Sin coste fiable', store=True, default=False)   
    # Importe total de la venta                 
    q2_sale_amount_net = fields.Float(string='Importe total de la venta Neto', store=True, digits=(16, 4)) 
    # Coste de neto 
    q2_sale_cost_net = fields.Float(string='Coste total de la venta Neto', store=True, digits=(16, 4))      
    # Importe de margen
    q2_sale_profit_gross = fields.Float(string='Beneficio bruto de la venta', store=True, digits=(16, 4))   
    # Porcentage de Margen
    q2_sale_margin_gross = fields.Float(string='Margen bruto de la venta', store=True, digits=(16, 4))      
    # Fecha de ultimo calculo
    q2_last_calculate_update = fields.Datetime(string="Last Stage Update", default=fields.Datetime.now)

    # #############################################################################
    # GESTION DE ALBARANES NO FACTURABLES
    # #############################################################################
    # Motivo de la cancelacion
    q2_cancel_reason = fields.Selection(
        [
             ('pp','PP  Presupuesto no aceptado')
            ,('cc','CC  Cambio Cliente')
            ,('pd','PD  Pedido duplicado')
            ,('nr','NR  No retirado / No entregado')
            ,('nf','NF  Albaran no facturable') # (CB)
            ,('om','sc  Sin clasificar, otros') 
        ]
        ,default='om'
        ,index=True
        ,required=True 
        ,editable=False
        ,tracking=True
    )

    """
    ##############################################################################
    # Gestion de acciones requeridas
    # Hay acciones que requieren accion por parte de un operador
    q2_action_required = fields.Boolean(default=False, editable=True, string= "Acción requerida por el usuario")
    # De que operador se requiere la accion
    q2_action_required_user = fields.Many2one(
        'res.users', string='Crea la orden', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)
    # Fecha y hora en la que se solicita la accion para poder temporizar los tiempos
    q2_last_calculate_update = fields.Datetime(
        string="Last Stage Update", default=fields.Datetime.now
    )
    """
    # #############################################################################
    # GESTION DE COMISIONES AGENTES EXTERNOS E INTERNOS (Comerciales y operadores)
    # #############################################################################
    # Agente externo asignado para este cliente se registra en el modelo de res.partner  en el campo agent_ids
    # Comercial de Soterma asignado para este cliente se registra en el modelo de res.partner  en el campo user_id, tendra que estar dentro del equipo de ventas
    # sales_team.group_sale_manager / sales_team.group_sale_salesman 
    # USUARIOS QUE INTERVIENEN EN EL PROCESO DE COMPRA
    #> User_id = Usuario que toma la razon o realiza el presupuesto segun sea comercial o no
    #> q2_user_salesman_owner = Usuario Comercial que toma la razon para atenderla y hacer el presupuesto, sera el owner del 
    #> q2_user_confirm_sale = Usuario que confirma el presupuesto pero que no tiene porque procesar el pedido
    
    # Usuario que realiza el presupuesto y lo notifica (solo puede ser un usuario del equipo de ventas )
    #q2_user_salesman_owner = fields.Many2one(
    #    'res.users', string='Crea la orden', index=True, tracking=2, default=lambda self: self.env.user,
    #    domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
    #        self.env.ref("sales_team.group_sale_salesman").id
    #    ),)

    q2_user_salesman_owner = fields.Many2one(
        'res.users', string='Crea la orden', index=True, tracking=2, default=None,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    # Usuario que confirma el presupuesto, que deberia de ser el mismo que lo realiza (solo puede ser un usuario del equipo de ventas )
    q2_user_confirm_sale = fields.Many2one(
        'res.users', string='Confirma la venta', index=True, tracking=2, default=None,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    # Usuario que confirma la compra a proveedor si fuese necesario, que deberia de ser el mismo que lo realiza (solo puede ser un usuario del equipo de ventas )
    q2_user_confirm_purchase = fields.Many2one(
        'res.users', string='Confirma la compra', index=True, tracking=2, default=None,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    # Usuario que cancela el pedido o presupuesto que solo podrá ser el mismo que lo genera o el administrador de ventas (siempre del equipo de ventas)
    q2_user_unlock = fields.Many2one(
        'res.users', string='Cancela la orden', index=True, tracking=2, default=None,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ),)

    # Usuario que recibe la consulta tecnica para este pedido 

    # El agente 
    # Persona externa o interna que capta o recupera al cliente
    # q2_partner_agent_account = fields.Many2one('res.partner', string='Agente de la cuenta', index=True, store=True)  
    # q2_partner_manager_account = fields.Many2one('res.users', string='Gestor de la cuenta', index=True, store=True)
    # #############################################################
    # METODOS DE VERIFICACION DE USUARIOS
    # #############################################################
    # Metodos a sobreescribir para el control y registro de eventos
    # @api.multi

    def action_is_sale(self):
        #wdb.set_trace()
        self.q2_sale_type = 'product' 

    def action_is_service(self):
        #wdb.set_trace()
        self.q2_sale_type = 'service' 

    # verifica si el usuario es valido para realizar la operacion 
    # para que lo sea se tiene que dar la condicion de que sea el usuario que lo creo o el administrador
    @api.model
    def _check_user_auth(self, auth_user):
        #wdb.set_trace()
        if self.q2_is_sales_team_manager or auth_user == self.env.uid :
            return True
        else:
            raise ValidationError(_('Esta orden solo puede ser modificada por el usuario que la creo, por favor pongase en contacto con él.'))

    # Verificamos que los presupuestos abiertos no tengan el producto demandado o algunos de sus equivalentes
    # En caso de que exista algun presupuesto para este cliente con algun producto equivalente, 
    # Notificaremos de su existencia y daremos la opcion de no hacer nada o lo abriremos en vez de crear otro

    # Convertimos la fecha 
    def convert_TZ_UTC(self, mydate=datetime.now(), tz=pytz.timezone('UTC')):
        #wdb.set_trace()
        tz = tz if tz else self.env.user.tz
        fmt = "%Y-%m-%d %H:%M:%S"
        # Current time in UTC
        now_utc = datetime.now(pytz.timezone('UTC'))
        # Convert to current user time zone
        now_timezone = now_utc.astimezone(tz)
        UTC_OFFSET_TIMEDELTA = datetime.strptime(now_utc.strftime(fmt), fmt) - datetime.strptime(now_timezone.strftime(fmt),fmt)
        local_datetime = datetime.strptime(mydate.strftime(fmt), fmt)
        return local_datetime + UTC_OFFSET_TIMEDELTA
        #result_utc_datetime = local_datetime + UTC_OFFSET_TIMEDELTA
        #return result_utc_datetime.strftime(fmt)
    
    def _check_duplicate_sale_order(self,days_ago = 7):
        #wdb.set_trace()
        today = fields.Date.context_today(self)
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        date_tz_utc = self.convert_TZ_UTC(today,user_tz)
        #date_tz = pytz.UTC.localize(today).astimezone(user_tz)
        # days_ago = 7  dias atras ue vamos a tener en cuenta en la busqueda
        day_from = date_tz_utc - timedelta(days = days_ago)
        day_to = date_tz_utc

        domain = []
        domain.append(("company_id", "=", self.env.user.company_id.id))
        domain.append(("partner_id","=",self.partner_id.id))
        domain.append(("state","not in",['cancel','done',]))
        #wdb.set_trace()
        # en el tema de las fechas tenemos que generar un rango de 24h y si es lunes que coja el viernes
        if self.name != 'New':
            domain.append(('create_date','>=',day_from.strftime('%Y-%m-%d 00:00:00')))
            domain.append(('create_date','<=',day_to.strftime('%Y-%m-%d 00:00:00')))
        sos = self.env["sale.order"].search(domain)

        for so in sos:
            if so.name != self.name:
                raise ValidationError(_('Este cliente ya tiene ordenes abiertas por otro comercial, por favor pongase en contacto con él o con el responsable de ventas para que la libere.'))
        return True

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        #wdb.set_trace()
        # Solo permitiremos la duplicacion de presupuestos propios o si es administrador
        auth_user = self.user_id
        if self._check_user_auth(auth_user):
            return super(SaleOrder, self).copy(default)

    # Al crear un prosupuesto nuevo desencadenaremos los siguientes eventos
    # > Se le asigna a ese presupuesto el usuario que lo está dando de alta
    # > Se verifica si tiene comercial asignado el cliente y se le asigna 
    # > Se verifica si tiene agente externo y se le asigna
    @api.model
    def new(self, values={}, origin=None, ref=None):
        #wdb.set_trace()
        res = super(SaleOrder, self).new(values, origin, ref)
        return res  

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        # La opcion de cambio de cliente solo podrá ser realizada por el comercial asignado o el responsable del dpto ventas
        # Update the following fields when the partner is changed:
        #- Pricelist
        #- Payment terms
        #- Invoice address
        #- Delivery address
        #- Sales Team
        #wdb.set_trace()
        change = False
        if self.name=="Nuevo":
            change = True
        if not self.partner_id:
            change = True
        else:
            if self._check_is_user_owner(): 
                change = True
        if change:
            res = super(SaleOrder, self).onchange_partner_id()
            return res
        else:
            # Solo los comerciales pueden 
            raise UserError(_(
                'El cliente solo puede ser modificado por el comercial de la cuenta: %s'
            ) % (self.env.user.name))
            #if self._is_member_sales_team():
            #    res = super(SaleOrder, self).onchange_partner_id()
          
    def action_operator_take_reason(self):
        #wdb.set_trace()
        vals = {}
        option = self.env.context.get('reason_type')
        vals['state'] = option
        vals['q2_is_reason'] = True
        self.write(vals)

    def action_salesman_take_reason(self):
        # Verificamos si se trata de un comercial
        #wdb.set_trace()
        vals = {}
        if self._check_is_salesman():
            if not self.q2_user_salesman_owner:
                vals['q2_user_salesman_owner'] = self.env.uid
                vals['state'] = 'draft'
            vals['q2_is_reason'] = False
        self.write(vals)

    @api.model
    def create(self, vals):
        # Verificamos que no haya otro presupuesto abierto para este cliente en las ultimas 12 horas
        # if self._check_duplicate_sale_order():
        duplicate = self._check_duplicate_sale_order()
        # Verificamos si se trata de un comercial
        #wdb.set_trace()
        if self._check_is_salesman():
            vals['q2_is_reason'] = False
            if not self.q2_user_salesman_owner:
                self.q2_user_salesman_owner = self.env.uid
            #if self.partner_id.user_id == self.env.uid:
                # Si se trata de un comercial tendremos que asignarle la operacion
                # Verificamos si el comercial es el mismo que tiene asignada la cuienta
                # self.q2_user_salesman_owner = self.env.uid
        else:
            vals['state'] = 'reason'    
        #wdb.set_trace()
        res = super(SaleOrder, self).create(vals)
        return res  
    # #############################################################################
    # EN UN PROCESO QUE SE LANZARA DIARIAMENTE SE AJUSTAN LS ESTADISTICAS
    # #############################################################################
    # > Se calculan las cantidades y margenes y se asignan a los campos de presupuestos y ordenes abiertas de res.users y re.partners
    # > 
    """
    @api.model
    def write(self, vals):
        #wdb.set_trace()
        if self._check_is_salesman():
            #wdb.set_trace()
            # Si es un comercial y aun es razon lo convertimos en su pedido            
            if self.q2_is_reason:
                vals['q2_is_reason'] = False
            if self.state == 'draft':
                self.q2_user_salesman_owner = self.env.uid
        res = super(SaleOrder, self).write(vals)
        return res
    """
    #@api.model
    #def update(self, vals):
    #    #wdb.set_trace()
    #    res = super(SaleOrder, self).update(vals)
    #    return res

    def action_confirm(self):
        #wdb.set_trace()
        if self._check_is_salesman():
            vals = {}
            if not self.q2_user_salesman_owner:
                vals['q2_user_salesman_owner'] = self.env.uid
            if not self.q2_user_confirm_sale:
                vals['q2_user_confirm_sale'] = self.env.uid
            vals['q2_is_reason'] = False
            self.write(vals)
            res = super(SaleOrder, self).action_confirm()
            return res

    # Accion enviar presupuesto
    #def action_quotation_sent(self):
    #    #wdb.set_trace()
    #    if not self.q2_user_salesman_owner:
    #        if self._check_is_salesman():
    #            self.q2_user_salesman_owner = self.env.uid
    #            res = super(SaleOrder, self).action_quotation_sent()
    #            return res        


    #Accion Presupuesto
    def action_draft(self):
        wdb.set_trace()
        # antes de ejecutar la accion de borrado 
        if self._check_is_user_owner(): 
            #wdb.set_trace()
            res = super(SaleOrder, self).action_draft()
            return res        
        else:
            # Solo los comerciales pueden 
            raise UserError(_(
                'El cliente solo puede ser modificado por el comercial de la cuenta  %s  o el responsable de ventas'
            ) % (self.q2_user_salesman_owner))

 
    def action_unlock(self):
        # Boton de confirmacion de presupuesto pasando a pedido
        # Un presupuesto o pedido solo podrá ser cancelado por su creador o por un responsable de venta, administraciom, o it
        # Verificamos si el usuario que quiere cancelar el pedido coincide con el que lo ha creado
        # o Es el Responsable del departamento comercial
        # Sobreescribimos el metodo
        # Comprobamos si cumple la condicion
        # Si la cumple ejecutamos la cancelacion y guardamos el usuario que realiza la accion y la fecha en la que se realiza
        wdb.set_trace()
        # antes de ejecutar la accion de cancelar 
        if self._check_is_user_owner(): 
            #wdb.set_trace()
            res = super(SaleOrder, self).action_unlock()
            return res        
        else:
            # Solo los comerciales pueden 
            raise UserError(_(
                'El cliente solo puede ser modificado por el comercial de la cuenta: %s'
            ) % (self.q2_user_salesman_owner))

    def action_cancel(self):
        # Boton de confirmacion de presupuesto pasando a pedido
        wdb.set_trace()
        # antes de ejecutar la accion de borrado 
        if self._check_is_user_owner(): 
            #wdb.set_trace()
            res = super(SaleOrder, self).action_cancel()
            return res        
        else:
            # Solo los comerciales pueden 
            raise UserError(_(
                'El cliente solo puede ser modificado por el comercial de la cuenta  %s  o el responsable de ventas'
            ) % (self.q2_user_salesman_owner))


    def action_set_devoluiones(self, userid=None):
        #wdb.set_trace()
        # self.ensure_one()
        # raise ValidationError(_('Prueba de llamada al módulo action_recalculate_commission()'))
        # Buscar ventas realizadas
        ls_dev = self.env['sale.order'].search([('client_order_ref','like','DEV')])
        # Recorremos todas las ventas
        for so in ls_dev:
            # verificamos que corresponde a una devolucion
            so_search = re.search('\s*DEV\s*(S\d*)\s*', so.client_order_ref , re.IGNORECASE)

            if so_search:
                so_name = so_search.group(1)
                # localizamos el so devuelto
                so_dev = self.env['sale.order'].search([('name','=',so_name)])
                if so_dev:
                    so.update({'q2_is_rma':True})    
                    so_dev.update({'q2_with_rma' : True })     
                    print(so)
                    print(so_dev)
                    
    def recalculate_commission(self):
        #wdb.set_trace()
        vals = [] # valores a actualizar
        #self.ensure_one()
        #raise ValidationError(_('Prueba de llamada al módulo action_recalculate_commission()'))

        # Recorremos todas las ventas
        for so in self:
            coste_envio = 5.0               # marcamos un coste medio a todas las compras de 5 € salvo que se detecte en la linea recogida
            margen_producto_default = 0.15  # Margen que le aplicaremos a los productos adquiridos para un servicio de taller para el calculo de comisiones
            margen_maniobra_st = 0.25       # Margen establecido por defecto sobre el precio del servicio de taller para el calculo del margen una vez descontado el coste del producto si lo llevara
            total_sale = so.amount_untaxed  # Importe total de la venta sin impuestos
            total_cost = 0.0                # Coste total en € calculado a partir de los costes de compra del producto y los costes de envio
            total_profit=0.0                # Benefiio total bruto de la operación antes del calculo de comisiones
            total_margin_maniobra=0.0       # Margen total bruto de la operación antes de aplicar comisiones 
            usr_open = so.user_id           # Usuario que crea la orden o presupuesto
            usr_close = None                # Ususario que termina de realizar todo el proceso, no se tendra en cuenta si el proceso no esta completado
            usr_close_date = None           # Fecha hora del último 
            user_close_look = False         # Bit que bloquea el cambio de usuario de cierre. Si la compra es modificada por otro usuario distinto al que crea la orden, quedará bloqueada
            usr_agent = None                # Agente del cliente, comercial externo o interno que capta el cliente
            usr_manager = None              # Agente del cliente, comercial interno que gestiona la cuenta


            # Recorreremos todas las lineas de la SO
            for sol in so.order_line:
                #wdb.set_trace()
                # Si es Servicio taller
                # Buscamos si se es recogida en tienda
                # Si no es de recogida en tienda le cargaremos el valor de envio por defecto que sera el coste medio de envio 
                sol_product = sol.product_id
                # buscamos que tipo de linea Ees 
                # Si es un transporte
                if sol_product.default_code[0:3] == 'DLV':
                    if sol_product.default_code == 'DLVT':
                        coste_envio = 0.0
                # Si es un servicio taller
                # elif sol_product.default_code[0:3] == 'STL' or sol_product.default_code[0:3] == 'STR' or sol_product.default_code[0:3] == 'STF' :
                
                    # Si es un SERVICIO TALLER
                    #   - Si es Servicio taller SIN PRODUCTO > tenemos que hacer el calculo del coste sobre un porcentaje de lo facturado
                    #   - Si es Servicio taller CON PRODUCTO > tenemos que Calcular el coste del producto añadirle un margen de operacion 
                    #                                          y el resto se computaria como servicio taller al que le aplicariamos el margen de maniobra sobre servicio taller 
                    # 
                    pass
                # Si es otro
                else:
                    # Si es prodcto
                    #   - 
                    pass
                # Verificamos si tiene compra asociada al pedido
                # Coste de los productos
                total_cost_po=0.0
                ls_po=None
                
                # Obtenemos las PO que se han generado para esta orden de compra
                ls_po = self.env['purchase.order'].search([('origin','=',so.name),('state','=','purchase')])
                
                # Si hay compra obtenemos todos los articulos de todas las compras
                if ls_po:
                    #wdb.set_trace()
                    for po in ls_po:
                        po_no_cost,po_total_cost, po_user_close, po_usr_close_date = po.get_total_cost_and_user_purchase()
                        # Si el coste no es objetivo lo marcamos 
                        if po_no_cost:
                            vals['q2_po_no_cost']=True
                        # Si el coste es superior a 0€
                        if po_total_cost > 0:
                            total_cost += po_total_cost
                        if po_user_close:
                            if po_user_close != usr_open:
                                user_close = po_user_close
                                usr_close_date = po_usr_close_date

                # Si no hay compra en la orden
                else:   
                    #wdb.set_trace()
                    #Buscamos el producto y cogemos su ultimo precio de compra para cualquier 
                    last_purchase_product = self.env['purchase.order.line'].search([
                        ('product_id','=',sol_product.id),
                        ('price_unit','>',0),
                        ('state','in',['purchase','sent']),
                        ],
                        order='write_date desc',
                        limit=1) 
                    if last_purchase_product:
                        #wdb.set_trace()
                        q2_po_no_cost = True 
                        pol = last_purchase_product[0]
                        # Calculamos el coste teniendo encuenta el ultimo precio de compra y la cantidad vendida de este articulo 
                        total_cost += pol.price_unit * sol.product_uom_qty
                    else:
                        #wdb.set_trace()
                        #Si no tuviera compraningun historico de compra, 
                        # Lo marcariamo la orden como coste de compra 
                        q2_po_no_cost = True 
                        # cogeriamos el precio de venta y aplicariamos un 60½ de descuentoprecio por
                        average_discount_supplier = 1 - 0.6 
                        total_cost += sol_product.list_price * average_discount_supplier

            # asignamos los costes
            #wdb.set_trace()
            if total_cost_po > 0:
                total_cost += total_cost_po + coste_envio
            else:
                q2_po_no_cost = True
           # Si se han realizado actualizaciones las actualizamos 
            if vals:
                #wdb.set_trace()
                self.update(vals)

    def action_recalculate_commission_from_order(self):
        self.recalculate_commission()

    def action_recalculate_commission_from_user (self, userid=None):
        self.action_recalculate__commission_from_user_data_range(userid)

    def action_recalculate__commission_from_user_data_range(self, userid=None,date_ini=time.strftime('%Y-12-31'), date_fin=time.strftime('%Y-01-01')):
        #Buscar ventas realizadas en la fecha determinada
        # fecha en formato YYYY-MM-DD
        domain=[]
        if userid:    
            domain=[('date_order','>=',date_ini),
                    ('date_order','<=', date_fin),
                    ('state', 'in', ['sale','done'])
                    ('user_uid','=',userid),
                ]
        else:
            domain=[('date_order','>=',date_ini),
                    ('date_order','<=', date_fin),
                    ('state', 'in', ['sale','done']),
                ]

        ls_so = self.env['sale.order'].search(domain)

        for so in ls_so:
            self.recalculate_commission()