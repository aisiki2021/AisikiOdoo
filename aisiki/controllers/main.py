from odoo.addons.base_rest.controllers import main


class AuthenticateController(main.RestController):
    _root_path = "/auth/"
    _collection_name = "aisiki.authenticate"


class ProcurementController(main.RestController):
    _root_path = "/procurement/"
    _collection_name = "procurement"
