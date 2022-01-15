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

    # @restapi.method(
    #     [(["/logout"], "POST")], auth="user",
    # )
    # def logout(self):
    #     request.session.logout(keep_db=True)
    #     return {"message": "Successful logout"}

    @restapi.method(
        [(["/changepassword"], "POST")], auth="user", input_param=Datamodel("changepassword.datamodel"),
    )
    def changepassword(self, payload):
        print(request.httprequest.headers, '!!!!!!!!!!!!!!', payload)
        return {"message": "Successful logout"}


    # def to_openapi(self, **params):
    #     """
    #     Return the description of this REST service as an OpenAPI json document
    #     :return: json document
    #     """
    #     api_spec = super(SessionAuthenticationService, self).to_openapi(**params)
    #     api_spec.update({
    #             "components":
    #                 {
    #                     "securitySchemes": {
    #                         "BearerAuth": {
    #                             "type": "http",
    #                             "scheme": "bearer",
    #                             "bearerFormat": "JWT"
    #                         },
    #                         "ApiKeyAuth": {
    #                             "type": "apiKey",
    #                             "in": "header",
    #                             "name": "api_key",
    #                         }
    #                     }
    #                 },
    #             "security": [{
    #                 "BearerAuth": [],
    #                 "ApiKeyAuth": []
    #             }]
    #         })
              
    #     print('!!!!!!!!!!!!!!!!!!!!11', api_spec)
    #     return api_spec
