from odoo import fields, models, api, _


class ResConfigSetting(models.TransientModel):
    _inherit = "res.config.settings"

    aisiki_username = fields.Char("Username")
    aisiki_api_key = fields.Char("API key")
    aisiki_overwrite_default = fields.Boolean("Overwrite Odoo SMS", default=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        param_obj = self.env["ir.config_parameter"]
        res.update(
            {
                "aisiki_username": param_obj.sudo().get_param("aisiki.username"),
                "aisiki_api_key": param_obj.sudo().get_param("aisiki.api.key"),
                "aisiki_overwrite_default": param_obj.sudo().get_param("aisiki.overwrite.default"),
            }
        )
        return res

    @api.model
    def set_values(self):
        super(ResConfigSetting, self).set_values()
        param_obj = self.env["ir.config_parameter"]
        param_obj.sudo().set_param("aisiki.username", self.aisiki_username)
        param_obj.sudo().set_param("aisiki.api.key", self.aisiki_api_key)
        param_obj.sudo().set_param("aisiki.overwrite.default", self.aisiki_overwrite_default)
