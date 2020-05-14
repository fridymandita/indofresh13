from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        so_id = self.env['stock.inventory'].search([('state', '=', 'confirm')])
        if so_id:
            raise ValidationError(
                _('Sorry, Masih Ada Inventory Adjustments Yang Belum Di Validate'))

        return super(StockMove, self)._action_done(cancel_backorder)
