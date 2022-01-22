from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class LoginDataModel(Datamodel):
    _name = "login.datamodel"

    login = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)


class ChangePassword(Datamodel):
    _name = "input.password.datamodel"

    old_passwd = fields.String(required=True, allow_none=False)
    new_passwd = fields.String(required=True, allow_none=False)


class ChangePasswordOutput(Datamodel):
    _name = "output.password.datamodel"

    old_passwd = fields.String(required=True, allow_none=False)
    new_passwd = fields.String(required=True, allow_none=False)
    message = fields.String(required=True, allow_none=False)


class GetPasswordDatamodel(Datamodel):
    _name = "get.password.datamodel"

    email = fields.String(required=True, allow_none=False)


class GetOutPasswordDatamodel(Datamodel):
    _name = "getout.password.datamodel"

    email = fields.String(required=False, allow_none=False)
    password_reset_url = fields.String(required=False, allow_none=False)
