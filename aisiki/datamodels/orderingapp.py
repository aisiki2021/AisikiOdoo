from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel


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


class IndividualRegister(Datamodel):
    _name = "orderingapp.inregister.datamodel.in"

    email = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    store_name = fields.String(required=True, allow_none=False)


class OrderingappRegisterOut(Datamodel):
    _name = "orderingapp.register.datamodel.out"

    email = fields.String(required=False, allow_none=True)
    message = fields.String(required=False, allow_none=True)
    error = fields.Boolean(required=False, allow_none=True)


class OrderingappTokenDatamodelIn(Datamodel):
    _name = "orderingapp.token.datamodel.in"

    token = fields.String(required=True, allow_none=False)


class OrderingappTokenDatamodelIn(Datamodel):
    _name = "orderingapp.token.datamodel.out"

    error = fields.Boolean(required=False, allow_none=True)


# class orderingappRegisterMobile(Datamodel):
#     _name = "orderingapp.signup.datamodel.mobilein"

#     email = fields.String(required=True, allow_none=False)
#     password = fields.String(required=True, allow_none=False)
#     store_name = fields.String(required=True, allow_none=False)


# class ChangePassword(Datamodel):
#     _name = "input.password.datamodel"

#     old_passwd = fields.String(required=True, allow_none=False)
#     new_passwd = fields.String(required=True, allow_none=False)


# class ChangePasswordOutput(Datamodel):
#     _name = "output.password.datamodel"

#     old_passwd = fields.String(required=True, allow_none=False)
#     new_passwd = fields.String(required=True, allow_none=False)
#     message = fields.String(required=True, allow_none=False)


# class GetPasswordDatamodel(Datamodel):
#     _name = "get.password.datamodel"

#     email = fields.String(required=True, allow_none=False)


# class GetOutPasswordDatamodel(Datamodel):
#     _name = "getout.password.datamodel"

#     email = fields.String(required=False, allow_none=False)
#     password_reset_url = fields.String(required=False, allow_none=False)
