import logging

from odoo import api, fields, models
from odoo.addons.auth_signup.models.res_partner import SignupError, now

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    delivery_agent_id = fields.Many2one(comodel_name="res.partner", domain=[('delivery_agent', '=', True)])

    