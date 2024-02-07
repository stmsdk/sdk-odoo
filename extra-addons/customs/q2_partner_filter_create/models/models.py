# -*- coding: utf-8 -*-
from unicodedata import decimal
from odoo.exceptions import ValidationError
from odoo import models, fields, api

#import wdb ##wdb.set_trace()

class q2_partner_filter_create(models.Model):
    _inherit = "res.partner"

    is_cb = fields.Boolean(string='Cliente Alb. Sin Valorar',
                           default=False,
                           copy=False
                           ) 
    # usaremos esta descripcion para los clientes B
    # Añadimos un campo para controlar los clientes nuevos 
    # Los clientes de paso se marcaran con un boleano que se desmarcaran en el momento que repitan en la cventa
    @api.model
    def create(self, vals):
        # Antes de crear el usuario, verificamos que tiene al menos unos de los campos requeridos para checkear duplicados 
        #wdb.set_trace()
        vat = None
        phone = None
        mobile = None
        email = None

        if 'vat' in vals.keys():
            vat = vals['vat']
        if 'phone' in vals.keys():
            phone = vals['phone']
        if 'mobile' in vals.keys():
            mobile = vals['mobile']
        if 'email' in vals.keys():
            email = vals['email']
        
        # Tenemos que verificar por un lado que se umplen algun criterio de filtro
        go_create = False
        # y por otro lado que no estan duplicados
        is_duplicate = False

        #wdb.set_trace()
        
        # Si tiene CIF, verificamos que no hay otro partner con el mismo cif
        if vat and len(vat)>0:
            go_create = True
            # Buscamos si hay un partner con ese valor
            qvat = self.env['res.partner'].search([('vat','=',vat)])
            if qvat:
                # Si existe un partner con ese valor lanzamos el mensaje de duplicidad
                is_duplicate = True
                raise ValidationError(
                    (
                        "Verifique que el cliente no esta duplicado, ya existe un cliente con este CIF"
                    )
                )

        # Si tiene teléfono, verificamos que no hay otro partner con el mismo teléfono
        if phone and len(phone)>0:
            # Buscamos si hay un partner con ese valor
            # Normalizamos el telefono
            # Quitamos los espacio y simbolos +-/,. 
            number = phone.replace(' ','').replace('+','').replace('-','').replace(',','').replace('/','').replace('.','')    
            # y tomamos los 9 ultimos digitos empezando por la izquierda para evitar los prefijos
            if len(number)<9:
                raise ValidationError(
                    (
                        "El numero de movil no es valido"
                    )
                )
            else:
                number = number[-9:]
            # Incluimos los € paa ampliar la busqueda con y sin espacion
            go_create = True
            number = "{}%{}%{}%{}%{}%{}%{}%{}%{}".format(number[0],number[1],number[2],number[3],number[4],number[5],number[6],number[7],number[8])
            qphone = self.env['res.partner'].search(['|',('phone','ilike',number),('mobile','ilike',number)])
            if qphone:
                # Si existe un partner con ese valor lanzamos el mensaje de duplicidad
                is_duplicate = True
                raise ValidationError(
                    (
                        "Verifique que el cliente no esta duplicado, ya existe un cliente con este Teléfono"
                    )
                )

        # Si tiene móvil, verificamos que no hay otro partner con el mismo movil
        if mobile and len(mobile)>0:
            # Buscamos si hay un partner con ese valor
            # Normalizamos el telefono
            # Quitamos los espacio y simbolos +-/,. 
            number = mobile.replace(' ','').replace('+','').replace('-','').replace(',','').replace('/','')    
            # y tomamos los 9 ultimos digitos empezando por la izquierda para evitar los prefijos
            if len(number)<9:
                raise ValidationError(
                    (
                        "El numero de movil no es valido"
                    )
                )
            else:
                number = number[-9:]
            # Incluimos los € paa ampliar la busqueda con y sin espacion
            # number = "{}%{}%{}%{}".format(number[:3],number[3:5],number[5:7],number[7:9])
            number = "{}%{}%{}%{}%{}%{}%{}%{}%{}".format(number[0],number[1],number[2],number[3],number[4],number[5],number[6],number[7],number[8])
            # Buscamos si hay un partner con ese valor
            go_create = True
            qmobile = self.env['res.partner'].search(['|',('mobile','=',number),('phone','ilike',number)])
            if qmobile:
                # Si existe un partner con ese valor lanzamos el mensaje de duplicidad
                is_duplicate = True
                raise ValidationError(
                    (
                        "Verifique que el cliente no esta duplicado, ya existe un cliente con este Móvil"
                    )
                )

        # Si tiene correo, verificamos que no hay otro partner con el mismo correo
        if email and len(email)>0:
            go_create = True
            # Buscamos si hay un partner con ese valor
            qemail = self.env['res.partner'].search([('email','=',email)])
            if qemail:
                # Si existe un partner con ese valor lanzamos el mensaje de duplicidad
                is_duplicate = True
                raise ValidationError(
                    (
                        "Verifique que el cliente no esta duplicado, ya existe un cliente con este Correo Electronico"
                    )
                )

        # Por ultimo si los criterios 
        if go_create and not is_duplicate:
            # Creamos el usuario
            new = super().create(vals)
            # Una vez creado el usuario crearremos las cuentas contables 
            """new_st = self.env['q2_workshop'].sudo().create(vals)"""
            p_vat = ''
            if new.vat and len(new.vat):
                p_vat = ' ({}) '.format(new.vat)
            
            num_acc = 100000 + new.id
            aar_vals = {
                'name':'Clientes (euros) - Nº {} {} {}'.format(new.id, p_vat, new.name),
                'code':'430{}'.format(num_acc),
                'user_type_id':1,
                'reconcile':True,
                'internal_type':'receivable',
            }

            aar = self.env['account.account'].sudo().create(aar_vals)
            aap_vals = {
                'name':'Proveedores (euros) - Nº {} {} {}'.format(new.id, p_vat, new.name),
                'code':'410{}'.format(num_acc),
                'user_type_id':2,
                'reconcile':True,
                'internal_type':'payable'
            }

            aap = self.env['account.account'].sudo().create(aap_vals)

            # Le asignamos al usuario las  cuentas contables
            #   property_account_payable_id             ['account.account']
            #   property_account_receivable_id          ['account.account']

            # Guardamos los cambios
            if aar and aap:
                new.sudo().write({
                    'property_account_receivable_id':aar.id,
                    'property_account_payable_id': aap.id,
                })
            else:
                raise ValidationError(
                    (
                        "El cliente ha sido creado, pero no se ha podido enlazar con una cuenta contable, por favor asocielo manualmente"
                    )
                )                

            return new
        else:
            raise ValidationError(
                (
                    "Por favor verifique los campos y compruebe que dispone al menos de alguno de estos campos (CIF, Teléfono, Móvil o Correo Electrónico)"
                )
            )

        return    
