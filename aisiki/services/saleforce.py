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
    _name = "saleforce"
    _usage = "saleforce"
    _collection = "saleforce"
    _description = """
        Business Sale Force
        
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
        [(["/forgotpassword"], "GET")],
        auth="public",
        input_param=Datamodel("saleforce.forgotpassword.datamodel.in"),
        output_param=Datamodel("saleforce.forgotpassword.datamodel.out"),
    )
    def forgotpassword(self, payload):
        agentid = payload.agentid.strip()
        user = (
            request.env["res.users"]
            .with_user(1)
            .search([("login", "=", agentid)], limit=1)
        )
        return self.env.datamodels["forgotpassword.datamodel.out"](
            password_reset_url=user.password_reset_url
        )

    @restapi.method(
        [(["/singup"], "POST")],
        auth="public",
        input_param=Datamodel("signup.saleforce.datamode.in"),
        output_param=Datamodel("signup.saleforce.datamode.out"),
    )
    def singup(self, payload):
        values = {
            "name": payload.first_name + " " + payload.last_name,
            "referral_code": payload.referral_code,
            "phone": payload.phone,
            "city": payload.city,
            "idnumber": payload.idnumber,
            "toc": payload.toc,
            "idtype": payload.idtype,
            "login": payload.agentid,
            "email": payload.email,
        }

        try:
            user = request.env["res.users"].with_user(1)._signup_create_user(values)
            user.write({"city": payload.city, "isagent": True})
            return self.env.datamodels["signup.saleforce.datamode.out"](
                name=user.name or "",
                phone=user.phone or "",
                city=user.city or "",
                agentid=user.login or "",
                referral_code=user.referral_code,
                idnumber=user.idnumber,
                toc=user.toc,
                idtype=user.idtype,
                email=user.email or "",
            )

        except Exception as e:

            return self.env.datamodels["datamodel.error.out"](
                message=str(e), error=True
            )

    @restapi.method(
        [(["/createvendor"], "POST")],
        auth="user",
        input_param=Datamodel("create.vendor.datamode.in"),
        output_param=Datamodel("create.vendor.datamode.out"),
    )
    def vendor(self, payload):
        values = {
            "name": payload.name,
            "purchase_frequency": payload.purchase_frequency,
            "partner_longitude": payload.longitude,
            "partner_latitude": payload.latitude,
            "phone": payload.phone,
            "email": payload.email,
            "business_type": payload.business_type,
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
        [(["/orderstotal"], "GET")],
        auth="user",
        input_param=Datamodel("orders.datamodel.in"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def total_order(self, payload):
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
        auth="user",
        # input_param=Datamodel("orders.datamodel.in"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def getorder(self, order_id=None):
        """."""
        res = []
        ids = request.env.user.partner_id.child_ids.ids
        ids.append(request.env.user.partner_id.id)
        domain = [("partner_id", "in", ids)]
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
        [(["/getvendor"], "GET")],
        auth="user",
        input_param=Datamodel("create.orders.datamodel.in"),
        output_param=Datamodel("vendor.datamodel.out", is_list=True),
    )
    def vendor_list(self):
        result = []
        partner_id = request.env.user.partner_id
        for partner_id in partner_id.child_ids:
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
        [(["/createorder"], "POST")],
        auth="user",
        input_param=Datamodel("create.orders.datamodel.in"),
        output_param=Datamodel("create.orders.datamodel.out",),
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
                        "name": "aaaaa",
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
        [(["/cart"], "GET")],
        auth="user",
        input_param=Datamodel("view.cart.datamodel.in"),
        output_param=Datamodel("orders.datamodel.out", is_list=True),
    )
    def view_cart(self, payload):
        """."""
        res = []
        _id = payload.partner_id

        domain = [("partner_id", "=", _id), ("state", "=", "draft")]

        orders = (
            request.env["sale.order"]
            .with_user(1)
            .search(domain, order="create_date", limit=1)
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
        [(["/editprofile"], "POST")],
        auth="user",
        input_param=Datamodel("editprofile.datamodel.in"),
        output_param=Datamodel("editprofile.datamodel.out"),
    )
    def editprofile(self, payload):
        image_base64 = payload.image_base64.encode()
        if image_base64:
            request.env.user.partner_id.write({'image_1920': image_base64})
        if payload.old_passwd and payload.new_passwd:
            try:
                request.env.user.change_password(payload.old_passwd, payload.new_passwd)
            except Exception as e:
                return self.env.datamodels["editprofile.datamodel.out"](
                message= "%s: old password is not correct" % (str(e), ), haserror=True
            )

        return self.env.datamodels["editprofile.datamodel.out"](image_base64=request.env.user.partner_id.image_1920)

    # @restapi.method(
    #     [(["/addbalance"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("wallet.addbalance.datamodel.in"),
    #     output_param=Datamodel("wallet.balance.datamodel.out"),
    # )
    # def postbalance(self, payload):
    #     """Add wallet balance"""
    #     wallet = (
    #         request.env["account.journal"]
    #         .with_user(1)
    #         .search([("name", "ilike", payload.name)], limit=1)
    #     )

    #     payment = request.env["account.payment"].with_user(1)

    #     payment_type = (
    #         request.env["account.payment.method"]
    #         .with_user(1)
    #         .search(
    #             [("code", "=", "manual"), ("payment_type", "=", payment_type)], limit=1
    #         )
    #     )

    #     payload = {
    #         "payment_type": "inbound",
    #         "partner_type": "customer",
    #         "journal_id": wallet.id,
    #         "partner_id": request.env.user.partner_id.id,
    #         "amount": payload.amount,
    #         "payment_method_id": payment_type.id,
    #     }
    #     payment.create(payload).action_post()
    #     total_due = abs(request.env.user.partner_id.total_due)
    #     return self.env.datamodels["wallet.balance.datamodel.out"](balance=total_due)

    # @restapi.method(
    #     [(["/payment"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("payment.datamodel.in"),
    #     output_param=Datamodel("cart.datamodel.out"),
    # )
    # def payment(self, payload):
    #     items = []
    #     partner_id = request.env.user.partner_id.id
    #     order = (
    #         request.env["sale.order"]
    #         .with_user(1)
    #         .search(
    #             [("partner_id", "=", partner_id), ("id", "=", payload.order_id)],
    #             limit=1,
    #         )
    #     )
    #     for line in order.order_line:
    #         items.append(
    #             {
    #                 "product_id": line.product_id.id,
    #                 "price_unit": line.price_unit,
    #                 "product_uom_qty": line.product_uom_qty,
    #                 "discount": line.discount,
    #             },
    #         )

    #     order._create_payment_transaction({"acquirer_id": 6, "state": "done"})
    #     order.action_confirm()

    #     return self.env.datamodels["cart.datamodel.out"](
    #         partner_id=order.partner_id.id,
    #         items=items,
    #         amount_total=order.amount_total,
    #         order_id=order.id,
    #         state=order.state,
    #     )

    # @restapi.method(
    #     [(["/cart"], "POST")],
    #     auth="user",
    #     input_param=Datamodel("cart.datamodel.in"),
    #     output_param=Datamodel("cart.datamodel.out"),
    # )
    # def cart(self, payload):
    #     items = []
    #     partner_id = request.env.user.partner_id.id
    #     order = (
    #         request.env["sale.order"]
    #         .with_user(1)
    #         .search([("partner_id", "=", partner_id)], limit=1)
    #     )
    #     if not order:
    #         for line in payload.items:
    #             items.append(
    #                 (
    #                     0,
    #                     0,
    #                     {
    #                         "product_id": line.product_id,
    #                         "price_unit": line.price_unit,
    #                         "product_uom_qty": line.quantity,
    #                         "discount": line.discount,
    #                     },
    #                 )
    #             )
    #         payload = {
    #             "partner_id": partner_id,
    #             "order_line": items,
    #         }
    #         order = request.env["sale.order"].with_user(1).create(payload)
    #     else:
    #         order.order_line.unlink()
    #         for line in payload.items:
    #             payload = {
    #                 "order_id": order.id,
    #                 "product_id": line.product_id,
    #                 "price_unit": line.price_unit,
    #                 "product_uom_qty": line.quantity,
    #                 "discount": line.discount,
    #             }
    #             request.env["sale.order.line"].with_user(1).create(payload)

    #         items = [
    #             {
    #                 "product_id": line.product_id.id,
    #                 "quantity": line.product_uom_qty,
    #                 "discount": line.discount,
    #                 "price_unit": line.price_unit,
    #                 "subtotal": line.price_subtotal,
    #             }
    #             for line in order.order_line
    #         ]

    #     return self.env.datamodels["cart.datamodel.out"](
    #         partner_id=order.partner_id.id,
    #         items=items,
    #         amount_total=order.amount_total,
    #         order_id=order.id,
    #     )

    # @restapi.method(
    #     [(["/updateprofile"], "PUT")],
    #     auth="user",
    #     input_param=Datamodel("profile.datamodel.update1"),
    #     output_param=Datamodel("profile.datamodel.update"),
    # )
    # def updateprofile(self, payload):
    #     partner_id = request.env.user.partner_id
    #     partner_id.write(
    #         {
    #             "name": payload.name,
    #             "street": payload.street,
    #             "phone": payload.phone,
    #             "partner_latitude": payload.latitude,
    #             "partner_longitude": payload.longitude,
    #         }
    #     )
    #     res = {
    #         "id": partner_id.name,
    #         "name": partner_id.name,
    #         "street": partner_id.street,
    #         "phone": partner_id.phone,
    #         "latitude": partner_id.partner_latitude,
    #         "longitude": partner_id.partner_longitude,
    #     }
    #     return self.env.datamodels["profile.datamodel.update"](**res)
