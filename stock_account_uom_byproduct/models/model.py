from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        if isinstance(res, dict) and res.get('domain'):
            res['domain']['uom_id'] = [
                ('product_id', '=', self.product_id.id)]
        return res
