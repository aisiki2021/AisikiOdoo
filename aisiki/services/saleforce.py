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
            "email": payload.email,
            "agentid": request.env['ir.sequence'].next_by_code('aisiki.agent.seq')
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

    # @restapi.method(
    #     [(["/createvendor"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("create.vendor.datamode.in"),
    #     output_param=Datamodel("create.vendor.datamode.out"),
    # )
    # def createvendor(self, payload):
    #     values = {
    #         "name": payload.name,
    #         "purchase_frequency": payload.purchase_frequency,
    #         "partner_longitude": payload.longitude,
    #         "partner_latitude": payload.latitude,
    #         "phone": payload.phone,
    #         "email": payload.email,
    #         "business_type": payload.business_type,
    #         "agent_ids": [(6, 0, [request.env.user.partner_id.id])],
    #     }

    #     try:
    #         vendor = request.env["res.partner"].with_user(1).create(values)
    #         return self.env.datamodels["create.vendor.datamode.in"](
    #             name=vendor.name,
    #             phone=vendor.phone,
    #             latitude=vendor.partner_longitude or 0.0,
    #             longitude=vendor.partner_latitude or 0.0,
    #             purchase_frequency=vendor.purchase_frequency or 0,
    #             email=vendor.email,
    #             business_type=vendor.business_type or "",
    #         )

    #     except Exception as e:
    #         return self.env.datamodels["datamodel.error.out"](
    #             message=str(e), error=True
    #         )

    # @restapi.method(
    #     [(["/orderstotal"], "GET")],
    #     auth="user",
    #     input_param=Datamodel("orders.datamodel.in"),
    #     output_param=Datamodel("orders.datamodel.out", is_list=True),
    # )
    # def total_order(self, payload):
    #     """."""
    #     res = []
    #     ids = request.env.user.partner_id.child_ids.ids
    #     ids.append(request.env.user.partner_id.id)
    #     domain = [("partner_id", "in", ids)]
    #     limit = payload.limit or 80
    #     offset = payload.offset or 0
    #     if limit:
    #         limit = int(limit)
    #     if offset:
    #         offset = int(offset)
    #     orders = (
    #         request.env["sale.order"]
    #         .with_user(1)
    #         .search(domain, limit=limit, order="create_date", offset=offset)
    #     )
    #     total_order = request.env["sale.order"].with_user(1).search_count(domain)
    #     for order in orders:
    #         res.append(
    #             self.env.datamodels["orders.datamodel.out"](
    #                 total_order=total_order,
    #                 id=order.id,
    #                 name=order.name,
    #                 state=order.state,
    #                 customer=order.partner_id.name,
    #                 phone=order.partner_id.phone,
    #                 date_order=str(order.date_order) or str(order.create_date),
    #                 amount_total=order.amount_total,
    #                 amount_untaxed=order.amount_untaxed,
    #                 items=[
    #                     {
    #                         "product_id": item.product_id.id,
    #                         "quantity": item.product_uom_qty,
    #                         "price_unit": item.price_unit,
    #                         "discount": item.discount,
    #                         "name": item.name,
    #                     }
    #                     for item in order.order_line
    #                 ],
    #             )
    #         )
    #     return res

    # @restapi.method(
    #     [(["/orders/<int:order_id>"], "GET")],
    #     auth="user",
    #     output_param=Datamodel("orders.datamodel.out", is_list=True),
    # )
    # def getorder(self, order_id=None):
    #     """."""
    #     res = []
    #     ids = request.env.user.partner_id.child_ids.ids
    #     ids.append(request.env.user.partner_id.id)
    #     domain = [("partner_id", "in", ids)]
    #     orders = (
    #         request.env["sale.order"].with_user(1).search(domain, order="create_date")
    #     )
    #     total_order = request.env["sale.order"].with_user(1).search_count(domain)
    #     for order in orders:
    #         res.append(
    #             self.env.datamodels["orders.datamodel.out"](
    #                 total_order=total_order,
    #                 id=order.id,
    #                 name=order.name,
    #                 state=order.state,
    #                 customer=order.partner_id.name,
    #                 phone=order.partner_id.phone,
    #                 date_order=str(order.date_order) or str(order.create_date),
    #                 amount_total=order.amount_total,
    #                 amount_untaxed=order.amount_untaxed,
    #                 items=[
    #                     {
    #                         "product_id": item.product_id.id,
    #                         "quantity": item.product_uom_qty,
    #                         "price_unit": item.price_unit,
    #                         "discount": item.discount,
    #                         "name": item.name,
    #                     }
    #                     for item in order.order_line
    #                 ],
    #             )
    #         )
    #     return res

    # @restapi.method(
    #     [(["/getvendors"], "GET")],
    #     auth="user",
    #     output_param=Datamodel("vendor.datamodel.out", is_list=True),
    # )
    # def getvendors(self):
    #     result = []
    #     partner_id = request.env.user.partner_id
    #     cr = request.env.cr
    #     cr.execute(
    #         "SELECT partner_id FROM partner_agent_rel WHERE agent_id=%s",
    #         tuple([partner_id.id]),
    #     )
    #     partner_ids = flatten(cr.fetchall())
    #     partner_ids = (
    #         request.env["res.partner"].with_user(1).browse(partner_ids)
    #         if partner_ids
    #         else partner_ids
    #     )
    #     for partner_id in partner_ids:
    #         res = {
    #             "id": partner_id.id,
    #             "name": partner_id.name,
    #             "street": partner_id.street or "",
    #             "phone": partner_id.phone or "",
    #             "latitude": partner_id.partner_latitude or 0.0,
    #             "longitude": partner_id.partner_longitude or 0.0,
    #             "create_date": str(partner_id.create_date),
    #         }
    #         result.append(self.env.datamodels["vendor.datamodel.out"](**res))
    #     return result

    # @restapi.method(
    #     [(["/createorder"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("create.orders.datamodel.in"),
    #     output_param=Datamodel("create.orders.datamodel.out",),
    # )
    # def createorder(self, payload):
    #     data = []
    #     partner_id = request.env.user.partner_id
    #     for item in payload.items:
    #         data.append(
    #             (
    #                 0,
    #                 0,
    #                 {
    #                     "product_id": item.product_id,
    #                     "product_uom_qty": item.quantity,
    #                     "price_unit": item.price_unit,
    #                     "discount": item.discount,
    #                     "name": item.name,
    #                 },
    #             )
    #         )

    #     values = {
    #         "partner_id": payload.partner_id,
    #         "partner_shipping_id": payload.partner_id,
    #         "partner_invoice_id": payload.partner_id,
    #         "order_line": data,
    #     }
    #     order = request.env["sale.order"].create(values)
    #     output = {
    #         "id": order.id,
    #         "name": order.name,
    #         "state": order.state,
    #         "amount_total": order.amount_total,
    #     }
    #     return self.env.datamodels["create.orders.datamodel.out"](**output)

    # @restapi.method(
    #     [(["/cart"], "GET")],
    #     auth="user",
    #     input_param=Datamodel("view.cart.datamodel.in"),
    #     output_param=Datamodel("orders.datamodel.out", is_list=True),
    # )
    # def view_cart(self, payload):
    #     """."""
    #     res = []
    #     _id = payload.partner_id

    #     domain = [("partner_id", "=", _id), ("state", "=", "draft")]

    #     orders = (
    #         request.env["sale.order"]
    #         .with_user(1)
    #         .search(domain, order="create_date", limit=1)
    #     )
    #     total_order = request.env["sale.order"].with_user(1).search_count(domain)
    #     for order in orders:
    #         res.append(
    #             self.env.datamodels["orders.datamodel.out"](
    #                 total_order=total_order,
    #                 id=order.id,
    #                 name=order.name,
    #                 state=order.state,
    #                 customer=order.partner_id.name,
    #                 phone=order.partner_id.phone,
    #                 date_order=str(order.date_order) or str(order.create_date),
    #                 amount_total=order.amount_total,
    #                 amount_untaxed=order.amount_untaxed,
    #                 items=[
    #                     {
    #                         "product_id": item.product_id.id,
    #                         "quantity": item.product_uom_qty,
    #                         "price_unit": item.price_unit,
    #                         "discount": item.discount,
    #                         "name": item.name,
    #                     }
    #                     for item in order.order_line
    #                 ],
    #             )
    #         )
    #     return res

    # @restapi.method(
    #     [(["/editprofile"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("editprofile.datamodel.in"),
    #     output_param=Datamodel("editprofile.datamodel.out"),
    # )
    # def editprofile(self, payload):
    #     image_base64 = payload.image_base64.encode()
    #     if image_base64:
    #         request.env.user.partner_id.write({"image_1920": image_base64})
    #     if payload.old_passwd and payload.new_passwd:
    #         try:
    #             request.env.user.change_password(payload.old_passwd, payload.new_passwd)
    #         except Exception as e:
    #             return self.env.datamodels["editprofile.datamodel.out"](
    #                 message="%s: old password is not correct" % (str(e),), haserror=True
    #             )

    #     return self.env.datamodels["editprofile.datamodel.out"](
    #         image_base64=request.env.user.partner_id.image_1920
    #     )

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
