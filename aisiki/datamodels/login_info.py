from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


class ChangePassword(Datamodel):
    _name = "changepassword.datamodel"

    oldpassword = fields.String(required=True, allow_none=False)
    newpassword = fields.String(required=True, allow_none=False)


class LoginDataModel(Datamodel):
    _name = "login.datamodel"

    login = fields.String(required=True, allow_none=False)
    db = fields.String(required=False, allow_none=True)
    password = fields.String(required=True, allow_none=False)
