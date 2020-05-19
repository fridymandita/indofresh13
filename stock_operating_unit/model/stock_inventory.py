from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',
        required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.default_operating_unit_id)

    def action_validate(self):
        return super(StockInventory, self.with_context(
            operating_unit=self.operating_unit_id.id)).action_validate()
