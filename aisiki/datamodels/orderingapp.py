from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class DatamodelErrorOut(Datamodel):
    _name = "datamodel.error.out"

    message = fields.String(required=False, allow_none=True)
    error = fields.Boolean(required=False, allow_none=True)


class OrderingAppRegisterLogin(Datamodel):
    _name = "orderingapp.login.datamodel.in"

    phone = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)


class OrderingAppRegisterLoginOut(Datamodel):
    _name = "orderingapp.login.datamodel.out"

    session_id = fields.String(required=True, allow_none=False)
    expires_at = fields.DateTime(required=True, allow_none=False)
    uid = fields.Integer(required=True, allow_none=False)
    username = fields.String(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    partner_id = fields.Integer(required=True, allow_none=False)


class ForgotPasswordDatamodelIn(Datamodel):
    _name = "forgotpassword.datamodel.in"

    phone = fields.String(required=True, allow_none=False)


class ForgotPasswordDatamodelOut(Datamodel):
    _name = "forgotpassword.datamodel.out"

    password_reset_url = fields.String(required=False, allow_none=True)


class IndividualRegisterIn(Datamodel):
    _name = "individual.register.datamodel.in"

    name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class IndividualRegisterDatamodelOut(Datamodel):
    _name = "individual.register.datamodel.out"

    name = fields.String(required=False, allow_none=False)
    phone = fields.String(required=False, allow_none=False)
    latitude = fields.Float(required=False, allow_none=False)
    longitude = fields.Float(required=False, allow_none=False)
    referral_code = fields.String(required=False, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=True)


class CorporateRegisterIn(Datamodel):
    _name = "corporate.register.datamodel.in"

    name = fields.String(required=True, allow_none=False)
    contact_person = fields.String(required=True, allow_none=False)
    business_category = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    number_of_offices = fields.Integer(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    logo = fields.String(required=False, allow_none=True)
    number_of_offices = fields.Integer(required=False, allow_none=True)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class CorporateRegisterOut(Datamodel):
    _name = "corporate.register.datamodel.out"

    name = fields.String(required=True, allow_none=False)
    contact_person = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class FooditemIn(Datamodel):
    _name = "fooditems.datamodel.in"

    type = fields.String(required=False, allow_none=True)


class Fooditems(Datamodel):
    _name = "fooditems.datamodel.out"

    id = fields.Integer(required=False, allow_none=False)
    name = fields.String(required=False, allow_none=False)
    type = fields.String(required=False, allow_none=True)
    image_url = fields.Url(required=False, allow_none=False)
    qty_available = fields.Integer(required=True, allow_none=False)
    price = fields.Decimal(required=True, allow_none=False)
    internal_ref = fields.String(required=True, allow_none=False)
    barcode = fields.String(required=True, allow_none=False)
    virtual_available = fields.Integer(required=True, allow_none=False)


class WalletBalance(Datamodel):
    _name = "wallet.balance.datamodel.out"

    balance = fields.Decimal(required=True, allow_none=False)


class CartItems(Datamodel):
    _name = "cart.datamodel.items"

    product_id = fields.Integer(required=True, allow_none=False)
    quantity = fields.Integer(required=True, allow_none=False)
    discount = fields.Integer(required=True, allow_none=False)
    price_unit = fields.Decimal(required=True, allow_none=False)
    name = fields.String(required=False, allow_none=True)


class CartIn(Datamodel):
    _name = "cart.datamodel.in"

    items = fields.List(NestedModel("cart.datamodel.items"))


class CartOut(Datamodel):
    _name = "cart.datamodel.out"

    partner_id = fields.Integer(required=True, allow_none=False)
    order_id = fields.Integer(required=True, allow_none=False)
    items = fields.List(fields.Dict())
    amount_total = fields.Decimal(required=True, allow_none=False)
    state = fields.String(required=False, allow_none=False)


class AddWalletBalance(Datamodel):
    _name = "wallet.addbalance.datamodel.in"

    amount = fields.Decimal(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class PaymentDtamodelIn(Datamodel):
    _name = "payment.datamodel.in"

    method = fields.String(required=True, allow_none=False)
    order_id = fields.Integer(required=True, allow_none=False)


class PartnerInfo(Datamodel):
    _name = "profile.datamodel"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    street = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=True)
    longitude = fields.Float(required=True, allow_none=True)


class PartnerUpdateInfo(Datamodel):
    _name = "profile.datamodel.update"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    street = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=True)
    longitude = fields.Float(required=True, allow_none=True)


class PartnerUpdateInfo(Datamodel):
    _name = "profile.datamodel.update1"

    name = fields.String(required=True, allow_none=False)
    street = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=True)
    longitude = fields.Float(required=True, allow_none=True)
