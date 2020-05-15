from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('management', 'Approval Management')])

    def action_management(self):
        self.state = 'sale'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for x in self.order_line:
            for y in self.pricelist_id.item_ids:
                if x.product_id.product_tmpl_id.id == y.product_tmpl_id.id and y.compute_price == 'fixed' and x.price_unit <= y.fixed_price:
                    self.state = 'management'
        return res
