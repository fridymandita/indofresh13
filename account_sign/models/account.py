# from datetime import date
# from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
# from odoo.exceptions import UserError
# from odoo.tools.safe_eval import safe_eval as eval
# from odoo.tools.translate import _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    default_debitcredit = fields.Selection([('debit', 'Debit'),
                                            ('credit', 'Credit')], string='Default Debit/Credit', store=True,
                                           compute='_set_account_debitcredit')

    @api.depends('user_type_id.include_initial_balance')
    def _set_account_debitcredit(self):
        for account in self:
            if account.user_type_id.include_initial_balance:
                account.default_debitcredit = 'debit'
            else:
                account.default_debitcredit = 'credit'


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    default_debitcredit = fields.Selection([('debit', 'Debit'),
                                            ('credit', 'Credit')], related='account_id.default_debitcredit', store=True,
                                           readonly=True)
    balance_sign = fields.Monetary(
        compute='_store_balance_sign', store=True, currency_field='company_currency_id')

    @api.depends('debit', 'credit', 'default_debitcredit')
    def _store_balance_sign(self):
        for line in self:
            if line.default_debitcredit == 'debit':
                line.balance_sign = line.debit - line.credit
            else:
                line.balance_sign = line.credit - line.debit
