from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if isinstance(res, dict) and res.get('domain'):
            res['domain']['product_uom'] = [
                ('product_id', '=', self.product_id.id)]
        return res
