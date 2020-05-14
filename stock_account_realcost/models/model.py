from odoo import models, fields, tools, api
from odoo.tools.float_utils import float_is_zero
from odoo.addons.stock_account.models.stock_move_line import StockMoveLine as StockMoveLineOriginal


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number', readonly=True, check_company=True)
    stock_move_line_id = fields.Many2one(
        'stock.move.line', 'Stock Move Line', readonly=True, check_company=True)

    def init(self):
        tools.create_index(
            self._cr, 'stock_valuation_layer_index',
            self._table, [
                'product_id', 'remaining_qty',
                'stock_move_id', 'stock_move_line_id',
                'lot_id', 'company_id', 'create_date']
        )


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_in_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_in_move_lines()
            unit_cost = abs(move._get_price_unit())
            if move.product_id.cost_method == 'standard':
                unit_cost = move.product_id.standard_price
            if forced_quantity:
                # TODO: add lot_id
                svl_vals = move.product_id._prepare_in_svl_vals(
                    forced_quantity, unit_cost)
                svl_vals.update(move._prepare_common_svl_vals())
                svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
                svl_vals.update({
                    'stock_move_line_id': self._context.get('forced_move_line').id,
                    'lot_id': self._context.get('forced_move_line').lot_id.id,
                })
                svl_vals_list.append(svl_vals)
            else:
                for valued_move_line in valued_move_lines:
                    valued_quantity = valued_move_line.product_uom_id._compute_quantity(
                        valued_move_line.qty_done, move.product_id.uom_id)
                    # May be negative (i.e. decrease an out move).
                    if float_is_zero(valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                        continue
                    svl_vals = move.product_id._prepare_in_svl_vals(
                        valued_quantity, unit_cost)
                    svl_vals.update(move._prepare_common_svl_vals())
                    svl_vals.update({
                        'stock_move_line_id': valued_move_line.id,
                        'lot_id': valued_move_line.lot_id.id,
                    })
                    svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_context(force_company=move.company_id.id)
            valued_move_lines = move._get_out_move_lines()
            if forced_quantity:
                # TODO: add lot_id
                context_fifo_lot = dict(
                    valued_lot_id=self._context.get('forced_move_line').lot_id.id) if move.product_id.is_fifo_per_lot() else {}
                svl_vals = move.product_id.with_context(context_fifo_lot)._prepare_out_svl_vals(
                    forced_quantity, move.company_id)
                svl_vals.update(move._prepare_common_svl_vals())
                svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
                svl_vals.update({
                    'stock_move_line_id': self._context.get('forced_move_line').id,
                    'lot_id': self._context.get('forced_move_line').lot_id.id,
                })
                svl_vals_list.append(svl_vals)
            else:
                for valued_move_line in valued_move_lines:
                    valued_quantity = valued_move_line.product_uom_id._compute_quantity(
                        valued_move_line.qty_done, move.product_id.uom_id)
                    if float_is_zero(valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                        continue
                    context_fifo_lot = dict(
                        valued_lot_id=valued_move_line.lot_id.id) if move.product_id.is_fifo_per_lot() else {}
                    svl_vals = move.product_id.with_context(context_fifo_lot)._prepare_out_svl_vals(
                        valued_quantity, move.company_id)
                    svl_vals.update(move._prepare_common_svl_vals())
                    svl_vals.update({
                        'stock_move_line_id': valued_move_line.id,
                        'lot_id': valued_move_line.lot_id.id,
                    })
                    svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_fifo_per_lot = fields.Boolean('Is Real Cost', default=False)

    @api.onchange('property_cost_method')
    def onchange_property_cost_method(self):
        self.is_fifo_per_lot = False


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def is_fifo_per_lot(self):
        return self.categ_id.is_fifo_per_lot

    def _run_fifo(self, quantity, company):
        self.ensure_one()

        # Find back incoming stock valuation layers (called candidates here) to
        # value `quantity`.
        qty_to_take_on_candidates = quantity
        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        candidates = self.env['stock.valuation.layer'].sudo(
        ).with_context(active_test=False).search([
            ('product_id', '=', self.id),
            ('remaining_qty', '>', 0),
            ('company_id', '=', company.id),
            ('lot_id', '=', self._context.get('valued_lot_id', False))
        ])
        for candidate in candidates:
            qty_taken_on_candidate = min(
                qty_to_take_on_candidates, candidate.remaining_qty)

            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            new_standard_price = candidate_unit_cost
            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
            value_taken_on_candidate = candidate.currency_id.round(
                value_taken_on_candidate)
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate

            candidate_vals = {
                'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                'remaining_value': new_remaining_value,
            }

            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
                break

        if not float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
            candidates = self.env['stock.valuation.layer'].sudo(
            ).with_context(active_test=False).search([
                ('product_id', '=', self.id),
                ('remaining_qty', '>', 0),
                ('company_id', '=', company.id),
                ('lot_id', '=', False)
            ])
            for candidate in candidates:
                qty_taken_on_candidate = min(
                    qty_to_take_on_candidates, candidate.remaining_qty)

                candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
                new_standard_price = candidate_unit_cost
                value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
                value_taken_on_candidate = candidate.currency_id.round(
                    value_taken_on_candidate)
                new_remaining_value = candidate.remaining_value - value_taken_on_candidate

                candidate_vals = {
                    'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                    'remaining_value': new_remaining_value,
                }

                candidate.write(candidate_vals)

                qty_to_take_on_candidates -= qty_taken_on_candidate
                tmp_value += value_taken_on_candidate
                if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
                    break

        # Update the standard price with the price of the last used candidate,
        # if any.
        if new_standard_price and self.cost_method == 'fifo':
            self.sudo().with_context(force_company=company.id).standard_price = new_standard_price

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is
        # called.
        vals = {}
        if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
            vals = {
                'value': -tmp_value,
                'unit_cost': tmp_value / quantity,
            }
        else:
            assert qty_to_take_on_candidates > 0
            last_fifo_price = new_standard_price or self.standard_price
            negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                'remaining_qty': -qty_to_take_on_candidates,
                'value': -tmp_value,
                'unit_cost': last_fifo_price,
            }
        return vals


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        move_lines = super(StockMoveLineOriginal, self).create(vals_list)
        for move_line in move_lines:
            if move_line.state != 'done':
                continue
            move = move_line.move_id
            rounding = move.product_id.uom_id.rounding
            diff = move_line.qty_done
            if float_is_zero(diff, precision_rounding=rounding):
                continue
            move_line._create_correction_svl(move, diff)
        return move_lines

    def write(self, vals):
        if 'qty_done' in vals:
            for move_line in self:
                if move_line.state != 'done':
                    continue
                move = move_line.move_id
                rounding = move.product_id.uom_id.rounding
                diff = vals['qty_done'] - move_line.qty_done
                if float_is_zero(diff, precision_rounding=rounding):
                    continue
                move_line._create_correction_svl(move, diff)
        return super(StockMoveLineOriginal, self).write(vals)

    # -------------------------------------------------------------------------
    # SVL creation helpers
    # -------------------------------------------------------------------------
    def _create_correction_svl(self, move, diff):
        stock_valuation_layers = self.env['stock.valuation.layer']
        if move._is_in() and diff > 0 or move._is_out() and diff < 0:
            move.product_price_update_before_done(forced_qty=diff)
            stock_valuation_layers |= move.with_context(forced_move_line=self)._create_in_svl(
                forced_quantity=abs(diff))
            if move.product_id.cost_method in ('average', 'fifo'):
                move.product_id._run_fifo_vacuum(move.company_id)
        elif move._is_in() and diff < 0 or move._is_out() and diff > 0:
            stock_valuation_layers |= move.with_context(forced_move_line=self)._create_out_svl(
                forced_quantity=abs(diff))
        elif move._is_dropshipped() and diff > 0 or move._is_dropshipped_returned() and diff < 0:
            stock_valuation_layers |= move._create_dropshipped_svl(
                forced_quantity=abs(diff))
        elif move._is_dropshipped() and diff < 0 or move._is_dropshipped_returned() and diff > 0:
            stock_valuation_layers |= move._create_dropshipped_returned_svl(
                forced_quantity=abs(diff))

        for svl in stock_valuation_layers:
            if not svl.product_id.valuation == 'real_time':
                continue
            svl.stock_move_id._account_entry_move(
                svl.quantity, svl.description, svl.id, svl.value)
