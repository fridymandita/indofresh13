from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[('management', 'Approval Management')])

    def action_management(self):
        self.state = 'sale'

    def action_confirm(self):

        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write({
            'state': 'sale',
            'confirmation_date': fields.Datetime.now()
        })
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        for x in self.order_line:
            for y in self.pricelist_id.item_ids:
                if x.product_id.product_tmpl_id.id == y.product_tmpl_id.id and y.compute_price == 'fixed' and x.price_unit <= y.fixed_price:
                    self.state = 'management'
        return True
