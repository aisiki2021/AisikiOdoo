from odoo.addons.component.core import Component


class PingService(Component):
    _inherit = "base.rest.service"
    _name = "ping.service"
    _usage = "ping"
    _collection = "aisiki.authentication"

    # The following method are 'public' and can be called from the controller..
    def get(self, _id, message):
        return {"response": "Get called with message " + message}

    def search(self, message):
        return {"response": "Search called search with message " + message}

    def update(self, _id, message):
        return {"response": "PUT called with message " + message}

    # pylint:disable=method-required-super
    def create(self, **params):
        return {"response": "POST called with message " + params["message"]}

    def delete(self, _id):
        return {"response": "DELETE called with id %s " % _id}

    # Validator
    def _validator_search(self):
        return {"message": {"type": "string"}}

    # Validator
    def _validator_get(self):
        # no parameters by default
        return {}

    def _validator_update(self):
        return {"message": {"type": "string"}}

    def _validator_create(self):
        return {"message": {"type": "string"}}
