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

from pypaystack import Transaction
import pyotp

secret = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(secret, interval=900)


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
        input_param=Datamodel("orderingapp.login.datamodel.in"),
        tags=["Authentication"],
    )
    def login(self, payload):
        params = request.params
        db_name = params.get("db", db_monodb())
        try:
            uid = request.session.authenticate(
                db_name, params["phone"], params["password"]
            )
            result = request.env["ir.http"].session_info()
            user = request.env["res.users"].with_user(1).browse(uid)
            _rotate_session(request)
            request.session.rotate = False
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            return {
                "session_id": request.session.sid,
                "expires_at": fields.Datetime.to_string(expiration),
                "uid": result.get("uid"),
                "username": result.get("username"),
                "name": result.get("name"),
                "partner_id": result.get("partner_id"),
                "registration_stage": user.registration_stage,
            }
        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method(
        [(["/otp/<string:phone>"], "GET")], auth="public", tags=["Authentication"],
    )
    def getotpcode(self, phone):
        phone = phone.strip()
        user = (
            request.env["res.users"]
            .with_user(1)
            .search([("login", "=", phone)], limit=1)
        )
        if not user:
            data = json.dumps({"error": "phone number not found"})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

        sms = (
            request.env["sms.sms"]
            .with_user(1)
            .create(
                {
                    "body": "Your Aisiki verification code is %s." % (totp.now(),),
                    "number": phone,
                }
            )
            .aisiki_send()
        )
        return sms.get("response", [])

    @restapi.method(
        [(["/otpverify"], "POST")],
        auth="public",
        input_param=Datamodel("otp.datamodel.in"),
        tags=["Authentication"],
    )
    def otpverify(self, payload):
        try:
            phone = payload.phone.strip()
            otp = payload.otp.strip()
            user = (
                request.env["res.users"]
                .with_user(1)
                .search([("login", "=", phone)], limit=1)
            )
            if not user:
                data = json.dumps({"error": "phone number not found"})
                resp = request.make_response(data)
                resp.status_code = 400
                return resp
            verify = totp.verify(otp)
            if not verify:
                data = json.dumps({"error": "OTP verification failed"})
                resp = request.make_response(data)
                resp.status_code = 400
                return resp
            request.uid = user.id
            _rotate_session(request)
            request.session.rotate = False
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=1)
            user.write({"registration_stage": "verified"})
            return {
                "session_id": request.session.sid,
                "expires_at": fields.Datetime.to_string(expiration),
                "uid": user.id,
                "username": user.login,
                "name": user.name,
                "registration_stage": user.registration_stage,
            }
        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method(
        [(["/register"], "POST")],
        auth="public",
        input_param=Datamodel("register.datamodel.in"),
        tags=["Authentication"],
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
            "company_type": "company" if payload.is_corporate else "person",
        }
        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)
            return user.read(
                fields=[
                    "name",
                    "phone",
                    "login",
                    "partner_longitude",
                    "partner_latitude",
                    "contact_person",
                    "company_type",
                    "registration_stage",
                ]
            )[0]

        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method(
        [(["/passwordforgot"], "GET")],
        auth="public",
        input_param=Datamodel("forgotpassword.datamodel.in"),
        output_param=Datamodel("forgotpassword.datamodel.out"),
        tags=["Authentication"],
    )
    def forgotpassword(self, payload):
        phone = payload.phone.strip()
        user = (
            request.env["res.users"]
            .with_user(request.env.user.id)
            .search([("login", "=", phone)], limit=1)
        )
        return self.env.datamodels["forgotpassword.datamodel.out"](
            password_reset_url=user.password_reset_url
        )

    @restapi.method(
        [(["/passwordchange"], "GET")],
        auth="user",
        input_param=Datamodel("input.password.datamodel"),
        tags=["Authentication"],
    )
    def passwordchange(self, payload):
        """Send change password email to the customer"""
        old_passwd = payload.old_passwd
        new_passwd = payload.new_passwd
        try:
            res = request.env.user.change_password(old_passwd, new_passwd)
            return {
                "message": "Password Successful changed"
                if res
                else "Something went wrong",
                "old_passwd": old_passwd,
                "new_passwd": new_passwd,
            }
        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method(
        [(["/profile"], "GET")], auth="user", tags=["Authentication"],
    )
    def profile(self):
        partner_id = request.env.user.partner_id

        res = {
            "id": partner_id.id,
            "name": partner_id.name,
            "street": partner_id.street,
            "phone": partner_id.phone,
            "latitude": partner_id.partner_latitude,
            "longitude": partner_id.partner_longitude,
            "business_category": partner_id.business_category,
            "number_of_offices": partner_id.number_of_offices,
            "contact_person": partner_id.contact_person,
            "referral_code": request.env.user.referral_code,
            "login": request.env.user.login,
            "food_items": partner_id.common_product_ids.ids,
        }
        return json.dumps(res)

    @restapi.method(
        [(["/updateprofile"], "PUT")],
        auth="user",
        input_param=Datamodel("profile.datamodel.update"),
        # output_param=Datamodel("profile.datamodel.update"),
        tags=["Authentication"],
    )
    def updateprofile(self, payload):
        partner_id = request.env.user.partner_id
        partner_id.write(
            {
                "name": payload.name if payload.name else partner_id.name,
                "street": payload.street if payload.street else partner_id.street,
                "phone": payload.phone if payload.phone else partner_id.phone,
                "partner_latitude": payload.latitude
                if payload.latitude
                else partner_id.partner_latitude,
                "partner_longitude": payload.longitude
                if payload.longitude
                else partner_id.partner_longitude,
            }
        )
        res = {
            "id": partner_id.id,
            "name": partner_id.name,
            "street": partner_id.street,
            "phone": partner_id.phone,
            "latitude": partner_id.partner_latitude,
            "longitude": partner_id.partner_longitude,
            "business_category": partner_id.business_category,
            "number_of_offices": partner_id.number_of_offices,
            "contact_person": partner_id.contact_person,
            "referral_code": request.env.user.referral_code,
        }
        return json.dumps(res)

    @restapi.method(
        [(["/products"], "GET")],
        auth="user",
        input_param=Datamodel("product.datamodel.in"),
        tags=["Products"],
    )
    def all_product(self, payload):
        res = {}
        domain = []
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        if payload.type:
            domain = [("aisiki_product_type", "=", payload.type)]
        fields = [
            "name",
            "lst_price",
            "image_url",
            "barcode",
            "aisiki_product_type",
            "type",
            "default_code",
            "categ_id",
            "description_sale",
            "weight",
            "volume",
            "cart_qty",
            "display_name",
            "description",
            "qty_available",
            "virtual_available",
            "incoming_qty",
        ]
        products = (
            request.env["product.product"]
            .with_user(request.env.user.id)
            .search_read(
                domain, fields=fields, limit=limit, offset=offset, order="id desc"
            )
        )

        res["total"] = (
            request.env["product.product"]
            .with_user(request.env.user.id)
            .search_count(domain)
        )
        res["data"] = products
        return res

    @restapi.method([(["/products/<int:id>"], "GET")], auth="user", tags=["Products"])
    def product_by_id(self, id):
        res = {}
        domain = [("id", "=", id)]
        fields = [
            "name",
            "lst_price",
            "image_url",
            "barcode",
            "aisiki_product_type",
            "type",
            "default_code",
            "categ_id",
            "description_sale",
            "weight",
            "volume",
            "cart_qty",
            "display_name",
            "description",
            "qty_available",
            "virtual_available",
            "incoming_qty",
        ]
        products = (
            request.env["product.product"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields)
        )
        res["data"] = products
        return res

    @restapi.method([(["/category"], "GET")], auth="user", tags=["Products"])
    def category(self):
        res = {}
        domain = []
        fields = ["name", "id"]
        products = (
            request.env["product.category"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields)
        )
        res["data"] = products
        return res

    @restapi.method(
        [(["/category/<int:categ_id>/products"], "GET")],
        auth="user",
        tags=["Products"],
    )
    def category_products(self, categ_id=None):
        res = {}
        domain = [("categ_id", "=", categ_id)]
        fields = ["name", "id"]
        products = (
            request.env["product.product"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields)
        )
        res["data"] = products
        return res

    @restapi.method(
        [(["/search/<string:query>"], "GET")], auth="user", tags=["Products"]
    )
    def category_products(self, query=None):
        res = {}
        domain = ["|", ("name", "ilike", query), ("description_sale", "ilike", query)]
        fields = [
            "name",
            "lst_price",
            "image_url",
            "barcode",
            "aisiki_product_type",
            "type",
            "default_code",
            "categ_id",
            "description_sale",
            "weight",
            "volume",
            "cart_qty",
            "display_name",
            "description",
            "qty_available",
            "virtual_available",
            "incoming_qty",
        ]
        products = (
            request.env["product.product"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields, limit=80)
        )
        res["data"] = products
        res["count"] = len(products)
        return res

    @restapi.method([(["/orders"], "GET")], auth="user", tags=["Order"])
    def orders(self):
        res = {}
        domain = [("partner_id", "=", request.env.user.partner_id.id)]
        orders = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search(domain, limit=80)
        )
        details = [
            {
                "name": order.name,
                "amount_total": order.amount_total,
                "state": order.state,
                "delivery_status": order.delivery_status,
                "customer": order.partner_id.name,
                "date_order": order.date_order,
                "items": [
                    {
                        "product_id": line.product_id.id,
                        "description": line.name,
                        "quantity": line.product_uom_qty,
                        "price_unit": line.price_unit,
                        "subtotal": line.price_subtotal,
                        "image_url": line.product_id.image_url,
                    }
                    for line in order.order_line
                ],
            }
            for order in orders
        ]
        res["data"] = details
        res["count"] = len(orders)
        return res
 

    @restapi.method(
        [(["/orders/<string:status>/status"], "GET")], auth="user", tags=["Order"],
    )
    def orders_by_status(self, status, id):
        """status: [nothing] | [to_deliver] | [partial] | [delivered] | [processing] """
        res = {}
        domain = [
            ("partner_id", "=", request.env.user.partner_id.id),
            ("delivery_status", "=", status),
        ]
        fields = ["name", "date_order", "delivery_status"]
        orders = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields, limit=80)
        )
        res["data"] = orders
        res["count"] = len(orders)
        return res

    @restapi.method(
        [(["/track/order/<int:id>"], "GET")], auth="user", tags=["Order"],
    )
    def orders_track(self, id):
        res = {}
        domain = [("partner_id", "=", request.env.user.partner_id.id), ("id", "=", id)]
        fields = [
            "name",
            "delivery_status",
            "date_order",
        ]
        orders = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search_read(domain, fields=fields, limit=80)
        )
        res["data"] = orders
        res["count"] = len(orders)
        return res

    @restapi.method([(["/orders/<int:id>"], "GET")], auth="user", tags=["Order"])
    def orders_by_id(self, id):
        res = {}
        domain = [("partner_id", "=", request.env.user.partner_id.id), ("id", "=", id)]
        fields = [
            "name",
            "amount_total",
            "state",
            "partner_id",
            "date_order",
            "delivery_status",
        ]
        orders = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search(domain, limit=80)
        )
        details = [
            {
                "name": order.name,
                "amount_total": order.amount_total,
                "state": order.state,
                "delivery_status": order.delivery_status,
                "customer": order.partner_id.name,
                "date_order": order.date_order,
                "items": [
                    {
                        "product_id": line.product_id.id,
                        "description": line.name,
                        "quantity": line.product_uom_qty,
                        "price_unit": line.price_unit,
                        "subtotal": line.price_subtotal,
                        "image_url": line.product_id.image_url,
                    }
                    for line in order.order_line
                ],
            }
            for order in orders
        ]
        res["data"] = details
        res["count"] = len(orders)
        return res

    @restapi.method(
        [(["/balance"], "GET")],
        auth="user",
        tags=["Wallet"],
        output_param=Datamodel("wallet.balance.datamodel.out"),
    )
    def getbalance(self):
        print(dir(request.env.user))
        total_due = abs(request.env.user.partner_id.total_due)
        return self.env.datamodels["wallet.balance.datamodel.out"](balance=total_due)

    @restapi.method([(["/balances"], "GET")], auth="user", tags=["Wallet"])
    def getbalances(self):
        partner_id = request.env.user.partner_id.id
        payments = (
            request.env["account.payment"]
            .with_user(request.env.user.id)
            .search_read(
                [("partner_id", "=", partner_id)],
                fields=["payment_type", "amount", "date", "name"],
            )
        )
        return payments

    @restapi.method(
        [(["/paymentlink/<int:amount>"], ["GET"])], auth="user", tags=["Wallet"]
    )
    def wallet_paymentlink(self, amount):
        """Get checkout payment link."""
        transaction = Transaction(
            authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610"
        )
        partner_id = request.env.user.partner_id
        initialize = transaction.initialize(
            partner_id.email or request.user.login, amount * 100
        )
        return initialize[3]

    @restapi.method(
        [(["/create"], "POST")],
        auth="user",
        tags=["Wallet"],
        input_param=Datamodel("wallet.addbalance.datamodel.in"),
    )
    def postbalance(self, payload):
        """Add wallet balance"""
        transaction = Transaction(
            authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610"
        )
        response = transaction.verify(payload.payment_ref)
        try:

            if response[3]["status"] == "success":
                wallet_id = request.env.ref("aisiki.aisiki_wallet_journal").with_user(
                    request.env.user.id
                )

                payment = request.env["account.payment"].with_user(request.env.user.id)

                payment_type = (
                    request.env["account.payment.method"]
                    .with_user(request.env.user.id)
                    .search(
                        [("code", "=", "manual"), ("payment_type", "=", "inbound")],
                        limit=1,
                    )
                )

                payload = {
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "journal_id": wallet_id.id,
                    "partner_id": request.env.user.partner_id.id,
                    "amount": response[3]["amount"],
                    "payment_method_id": payment_type.id,
                }
                payment.create(payload).action_post()
                total_due = abs(request.env.user.partner_id.total_due)
                resp = request.make_response(json.dumps({"balance": total_due}))
                resp.status_code = 404
                return resp
        except Exception as e:
            resp = request.make_response(json.dumps({"error": str(response)}))
            resp.status_code = 402
            return resp

    @restapi.method([(["/cart"], "GET")], auth="user", tags=["Cart"])
    def cartitem(self):
        res = {}
        data = []
        domain = [
            ("partner_id", "=", request.env.user.partner_id.id),
            ("state", "=", "draft"),
        ]
        orders = request.env["sale.order"].with_user(1).search(domain, limit=80)
        for order in orders:
            data.append(
                {
                    "id": order.id,
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "name": order.name,
                    "date_order": order.date_order,
                    "items": [
                        {
                            "product_id": line.product_id.id,
                            "description": line.name,
                            "quantity": line.product_uom_qty,
                            "price_unit": line.price_unit,
                            "subtotal": line.price_subtotal,
                            "image_url": line.product_id.image_url,
                        }
                        for line in order.order_line
                    ],
                }
            )
        res["data"] = data
        res["count"] = len(orders)
        return res

    @restapi.method([(["/cancel/<int:order_id>"], "PATCH")], auth="user", tags=["Cart"])
    def cartcancel(self, order_id):
        res = {}
        domain = [
            ("partner_id", "=", request.env.user.partner_id.id),
            ("state", "=", "draft"),
            ("id", "=", order_id),
        ]
        order = request.env["sale.order"].with_user(request.env.user.id).search(domain)
        try:
            if order:
                order.action_cancel()
                resp = request.make_response(
                    json.dumps(
                        {"message": "sale.order %s has been cancelled" % (order_id,)}
                    )
                )
                resp.status_code = 200
                return resp
            else:
                resp = request.make_response(
                    json.dumps({"error": "order %s not found" % (order_id,)})
                )
                resp.status_code = 404
                return resp

        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method(
        [(["/cart/<int:order_id>"], ["DELETE"])], auth="user", tags=["Cart"]
    )
    def delete(self, order_id):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search(
                [
                    ("partner_id", "=", partner_id),
                    ("state", "in", ['cancel', "draft"]),
                    ("id", "=", order_id),
                ],
                limit=1,
            )
        )
        
        order.unlink()
        resp = request.make_response(
            json.dumps({"message": "sale.order %s has been deleted" % (order_id,)})
        )
        resp.status_code = 200
        return resp

    @restapi.method(
        [(["/pay"], ["POST"])],
        input_param=Datamodel("list.order.datamodel.in"),
        auth="user",
        tags=["Cart"],
    )
    def pay(self, payload):
        """Generate paystack payment link."""
        transaction = Transaction(
            authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610"
        )
        partner_id = request.env.user.partner_id
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [
                    ("partner_id", "=", partner_id.id),
                    ("state", "=", "draft"),
                    ("id", "in", payload.ids),
                ],
                limit=len(payload.ids),
            )
        )
        if not orders:
            resp = request.make_response(
                json.dumps(
                    {"error": "No other found for the given id(s) %s" % (payload.ids)}
                )
            )
            resp.status_code = 401
            return resp

        total = sum([o.amount_total for o in orders]) * 100

        initialize = transaction.initialize(partner_id.email or request.env.user.company_id.email, total)
        return initialize

    @restapi.method(
        [(["/confirm"], ["POST"])],
        input_param=Datamodel("checkout.order.datamodel"),
        auth="user",
        tags=["Cart"],
    )
    def comfirm_payment(self, payload):
        partner_id = request.env.user.partner_id.id
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [
                    ("partner_id", "=", partner_id),
                    ("state", "=", "draft"),
                    ("id", "in", payload.ids),
                ],
                limit=len(payload.ids),
            )
        )
        if not orders:
            resp = request.make_response(
                json.dumps({"error": "There is no open order in cart or draft state"})
            )
            resp.status_code = 400
            return resp
        transaction = Transaction(
            authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610"
        )
        response = transaction.verify(payload.payment_ref)
        state = "error"
        if response[3] != None and response[3]["status"] == "success":
            state = "done"

            [
                [
                    order.action_confirm(),
                    order.with_user(1)._create_payment_transaction(
                        {
                            "acquirer_id": 14,
                            "acquirer_reference": response[3]["reference"],
                            "state": state,
                            "state_message": response[3],
                            "partner_country_id": request.env.ref('base.ng').id,
                        }
                    ),
                ]
                for order in orders
            ]
        error = request.make_response(json.dumps(response))
        error.status_code = 401
        return response[3] if response[3] else error

    @restapi.method(
        [(["/cart"], ["PUT"])],
        auth="user",
        input_param=Datamodel("update.cart.datamodel.in"),
        tags=["Cart"],
    )
    def updatecart(self, payload):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(request.env.user.id)
            .search(
                [
                    ("partner_id", "=", partner_id),
                    ("state", "=", "draft"),
                    ("id", "=", payload.cart_id),
                ],
                limit=1,
            )
        )
        if not order:
            resp = request.make_response(
                json.dumps({"error": "There is no open order in cart or draft state"})
            )
            resp.status_code = 400
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
                request.env["sale.order.line"].with_user(request.env.user.id).create(
                    payload
                )

            items = [
                {
                    "product_id": line.product_id.id,
                    "image_url": line.product_id.image_url,
                    "quantity": line.product_uom_qty,
                    "discount": str(line.discount),
                    "price_unit": str(line.price_unit),
                    "subtotal": str(line.price_subtotal),
                }
                for line in order.order_line
            ]

        return {
            "name": order.name,
            "amount_total": order.amount_total,
            "state": order.state,
            "delivery_status": order.delivery_status,
            "customer": order.partner_id.name,
            "date_order": order.date_order,
            "items": [
                {
                    "product_id": line.product_id.id,
                    "description": line.name,
                    "quantity": line.product_uom_qty,
                    "price_unit": line.price_unit,
                    "subtotal": line.price_subtotal,
                }
                for line in order.order_line
            ],
        }

    @restapi.method(
        [(["/cart"], ["POST"])],
        auth="user",
        input_param=Datamodel("cart.datamodel.in"),
        tags=["Cart"],
    )
    def createcart(self, payload):
        items = []
        partner_id = request.env.user.partner_id.id
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
            "team_id": request.env.ref("sales_team.salesteam_website_sales").id,
        }
        order = request.env["sale.order"].with_user(1).create(payload)

        return {
            "name": order.name,
            "amount_total": order.amount_total,
            "state": order.state,
            "delivery_status": order.delivery_status,
            "customer": order.partner_id.name,
            "date_order": order.date_order,
            "items": [
                {
                    "product_id": line.product_id.id,
                    "description": line.name,
                    "quantity": line.product_uom_qty,
                    "price_unit": line.price_unit,
                    "subtotal": line.price_subtotal,
                    'image_url': line.product_id.image_url
                }
                for line in order.order_line
            ],
        }
