from marshmallow import fields
from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class LimitOffset(Datamodel):
    _name = "limit.offset.datamodel"

    limit = fields.Integer(required=False, allow_none=False, load_default=80)
    offset = fields.Integer(required=False, allow_none=False, load_default=0)


class PartnerSearchParam(Datamodel):
    _name = "partner.search.param"

    id = fields.Integer(required=False, allow_none=False)
    name = fields.String(required=False, allow_none=False)


class PartnerShortInfo(Datamodel):
    _name = "partner.short.info"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
