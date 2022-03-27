from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

from datetime import datetime, timedelta

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


import werkzeug

from pypaystack import Transaction


class OrderingApp(Component):
    _inherit = "aisiki.base.rest"
    _name = "orderingapp"
    _usage = "OrderingApp"
    _collection = "orderingapp"
    _description = """
        Ordering App
        
    """

    @restapi.method(
        [(["/products"], "GET")], auth="user", input_param=Datamodel("product.datamodel.in"), tags=["Products"],
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
            .with_user(1)
            .search_read(domain, fields=fields, limit=limit, offset=offset, order="id desc")
        )

        res["total"] = request.env["product.product"].with_user(1).search_count(domain)
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
        products = request.env["product.product"].with_user(1).search_read(domain, fields=fields)
        res["data"] = products
        return res

    @restapi.method([(["/category"], "GET")], auth="user", tags=["Products"])
    def category(self):
        res = {}
        domain = []
        fields = ["name", "id"]
        products = request.env["product.category"].with_user(1).search_read(domain, fields=fields)
        res["data"] = products
        return res

    @restapi.method(
        [(["/category/<int:categ_id>/products"], "GET")], auth="user", tags=["Products"],
    )
    def category_products(self, categ_id=None):
        res = {}
        domain = [("categ_id", "=", categ_id)]
        fields = ["name", "id"]
        products = request.env["product.product"].with_user(1).search_read(domain, fields=fields)
        res["data"] = products
        return res

    @restapi.method([(["/search/<string:query>"], "GET")], auth="user", tags=["Products"])
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
        products = request.env["product.product"].with_user(1).search_read(domain, fields=fields, limit=80)
        res["data"] = products
        res["count"] = len(products)
        return res


    @restapi.method([(["/orders/metric/<int:days>"], "GET")], auth="user", tags=["Order"])
    def orders_metric(self, days=1):
        """Metric in days default is 1"""
        date = fields.Date.today() - timedelta(days=days)
        domain = [("partner_id", "=", request.env.user.partner_id.id), ('create_date', '>=', date), ('state', '=','sale')]
        return {'amount_total': sum([o.amount_total for o in request.env["sale.order"].with_user(1).search(domain)])}


    @restapi.method([(["/orders"], "GET")], auth="user", tags=["Order"])
    def orders(self):
        res = {}
        domain = [("partner_id", "=", request.env.user.partner_id.id)]
        orders = request.env["sale.order"].with_user(1).search(domain, limit=80)
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
    def orders_by_status(self, status):
        """status: [nothing] | [to_deliver] | [partial] | [delivered] | [processing] """
        res = {}
        domain = [
            ("partner_id", "=", request.env.user.partner_id.id),
            ("delivery_status", "=", status),
        ]
        fields = ["name", "date_order", "delivery_status"]
        orders = request.env["sale.order"].with_user(1).search_read(domain, fields=fields, limit=80)
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
        orders = request.env["sale.order"].with_user(1).search_read(domain, fields=fields, limit=80)
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
        orders = request.env["sale.order"].with_user(1).search(domain, limit=80)
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
        [(["/balance"], "GET")], auth="user", tags=["Wallet"], output_param=Datamodel("wallet.balance.datamodel.out"),
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
            .with_user(1)
            .search_read([("partner_id", "=", partner_id)], fields=["payment_type", "amount", "date", "name"],)
        )
        return payments

    @restapi.method([(["/paymentlink/<int:amount>"], ["GET"])], auth="user", tags=["Wallet"])
    def wallet_paymentlink(self, amount):
        """Get checkout payment link."""
        transaction = Transaction(authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610")
        partner_id = request.env.user.partner_id
        initialize = transaction.initialize(partner_id.email or request.user.login, amount * 100)
        return initialize[3]

    @restapi.method(
        [(["/create"], "POST")], auth="user", tags=["Wallet"], input_param=Datamodel("wallet.addbalance.datamodel.in"),
    )
    def postbalance(self, payload):
        """Add wallet balance"""
        transaction = Transaction(authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610")
        response = transaction.verify(payload.payment_ref)
        try:

            if response[3]["status"] == "success":
                wallet_id = request.env.ref("aisiki.aisiki_wallet_journal").with_user(request.env.user.id)

                payment = request.env["account.payment"].with_user(1)

                payment_type = (
                    request.env["account.payment.method"]
                    .with_user(1)
                    .search([("code", "=", "manual"), ("payment_type", "=", "inbound")], limit=1,)
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
        order = request.env["sale.order"].with_user(1).search(domain)
        try:
            if order:
                order.action_cancel()
                resp = request.make_response(json.dumps({"message": "sale.order %s has been cancelled" % (order_id,)}))
                resp.status_code = 200
                return resp
            else:
                resp = request.make_response(json.dumps({"error": "order %s not found" % (order_id,)}))
                resp.status_code = 404
                return resp

        except Exception as e:
            data = json.dumps({"error": str(e)})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

    @restapi.method([(["/cart/<int:order_id>"], ["DELETE"])], auth="user", tags=["Cart"])
    def delete(self, order_id):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [("partner_id", "=", partner_id), ("state", "in", ["cancel", "draft"]), ("id", "=", order_id),],
                limit=1,
            )
        )

        order.unlink()
        resp = request.make_response(json.dumps({"message": "sale.order %s has been deleted" % (order_id,)}))
        resp.status_code = 200
        return resp

    @restapi.method(
        [(["/pay"], ["POST"])], input_param=Datamodel("list.order.datamodel.in"), auth="user", tags=["Cart"],
    )
    def pay(self, payload):
        """Generate paystack payment link."""
        transaction = Transaction(authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610")
        partner_id = request.env.user.partner_id
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [("partner_id", "=", partner_id.id), ("state", "=", "draft"), ("id", "in", payload.ids),],
                limit=len(payload.ids),
            )
        )
        if not orders:
            resp = request.make_response(json.dumps({"error": "No other found for the given id(s) %s" % (payload.ids)}))
            resp.status_code = 401
            return resp

        total = sum([o.amount_total for o in orders]) * 100

        initialize = transaction.initialize(partner_id.email or request.env.user.company_id.email, total)
        return initialize

    @restapi.method(
        [(["/confirm"], ["POST"])], input_param=Datamodel("checkout.order.datamodel"), auth="user", tags=["Cart"],
    )
    def comfirm_payment(self, payload):
        partner_id = request.env.user.partner_id.id
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [("partner_id", "=", partner_id), ("state", "=", "draft"), ("id", "in", payload.ids),],
                limit=len(payload.ids),
            )
        )
        if not orders:
            resp = request.make_response(json.dumps({"error": "There is no open order in cart or draft state"}))
            resp.status_code = 400
            return resp
        transaction = Transaction(authorization_key="sk_test_6613ae6de9e50d198ba22637e6df1fecf3611610")
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
                            "partner_country_id": request.env.ref("base.ng").id,
                        }
                    ),
                ]
                for order in orders
            ]
        error = request.make_response(json.dumps(response))
        error.status_code = 401
        return response[3] if response[3] else error

    @restapi.method(
        [(["/cart"], ["PUT"])], auth="user", input_param=Datamodel("update.cart.datamodel.in"), tags=["Cart"],
    )
    def updatecart(self, payload):
        items = []
        partner_id = request.env.user.partner_id.id
        order = (
            request.env["sale.order"]
            .with_user(1)
            .search([("partner_id", "=", partner_id), ("state", "=", "draft"), ("id", "=", payload.cart_id),], limit=1,)
        )
        if not order:
            resp = request.make_response(json.dumps({"error": "There is no open order in cart or draft state"}))
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
                request.env["sale.order.line"].with_user(1).create(payload)

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
        [(["/cart"], ["POST"])], auth="user", input_param=Datamodel("cart.datamodel.in"), tags=["Cart"],
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
                    "image_url": line.product_id.image_url,
                }
                for line in order.order_line
            ],
        }
