from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class DataModelOTP(Datamodel):
    _name = "otp.datamodel.in"
    phone = fields.String(required=True, allow_none=False)
    otp = fields.String(required=True, allow_none=False)


class DatamodelErrorOut(Datamodel):
    _name = "datamodel.error.out"

    message = fields.String(required=False, allow_none=True)
    error = fields.Boolean(required=False, allow_none=True)


class OrderingAppRegisterLogin(Datamodel):
    _name = "orderingapp.login.datamodel.in"

    phone = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    origin = fields.String(required=True, allow_none=False)


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


class CorporateRegisterIn(Datamodel):
    _name = "register.datamodel.in"

    name = fields.String(
        required=False, allow_none=False, load_default="Babatope Ajepe"
    )
    contact_person = fields.String(
        required=False, allow_none=False, load_default="Esanju Babatunde"
    )
    business_category = fields.Integer(required=False, allow_none=False, load_default=1)
    password = fields.String(required=False, allow_none=False, load_default="password")
    number_of_offices = fields.Integer(required=False, allow_none=False, load_default=1)
    phone = fields.String(required=False, allow_none=False, load_default="0908865544")
    login = fields.String(required=False, allow_none=False, load_default="0908865544")
    latitude = fields.Float(required=False, allow_none=False, load_default=6.601838)
    longitude = fields.Float(required=False, allow_none=False, load_default=3.351486)
    referral_code = fields.String(required=True, allow_none=False)
    logo = fields.String(required=False, allow_none=True)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)
    is_corporate = fields.Boolean(load_default=True)
    origin = fields.String(required=True, allow_none=False)


class CorporateRegisterOut(Datamodel):
    _name = "register.datamodel.out"

    name = fields.String(required=True, allow_none=False)
    contact_person = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    login = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class FooditemIn(Datamodel):
    _name = "product.datamodel.in"

    type = fields.String(required=False, allow_none=True)
    limit = fields.String(required=False, allow_none=True, load_default=80)
    offset = fields.String(required=False, allow_none=True, load_default=0)


class WalletBalance(Datamodel):
    _name = "wallet.balance.datamodel.out"

    balance = fields.Decimal(required=True, allow_none=False)


class CartItems(Datamodel):
    _name = "cart.datamodel.items"

    product_id = fields.Integer(required=False, allow_none=False, load_default=18)
    quantity = fields.Integer(required=False, allow_none=False, load_default=5)
    discount = fields.Integer(required=False, allow_none=False, load_default=10)
    price_unit = fields.Float(required=False, allow_none=False, load_default=700)
    name = fields.String(
        required=False, allow_none=True, load_default="Default Order Description"
    )


class CartIn(Datamodel):
    _name = "cart.datamodel.in"

    items = fields.List(NestedModel("cart.datamodel.items"))


class CartUpdateIn(Datamodel):
    _name = "update.cart.datamodel.in"

    items = fields.List(NestedModel("cart.datamodel.items"))
    cart_id = fields.Integer(required=True, allow_none=False)


class AddWalletBalance(Datamodel):
    _name = "wallet.addbalance.datamodel.in"

    payment_ref = fields.String(required=True, allow_none=False)


class PaymentDtamodelIn(Datamodel):
    _name = "payment.datamodel.in"

    method = fields.String(required=True, allow_none=False)
    order_id = fields.Integer(required=True, allow_none=False)


class ListOrderDatamodelIn(Datamodel):
    _name = "list.order.datamodel.in"
    ids = fields.List(fields.Integer(), required=True, allow_none=False)


class PartnerUpdateInfo(Datamodel):
    _name = "profile.datamodel.update"

    name = fields.String(required=True, allow_none=False)
    street = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=True)
    latitude = fields.Float(required=True, allow_none=True)
    longitude = fields.Float(required=True, allow_none=True)


class CheckoutOrderDatamodel(Datamodel):
    _name = "checkout.order.datamodel"
    ids = fields.List(fields.Integer(), required=True, allow_none=False)
    payment_ref = fields.String(required=True, allow_none=False)


class ConfirmOrder(Datamodel):
    _name = "confirm.order.datamodel"
    ids = fields.List(fields.Integer(), required=True, allow_none=False)
