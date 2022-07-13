from odoo.addons.base_rest.controllers import main


class OrderingAppController(main.RestController):
    _root_path = "/oa/"
    _collection_name = "orderingapp"


class SaleForceAppController(main.RestController):
    _root_path = "/sf/"
    _collection_name = "saleforce"


class ProductController(main.RestController):
    _root_path = "/prod/"
    _collection_name = "catlog"


class DeliveryController(main.RestController):
    _root_path = "/dl/"
    _collection_name = "delivery"


class Procurement(main.RestController):
    _root_path = "/c/"
    _collection_name = "collection"
