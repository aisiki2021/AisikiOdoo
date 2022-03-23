from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

import datetime
import json
from odoo import fields

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
            "password": payload.password,
            "email": payload.email,
            "agentid": request.env['ir.sequence'].with_user(1).next_by_code('aisiki.agent.seq')
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

    @restapi.method(
        [(["/all_agents"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"])
    def get_agents(self):
        domain = [('agent', '=', True)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        
        ]
        agents = request.env['res.partner'].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents

    @restapi.method(
        [(['/agents/<int:id>'], "GET")],
        auth="user",
        tags=["BusinessSaleForce"])
    def agent_by_id(self, id=None):
        domain = [('agent', '=', True), ('id', '=', id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        
        ]

        agents = request.env['res.partner'].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents


    @restapi.method(
        [(['/agent/<int:id>/vendors'], "GET")],
        auth="user",
        tags=["BusinessSaleForce"])
    def agents_vendor(self, id=None):
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        
        ]
        domain = [('parent_id', '=', id), ('parent_id.agent', '=', True)]
        agents = request.env['res.partner'].with_user(1).search_read(domain, fields=fields, limit=80)
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
        [(["/getvendors"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"]
    )
    def getvendors(self):
        domain = [('parent_id', '=', request.env.user.partner_id.id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        
        ]

        return request.env['res.partner'].with_user(1).search_read(domain, fields=fields, limit=80)
     

    @restapi.method(
        [(["/getvendor/<int:vendor_id>"], "GET")],
        auth="user",
        tags=["BusinessSaleForce"]
    )
    def getvendor(self, vendor_id=None):
        domain = [('parent_id', '=', request.env.user.partner_id.id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
        
        ]
        if vendor_id:
            domain.append(('id', '=', vendor_id))
        agents = request.env['res.partner'].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents

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
        domain = [("partner_id", "in", ids)]
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
        domain = [("partner_id", "in", ids), ]
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
        [(["/order"], "POST")],
        auth="user",
        tags=["Order"],
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
        domain = [
            ("partner_id.parent_id", "=", request.env.user.partner_id.id),
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
    





    # @restapi.method(
    #     [(["/paymenthistory"], "GET")],
    #     auth="user",
    #     input_param=Datamodel("paymenthistory.datamodel.in"),
    #     output_param=Datamodel("paymenthistory.datamodel.out", is_list=True),
    # )
    # def paymenthistory(self, payload):

    #     res = []
    #     limit = payload.limit or 80

    #     settlements = (
    #         request.env["sale.commission.settlement"]
    #         .with_user(1)
    #         .search(
    #             [
    #                 ("agent_id", "=", request.env.user.partner_id.id),
    #                 ("state", "=", "invoiced"),
    #             ],
    #             limit=limit,
    #         )
    #     )
    #     for settlement in settlements:
    #         res.append(
    #             self.env.datamodels["paymenthistory.datamodel.out"](
    #                 date_from=fields.Date.to_string(settlement.date_from),
    #                 date_to=fields.Date.to_string(settlement.date_to),
    #                 total=settlement.total,
    #                 commission_lines=[
    #                     {
    #                         "settled_amount": line.settled_amount,
    #                         "date": fields.Date.to_string(line.date),
    #                     }
    #                     for line in settlement.line_ids
    #                 ],
    #             )
    #         )

    #     return res

    # @restapi.method(
    #     [(["/withdrawable"], "GET")],
    #     auth="user",
    #     output_param=Datamodel("withdrawable.datamodel.out"),
    # )
    # def withdrawable_balance(self):
    #     """Withdrawable Balance."""

    #     settlements = (
    #         request.env["sale.commission.settlement"]
    #         .with_user(1)
    #         .search(
    #             [
    #                 ("agent_id", "=", request.env.user.partner_id.id),
    #                 ("state", "=", "settled"),
    #             ]
    #         )
    #     )
    #     withdrawable = sum([settlement.total for settlement in settlements])
    #     return self.env.datamodels["withdrawable.datamodel.out"](
    #         withdrawable=withdrawable,
    #     )

    # @restapi.method(
    #     [(["/withdrawal"], "GET")],
    #     auth="user",
    #     input_param=Datamodel("paymenthistory.datamodel.in"),
    #     output_param=Datamodel("paymenthistory.datamodel.out", is_list=True),
    # )
    # def withdrawal(self, payload):
    #     """ withdrawal History"""

    #     res = []
    #     limit = payload.limit or 80

    #     settlements = (
    #         request.env["sale.commission.settlement"]
    #         .with_user(1)
    #         .search(
    #             [
    #                 ("agent_id", "=", request.env.user.partner_id.id),
    #                 ("state", "=", "invoiced"),
    #             ],
    #             limit=limit,
    #         )
    #     )
    #     for settlement in settlements:
    #         res.append(
    #             self.env.datamodels["paymenthistory.datamodel.out"](
    #                 date_from=fields.Date.to_string(settlement.date_from),
    #                 date_to=fields.Date.to_string(settlement.date_to),
    #                 total=settlement.total,
    #                 commission_lines=[
    #                     {
    #                         "settled_amount": line.settled_amount,
    #                         "date": fields.Date.to_string(line.date),
    #                     }
    #                     for line in settlement.line_ids
    #                 ],
    #             )
    #         )

    #     return res

    # @restapi.method(
    #     [(["/total_earning"], "GET")],
    #     auth="user",
    #     output_param=Datamodel("withdrawable.datamodel.out"),
    # )
    # def total_earning(self):
    #     """Withdrawable Balance."""

    #     settlements = (
    #         request.env["sale.commission.settlement"]
    #         .with_user(1)
    #         .search([("agent_id", "=", request.env.user.partner_id.id),])
    #     )
    #     withdrawable = sum([settlement.total for settlement in settlements])
    #     return self.env.datamodels["withdrawable.datamodel.out"](
    #         withdrawable=withdrawable,
    #     )
