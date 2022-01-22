from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel


# class ProcurementRegisterMobile(Datamodel):
#     _name = "procurement.signup.datamodel.mobilein"

#     email = fields.String(required=True, allow_none=False)
#     password = fields.String(required=True, allow_none=False)
#     store_name = fields.String(required=True, allow_none=False)


class ProcurementRegisterEmail(Datamodel):
    _name = "procurement.signup.datamodel.in"

    email = fields.String(required=True, allow_none=False)
    password = fields.String(required=True, allow_none=False)
    store_name = fields.String(required=True, allow_none=False)


class ProcurementRegisterOut(Datamodel):
    _name = "procurement.signup.datamodel.out"

    email = fields.String(required=False, allow_none=True)
    message = fields.String(required=False, allow_none=True)
    error = fields.Boolean(required=False, allow_none=True)


class ProcurementTokenDatamodelIn(Datamodel):
    _name = "procurement.token.datamodel.in"

    token = fields.String(required=True, allow_none=False)
    error = fields.Boolean(required=False, allow_none=True)

class ProcurementTokenDatamodelIn(Datamodel):
    _name = "procurement.token.datamodel.out"

    token = fields.String(required=False, allow_none=False)
    error = fields.Boolean(required=False, allow_none=True)






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
