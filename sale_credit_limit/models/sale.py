from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_limit_approval = fields.Boolean(
        'Waiting Approval Credit Limit')

    def action_confirm(self):
        if self._context.get('approve_credit_limit'):
            return super(SaleOrder, self).action_confirm()
        invs = self.env['account.move'].search([
            ('commercial_partner_id', '=', self.partner_id.id),
            ('type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_payment_state', '=', 'not_paid')
        ])
        total_credit = sum(inv.amount_total for inv in invs) + \
            self.amount_total
        if self.partner_id.credit_limit > 0 and total_credit > self.partner_id.credit_limit:
            raise UserError(_('This customer has excess it credit limit!'))
        for inv in invs:
            if inv.date_maturity < fields.Date.today():
                raise UserError(
                    _('This customer has overdue invoice! (%s)' % inv.move_name))
        return super(SaleOrder, self).action_confirm()

    def action_credit_limit_approval(self):
        self.write({'credit_limit_approval': True})

    def action_credit_limit_approve(self):
        self.write({'credit_limit_approval': False})
        self.with_context(approve_credit_limit=True).action_confirm()
