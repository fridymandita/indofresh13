from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id:
            unit = self.location_id.operating_unit_id
            self.operating_unit_id = unit

    def action_validate(self):
        self = self.with_context(
            operating_unit=self.location_id.operating_unit_id.id)
        stock = super(StockScrap, self).action_validate()
        return stock
