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
        [(["/register/corporate"], "POST")],
        auth="public",
        input_param=Datamodel("corporate.register.datamodel.in"),
        output_param=Datamodel("corporate.register.datamodel.out"),
    )
    def corporate(self, payload):
        values = {
            "name": payload.name,
            "login": payload.phone,
            "password": payload.password,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "password": payload.password,
            "referral_code": payload.referral_code,
            "contact_person": payload.contact_person,
            "business_category": payload.business_category,
            "number_of_offices": payload.number_of_offices,
        }
        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)

        except Exception as e:
            return self.env.datamodels["datamodel.error.out"](
                message=str(e), error=True
            )

        return self.env.datamodels["corporate.register.datamodel.out"](
            name=user.name,
            phone=user.login,
            latitude=user.partner_longitude,
            longitude=user.partner_latitude,
            referral_code=user.referral_code,
            contact_person=user.contact_person,
        )

    @restapi.method(
        [(["/register/individual"], "POST")],
        auth="public",
        input_param=Datamodel("individual.register.datamodel.in"),
        output_param=Datamodel("individual.register.datamodel.out"),
    )
    def individual(self, payload):
        values = {
            "name": payload.name,
            "login": payload.phone,
            "password": payload.password,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "password": payload.password,
            "referral_code": payload.referral_code,
            "company_type": "person",
        }
        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)

        except Exception as e:
            return self.env.datamodels["datamodel.error.out"](
                message=str(e), error=True
            )
        return self.env.datamodels["individual.register.datamodel.out"](
            name=user.name,
            phone=user.login,
            latitude=user.partner_longitude,
            longitude=user.partner_latitude,
            referral_code=user.referral_code,
        )

    @restapi.method(
        [(["/forgotpassword"], "GET")],
        auth="public",
        input_param=Datamodel("forgotpassword.datamodel.in"),
        output_param=Datamodel("forgotpassword.datamodel.out"),
    )
    def forgotpassword(self, payload):
        phone = payload.phone.strip()
        user = (
            request.env["res.users"]
            .with_user(1)
            .search([("login", "=", phone)], limit=1)
        )
        return self.env.datamodels["forgotpassword.datamodel.out"](
            password_reset_url=user.password_reset_url
        )

    @restapi.method(
        [(["/fooditems"], "GET")],
        auth="public",
        output_param=Datamodel("fooditems.datamodel.out", is_list=True),
    )
    def fooditems(self):
        res = []
        products = (
            request.env["product.product"]
            .with_user(1)
            .search([], limit=200, order="aisiki_product_type")
        )
        for product in products:
            res.append(
                self.env.datamodels["fooditems.datamodel.out"](
                    id=product.id,
                    name=product.name,
                    image_url=product.image_url,
                    type=product.aisiki_product_type or "",
                    qty_available=product.qty_available,
                    price=product.lst_price,
                    internal_ref=product.default_code or "",
                    barcode=product.barcode or "",
                    virtual_available=product.virtual_available,
                )
            )
        return res

    @restapi.method(
        [(["/walletbalance"], "POST")],
        auth="user",
        output_param=Datamodel("wallet.balance.datamodel.out"),
    )
    def walletbalance(self):
        total_due = request.env.user.partner_id.total_due
        return self.env.datamodels["wallet.balance.datamodel.out"](balance=total_due)

    @restapi.method(
        [(["/cart"], "POST")],
        auth="user",
        input_param=Datamodel("cart.datamodel.in"),
        output_param=Datamodel("cart.datamodel.out"),
    )
    def cart(self):
        total_due = request.env.user.partner_id.total_due
        return self.env.datamodels["cart.datamodel.out"](balance=total_due)

    def _partner_to_json(self, partner):
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
