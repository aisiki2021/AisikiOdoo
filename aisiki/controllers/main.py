from odoo.addons.base_rest.controllers import main


class AuthenticateController(main.RestController):
    _root_path = "/aisiki/"
    _collection_name = "aisiki.authenticate"


# class SessionRestController(main.RestController):
#     _root_path = "/aisiki/"
#     _collection_name = "aisiki.authenticate"
