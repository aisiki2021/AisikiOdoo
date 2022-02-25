import datetime
import json
from odoo import fields
from odoo.http import db_monodb, request, root
from odoo.service import security

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component

from odoo.addons.base_rest_datamodel.restapi import Datamodel


def _rotate_session(httprequest):
    if httprequest.session.rotate:
        root.session_store.delete(httprequest.session)
        httprequest.session.sid = root.session_store.generate_key()
        if httprequest.session.uid:
            httprequest.session.session_token = security.compute_session_token(
                httprequest.session, request.env
            )
        httprequest.session.modified = True


class SessionAuthenticationService(Component):
    _inherit = "base.rest.service"
    _name = "aisiki.authenticate.service"
    _usage = "auth"
    _collection = "aisiki.authenticate"

    @restapi.method(
        [(["/login"], "POST")], auth="public", input_param=Datamodel("login.datamodel")
    )
    def authenticate(self, body):
        """Authentication.

        To authenticate you need to :code:`POST` a request on :code:[ODOO HOST]/auth/login
        """
        params = request.params
        db_name = params.get("db", db_monodb())
        request.session.authenticate(db_name, params["login"], params["password"])
        result = request.env["ir.http"].session_info()
        _rotate_session(request)
        request.session.rotate = False
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=90)
        result["session"] = {
            "sid": request.session.sid,
            "expires_at": fields.Datetime.to_string(expiration),
        }
        return result

    @restapi.method(
        [(["/logout"], "POST")], auth="user",
    )
    def logout(self):
        request.session.logout(keep_db=True)
        return {"message": "Successful logout"}

    @restapi.method(
        [(["/get_change_password"], "GET")],
        auth="public",
        input_param=Datamodel("get.password.datamodel"),
        output_param=Datamodel("getout.password.datamodel"),
    )
    def get_change_password(self, payload):
        """Send change password email to the customer"""
        email = payload.email
        response = self.env.datamodels["getout.password.datamodel"]
        response = response()
        user = (
            request.env["res.users"]
            .with_user(1)
            .search([("login", "=", email.strip())], limit=1)
        )
        response.password_reset_url = user.password_reset_url
        response.email = request.env.user.email or request.env.user.login

        return response

    @restapi.method(
        [(["/change_password"], "POST")],
        auth="user",
        input_param=Datamodel("input.password.datamodel"),
    )
    def post_change_password(self, payload):
        """This is call to force password reset without token verification."""
        old_passwd = payload.old_passwd
        new_passwd = payload.new_passwd
        res = request.env.user.change_password(old_passwd, new_passwd)
        return {
            "message": "Password Successful changed" if res else "Something went wrong",
            "old_passwd": old_passwd,
            "new_passwd": new_passwd,
        }
