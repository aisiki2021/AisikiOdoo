from odoo.addons.base_rest.controllers import main


# class AuthenticateController(main.RestController):
#     _root_path = "/auth/"
#     _collection_name = "aisiki.authenticate"


class OrderingAppController(main.RestController):
    _root_path = "/oa/"
    _collection_name = "orderingapp"
