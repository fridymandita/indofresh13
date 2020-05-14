from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})

    def action_validate(self):
        self = self.with_context({
            'operating_unit': self.location_id.operating_unit_id.id
        })
        stock = super(StockInventory, self).action_validate()
        return stock
