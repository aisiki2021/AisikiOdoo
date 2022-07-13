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




class CollectionApp(Component):
    _inherit = "aisiki.base.rest"
    _name = "procurement"
    _usage = "collection"
    _collection = "collection"
    _description = """
        CollectionApp
        
    """

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
            "origin": payload.origin,
            "password": payload.password,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "referral_code": payload.referral_code,
            "contact_person": payload.contact_person,
            "business_category": payload.business_category,
            "number_of_offices": payload.number_of_offices,
            "company_type": "company" if payload.is_corporate else "person",
            "procurement_agent": True,
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


    @restapi.method([(["/agents"], "GET")], auth="user", tags=["Agents"])
    def get_agents(self):
        domain = [("procurement_agent", "=", True)]
        fields = ["name", "phone", "email", "image_url"]
        agents = request.env["res.partner"].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents

    @restapi.method([(["/agents/<int:id>"], "GET")], auth="user", tags=["Agents"])
    def agent_by_id(self, id=None):
        domain = [("procurement_agent", "=", True), ("id", "=", id)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "image_url",
            "phone",
            "email",
        ]

        agents = request.env["res.partner"].with_user(1).search_read(domain, fields=fields, limit=1)
        return agents

    @restapi.method(
        [(["/vendor"], "POST")],
        auth="user",
        tags=["Agents"],
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
            "image_1920": payload.image,
            "procurement_agent": True,
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
            return self.env.datamodels["datamodel.error.out"](message=str(e), error=True)


    @restapi.method([(["/agent/<int:id>/vendors"], "GET")], auth="user", tags=["Agents"])
    def agents_vendor(self, id=None):
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
            "image_url",
        ]
        domain = [("parent_id", "=", id), ("parent_id.procurement_agent", "=", True)]
        agents = request.env["res.partner"].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents


    @restapi.method(
        [(["/vendors"], "POST")],
        auth="user",
        tags=["Agents"],
        input_param=Datamodel("create.vendor.bulk.datamode.in"),
    
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
                "image_1920": payload.image,
                "procurement_agent": True,
            }

            try:
                p = request.env["res.partner"].with_user(1).create(values)
                vendor.append({"name": p.name, "id": p.id})
            except Exception as e:
                return self.env.datamodels["datamodel.error.out"](message=str(e), error=True)
        return vendor


    @restapi.method([(["/getvendors"], "GET")], auth="user", tags=["Agents"])
    def getvendors(self):
        domain = [("parent_id", "=", request.env.user.partner_id.id), ("procurement_agent", "=", True)]
        fields = [
            "name",
            "purchase_frequency",
            "partner_longitude",
            "partner_latitude",
            "phone",
            "email",
            "image_url",
        ]

        return request.env["res.partner"].with_user(1).search_read(domain, fields=fields, limit=80)


    @restapi.method(
        [(["/getvendor/<int:vendor_id>"], "GET")],
        auth="user",
        tags=["Agents"],
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
        agents = request.env["res.partner"].with_user(1).search_read(domain, fields=fields, limit=80)
        return agents


    @restapi.method([(["/orders"], "GET")], auth="user", tags=["Procurement"])
    def orders(self):
        res = {}
        domain = [("partner_id", "in", request.env.user.partner_id.child_ids.ids)]
        domain = []
        orders = request.env["purchase.order"].with_user(1).search(domain, limit=80)

        details = [
            {
                "id": order.id,
                "name": order.name,
                "amount_total": order.amount_total,
                "state": order.state,
                "vendor": order.partner_id.name,
                "date_order": order.date_order,
                "date_planned": order.date_planned,
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

    @restapi.method([(["/orders/<int:id>"], "GET")], auth="user", tags=["Procurement"])
    def orders_by_id(self, id):
        res = {}
        # domain = [("partner_id", "=", request.env.user.partner_id.id), ("id", "=", id)]
        domain = [("id", "=", id)]
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
        [(["/create_order"], ["POST"])],
        auth="user",
        input_param=Datamodel("cart.datamodel.in"),
        tags=["Procurement"],
    )
    def create_order(self, payload):
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
