from odoo import http
from odoo.http import request, route

from ..jwt.login import token_required


class ApiProductCategory(http.Controller):

    @route('/api/v2/product/category', methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_category(self, debug=False, **kwargs):
        categories = request.env['product.category'].sudo(
            kwargs.get('uid', 1)).api_get_category()
        if not bool(categories):
            return {'result': categories, 'code': 204}
        return {'result': categories, 'code': 201}
