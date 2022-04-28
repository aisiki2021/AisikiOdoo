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


class OrderingApp(Component):
    _inherit = "aisiki.base.rest"
    _name = "saleforce"
    _usage = "saleforce"
    _collection = "saleforce"
    _description = """
        Business Sale Force
        
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
            "origin": payload.origin,
            "password": payload.password,
            "email": payload.email,
            "agentid": request.env["ir.sequence"]
            .with_user(1)
            .next_by_code("aisiki.agent.seq"),
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

    @restapi.method([(["/all_agents"], "GET")], auth="user", tags=["BusinessSaleForce"])
    def get_agents(self):
        domain = [("agent", "=", True)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
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
        [(["/agents/<int:id>"], "GET")], auth="user", tags=["BusinessSaleForce"]
    )
    def agent_by_id(self, id=None):
        domain = [("agent", "=", True), ("id", "=", id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
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
        [(["/agent/<int:id>/vendors"], "GET")], auth="user", tags=["BusinessSaleForce"]
    )
    def agents_vendor(self, id=None):
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        ]
        domain = [("parent_id", "=", id), ("parent_id.agent", "=", True)]
        agents = (
            request.env["res.partner"]
            .with_user(1)
            .search_read(domain, fields=fields, limit=80)
        )
        return agents

    @restapi.method(
        [(["/vendor"], "POST")],
        auth="user",
        tags=["BusinessSaleForce"],
        input_param=Datamodel("create.vendor.datamode.in"),
        output_param=Datamodel("create.vendor.datamode.out"),
    )
    def createvendor(self, payload):
        values = {
            "name": payload.name,
            "purchase_frequency": payload.purchase_frequency,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "phone": payload.phone,
            "email": payload.email,
            "business_type": payload.business_type,
            "agent_ids": [(6, 0, [request.env.user.partner_id.id])],
            "parent_id": request.env.user.partner_id.id,
            "business_name": payload.business_name,
            "business_branch": payload.business_branch,
            "addressline": payload.addressline,
            "state": payload.state,
            "business_category": payload.business_category,
            "emergency_firstname": payload.emergency_firstname,
            "emergency_lastname": payload.emergency_lastname,
            "emergency_relationship": payload.emergency_relationship,
            "emergency_phonenumber": payload.emergency_phonenumber,
            "emergency_address": payload.emergency_address,
            "emergency_state": payload.emergency_state,
            "emergency_city": payload.emergency_city,
        }

        try:
            vendor = request.env["res.partner"].with_user(1).create(values)
            return self.env.datamodels["create.vendor.datamode.in"](
                name=vendor.name,
                phone=vendor.phone,
                latitude=vendor.partner_longitude or 0.0,
                longitude=vendor.partner_latitude or 0.0,
                purchase_frequency=vendor.purchase_frequency or 0,
                email=vendor.email,
                business_type=vendor.business_type or "",
            )

        except Exception as e:
            return self.env.datamodels["datamodel.error.out"](
                message=str(e), error=True
            )

    @restapi.method(
        [(["/vendors"], "POST")],
        auth="user",
        tags=["BusinessSaleForce"],
        input_param=Datamodel("create.vendor.bulk.datamode.in"),
        # output_param=Datamodel("create.vendor.datamode.out"),
    )
    def createvendors(self, payload):
        vendor = []
        vendor_list = payload.vendor_list
        for payload in vendor_list:
            values = {
                "name": payload.name,
                "purchase_frequency": payload.purchase_frequency,
                "partner_longitude": payload.longitude,
                "partner_latitude": payload.latitude,
                "phone": payload.phone,
                "email": payload.email,
                "business_type": payload.business_type,
                "agent_ids": [(6, 0, [request.env.user.partner_id.id])],
                "parent_id": request.env.user.partner_id.id,
                "business_name": payload.business_name,
                "business_branch": payload.business_branch,
                "addressline": payload.addressline,
                "state": payload.state,
                "business_category": payload.business_category,
                "emergency_firstname": payload.emergency_firstname,
                "emergency_lastname": payload.emergency_lastname,
                "emergency_relationship": payload.emergency_relationship,
                "emergency_phonenumber": payload.emergency_phonenumber,
                "emergency_address": payload.emergency_address,
                "emergency_state": payload.emergency_state,
                "emergency_city": payload.emergency_city,
            }

            try:
                p = request.env["res.partner"].with_user(1).create(values)
                vendor.append({'name': p.name, 'id': p.id})
            except Exception as e:
                return self.env.datamodels["datamodel.error.out"](
                    message=str(e), error=True
                )
        return vendor
        

    @restapi.method([(["/getvendors"], "GET")], auth="user", tags=["BusinessSaleForce"])
    def getvendors(self):
        domain = [("parent_id", "=", request.env.user.partner_id.id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        ]

        return (
            request.env["res.partner"]
            .with_user(1)
            .search_read(domain, fields=fields, limit=80)
        )

    @restapi.method(
        [(["/vendor/metric/<int:days>"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"],
    )
    def vendor_metric(self, days=1):
        """Metric in days default is 1"""
        date = fields.Date.today() - timedelta(days=days)
        domain = [
            ("parent_id", "=", request.env.user.partner_id.id),
            ("create_date", ">=", date),
        ]
        return {"count": request.env["res.partner"].with_user(1).search_count(domain)}

    @restapi.method(
        [(["/getvendor/<int:vendor_id>"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"],
    )
    def getvendor(self, vendor_id=None):
        domain = [("parent_id", "=", request.env.user.partner_id.id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        ]
        if vendor_id:
            domain.append(("id", "=", vendor_id))
        agents = (
            request.env["res.partner"]
            .with_user(1)
            .search_read(domain, fields=fields, limit=80)
        )
        return agents

    @restapi.method(
        [(["/confirm"], ["POST"])],
        input_param=Datamodel("confirm.order.datamodel"),
        auth="user",
        tags=["Order"],
    )
    def comfirm_payment(self, payload):
        partner_id = request.env.user.partner_id.id
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(
                [
                    ("partner_id.parent_id", "=", partner_id),
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

        [order.action_confirm() for order in orders]
        res = []
        for order in orders:
            res.append(
                dict(
                    id=order.id,
                    name=order.name,
                    state=order.state,
                    customer=order.partner_id.name,
                    phone=order.partner_id.phone,
                    date_order=str(order.date_order) or str(order.create_date),
                    amount_total=order.amount_total,
                    amount_untaxed=order.amount_untaxed,
                    items=[
                        {
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_unit": item.price_unit,
                            "discount": item.discount,
                            "name": item.name,
                        }
                        for item in order.order_line
                    ],
                )
            )
        return res

    @restapi.method(
        [(["/orders"], "GET")],
        auth="user",
        tags=["Order"],
        input_param=Datamodel("orders.datamodel.in"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def orders(self, payload):
        """."""
        res = []
        ids = request.env.user.partner_id.child_ids.ids
        ids.append(request.env.user.partner_id.id)
        domain = [("partner_id", "in", ids), ("state", "=", "sale")]
        limit = payload.limit or 80
        offset = payload.offset or 0
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(domain, limit=limit, order="create_date", offset=offset)
        )
        total_order = request.env["sale.order"].with_user(1).search_count(domain)
        for order in orders:
            res.append(
                self.env.datamodels["orders.datamodel.out"](
                    total_order=total_order,
                    id=order.id,
                    name=order.name,
                    state=order.state,
                    customer=order.partner_id.name,
                    phone=order.partner_id.phone,
                    date_order=str(order.date_order) or str(order.create_date),
                    amount_total=order.amount_total,
                    amount_untaxed=order.amount_untaxed,
                    items=[
                        {
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_unit": item.price_unit,
                            "discount": item.discount,
                            "name": item.name,
                        }
                        for item in order.order_line
                    ],
                )
            )
        return res

    @restapi.method(
        [(["/sales_groupby_vendors"], "GET")],
        tags=["Order"],
        auth="user",
    )
    def sales_groupby_vendors(self):
        """."""
        res = []
        ids = tuple(request.env.user.partner_id.child_ids.ids)
        domain = [
            ("partner_id", "in", ids),
        ]
        sql = """SELECT partner_id, sum(amount_total), COUNT(*) FROM sale_order WHERE partner_id IN %s GROUP BY partner_id"""
        request.env.cr.execute(sql, [tuple(ids)])
        group_by = request.env.cr.fetchall()
        for group in group_by:
            partner_id = request.env["res.partner"].browse(group[0])
            res.append(
                {
                    "id": partner_id.id,
                    "name": partner_id.name,
                    "total_sale": group[1],
                    "count": group[2],
                }
            )
        return res

    @restapi.method(
        [(["/orders/<int:order_id>"], "GET")],
        tags=["Order"],
        auth="user",
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def getorder(self, order_id=None):
        """."""
        res = []
        ids = request.env.user.partner_id.child_ids.ids
        ids.append(request.env.user.partner_id.id)
        domain = [
            ("partner_id", "in", ids),
        ]
        orders = (
            request.env["sale.order"].with_user(1).search(domain, order="create_date")
        )
        total_order = request.env["sale.order"].with_user(1).search_count(domain)
        for order in orders:
            res.append(
                self.env.datamodels["orders.datamodel.out"](
                    total_order=total_order,
                    id=order.id,
                    name=order.name,
                    state=order.state,
                    customer=order.partner_id.name,
                    phone=order.partner_id.phone,
                    date_order=str(order.date_order) or str(order.create_date),
                    amount_total=order.amount_total,
                    amount_untaxed=order.amount_untaxed,
                    items=[
                        {
                            "product_id": item.product_id.id,
                            "quantity": item.product_uom_qty,
                            "price_unit": item.price_unit,
                            "discount": item.discount,
                            "name": item.name,
                        }
                        for item in order.order_line
                    ],
                )
            )
        return res

    @restapi.method(
        [(["/order"], "PUT")],
        auth="user",
        tags=["Cart"],
        input_param=Datamodel("update.order.datamodel.in"),
    )
    def updateorder(self, payload):
        """partner_id is the vendor or customer id"""
        data = []
        partner_id = request.env.user.partner_id
        domain = [
            ("partner_id.parent_id", "=", partner_id.id),
            ("id", "=", payload.cart_id),
            ("state", "=", "draft"),
        ]
        orders = request.env["sale.order"].with_user(1).search(domain, limit=1)
        if orders:
            for item in payload.items:
                orders._cart_update(product_id=item.product_id, add_qty=item.quantity)
            data = []
            res = {}
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

    @restapi.method(
        [(["/order"], "POST")],
        auth="user",
        tags=["Cart"],
        input_param=Datamodel("create.orders.datamodel.in"),
    )
    def createorder(self, payload):
        """partner_id is the vendor or customer id"""
        data = []
        partner_id = request.env.user.partner_id
        for item in payload.items:
            data.append(
                (
                    0,
                    0,
                    {
                        "product_id": item.product_id,
                        "product_uom_qty": item.quantity,
                        "price_unit": item.price_unit,
                        "discount": item.discount,
                        "name": item.name,
                    },
                )
            )

        values = {
            "partner_id": payload.partner_id,
            "partner_shipping_id": payload.partner_id,
            "partner_invoice_id": payload.partner_id,
            "order_line": data,
        }
        orders = request.env["sale.order"].with_user(1).create(values)
        data = []
        res = {}
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

    @restapi.method([(["/cart"], "GET")], auth="user", tags=["Cart"])
    def cartitem(self):
        res = {}
        data = []
        domain = ["|",
            ("partner_id", "=", request.env.user.partner_id.id),
            ("partner_id", "in", request.env.user.partner_id.ids),
            ("state", "=", "draft"),
        ]
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!', domain)
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
            ("partner_id.parent_id", "=", request.env.user.partner_id.id),
            ("state", "=", "draft"),
            ("id", "=", order_id),
        ]
        order = request.env["sale.order"].with_user(1).search(domain)
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
            .with_user(1)
            .search(
                [
                    ("partner_id", "=", partner_id),
                    ("state", "in", ["cancel", "draft"]),
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
        [(["/products"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"],
        input_param=Datamodel("limit.offset.datamodel"),
    )
    def products(self, payload):
        res = {}
        domain = []
        limit = int(payload.limit) or 80
        offset = int(payload.offset) or 0
        domain = [("aisiki_product_type", "!=", False)]
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
            .search_read(
                domain, fields=fields, limit=limit, offset=offset, order="id desc"
            )
        )

        res["data"] = products
        res["count"] = len(products)
        return res

    @restapi.method(
        [
            (
                [
                    "/vendorrsearch",
                ],
                "GET",
            )
        ],
        input_param=restapi.Datamodel("partner.search.param"),
        output_param=restapi.Datamodel("partner.short.info", is_list=True),
        tags=["BusinessSaleForce"],
        auth="user",
    )
    def search(self, partner_search_param):
        domain = []
        if partner_search_param.name:
            domain.append(("name", "ilike", partner_search_param.name))
        if partner_search_param.id:
            domain.append(("id", "=", partner_search_param.id))
        result = []
        partner_ids = (
            request.env["res.partner"]
            .with_user(1)
            .search(domain, limit=80, order="create_date desc")
        )
        for partner_id in partner_ids:
            res = {
                "id": partner_id.id,
                "name": partner_id.name,
                "street": partner_id.street or "",
                "phone": partner_id.phone or "",
                "latitude": partner_id.partner_latitude or 0.0,
                "longitude": partner_id.partner_longitude or 0.0,
                "create_date": str(partner_id.create_date),
            }
            result.append(self.env.datamodels["vendor.datamodel.out"](**res))
        return result

    @restapi.method(
        [(["/paymenthistory"], "GET")],
        auth="user",
        input_param=Datamodel("paymenthistory.datamodel.in"),
        output_param=Datamodel("paymenthistory.datamodel.out", is_list=True),
        tags=["Earning"],
    )
    def paymenthistory(self, payload):

        res = []
        limit = payload.limit or 80

        settlements = (
            request.env["sale.commission.settlement"]
            .with_user(1)
            .search(
                [
                    ("agent_id", "=", request.env.user.partner_id.id),
                    ("state", "=", "invoiced"),
                ],
                limit=limit,
            )
        )
        for settlement in settlements:
            res.append(
                self.env.datamodels["paymenthistory.datamodel.out"](
                    date_from=fields.Date.to_string(settlement.date_from),
                    date_to=fields.Date.to_string(settlement.date_to),
                    total=settlement.total,
                    commission_lines=[
                        {
                            "settled_amount": line.settled_amount,
                            "date": fields.Date.to_string(line.date),
                        }
                        for line in settlement.line_ids
                    ],
                )
            )

        return res

    @restapi.method(
        [(["/withdrawable"], "GET")],
        auth="user",
        output_param=Datamodel("withdrawable.datamodel.out"),
        tags=["Earning"],
    )
    def withdrawable_balance(self):
        settlements = (
            request.env["sale.commission.settlement"]
            .with_user(1)
            .search(
                [
                    ("agent_id", "=", request.env.user.partner_id.id),
                    ("state", "=", "settled"),
                ]
            )
        )
        withdrawable = sum([settlement.total for settlement in settlements])
        return self.env.datamodels["withdrawable.datamodel.out"](
            withdrawable=withdrawable,
        )

    @restapi.method(
        [(["/withdrawal"], "GET")],
        auth="user",
        tags=["Earning"],
        input_param=Datamodel("paymenthistory.datamodel.in"),
        output_param=Datamodel("paymenthistory.datamodel.out", is_list=True),
    )
    def withdrawal(self, payload):
        res = []
        limit = payload.limit or 80

        settlements = (
            request.env["sale.commission.settlement"]
            .with_user(1)
            .search(
                [
                    ("agent_id", "=", request.env.user.partner_id.id),
                    ("state", "=", "invoiced"),
                ],
                limit=limit,
            )
        )
        for settlement in settlements:
            res.append(
                self.env.datamodels["paymenthistory.datamodel.out"](
                    date_from=fields.Date.to_string(settlement.date_from),
                    date_to=fields.Date.to_string(settlement.date_to),
                    total=settlement.total,
                    commission_lines=[
                        {
                            "settled_amount": line.settled_amount,
                            "date": fields.Date.to_string(line.date),
                        }
                        for line in settlement.line_ids
                    ],
                )
            )

        return res

    @restapi.method(
        [(["/total_earning"], "GET")],
        auth="user",
        tags=["Earning"],
        output_param=Datamodel("withdrawable.datamodel.out"),
    )
    def total_earning(self):
        settlements = (
            request.env["sale.commission.settlement"]
            .with_user(1)
            .search(
                [
                    ("agent_id", "=", request.env.user.partner_id.id),
                ]
            )
        )
        withdrawable = sum([settlement.total for settlement in settlements])
        return self.env.datamodels["withdrawable.datamodel.out"](
            withdrawable=withdrawable,
        )

    @restapi.method(
        [(["/metrics"], "GET")],
        auth="user",
        tags=["Metrics"],
        output_param=Datamodel("metrics.datamodel.out"),
    )
    def metrics(self):
        total = []
        weekly = []
        monthly = []
        today = fields.Date.today() - timedelta(days=1)
        this_week = fields.Date.today() - timedelta(days=7)
        this_month = fields.Date.today() - timedelta(days=30)
        vendor_today = (
            request.env["res.partner"]
            .with_user(1)
            .search_count(
                [
                    ("parent_id", "=", request.env.user.partner_id.id),
                    ("create_date", ">=", today),
                ]
            )
        )
        vendor_week = (
            request.env["res.partner"]
            .with_user(1)
            .search_count(
                [
                    ("parent_id", "=", request.env.user.partner_id.id),
                    ("create_date", ">=", this_week),
                ]
            )
        )
        vendor_month = (
            request.env["res.partner"]
            .with_user(1)
            .search_count(
                [
                    ("parent_id", "=", request.env.user.partner_id.id),
                    ("create_date", ">=", this_month),
                ]
            )
        )

        sale_today = sum(
            [
                o.amount_total
                for o in request.env["sale.order"]
                .with_user(1)
                .search(
                    [
                        ("partner_id.parent_id", "=", request.env.user.partner_id.id),
                        ("create_date", ">=", today),
                    ]
                )
            ]
        )
        sale_week = sum(
            [
                o.amount_total
                for o in request.env["sale.order"]
                .with_user(1)
                .search(
                    [
                        ("partner_id.parent_id", "=", request.env.user.partner_id.id),
                        ("create_date", ">=", this_week),
                    ]
                )
            ]
        )
        sale_month = sum(
            [
                o.amount_total
                for o in request.env["sale.order"]
                .with_user(1)
                .search(
                    [
                        ("partner_id.parent_id", "=", request.env.user.partner_id.id),
                        ("create_date", ">=", this_month),
                    ]
                )
            ]
        )

        return self.env.datamodels["metrics.datamodel.out"](
            today=[
                {
                    "total_number_of_vendors": vendor_today,
                    "total_amount_of_sales": sale_today,
                }
            ],
            weekly=[
                {
                    "total_number_of_vendors": vendor_week,
                    "total_amount_of_sales": sale_week,
                }
            ],
            monthly=[
                {
                    "total_number_of_vendors": vendor_month,
                    "total_amount_of_sales": sale_month,
                }
            ],
        )
