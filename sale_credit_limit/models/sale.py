from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        invs = self.env['account.move'].search([
            ('partner_id', '=', self.partner_id.id),
            ('type', '=', 'out_invoice'),
        ])
        if not invs:
            return super(SaleOrder, self).action_confirm()
        total_credit = sum(inv.amount_total for inv in invs) + \
            self.amount_total
        if self.partner_id.credit_limit > 0 and total_credit > self.partner_id.credit_limit:
            raise UserError(_('This customer has excess it credit limit!'))
        for inv in invs:
            if inv.invoice_date_due < fields.Date.today():
                raise UserError(
                    _('This customer has overdue invoice! (%s)' % inv.name))
        return super(SaleOrder, self).action_confirm()
