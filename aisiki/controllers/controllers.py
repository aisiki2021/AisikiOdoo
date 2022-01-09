# -*- coding: utf-8 -*-
# from odoo import http


# class AisikiConnector(http.Controller):
#     @http.route('/aisiki_connector/aisiki_connector/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aisiki_connector/aisiki_connector/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aisiki_connector.listing', {
#             'root': '/aisiki_connector/aisiki_connector',
#             'objects': http.request.env['aisiki_connector.aisiki_connector'].search([]),
#         })

#     @http.route('/aisiki_connector/aisiki_connector/objects/<model("aisiki_connector.aisiki_connector"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aisiki_connector.object', {
#             'object': obj
#         })
