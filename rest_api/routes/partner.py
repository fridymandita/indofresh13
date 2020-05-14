from odoo import http
from odoo.http import request, route

from ..jwt.login import token_required


class ApiPartner(http.Controller):

    @route(route=['/api/v1/customer/',
                  '/api/v1/customer/<int:partner_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_customer(self, partner_id=False, debug=False, **kwargs):
        if partner_id:
            partner = request.env['res.partner'].sudo(
            ).api_get_partner(partner_id)
            return {'result': partner}
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        partner = request.env['res.partner'].sudo().api_get_partner(
            partner_type='customer', limit=limit, offset=offset, order=order)
        return {'result': partner}

    @route(route=['/api/v1/vendor/',
                  '/api/v1/vendor/<int:partner_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_vendor(self, partner_id=False, debug=False, **kwargs):
        if partner_id:
            partner = request.env['res.partner'].sudo(
            ).api_get_partner(partner_id)
            return {'result': partner}
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        partner = request.env['res.partner'].sudo().api_get_partner(
            partner_type='supplier', limit=limit, offset=offset, order=order)
        return {'result': partner}
