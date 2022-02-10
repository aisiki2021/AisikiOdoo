from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


# class DatamodelErrorOut(Datamodel):
#     _name = "datamodel.error.out"

#     message = fields.String(required=False, allow_none=True)
#     error = fields.Boolean(required=False, allow_none=True)


class OrderingAppRegisterLogin(Datamodel):
    _name = "saleforce.login.datamodel.in"

    agentid = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)


class OrderingAppRegisterLoginOut(Datamodel):
    _name = "saleforce.login.datamodel.out"

    session_id = fields.String(required=True, allow_none=False)
    expires_at = fields.DateTime(required=True, allow_none=False)
    uid = fields.Integer(required=True, allow_none=False)
    agentid = fields.String(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    partner_id = fields.Integer(required=True, allow_none=False)


class ForgotPasswordDatamodelIn(Datamodel):
    _name = "saleforce.forgotpassword.datamodel.in"

    agentid = fields.String(required=True, allow_none=False)


class ForgotPasswordDatamodelOut(Datamodel):
    _name = "saleforce.forgotpassword.datamodel.out"

    password_reset_url = fields.String(required=False, allow_none=True)


class SingupIn(Datamodel):
    _name = "signup.saleforce.datamode.in"

    first_name = fields.String(required=True, allow_none=False)
    last_name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    city = fields.String(required=True, allow_none=False)
    idnumber = fields.String(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    toc = fields.Boolean(required=False, allow_none=False)
    idtype = fields.String(required=False, allow_none=False)
    agentid = fields.String(required=True, allow_none=False)
    email = fields.Email(required=False, allow_none=True)


class SingupOut(Datamodel):
    _name = "signup.saleforce.datamode.out"

    name = fields.String(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True)
    city = fields.String(required=False, allow_none=True)
    idnumber = fields.String(required=False, allow_none=True)
    referral_code = fields.String(required=False, allow_none=True)
    toc = fields.Boolean(required=False, allow_none=True)
    idtype = fields.String(required=False, allow_none=True)
    agentid = fields.String(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)


class CreateVendor(Datamodel):
    _name = "create.vendor.datamode.in"

    name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    business_type = fields.String(required=True, allow_none=False)
    purchase_frequency = fields.Float(required=False, allow_none=True)
    image = fields.Raw(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)


class CreateVendorOut(Datamodel):
    _name = "create.vendor.datamode.out"

    name = fields.String(required=False, allow_none=True)
    phone = fields.String(required=False, allow_none=True)
    latitude = fields.Float(required=False, allow_none=True)
    longitude = fields.Float(required=False, allow_none=True)
    business_type = fields.String(required=False, allow_none=True)
    purchase_frequency = fields.Float(required=False, allow_none=True)
    image = fields.Raw(required=False, allow_none=True)
    email = fields.Email(required=False, allow_none=True)


class OrderOut(Datamodel):
    _name = "orders.datamodel.out"

    id = fields.Integer(required=True)
    name = fields.String(required=True)
    state = fields.String(required=True)
    customer = fields.String(required=True)
    phone = fields.String(required=True)
    date_order = fields.String(required=True)
    amount_total = fields.Decimal(required=True)
    amount_untaxed = fields.Decimal(required=True)
    items = fields.List(
        NestedModel("cart.datamodel.items"), required=False, allow_none=False
    )
    total_order = fields.Integer(required=True)


class OrderIn(Datamodel):
    _name = "orders.datamodel.in"


    limit = fields.String(required=False, missing=80)
    offset = fields.String(required=False, missing=0)


class PartnerInfo(Datamodel):
    _name = "vendor.datamodel.out"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    street = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=True)
    longitude = fields.Float(required=True, allow_none=True)
    create_date =  fields.String(required=True, allow_none=True)