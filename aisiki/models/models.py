import logging

from odoo import api, fields, models
from odoo.addons.auth_signup.models.res_partner import SignupError, now
_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    password_reset_url = fields.Char(related="signup_url", string="Password Reset URL")
    referral_code = fields.Char(string="Referral Code")
    city = fields.Char()
    agentid = fields.Char()
    toc = fields.Char()
    idtype = fields.Char()
    registration_stage = fields.Selection(
        selection=[("not_verified", "Not Verified"), ("verified", "Verify")],
        string="Registration Stage",
        default="not_verified",
    )

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        if self.env.context.get('install_mode', False):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                pass
                # logger.info(_("Cannot send email: user %s has no email address.", user.name))
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.send_mail(user.id, force_send=force_send, raise_exception=False)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)


class ResPartner(models.Model):
    _inherit = "res.partner"

    common_product_ids = fields.Many2many(comodel_name="product.product")
    contact_person = fields.Char(string="Contact Person")
    business_category = fields.Char(string="Business Category")
    number_of_offices = fields.Char(string="Number of Offices")
    referral_code = fields.Char(
        string="Referral Code", related="user_id.referral_code", store=True
    )
    city = fields.Char(related="user_id.city")
    agentid = fields.Char(related="user_id.agentid", store=True)
    toc = fields.Char(related="user_id.toc", store=True)
    idtype = fields.Char(related="user_id.idtype", store=True)
    business_type = fields.Char()
    purchase_frequency = fields.Float()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    aisiki_product_type = fields.Selection(
        selection=[("fresh", "Fresh Food"), ("fmcg", "FMCG")], string="Aisiki Type"
    )

    image_url = fields.Char(string="Image URL", compute="_compute_image_url_link")

    def _compute_image_url_link(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for rec in self:
            rec.image_url = "%s/web/image/%s/%s/image_1024" % (
                base_url,
                rec._name,
                rec.id,
            )


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     @api.model
#     def create(self, values):
#         res = super(SaleOrder, self).create(values)
#         print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', self.env.context)
#         [o.write({'team_id':    sales_team.salesteam_website_sales}) for o in res]
#         return res
