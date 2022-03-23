import datetime
import json
from odoo import fields
from odoo.http import db_monodb, request, root
from odoo.service import security

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

from odoo.addons.base_rest_datamodel.restapi import Datamodel


import pyotp

secret = "JBSWY3DPEHPK3PXP"
totp = pyotp.TOTP(secret, interval=900)


def _rotate_session(httprequest):
    if httprequest.session.rotate:
        root.session_store.delete(httprequest.session)
        httprequest.session.sid = root.session_store.generate_key()
        if httprequest.session.uid:
            httprequest.session.session_token = security.compute_session_token(httprequest.session, request.env)
        httprequest.session.modified = True


class AisikiBaseRest(Component):
    _inherit = "base.rest.service"
    _name = "aisiki.base.rest"
    _usage = "aisiki.base.rest"
    _collection = "aisiki.base.rest"

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
            uid = request.session.authenticate(db_name, params["phone"], params["password"])
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
        user = request.env["res.users"].with_user(1).search([("login", "=", phone)], limit=1)
        if not user:
            data = json.dumps({"error": "phone number not found"})
            resp = request.make_response(data)
            resp.status_code = 400
            return resp

        sms = (
            request.env["sms.sms"]
            .with_user(1)
            .create({"body": "Your Aisiki verification code is %s." % (totp.now(),), "number": phone,})
            .aisiki_send()
        )
        return sms.get("response", [])

    @restapi.method(
        [(["/otpverify"], "POST")], auth="public", input_param=Datamodel("otp.datamodel.in"), tags=["Authentication"],
    )
    def otpverify(self, payload):
        try:
            phone = payload.phone.strip()
            otp = payload.otp.strip()
            user = request.env["res.users"].with_user(1).search([("login", "=", phone)], limit=1)
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
        user = request.env["res.users"].with_user(1).search([("login", "=", phone)], limit=1)
        user.action_reset_password()
        return self.env.datamodels["forgotpassword.datamodel.out"](password_reset_url=user.password_reset_url)

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
                "message": "Password Successful changed" if res else "Something went wrong",
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
        res = json.dumps(res)
        resp = request.make_response(res)
        resp.status_code = 200
        return resp

    @restapi.method(
        [(["/updateprofile"], "PUT")],
        auth="user",
        input_param=Datamodel("profile.datamodel.update"),
        tags=["Authentication"],
    )
    def updateprofile(self, payload):
        partner_id = request.env.user.partner_id
        partner_id.write(
            {
                "name": payload.name if payload.name else partner_id.name,
                "street": payload.street if payload.street else partner_id.street,
                "phone": payload.phone if payload.phone else partner_id.phone,
                "partner_latitude": payload.latitude if payload.latitude else partner_id.partner_latitude,
                "partner_longitude": payload.longitude if payload.longitude else partner_id.partner_longitude,
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

        resp = request.make_response(json.dumps(res))
        resp.status_code = 200
        return resp
