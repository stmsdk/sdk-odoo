# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import html2plaintext
from datetime import datetime
from datetime import date
from datetime import timedelta
import base64
import re
import pytz
import wdb #wdb.set_trace()

# Tipo de producto sobre el que se actua 
# [ Vehiculo, Filtro, Tuberia, Radiador Agua, Radiador Aceite, Radiador Agua/Aceite, Entriador Aceite, Enfriador de aceite tubular, Intercooler, Condenador, otros ]
class Q2_Workshop_Product_Type(models.Model):

    _name = "q2_workshop.product_type"
    _description = "Workshop Product Type"

    name = fields.Char('Product Type name', required=True, translate=True)
    code = fields.Char('Product Type code', translate=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]

# Tipo de servicio sobre el que se actua [ Mecanica Circuitos T/A, Filtros/Escapes, Dispositivos, Otros]
class Q2_Workshop_Service_Type(models.Model):

    _name = "q2_workshop.service_type"
    _description = "Workshop Service Type"

    name = fields.Char('Service Type name', required=True, translate=True)
    code = fields.Char('Service Type code', translate=True)
    color = fields.Integer('Color Index')
    active = fields.Boolean('Activo', default=True )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]

class Q2_Workshop_Stage(models.Model):

    _name = "q2_workshop.stage"
    _description = "Workshop Stage"
    _order = 'sequence'

    name = fields.Char('Stage Name', translate=True, required=True)
    code = fields.Char('Stage code', translate=True)
    sequence = fields.Integer(help="Used to order the q2_workshop stages", default=1)
    user_id = fields.Many2one('res.users', string='Owner', required=True, ondelete='cascade', default=lambda self: self.env.uid, help="Owner of the q2_workshop stage")
    fold = fields.Boolean('Folded by Default')
    active = fields.Boolean('Activo', default=True )

