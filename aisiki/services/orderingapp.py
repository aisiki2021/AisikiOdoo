from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

import datetime
import json
from odoo import fields

from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)

from .authenticate import _rotate_session

import werkzeug


class OrderingApp(Component):
    _inherit = "base.rest.service"
    _name = "orderingapp"
    _usage = "OrderingApp"
    _collection = "orderingapp"
    _description = """
        Ordering App
        
    """


    @restapi.method(
        [(["/login"], "POST")],
        auth="public",
        input_param=Datamodel("orderingapp.login.datamodel.in"), tags=['Authentication']
    )
    def login(self, payload):
        params = request.params
        db_name = params.get("db", db_monodb())
        try:
            request.session.authenticate(db_name, params["phone"], params["password"])
            result = request.env["ir.http"].session_info()
            _rotate_session(request)
            request.session.rotate = False
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            return {
            'session_id':request.session.sid,
            'expires_at':fields.Datetime.to_string(expiration),
            'uid':result.get("uid"),
            'username':result.get("username"),
            'name':result.get("name"),
            'partner_id':result.get("partner_id"),
        }
        except Exception as e:
            data = json.dumps({'error': str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp
        

    @restapi.method(
        [(["/register"], "POST")],
        auth="public",
        input_param=Datamodel("register.datamodel.in"),
         tags=['Authentication']
    )
    def register(self, payload):
        values = {
            "name": payload.name,
            "login": payload.login,
            "phone": payload.phone,
            "password": payload.password,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "password": payload.password,
            "referral_code": payload.referral_code,
            "contact_person": payload.contact_person,
            "business_category": payload.business_category,
            "number_of_offices": payload.number_of_offices,
            'company_type': 'company' if payload.is_corporate else 'person',
        }
        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)
            return user.read(fields=['name', 'phone', 'login', 'partner_longitude', 'partner_latitude', 'contact_person', 'company_type'])

        except Exception as e:
            data = json.dumps({'error': str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp
        


    @restapi.method(
        [(["/passwordforgot"], "GET")],
        auth="public",
        input_param=Datamodel("forgotpassword.datamodel.in"),
        output_param=Datamodel("forgotpassword.datamodel.out"),
        tags=['Authentication']
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
        [(["/passwordchange"], "GET")],
        auth="public",
        input_param=Datamodel("get.password.datamodel"),
        output_param=Datamodel("getout.password.datamodel"),
         tags=['Authentication']
    )
    def get_change_password(self, payload):
        """Send change password email to the customer"""
        email = payload.email
        response = self.env.datamodels["getout.password.datamodel"]
        response = response()
        user = (
            request.env["res.users"]
            .with_user(1)
            .search([("login", "=", email.strip())], limit=1)
        )
        response.password_reset_url = user.password_reset_url
        response.email = request.env.user.email or request.env.user.login

        return response

    @restapi.method(
        [(["/products"], "GET")],
        auth="public",
        input_param=Datamodel("fooditems.datamodel.in"),
        output_param=Datamodel("fooditems.datamodel.out", is_list=True),
    )
    def product(self, payload):
        """Types are fresh and fmcg"""
        res = []
        aisiki_product_type = payload.type
        domain = []
        if aisiki_product_type:
            domain = [("aisiki_product_type", "=", aisiki_product_type)]
        products = (
            request.env["product.product"]
            .with_user(1)
            .search(domain, limit=80, order="aisiki_product_type")
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
        [(["/getbalance"], "GET")],
        auth="user",
        output_param=Datamodel("wallet.balance.datamodel.out"),
    )
    def getbalance(self):
        """Get wallet balance"""

        total_due = abs(request.env.user.partner_id.total_due)
        return self.env.datamodels["wallet.balance.datamodel.out"](balance=total_due)

    @restapi.method(
        [(["/addbalance"], "POST")],
        auth="user",
        input_param=Datamodel("wallet.addbalance.datamodel.in"),
        output_param=Datamodel("wallet.balance.datamodel.out"),
    )
    def postbalance(self, payload):
        """Add wallet balance"""
        wallet = (
            request.env["account.journal"]
            .with_user(1)
            .search([("name", "ilike", payload.name)], limit=1)
        )

        payment = request.env["account.payment"].with_user(1)

        payment_type = (
            request.env["account.payment.method"]
            .with_user(1)
            .search(
                [("code", "=", "manual"), ("payment_type", "=", payment_type)], limit=1
            )
        )

        payload = {
            "payment_type": "inbound",
            "partner_type": "customer",
            "journal_id": wallet.id,
            "partner_id": request.env.user.partner_id.id,
            "amount": payload.amount,
            "payment_method_id": payment_type.id,
        }
        payment.create(payload).action_post()
        total_due = abs(request.env.user.partner_id.total_due)
        return self.env.datamodels["wallet.balance.datamodel.out"](balance=total_due)

    @restapi.method(
        [(["/payment"], "POST")],
        auth="user",
        input_param=Datamodel("payment.datamodel.in"),
        output_param=Datamodel("cart.datamodel.out"),
    )
    def payment(self, payload):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [("partner_id", "=", partner_id), ("id", "=", payload.order_id)],
                limit=1,
            )
        )
        for line in order.order_line:
            items.append(
                {
                    "product_id": line.product_id.id,
                    "price_unit": line.price_unit,
                    "product_uom_qty": line.product_uom_qty,
                    "discount": line.discount,
                },
            )

        order._create_payment_transaction({"acquirer_id": 6, "state": "done"})
        order.action_confirm()

        return self.env.datamodels["cart.datamodel.out"](
            partner_id=order.partner_id.id,
            items=items,
            amount_total=order.amount_total,
            order_id=order.id,
            state=order.state,
        )

    @restapi.method(
        [(["/cart"], "POST")],
        auth="user",
        input_param=Datamodel("cart.datamodel.in"),
        output_param=Datamodel("cart.datamodel.out"),
    )
    def cart(self, payload):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(1)
            .search([("partner_id", "=", partner_id)], limit=1)
        )
        if not order:
            for line in payload.items:
                items.append(
                    (
                        0,
                        0,
                        {
                            "product_id": line.product_id,
                            "price_unit": line.price_unit,
                            "product_uom_qty": line.quantity,
                            "discount": line.discount,
                        },
                    )
                )
            payload = {
                "partner_id": partner_id,
                "order_line": items,
            }
            order = request.env["sale.order"].with_user(1).create(payload)
        else:
            order.order_line.unlink()
            for line in payload.items:
                payload = {
                    "order_id": order.id,
                    "product_id": line.product_id,
                    "price_unit": line.price_unit,
                    "product_uom_qty": line.quantity,
                    "discount": line.discount,
                }
                request.env["sale.order.line"].with_user(1).create(payload)

            items = [
                {
                    "product_id": line.product_id.id,
                    "quantity": line.product_uom_qty,
                    "discount": line.discount,
                    "price_unit": line.price_unit,
                    "subtotal": line.price_subtotal,
                }
                for line in order.order_line
            ]

        return self.env.datamodels["cart.datamodel.out"](
            partner_id=order.partner_id.id,
            items=items,
            amount_total=order.amount_total,
            order_id=order.id,
        )

    @restapi.method(
        [(["/profile"], "GET")],
        auth="user",
        output_param=Datamodel("profile.datamodel"),
    )
    def profile(self):
        partner_id = request.env.user.partner_id
        res = {
            "id": partner_id.id,
            "name": partner_id.name,
            "street": partner_id.street or "",
            "phone": partner_id.phone or "",
            "latitude": partner_id.partner_latitude or 0.0,
            "longitude": partner_id.partner_longitude or 0.0,
        }
        return self.env.datamodels["profile.datamodel"](**res)

    @restapi.method(
        [(["/updateprofile"], "PUT")],
        auth="user",
        input_param=Datamodel("profile.datamodel.update1"),
        output_param=Datamodel("profile.datamodel.update"),
    )
    def updateprofile(self, payload):
        partner_id = request.env.user.partner_id
        partner_id.write(
            {
                "name": payload.name,
                "street": payload.street,
                "phone": payload.phone,
                "partner_latitude": payload.latitude,
                "partner_longitude": payload.longitude,
            }
        )
        res = {
            "id": partner_id.name,
            "name": partner_id.name,
            "street": partner_id.street,
            "phone": partner_id.phone,
            "latitude": partner_id.partner_latitude,
            "longitude": partner_id.partner_longitude,
        }
        return self.env.datamodels["profile.datamodel.update"](**res)
