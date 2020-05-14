from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_create_advance_invoice(self):
        return {
            'name': _('Create Advance Bill'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'wizard.purchase.advance',
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    def unlink(self):
        downpayment_lines = self.mapped('line_ids.purchase_line_id').filtered(
            lambda line: line.is_downpayment)
        res = super(AccountMove, self).unlink()
        if downpayment_lines:
            query = '''delete from purchase_order_line where id in (%s)'''
            self._cr.execute(query, (tuple(downpayment_lines.ids)))
            # downpayment_lines.unlink()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    is_downpayment = fields.Boolean(
        string="Is a down payment", help="Down payments are made when creating invoices from a sales order."
        " They are not copied when duplicating a sales order.")
