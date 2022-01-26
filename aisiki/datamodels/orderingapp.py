from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel


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


class IndividualRegisterOut(Datamodel):
    _name = "individual.register.datamodel.out"

    name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class CorporateRegisterIn(Datamodel):
    _name = "corporate.register.datamodel.in"

    name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class CorporateRegisterOut(Datamodel):
    _name = "corporate.register.datamodel.out"

    name = fields.String(required=True, allow_none=False)
    phone = fields.String(required=True, allow_none=False)
    latitude = fields.Float(required=True, allow_none=False)
    longitude = fields.Float(required=True, allow_none=False)
    referral_code = fields.String(required=True, allow_none=False)
    food_items = fields.List(fields.Integer(), required=False, allow_none=False)


class Fooditems(Datamodel):
    _name = "fooditems.datamodel.out"

    id = fields.Integer(required=False, allow_none=False)
    name = fields.String(required=False, allow_none=False)
