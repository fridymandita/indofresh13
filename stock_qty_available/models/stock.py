from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    
    @api.depends('quantity', 'reserved_quantity')
    def _available_quantity(self):
        for quant in self:
            quant.available_quantity = quant.quantity - quant.reserved_quantity

    available_quantity = fields.Float(
        'Available Quantity', readonly=True, compute='_available_quantity', store=True)
