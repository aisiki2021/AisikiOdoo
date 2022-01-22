from odoo import api, fields, models


class Users(models.Model):
    _inherit = "res.users"

    password_reset_url = fields.Char(related="signup_url")
