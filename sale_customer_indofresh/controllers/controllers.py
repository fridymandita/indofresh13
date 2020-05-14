# -*- coding: utf-8 -*-
from odoo import http

# class SaleCustomerIndofresh(http.Controller):
#     @http.route('/sale_customer_indofresh/sale_customer_indofresh/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_customer_indofresh/sale_customer_indofresh/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_customer_indofresh.listing', {
#             'root': '/sale_customer_indofresh/sale_customer_indofresh',
#             'objects': http.request.env['sale_customer_indofresh.sale_customer_indofresh'].search([]),
#         })

#     @http.route('/sale_customer_indofresh/sale_customer_indofresh/objects/<model("sale_customer_indofresh.sale_customer_indofresh"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_customer_indofresh.object', {
#             'object': obj
#         })