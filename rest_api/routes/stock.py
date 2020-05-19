from odoo import http, _
from odoo.http import request, route

from ..jwt.login import token_required


class ApiLocation(http.Controller):
    @route(route=['/api/v1/location',
                  '/api/v1/location/<int:location_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_location(self, location_id=False, debug=False, **kwargs):
        if location_id:
            location = request.env['stock.location'].sudo(
            ).api_get_location(location_id)
            return {'result': location}
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        location = request.env['stock.location'].sudo().api_get_location(
            limit=limit, offset=offset, order=order)
        return {'result': location}


class ApiWarehouse(http.Controller):
    @route(route=['/api/v1/warehouse',
                  '/api/v1/warehouse/<int:warehouse_id>'],
           methods=['GET'], type='json', auth='public', csrf=False)
    @token_required()
    def get_warehouse(self, warehouse_id=False, debug=False, **kwargs):
        if warehouse_id:
            warehouse = request.env['stock.warehouse'].sudo(
            ).api_get_warehouse(warehouse_id)
            return {'result': warehouse}
        arguments = request.httprequest.args
        limit = arguments.get('limit', '')
        offset = arguments.get('offset', False)
        order = arguments.get('order')
        if limit:
            limit = int(limit)
        if offset:
            offset = int(offset)
        warehouse = request.env['stock.warehouse'].sudo().api_get_warehouse(
            limit=limit, offset=offset, order=order)
        return {'result': warehouse}


class ApiPicking(http.Controller):

    @route('/api/v1/receipt',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def receipt(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_receipt(
                request.jsonrequest)
        }

    @route('/api/v1/qc',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def qc(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_qc(
                request.jsonrequest)
        }

    @route('/api/v1/picking',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def picking(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_picking(
                request.jsonrequest)
        }

    @route('/api/v1/delivery',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def delivery(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_delivery(
                request.jsonrequest)
        }

    @route('/api/v1/bintransfer',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def bintransfer(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_bintransfer(
                request.jsonrequest)
        }

    @route('/api/v1/opname',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def opname(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_opname(
                request.jsonrequest)
        }

    @route('/api/v1/return/checking',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def return_checking(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_return_checking(
                request.jsonrequest)
        }

    @route('/api/v1/return/loading',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def return_loading(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_return_loading(
                request.jsonrequest)
        }

    @route('/api/v1/return/receipt',
           methods=['POST'], type='json', auth='public', csrf=False)
    @token_required()
    def return_receipt(self, debug=False, **kwargs):
        return {
            'result': request.env['stock.picking'].sudo().api_post_return_receipt(
                request.jsonrequest)
        }
