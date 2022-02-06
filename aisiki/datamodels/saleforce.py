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
    toc = fields.Boolean(required=False, allow_none=True)
    idtype = fields.String(required=False, allow_none=True)
   

class SingupOut(Datamodel):
    _name = "signup.saleforce.datamode.out"

    first_name = fields.String(required=True, allow_none=False)
    last_name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    city = fields.String(required=True, allow_none=False)
    idnumber = fields.String(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    toc = fields.Boolean(required=False, allow_none=True)
    idtype = fields.String(required=False, allow_none=True)


# class FooditemIn(Datamodel):
#     _name = "fooditems.datamodel.in"

#     type = fields.String(required=False, allow_none=True)


# class Fooditems(Datamodel):
#     _name = "fooditems.datamodel.out"

#     id = fields.Integer(required=False, allow_none=False)
#     name = fields.String(required=False, allow_none=False)
#     type = fields.String(required=False, allow_none=True)
#     image_url = fields.Url(required=False, allow_none=False)
#     qty_available = fields.Integer(required=True, allow_none=False)
#     price = fields.Decimal(required=True, allow_none=False)
#     internal_ref = fields.String(required=True, allow_none=False)
#     barcode = fields.String(required=True, allow_none=False)
#     virtual_available = fields.Integer(required=True, allow_none=False)


# class WalletBalance(Datamodel):
#     _name = "wallet.balance.datamodel.out"

#     balance = fields.Decimal(required=True, allow_none=False)


# class CartItems(Datamodel):
#     _name = "cart.datamodel.items"

#     product_id = fields.Integer(required=True, allow_none=False)
#     quantity = fields.Integer(required=True, allow_none=False)
#     discount = fields.Integer(required=True, allow_none=False)
#     price_unit = fields.Decimal(required=True, allow_none=False)


# class CartIn(Datamodel):
#     _name = "cart.datamodel.in"

#     items = fields.List(NestedModel("cart.datamodel.items"))


# class CartOut(Datamodel):
#     _name = "cart.datamodel.out"

#     partner_id = fields.Integer(required=True, allow_none=False)
#     order_id = fields.Integer(required=True, allow_none=False)
#     items = fields.List(fields.Dict())
#     amount_total = fields.Decimal(required=True, allow_none=False)
#     state = fields.String(required=False, allow_none=False)


# class AddWalletBalance(Datamodel):
#     _name = "wallet.addbalance.datamodel.in"

#     amount = fields.Decimal(required=True, allow_none=False)
#     name = fields.String(required=True, allow_none=False)


# class PaymentDtamodelIn(Datamodel):
#     _name = "payment.datamodel.in"

#     method = fields.String(required=True, allow_none=False)
#     order_id = fields.Integer(required=True, allow_none=False)


# class PartnerInfo(Datamodel):
#     _name = "profile.datamodel"

#     id = fields.Integer(required=True, allow_none=False)
#     name = fields.String(required=True, allow_none=False)
#     street = fields.String(required=True, allow_none=False)
#     phone = fields.String(required=True, allow_none=True)
#     latitude = fields.Float(required=True, allow_none=True)
#     longitude = fields.Float(required=True, allow_none=True)


# class PartnerUpdateInfo(Datamodel):
#     _name = "profile.datamodel.update"

#     id = fields.Integer(required=True, allow_none=False)
#     name = fields.String(required=True, allow_none=False)
#     street = fields.String(required=True, allow_none=False)
#     phone = fields.String(required=True, allow_none=True)
#     latitude = fields.Float(required=True, allow_none=True)
#     longitude = fields.Float(required=True, allow_none=True)


# class PartnerUpdateInfo(Datamodel):
#     _name = "profile.datamodel.update1"

#     name = fields.String(required=True, allow_none=False)
#     street = fields.String(required=True, allow_none=False)
#     phone = fields.String(required=True, allow_none=True)
#     latitude = fields.Float(required=True, allow_none=True)
#     longitude = fields.Float(required=True, allow_none=True)
