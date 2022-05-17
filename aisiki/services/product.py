from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

from odoo.addons.base_rest import restapi
from odoo.http import db_monodb, request, root
from odoo.addons.base_rest_datamodel.restapi import Datamodel

import datetime
import json
from odoo import fields

from odoo.tools.misc import flatten
from .authenticate import _rotate_session


class OrderingApp(Component):
    _inherit = "base.rest.service"
    _name = "catlog"
    _usage = "catlog"
    _collection = "catlog"
    _description = """
        Product Catalog
        
    """

    @restapi.method(
        [(["/authentication"], "POST")],
        auth="public",
        input_param=Datamodel("saleforce.login.datamodel.in"),
        output_param=Datamodel("saleforce.login.datamodel.out"),
    )
    def authentication(self, payload):
        params = request.params
        db_name = params.get("db", db_monodb())
        request.session.authenticate(db_name, params["agentid"], params["password"])
        result = request.env["ir.http"].session_info()
        _rotate_session(request)
        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        return self.env.datamodels["saleforce.login.datamodel.out"](
            session_id=request.session.sid,
            expires_at=fields.Datetime.to_string(expiration),
            uid=result.get("uid"),
            agentid=result.get("username"),
            name=result.get("name"),
            partner_id=result.get("partner_id"),
        )

    @restapi.method(
        [(["/createcustomer"], "POST")],
        auth="user",
        input_param=Datamodel("create.vendor.datamode.in"),
        output_param=Datamodel("create.vendor.datamode.out"),
    )
    def createcustomer(self, payload):
        values = {
            "name": payload.name,
            "purchase_frequency": payload.purchase_frequency,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "phone": payload.phone,
            "email": payload.email,
            "business_type": payload.business_type,
            # "agent_ids": [(6, 0, [request.env.user.partner_id.id])]
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

    @restapi.method(
        [(["/customers"], "GET")],
        auth="user",
        input_param=Datamodel("limit.offset.datamodel"),
        output_param=Datamodel("vendor.datamodel.out", is_list=True),
    )
    def customers(self, payload):
        result = []
        limit = int(payload.limit) or 80
        offset = int(payload.offset) or 0
        partner_ids = (
            request.env["res.partner"].with_user(1).search([], limit=limit, offset=offset, order="create_date desc")
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
        [(["/orders/<int:order_id>"], "GET")],
        auth="user",
        # input_param=Datamodel("orders.datamodel.in"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def getorder(self, order_id=None):
        """."""
        res = []
        domain = [("id", "=", int(order_id))]
        orders = request.env["sale.order"].with_user(1).search(domain, order="create_date")
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
        [(["/orders"], "GET")],
        auth="user",
        input_param=Datamodel("limit.offset.datamodel"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def getorders(self, payload):
        """."""
        res = []
        limit = int(payload.limit) or 80
        offset = int(payload.offset) or 0
        orders = request.env["sale.order"].with_user(1).search([], order="create_date desc")
        total_order = request.env["sale.order"].with_user(1).search_count([])
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
        [(["/createorder"], "POST")],
        auth="user",
        input_param=Datamodel("create.orders.datamodel.in"),
        output_param=Datamodel(
            "create.orders.datamodel.out",
        ),
    )
    def createorder(self, payload):
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
        order = request.env["sale.order"].create(values)
        output = {
            "id": order.id,
            "name": order.name,
            "state": order.state,
            "amount_total": order.amount_total,
        }
        return self.env.datamodels["create.orders.datamodel.out"](**output)

    @restapi.method(
        [(["/products"], "GET")],
        auth="public",
        input_param=Datamodel("limit.offset.datamodel"),
        output_param=Datamodel("fooditems.datamodel.out", is_list=True),
    )
    def products(self, payload):
        res = []
        domain = []
        limit = int(payload.limit) or 80
        offset = int(payload.offset) or 0
        domain = [("aisiki_product_type", "!=", False)]
        products = (
            request.env["product.product"].with_user(1).search(domain, limit=limit, offset=offset, order="id desc")
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
        [
            (
                [
                    "/customersearch",
                ],
                "GET",
            )
        ],
        input_param=restapi.Datamodel("partner.search.param"),
        output_param=restapi.Datamodel("partner.short.info", is_list=True),
        auth="public",
    )
    def search(self, partner_search_param):
        domain = []
        if partner_search_param.name:
            domain.append(("name", "ilike", partner_search_param.name))
        if partner_search_param.id:
            domain.append(("id", "=", partner_search_param.id))
        result = []
        partner_ids = request.env["res.partner"].with_user(1).search(domain, limit=80, order="create_date desc")
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