class Q2_Workshop_Tag(models.Model):

    _name = "q2_workshop.tag"
    _description = "Workshop Tag"

    name = fields.Char('Tag Name', required=True, translate=True)
    code = fields.Char('Tag code', translate=True)
    color = fields.Integer('Color Index')
    active = fields.Boolean('Activo', default=True )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class Q2_Workshop(models.Model):

    _name = 'q2_workshop'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Servicio Taller"
    _order = 'sequence, id desc'

    def _get_default_stage_id(self):
        #wdb.set_trace()
        #return self.env['q2_workshop.stage'].search([('user_id', '=', self.env.uid)], limit=1)
        res = self.env['q2_workshop.stage'].search([], limit=1)
        return res

    #name = fields.Text(compute='_compute_name', string='Servicio', store=True)
    name = fields.Text(string='Servicio', store=True)
    user_id = fields.Many2one('res.users', string='Owner', default=lambda self: self.env.uid)
    memo = fields.Html('Workshop Content')
    sequence = fields.Integer('Sequence', default=0)
    stage_ids = fields.Many2many('q2_workshop.stage', 
                                'q2_workshop_stage_rel', 
                                'q2_workshop_id', 'stage_id',
                                string='Stages of Users',  
                                default=_get_default_stage_id
                                )
    stage_id = fields.Many2one('q2_workshop.stage', 
                                #compute='_compute_stage_id',
                                #inverse='_inverse_stage_id', 
                                string='Stage', 
                                #default='_compute_stage_id'
                                )
    service_type_id = fields.Many2one(
                                comodel_name='q2_workshop.service_type', 
                                string='Tipo Servicio', 
                                )
    product_type_id = fields.Many2one(
                                comodel_name='q2_workshop.product_type', 
                                string='Tipo Producto',
                                )
    tag_ids = fields.Many2many('q2_workshop.tag', 
                               'q2_workshop_tags_rel', 
                               'q2_workshop_id', 
                               'tag_id', 
                               string='Tags'
                               )
    open = fields.Boolean(string='Active', default=True)
    date_done = fields.Date('Date done',default= datetime.now())
    color = fields.Integer(string='Color Index')
    origin = fields.Char(
        string="Source Document",
        help="Documento origen.",
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Orden de venta",
    )

    #img_attach = fields.Html('Image', compute="_compute_get_img_url_attachments")
    img_attach = fields.Html('Image', compute="_compute_get_img_url_attachments")

    def create(self,vals):
        #wdb.set_trace()
        # verificamos que no este dado de alta el servicio
        st = self.env['q2_workshop'].search([('origin','=',vals['origin'])])
        if not st:
            res = super(Q2_Workshop, self).create(vals)
            return res
        
    @api.onchange('stage_id') 
    def _onchange_stage(self):
        #wdb.set_trace()
        self.sudo().write({
                'stage_id':self.stage_id
            }
        )        
        if self.sale_id:
            vals = {
                'q2_ws_status': self.stage_id.code
            }
            if self.stage_id == 'stend':
                self.sale_id.checked_production()

            self.sale_id.sudo().write(vals)
    
    @api.depends('memo')
    def _compute_name(self):
        """ Read the first line of the memo to determine the q2_workshop name """
        #wdb.set_trace()
        for q2_workshop in self:
            text = html2plaintext(q2_workshop.memo) if q2_workshop.memo else ''
            q2_workshop.name = text.strip().replace('*', '').split("\n")[0]

    def _compute_stage_id(self):
        #wdb.set_trace()
        #first_user_stage = self.env['q2_workshop.stage'].search([('user_id', '=', self.env.uid)], limit=1)
        #first_user_stage = self.env['q2_workshop.stage'].search([], limit=1)

        for q2_workshop in self:
            if q2_workshop.origin == 'S15959':
                #wdb.set_trace()
                last_stage_id = None 
            #for stage in q2_workshop.stage_ids.filtered(lambda stage: stage.user_id == self.env.user):
            for stage in q2_workshop.stage_ids.filtered(lambda stage: stage.active == True):
                last_stage_id = stage
            q2_workshop.stage_id = last_stage_id
            # q2_workshop without user's stage
            #if not q2_workshop.stage_id:
            #    q2_workshop.stage_id = q2_workshop.stage_id #first_user_stage

    def _compute_service_type_id(self):
        #wdb.set_trace()
        items = self.env['q2_workshop.product_type'].search([])
        for ws in self:
            if items:
                ws.service_type_id = items

    def _compute_product_type_id(self):
        #wdb.set_trace()
        items = self.env['q2_workshop.product_type'].search([])
        for ws in self:
            if items:
                ws.service_type_id = items

    def _inverse_stage_id(self):
        #wdb.set_trace()
        for q2_workshop in self.filtered('stage_id'):
            #q2_workshop.stage_ids = q2_workshop.stage_id + q2_workshop.stage_ids.filtered(lambda stage: stage.user_id != self.env.user)
            q2_workshop.stage_ids = q2_workshop.stage_id + q2_workshop.stage_ids.filtered(lambda stage: stage.open == True)

    @api.model
    def name_create(self, name):
        #wdb.set_trace()
        return self.sudo().create({'memo': name}).name_get()[0]

    """
    # Funcion de obtencion de items a mostrar en la lista
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        #wdb.set_trace()
        # Primero verificamos que tenga stages
        if groupby and groupby[0] == "stage_id" and (len(groupby) == 1 or lazy):
            # Obtenemos los stages para el usuario
            stages = self.env['q2_workshop.stage'].search([('user_id', '=', self.env.uid)])
            
            if stages:  # if the user has some stages
                result = [{  # q2_workshops by stage for stages user
                    '__context': {'group_by': groupby[1:]},
                    '__domain': domain + [('stage_ids.id', '=', stage.id)],
                    'stage_id': (stage.id, stage.name),
                    'stage_id_count': self.search_count(domain + [('stage_ids', '=', stage.id)]),
                    '__fold': stage.fold,
                } for stage in stages]

                # q2_workshop without user's stage
                nb_q2_workshops_ws = self.search_count(domain + [('stage_ids', 'not in', stages.ids)])
                if nb_q2_workshops_ws:
                    # add q2_workshop to the first column if it's the first stage
                    dom_not_in = ('stage_ids', 'not in', stages.ids)
                    if result and result[0]['stage_id'][0] == stages[0].id:
                        dom_in = result[0]['__domain'].pop()
                        result[0]['__domain'] = domain + ['|', dom_in, dom_not_in]
                        result[0]['stage_id_count'] += nb_q2_workshops_ws
                    else:
                        # add the first stage column
                        result = [{
                            '__context': {'group_by': groupby[1:]},
                            '__domain': domain + [dom_not_in],
                            'stage_id': (stages[0].id, stages[0].name),
                            'stage_id_count': nb_q2_workshops_ws,
                            '__fold': stages[0].name,
                        }] + result
            else:  # if stage_ids is empty, get q2_workshop without user's stage
                nb_q2_workshops_ws = self.search_count(domain)
                if nb_q2_workshops_ws:
                    result = [{  # q2_workshops for unknown stage
                        '__context': {'group_by': groupby[1:]},
                        '__domain': domain,
                        'stage_id': False,
                        'stage_id_count': nb_q2_workshops_ws
                    }]
                else:
                    result = []
            #wdb.set_trace()
            return result
        #wdb.set_trace()
        return super(Q2_Workshop, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
    """

    # Funcion de obtencion de items a mostrar en la lista
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        #wdb.set_trace() 
        # Primero verificamos que tenga stages
        if groupby and groupby[0] == "stage_id" and (len(groupby) == 1 or lazy):
            # Obtenemos los stages para el usuario
            #stages = self.env['q2_workshop.stage'].search([('user_id', '=', self.env.uid)])
            stages = self.env['q2_workshop.stage'].search([('fold', '=', True)])
            #stages = self.env['q2_workshop.stage'].search([])
            
            if stages:  # if the user has some stages
                result = [{  # q2_workshops by stage for stages user
                    '__context': {'group_by': groupby[1:]},
                    '__domain': domain + [('stage_ids.id', '=', stage.id)],
                    #'__domain': domain + [('stage_ids', '=', stage.id)],
                    'stage_id': (stage.id, stage.name),
                    'stage_id_count': self.search_count(domain + [('stage_ids', '=', stage.id)]),
                    '__fold': stage.fold,
                } for stage in stages]

                # q2_workshop without user's stage
                nb_q2_workshops_ws = self.search_count(domain + [('stage_ids', 'not in', stages.ids)])
                if nb_q2_workshops_ws:
                    # add q2_workshop to the first column if it's the first stage
                    dom_not_in = ('stage_ids', 'not in', stages.ids)
                    if result and result[0]['stage_id'][0] == stages[0].id:
                        dom_in = result[0]['__domain'].pop()
                        result[0]['__domain'] = domain + ['|', dom_in, dom_not_in]
                        result[0]['stage_id_count'] += nb_q2_workshops_ws
                    else:
                        # add the first stage column
                        result = [{
                            '__context': {'group_by': groupby[1:]},
                            '__domain': domain + [dom_not_in],
                            'stage_id': (stages[0].id, stages[0].name),
                            'stage_id_count': nb_q2_workshops_ws,
                            '__fold': stages[0].name,
                        }] + result
            else:  # if stage_ids is empty, get q2_workshop without user's stage
                nb_q2_workshops_ws = self.search_count(domain)
                if nb_q2_workshops_ws:
                    result = [{  # q2_workshops for unknown stage
                        '__context': {'group_by': groupby[1:]},
                        '__domain': domain,
                        'stage_id': False,
                        'stage_id_count': nb_q2_workshops_ws
                    }]
                else:
                    result = []
            #wdb.set_trace()
            return result
        #wdb.set_trace()
        return super(Q2_Workshop, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    def action_close(self):
        #wdb.set_trace()
        return self.sudo().write({'open': False, 'date_done': fields.date.today()})

    def action_open(self):
        #wdb.set_trace()
        return self.sudo().write({'open': True})

    # Accions de visualizacion
    def action_view_sale_order(self):
        #wdb.set_trace()
        """This function returns an action that display existing sales order
        of given rma.
        """
        self.ensure_one()
        # Vissualizamos el formulario para el id de la orden de venta asciada a la reparacion
        return self.sale_id.get_formview_action()
    
    # modulo que obtiene el id de la imagen adjunta al servicio taller
    def _compute_get_img_url_attachments(self):
        # http://localhost:8069/web/content/429339
        # raiz_url/web/content/<int:id_attachments
        #wdb.set_trace()
        for elem in self:
            domain = [
            ('res_model', '=', 'sale.order'),
            ('mimetype', 'ilike', 'image/'),
            ('res_id', '=', elem.sale_id.id),
            ]

            attach_id = self.env['ir.attachment'].sudo().search(domain)
            #wdb.set_trace()
            if attach_id:
                #decoded_data = base64.b64decode(attach_id[0])
                #wdb.set_trace()
                #elem.img_attach = decoded_data
                img_url = 'data:image/jpeg;base64,%s' % attach_id[0].datas
                elem.img_attach = '<img src="%s"/>' % img_url
            else:
                elem.img_attach = '<br/>'
                #elem.img_attach = None
                