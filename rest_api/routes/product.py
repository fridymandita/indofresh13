import json

from odoo import http, _
from odoo.http import request, route

from ..jwt.login import token_required


class ApiProduct(http.Controller):
    @route(route=['/api/v1/product',
                  '/api/v1/product/<int:product_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_product(self, product_id=False, debug=False, **kwargs):
        if product_id:
            product = request.env['product.product'].sudo(
            ).api_get_product(product_id)
            return {'result': product}
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        product = request.env['product.product'].sudo().api_get_product(
            limit=limit, offset=offset, order=order)
        return {'result': product}


class ApiProductCategory(http.Controller):

    @route('/api/v1/product_category',
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_category(self, debug=False, **kwargs):
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        category = request.env['product.category'].sudo().api_get_category(
            limit=limit, offset=offset, order=order)
        return {'result': category}
