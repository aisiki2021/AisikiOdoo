import datetime

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
            httprequest.session.session_token = security.compute_session_token(httprequest.session, request.env)
        httprequest.session.modified = True


class SessionAuthenticationService(Component):
    _inherit = "base.rest.service"
    _name = "aisiki.authenticate.service"
    _usage = "authentication"
    _collection = "aisiki.authenticate"

    @restapi.method(
        [(["/login"], "POST")], auth="public", input_param=Datamodel("login.datamodel"),
    )
    def authenticate(self, body):
        params = request.params
        db_name = params.get("db", db_monodb())
        request.session.authenticate(db_name, params["login"], params["password"])
        result = request.env["ir.http"].session_info()
        # avoid to rotate the session outside of the scope of this method
        # to ensure that the session ID does not change after this method
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

    @restapi.method([(["/get_change_password"], "GET")], auth="user")
    def get_change_password(self):
        """Send change password email to the customer"""
        request.env.user.action_reset_password()
        return {
            "message": "Password reset link has been sent your email",
            "email": request.env.user.email or request.env.user.login,
        }

    @restapi.method(
        [(["/post_change_password"], "POST")], auth="user", input_param=Datamodel("change.password.datamodel")
    )
    def post_change_password(self, payload):
        """This is call to force password reset without token verification"""
        old_passwd = payload.old_passwd
        new_passwd = payload.new_passwd
        return request.env.user.change_password(old_passwd, new_passwd)
        return {"message": "Successful logout"}
