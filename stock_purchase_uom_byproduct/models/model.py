from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if isinstance(res, dict) and res.get('domain'):
            res['domain']['product_uom'] = [
                ('product_id', '=', self.product_id.id)]
        return res
