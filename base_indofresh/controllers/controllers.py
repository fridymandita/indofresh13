# -*- coding: utf-8 -*-
# from odoo import http


# class BaseIndofresh(http.Controller):
#     @http.route('/base_indofresh/base_indofresh/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_indofresh/base_indofresh/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_indofresh.listing', {
#             'root': '/base_indofresh/base_indofresh',
#             'objects': http.request.env['base_indofresh.base_indofresh'].search([]),
#         })

#     @http.route('/base_indofresh/base_indofresh/objects/<model("base_indofresh.base_indofresh"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_indofresh.object', {
#             'object': obj
#         })
