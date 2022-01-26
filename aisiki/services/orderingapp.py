from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

import datetime
import json
from odoo import fields


from .authenticate import _rotate_session


class OrderingApp(Component):
    _inherit = "base.rest.service"
    _name = "orderingapp"
    _usage = "orderingapp"
    _collection = "orderingapp"
    _description = """
        Ordering App
        
    """

    @restapi.method(
        [(["/login"], "POST")],
        auth="public",
        input_param=Datamodel("orderingapp.login.datamodel.in"),
        output_param=Datamodel("orderingapp.login.datamodel.out"),
    )
    def login(self, payload):
        params = request.params
        db_name = params.get("db", db_monodb())
        request.session.authenticate(db_name, params["phone"], params["password"])
        result = request.env["ir.http"].session_info()
        _rotate_session(request)
        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        return self.env.datamodels["orderingapp.login.datamodel.out"](
            session_id=request.session.sid,
            expires_at=fields.Datetime.to_string(expiration),
            uid=result.get("uid"),
            username=result.get("username"),
            name=result.get("name"),
            partner_id=result.get("partner_id"),
        )

    @restapi.method(
        [(["/register"], "POST")],
        auth="public",
        input_param=Datamodel("orderingapp.inregister.datamodel.in"),
        output_param=Datamodel("orderingapp.register.datamodel.out"),
    )
    def register(self, payload):
        """
        Register a new customer.
        """
        values = {
            "name": payload.store_name,
            "login": payload.email,
            "email": payload.email,
            "password": payload.password,
        }
        try:
            user = (
                request.env["res.users"]
                .with_context(no_reset_password=False)
                .signup(values)
            )
        except Exception as e:
            return self.env.datamodels["orderingapp.signup.datamodel.out"](
                message=str(e), error=True
            )
        request.env["res.users"].reset_password(user[1])
        return self.env.datamodels["orderingapp.signup.datamodel.out"](
            email=user[1], error=False
        )

    @restapi.method(
        [(["/verify_token"], "POST")],
        auth="public",
        input_param=Datamodel("orderingapp.token.datamodel.in"),
        # output_param=Datamodel("orderingapp.token.datamodel.out"),
    )
    def verify_token(self, payload):
        """
        Verify registration token.
        """

        token = payload.token

        try:
            user = request.env["res.users"].signup(values, token)

        except Exception as e:
            return self.env.datamodels["orderingapp.token.datamodel.out"](
                message=str(e), error=True
            )

        return self.env.datamodels["orderingapp.token.datamodel.in"](
            email=user[1], error=False
        )

    # def search(self, name):
    #     """
    #     Searh partner by name
    #     """
    #     partners = self.env["res.partner"].name_search(name)
    #     partners = self.env["res.partner"].browse([i[0] for i in partners])
    #     rows = []
    #     res = {"count": len(partners), "rows": rows}
    #     for partner in partners:
    #         rows.append(self._to_json(partner))
    #     return res

    # # pylint:disable=method-required-super
    # def create(self, **params):
    #     """
    #     Create a new partner
    #     """
    #     partner = self.env["res.partner"].create(self._prepare_params(params))
    #     return self._to_json(partner)

    # def update(self, _id, **params):
    #     """
    #     Update partner informations
    #     """
    #     partner = self._get(_id)
    #     partner.write(self._prepare_params(params))
    #     return self._to_json(partner)

    # def archive(self, _id, **params):
    #     """
    #     Archive the given partner. This method is an empty method, IOW it
    #     don't update the partner. This method is part of the demo data to
    #     illustrate that historically it's not mandatory to defined a schema
    #     describing the content of the response returned by a method.
    #     This kind of definition is DEPRECATED and will no more supported in
    #     the future.
    #     :param _id:
    #     :param params:
    #     :return:
    #     """
    #     return {"response": "Method archive called with id %s" % _id}

    # # The following method are 'private' and should be never never NEVER call
    # # from the controller.

    def _get(self, _id):
        return self.env["res.partner"].browse(_id)

    # def _prepare_params(self, params):
    #     for key in ["country", "state"]:
    #         if key in params:
    #             val = params.pop(key)
    #             if val.get("id"):
    #                 params["%s_id" % key] = val["id"]
    #     return params

    # # Validator
    # def _validator_return_get(self):
    #     res = self._validator_create()
    #     res.update({"id": {"type": "integer", "required": True, "empty": False}})
    #     return res

    # def _validator_search(self):
    #     return {"name": {"type": "string", "nullable": False, "required": True}}

    # def _validator_return_search(self):
    #     return {
    #         "count": {"type": "integer", "required": True},
    #         "rows": {
    #             "type": "list",
    #             "required": True,
    #             "schema": {"type": "dict", "schema": self._validator_return_get()},
    #         },
    #     }

    # def _validator_create(self):
    #     res = {
    #         "name": {"type": "string", "required": True, "empty": False},
    #         "street": {"type": "string", "required": True, "empty": False},
    #         "street2": {"type": "string", "nullable": True},
    #         "zip": {"type": "string", "required": True, "empty": False},
    #         "city": {"type": "string", "required": True, "empty": False},
    #         "phone": {"type": "string", "nullable": True, "empty": False},
    #         "state": {
    #             "type": "dict",
    #             "schema": {
    #                 "id": {"type": "integer", "coerce": to_int, "nullable": True},
    #                 "name": {"type": "string"},
    #             },
    #         },
    #         "country": {
    #             "type": "dict",
    #             "schema": {
    #                 "id": {
    #                     "type": "integer",
    #                     "coerce": to_int,
    #                     "required": True,
    #                     "nullable": False,
    #                 },
    #                 "name": {"type": "string"},
    #             },
    #         },
    #         "is_company": {"coerce": to_bool, "type": "boolean"},
    #     }
    #     return res

    # def _validator_return_create(self):
    #     return self._validator_return_get()

    # def _validator_update(self):
    #     res = self._validator_create()
    #     for key in res:
    #         if "required" in res[key]:
    #             del res[key]["required"]
    #     return res

    # def _validator_return_update(self):
    #     return self._validator_return_get()

    # def _validator_archive(self):
    #     return {}

    def _to_json(self, partner):
        res = {
            "id": partner.id,
            "name": partner.name,
            "street": partner.street,
            "street2": partner.street2 or "",
            "zip": partner.zip,
            "city": partner.city,
            "phone": partner.city,
        }
        if partner.country_id:
            res["country"] = {
                "id": partner.country_id.id,
                "name": partner.country_id.name,
            }
        if partner.state_id:
            res["state"] = {"id": partner.state_id.id, "name": partner.state_id.name}
        return res
