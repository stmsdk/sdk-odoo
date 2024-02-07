# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from datetime import date
from datetime import timedelta
import re
import pytz
 
# loque sea n
class SaleCommission(models.Model):
    _inherit = "sale.commission"
    _description = "Commission in sales for actions"

    """
    # Añadiendo y eliminando items de un fields.Selection
    my_selection = fields.Selection(selection_add=[
        ('pikachu', "Pikachu"),
        ('eevee', "Eevee"),
        ], 
        ondelete={'pikachu': 'set default', 'eevee':'set default'}
    )
    """

    # Incluimos la opcion de comisionar por acciones realizadas en el proceso de venta
    commission_type = fields.Selection(
          selection_add=[("actions", "By fragmented sale actions")]
        , ondelete={"actions": "set default"}
    )
    actions_ids = fields.One2many(
        string="Actions",
        comodel_name="sale.commission.actions",
        inverse_name="commission_id",
    )
    # Incluimos la opcion de comisionar por pedido entregado
    invoice_state = fields.Selection(
        selection_add=[("delivered", "Sale delivered")]
        , ondelete={"delivered": "set default"}
    )
    amount_base_type = fields.Selection(
        selection_add=[("margin", "Margin gros profit ")]
        , ondelete={"margin": "set default"}
    )

    """
    # def calculate_actions(self, base):
        #self.ensure_one()
        # Tenemos que obtener de la venta el campo de cada accion que contendra el usuario que la realizo
        # Una vez tengamos el usuario que la realizo verificamos que sea el que estamos calculando
            for action in self.actions_ids:
                if action.amount_from <= base <= action.amount_to:
                    return base * action.percent / 100.0
            return 0.0
    """


class SaleCommissionAction(models.Model):
    _name = "sale.commission.actions"
    _description = "Commission by fragmented sale actions"

    commission_id = fields.Many2one("sale.commission", string="Commission")
    name = fields.Char(string="Accion")
    field_action = fields.Char(string="field action", required=True)
    percent = fields.Float(string="Percent", required=True)
    active = fields.Boolean(string="Activo", default=True)


