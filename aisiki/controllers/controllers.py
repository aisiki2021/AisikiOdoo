from odoo.addons.base_rest.controllers import main


class MyRestController(main.RestController):
    _root_path = "/aisiki/"
    _collection_name = "aisiki.authentication"
