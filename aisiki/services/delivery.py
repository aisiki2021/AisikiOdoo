from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

import datetime
import json
from odoo import fields
from datetime import datetime, timedelta

from odoo.tools.misc import flatten


class Delivery(Component):
    _inherit = "aisiki.base.rest"
    _name = "aisiki.delivery.rest"
    _usage = "delivery"
    _collection = "delivery"
    _description = """
        Delivery
        
    """

    @restapi.method(
        [(["/register"], "POST")],
        auth="public",
        tags=["Authentication"],
        input_param=Datamodel("signup.saleforce.datamode.in"),
        output_param=Datamodel("signup.saleforce.datamode.out"),
    )
    def register(self, payload):
        values = {
            "name": payload.first_name + " " + payload.last_name,
            "referral_code": payload.referral_code,
            "phone": payload.phone,
            "city": payload.city,
            "toc": payload.toc,
            "login": payload.phone,
            "password": payload.password,
            "email": payload.email,
            "delivery_agent": True,
            "agentid": request.env["ir.sequence"]
            .with_user(1)
            .next_by_code("aisiki.agent.seq"),
            "origin": payload.origin,
        }

        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)
            user.write({"city": payload.city, "agent": True})
            return self.env.datamodels["signup.saleforce.datamode.out"](
                name=user.name or "",
                phone=user.phone or "",
                city=user.city or "",
                agentid=user.agentid or "",
                referral_code=user.referral_code,
                toc=user.toc,
                email=user.email or "",
                login=user.login or "",
            )

        except Exception as e:

            return self.env.datamodels["datamodel.error.out"](
                message=str(e), error=True
            )

    @restapi.method([(["/agents"], "GET")], auth="user", tags=["Delivery"])
    def get_agents(self):
        domain = [("delivery_agent", "=", True)]
        fields = [
            "name",
            "phone",
            "email",
        ]
        agents = (
            request.env["res.partner"]
            .with_user(1)
            .search_read(domain, fields=fields, limit=80)
        )
        return agents

    @restapi.method(
        [(["/orders/<string:order_id>"], "GET")], auth="user", tags=["Order"]
    )
    def order(self, order_id):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        domain = [
            ("delivery_agent_id", "=", _id),
            ("id", "=", order_id),
            ("picking_type_id.sequence_code", "=", "OUT"),
        ]
        orders = request.env["stock.picking"].with_user(1).search(domain, limit=1)

        res = []
        for order in orders:
            res.append(
                {
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/orders"], "GET")],
        auth="user",
        tags=["Order"],
        input_param=Datamodel("delivery.datamodel.in"),
    )
    def orders(self, payload):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        date = fields.Date.today() - timedelta(days=payload.days or 1)
        domain = [
            ("delivery_agent_id", "=", _id),
            ("picking_type_id.sequence_code", "=", "OUT"),
            ("state", "in", ["assigned"]),
            ("create_date", ">=", date),
        ]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["stock.picking"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )

        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "create_date": str(order.create_date),
                    "delivery_status": order.delivery_status,
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/completed"], "GET")],
        auth="user",
        tags=["Delivery"],
        input_param=Datamodel("delivery.datamodel.in"),
    )
    def completed(self, payload):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        date = fields.Date.today() - timedelta(days=payload.days or 1)
        domain = [
            ("delivery_agent_id", "=", _id),
            ("picking_type_id.sequence_code", "=", "OUT"),
            ("delivery_status", "=", "completed"),
            ("create_date", ">=", date),
        ]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["stock.picking"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )
        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/incomplete"], "GET")],
        auth="user",
        tags=["Order"],
        input_param=Datamodel("delivery.datamodel.in"),
    )
    def incompleted(self, payload):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        date = fields.Date.today() - timedelta(days=payload.days or 1)
        domain = [
            ("delivery_agent_id", "=", _id),
            ("picking_type_id.sequence_code", "=", "OUT"),
            ("state", "in", ["assigned"]),
            ("create_date", ">=", date),
        ]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["stock.picking"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )

        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method([(["/search/<string:query>"], "GET")], auth="user", tags=["Order"])
    def search(self, query=None):
        _id = request.env.user.partner_id.id
        domain = [
            ("delivery_agent_id", "=", _id),
            "|",
            "|",
            ("name", "ilike", query),
            ("origin", "ilike", query),
            ("partner_id.name", "ilike", query),
        ]

        orders = request.env["stock.picking"].with_user(1).search(domain, limit=25)
        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/delivered/<int:order_id>"], "PATCH")], auth="user", tags=["Delivery"]
    )
    def delivered(self, order_id):
        """To mark an order as delivered"""
        _id = request.env.user.partner_id.id
        domain = [
            ("delivery_agent_id", "=", _id),
            ("id", "=", order_id),
            ("delivery_status", "!=", "completed"),
        ]
        order = request.env["stock.picking"].with_user(1).search(domain, limit=1)
        if order:
            for move_id in order.move_lines:
                move_id.write({"quantity_done": move_id.product_uom_qty})
                move_id._action_assign()
            order._compute_state()
            order.button_validate()
            order.write({"delivery_status": "completed"})
            return {
                "id": order.id,
                "name": order.name,
                "state": order.state,
                "delivery_address": order.partner_id._display_address(
                    without_company=True
                ),
                "delivery_status": order.delivery_status,
                "customer": order.partner_id.name,
                "phone": order.partner_id.phone,
                "lat": order.partner_id.partner_latitude,
                "lng": order.partner_id.partner_longitude,
                "email": order.partner_id.phone,
                "mobile": order.partner_id.phone,
                "scheduled_date": order.scheduled_date,
                "create_date": str(order.create_date),
                "amount_total": order.sale_id.amount_total,
                "payment_term": order.payment_term_id.name,
                "items": [
                    {
                        "image_url": item.product_id.image_url,
                        "product_id": item.product_id.id,
                        "quantity": item.product_uom_qty,
                        "price_subtotal": item.sale_line_id.price_subtotal,
                        "quantity_done": item.quantity_done,
                        "description": item.description_picking,
                    }
                    for item in order.move_ids_without_package
                ],
            }
        data = json.dumps({"error": "order with id %s is not found" % (order_id,)})
        resp = request.make_response(data)
        resp.status_code = 400
        return resp

    # Delivery

    @restapi.method(
        [(["/assigned"], "GET")],
        auth="user",
        tags=["Delivery"],
        input_param=Datamodel("delivery.datamodel.in"),
    )
    def order_assign(self, payload):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        date = fields.Date.today() - timedelta(days=payload.days or 1)
        domain = [
            ("delivery_agent_id", "=", _id),
            ("picking_type_id.sequence_code", "=", "OUT"),
            ("delivery_status", "=", "assigned"),
            ("create_date", ">=", date),
        ]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["stock.picking"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )

        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "create_date": str(order.create_date),
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/in_transist"], "GET")],
        auth="user",
        tags=["Delivery"],
        input_param=Datamodel("delivery.datamodel.in"),
    )
    def in_transist(self, payload):
        """."""
        res = []

        _id = request.env.user.partner_id.id
        date = fields.Date.today() - timedelta(days=payload.days or 1)
        domain = [
            ("delivery_agent_id", "=", _id),
            ("picking_type_id.sequence_code", "=", "OUT"),
            ("delivery_status", "=", "in_transist"),
            ("create_date", ">=", date),
        ]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["stock.picking"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )

        res = []
        for order in orders:
            res.append(
                {
                    "id": order.id,
                    "name": order.name,
                    "delivery_address": order.partner_id._display_address(
                        without_company=True
                    ),
                    "customer": order.partner_id.name,
                    "phone": order.partner_id.phone,
                    "delivery_status": order.delivery_status,
                    "create_date": str(order.create_date),
                    "lat": order.partner_id.partner_latitude,
                    "lng": order.partner_id.partner_longitude,
                    "email": order.partner_id.phone,
                    "mobile": order.partner_id.phone,
                    "scheduled_date": order.scheduled_date,
                    "create_date": str(order.create_date),
                    "amount_total": order.sale_id.amount_total,
                    "payment_term": order.payment_term_id.name,
                    "items": [
                        {
                            "image_url": item.product_id.image_url,
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_subtotal": item.sale_line_id.price_subtotal,
                            "quantity_done": item.quantity_done,
                            "description": item.description_picking,
                        }
                        for item in order.move_ids_without_package
                    ],
                }
            )
        return res

    @restapi.method(
        [(["/metrics"], "GET")],
        auth="user",
        tags=["Metrics"],
        output_param=Datamodel("dmetrics.datamodel.out"),
    )
    def metrics(self):
        """."""

        _id = request.env.user.partner_id.id

        # daily
        number_of_orders_daily = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        # ("delivery_status", "=", "in_transist"),
                        ("create_date", ">=", fields.Date.today() - timedelta(1)),
                    ]
                )
            )
        )
        number_of_completed_orders_daily = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "=", "completed"),
                        ("create_date", ">=", fields.Date.today() - timedelta(1)),
                    ]
                )
            )
        )
        number_of_incomplete_orders_daily = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "in", ["new", "assigned", "in_transist"]),
                        ("create_date", ">=", fields.Date.today() - timedelta(1)),
                    ]
                )
            )
        )
        amount_of_money_to_collect_daily = sum(
            [
                s.amount_total
                for s in (
                    request.env["stock.picking"]
                    .with_user(1)
                    .search(
                        (
                            [
                                ("delivery_agent_id", "=", _id),
                                ("payment_term_id", "!=", False),
                                ("picking_type_id.sequence_code", "=", "OUT"),
                                (
                                    "delivery_status",
                                    "in",
                                    ["completed", "assigned", "in_transist"],
                                ),
                                (
                                    "create_date",
                                    ">=",
                                    fields.Date.today() - timedelta(1),
                                ),
                            ]
                        )
                    )
                ).mapped("sale_id")
            ]
        )

        # Weekly
        number_of_orders_weekly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("create_date", ">=", fields.Date.today() - timedelta(7)),
                    ]
                )
            )
        )
        number_of_completed_orders_weekly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "=", "completed"),
                        ("create_date", ">=", fields.Date.today() - timedelta(7)),
                    ]
                )
            )
        )
        number_of_incomplete_orders_weekly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "in", ["new", "assigned", "in_transist"]),
                        ("create_date", ">=", fields.Date.today() - timedelta(7)),
                    ]
                )
            )
        )
        amount_of_money_to_collect_weekly = sum(
            [
                s.amount_total
                for s in (
                    request.env["stock.picking"]
                    .with_user(1)
                    .search(
                        (
                            [
                                ("delivery_agent_id", "=", _id),
                                ("payment_term_id", "!=", False),
                                ("picking_type_id.sequence_code", "=", "OUT"),
                                (
                                    "delivery_status",
                                    "in",
                                    ["completed", "assigned", "in_transist"],
                                ),
                                (
                                    "create_date",
                                    ">=",
                                    fields.Date.today() - timedelta(7),
                                ),
                            ]
                        )
                    )
                ).mapped("sale_id")
            ]
        )
        # monthly

        number_of_orders_monthly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("create_date", ">=", fields.Date.today() - timedelta(30)),
                    ]
                )
            )
        )
        number_of_completed_orders_monthly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "=", "completed"),
                        ("create_date", ">=", fields.Date.today() - timedelta(30)),
                    ]
                )
            )
        )
        number_of_incomplete_orders_monthly = (
            request.env["stock.picking"]
            .with_user(1)
            .search_count(
                (
                    [
                        ("delivery_agent_id", "=", _id),
                        ("picking_type_id.sequence_code", "=", "OUT"),
                        ("delivery_status", "in", ["new", "assigned", "in_transist"]),
                        ("create_date", ">=", fields.Date.today() - timedelta(30)),
                    ]
                )
            )
        )
        amount_of_money_to_collect_monthly = sum(
            [
                s.amount_total
                for s in (
                    request.env["stock.picking"]
                    .with_user(1)
                    .search(
                        (
                            [
                                ("delivery_agent_id", "=", _id),
                                ("payment_term_id", "!=", False),
                                ("picking_type_id.sequence_code", "=", "OUT"),
                                (
                                    "delivery_status",
                                    "in",
                                    ["completed", "assigned", "in_transist"],
                                ),
                                (
                                    "create_date",
                                    ">=",
                                    fields.Date.today() - timedelta(30),
                                ),
                            ]
                        )
                    )
                ).mapped("sale_id")
            ]
        )
        return self.env.datamodels["dmetrics.datamodel.out"](
            today=[
                {
                    "number_of_orders": number_of_orders_daily,
                    "number_of_completed_orders": number_of_completed_orders_daily,
                    "number_of_incomplete_orders": number_of_incomplete_orders_daily,
                    "amount_of_money_to_collect": amount_of_money_to_collect_daily,
                }
            ],
            weekly=[
                {
                    "number_of_orders": number_of_orders_weekly,
                    "number_of_completed_orders": number_of_completed_orders_weekly,
                    "number_of_incomplete_orders": number_of_incomplete_orders_weekly,
                    "amount_of_money_to_collect": amount_of_money_to_collect_weekly,
                }
            ],
            monthly=[
                {
                    "number_of_orders": 1,
                    "number_of_completed_orders": number_of_completed_orders_monthly,
                    "number_of_incomplete_orders": number_of_incomplete_orders_monthly,
                    "amount_of_money_to_collect": amount_of_money_to_collect_monthly,
                }
            ],
        )
