from odoo import models, fields, _
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def api_get_location(self, location_id=False, limit=False, offset=False, order=None):
        field_list = [
            'name',
            'location_id',
            'parent_path',
        ]
        whs = self.env['stock.warehouse'].search([])
        wh_locs = {}
        for wh in whs:
            locs = [
                wh.wh_input_stock_loc_id,
                wh.wh_qc_stock_loc_id,
                wh.lot_stock_id,
                wh.wh_output_stock_loc_id,
                wh.wh_pack_stock_loc_id]
            for loc in locs:
                wh_locs[loc.parent_path] = [wh.id, wh.name]

        def get_wh_id(res):
            for parent_path, wh_id in wh_locs.items():
                if parent_path in res['parent_path']:
                    del res['parent_path']
                    return wh_id
            del res['parent_path']
            return False

        if location_id:
            result = self.browse(location_id).read(field_list)
            result[0]['warehouse_id'] = get_wh_id(result[0])
            count = 1
        else:
            search_list = []
            location_ids = self.search(
                search_list, limit=limit, offset=offset, order=order)
            result = location_ids.read(field_list)
            for res in result:
                res['warehouse_id'] = get_wh_id(res)
            count = len(result)
        return result, count


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def api_get_warehouse(self, warehouse_id=False, limit=False, offset=False, order=None):
        field_list = ['name']
        if warehouse_id:
            result = self.browse(warehouse_id).read(field_list)
            count = 1
        else:
            search_list = []
            warehouse_ids = self.search(
                search_list, limit=limit, offset=offset, order=order)
            result = warehouse_ids.read(field_list)
            count = len(result)
        return result, count


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    grade = fields.Char('Grade')
    use_date = fields.Datetime(
        'Expired Date', help='This is the date on which the goods with this Serial Number start deteriorating, without being dangerous yet.')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    grade = fields.Char('Grade')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    wms_operator = fields.Char('Operator', copy=False)
    wms_transfer_date = fields.Date('Transfer Date', copy=False)
    wms_reference = fields.Char('WMS Reference Number', copy=False)
    wms_vehicle = fields.Char('Vehicle Number', copy=False)

    def api_post_receipt(self, data):
        if data.get('purchase_id'):
            domain = [('id', '=', data['purchase_id'])]
        elif data.get('purchase'):
            domain = [('name', '=', data['purchase_id'])]
        else:
            raise UserError(_("No Purchase reference defined!"))
        purchase = self.env['purchase.order'].search(domain, limit=1)
        if not purchase:
            raise UserError(_("Purchase Order not found!"))
        picking = purchase.picking_ids.filtered(
            lambda p: p.state == 'assigned' and p.picking_type_code == 'incoming')
        if not picking:
            raise UserError(
                _("Purchase Order reception is already completed!"))
        picking.write({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('receiving'),
            'wms_vehicle': data.get('vehicle'),
        })
        for line in data.get('products', []):
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == line.get('product_id'))
            if not move:
                raise UserError(
                    _("Product already received or is not listed on purchase order"))
            move.move_line_ids.create({
                'move_id': move.id,
                'product_id': line.get('product_id'),
                'location_id': line.get('location_id'),
                'location_dest_id': picking.location_dest_id.id,
                'lot_id': self.env['stock.production.lot'].create({
                    'product_id': line.get('product_id'),
                    'name': line.get('pallet'),
                    'grade': line.get('grade'),
                    'use_date': line.get('date_expired')
                }).id,
                'product_uom_id': line.get('uom_id', move.product_uom.id),
                'product_uom_qty': line.get('qty', 0),
                'qty_done': line.get('qty', 0),
            })
        picking.move_lines.mapped('move_line_ids').filtered(
            lambda l: abs(l.qty_done) < 0.01).unlink()
        picking.action_done()
        if data.get('close_po') is True:
            picking.backorder_ids.action_cancel()
        result = {'success': True, 'ref': picking.name}
        count = 1
        return result, count

    def api_post_qc(self, data):
        result = {'success': True}
        count = 1
        return result, count

    def api_post_picking(self, data):
        if data.get('sale_id'):
            domain = [('id', '=', data['sale_id'])]
        elif data.get('sale'):
            domain = [('name', '=', data['sale'])]
        else:
            raise UserError(_("No Sale reference defined!"))
        sale = self.env['sale.order'].search(domain, limit=1)
        if not sale:
            raise UserError(_("Sale Order not found!"))
        picking = sale.picking_ids.filtered(
            lambda p: p.state != 'done' and p.picking_type_code == 'internal')
        if not picking:
            raise UserError(
                _("Sale Order Picking is already completed!"))
        picking.write({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('picking'),
            'wms_vehicle': data.get('vehicle'),
        })
        for line in data.get('products', []):
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == line.get('product_id'))
            if not move:
                raise UserError(
                    _("Product already delivered or is not listed on sale order"))
            move._do_unreserve()
            lot_id = self.env['stock.production.lot'].search([
                ('product_id', '=', line.get('product_id')),
                ('name', '=', line.get('pallet'))], limit=1).id
            if not lot_id:
                raise UserError(
                    _("Pallet number not found!"))
            move.move_line_ids.create({
                'picking_id': picking.id,
                'move_id': move.id,
                'product_id': line.get('product_id'),
                'location_id': line.get('location_id'),
                'location_dest_id': move.location_dest_id.id,
                'lot_id': lot_id,
                'product_uom_id': line.get('uom_id', move.product_uom.id),
                'qty_done': line.get('qty', 0),
            })
        picking.move_lines.mapped('move_line_ids').filtered(
            lambda l: abs(l.qty_done) < 0.01).unlink()
        picking.action_done()
        if data.get('close_so') is True:
            picking.backorder_ids.action_cancel()
        result = {'success': True, 'ref': picking.name}
        count = 1
        return result, count

    def api_post_delivery(self, data):
        if data.get('sale_id'):
            domain = [('id', '=', data['sale_id'])]
        elif data.get('sale'):
            domain = [('name', '=', data['sale'])]
        else:
            raise UserError(_("No Sale reference defined!"))
        sale = self.env['sale.order'].search(domain, limit=1)
        if not sale:
            raise UserError(_("Sale Order not found!"))
        picking = sale.picking_ids.filtered(
            lambda p: p.state != 'done' and p.picking_type_code == 'outgoing')
        if not picking:
            raise UserError(
                _("Sale Order Picking is already completed!"))
        picking.write({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('picking'),
            'wms_vehicle': data.get('vehicle'),
        })
        for line in data.get('products', []):
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == line.get('product_id'))
            if not move:
                raise UserError(
                    _("Product already delivered or is not listed on sale order"))
            lot_id = self.env['stock.production.lot'].search([
                ('product_id', '=', line.get('product_id')),
                ('name', '=', line.get('pallet'))], limit=1).id
            if not lot_id:
                raise UserError(
                    _("Pallet number not found!"))
            move.move_line_ids.create({
                'picking_id': picking.id,
                'move_id': move.id,
                'product_id': line.get('product_id'),
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
                'lot_id': lot_id,
                'product_uom_id': line.get('uom_id', move.product_uom.id),
                'qty_done': line.get('qty', 0),
            })
        picking.move_lines.mapped('move_line_ids').filtered(
            lambda l: abs(l.qty_done) < 0.01).unlink()
        picking.action_done()
        if data.get('close_so') is True:
            picking.backorder_ids.action_cancel()
        result = {'success': True, 'ref': picking.name}
        count = 1
        return result, count

    def api_post_bintransfer(self, data):
        wh = self.env['stock.warehouse'].browse(
            data.get('warehouse_id'))
        products = data.get('products', [])
        location_id = products and products[0].get('location_id')
        location_dest_id = products and products[0].get('location_dest_id')
        picking = self.create({
            'location_id': location_id,
            'location_dest_id': location_dest_id,
            'picking_type_id': wh.int_type_id.id,
            'origin': data.get('ref'),
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('ref'),
            'move_lines': [(0, 0, {
                'product_id': line.get('product_id'),
                'name': 'BINTRANSFER %s' % data.get('ref'),
                'location_id': line.get('location_id'),
                'location_dest_id': line.get('location_dest_id'),
                'product_uom': line.get('uom_id'),
                'quantity_done': line.get('qty', 0),
                'move_line_ids': [(0, 0, {
                    'product_id': line.get('product_id'),
                    'location_id': line.get('location_id'),
                    'location_dest_id': line.get('location_dest_id'),
                    'product_uom_id': line.get('uom_id'),
                    'qty_done': line.get('qty', 0),
                    'lot_id': self.env['stock.production.lot'].search([
                        ('product_id', '=', line.get('product_id')),
                        ('name', '=', line.get('pallet'))], limit=1).id
                })]
            }) for line in products],
        })
        picking.action_done()
        result = {'success': True, 'ref': picking.name}
        count = 1
        return result, count

    def api_post_opname(self, data):
        wh = self.env['stock.warehouse'].browse(
            data.get('warehouse_id'))
        vals = {
            'name': data.get('ref'),
            'accounting_date': data.get('date'),
            'filter': 'none',
            'state': 'confirm',
            'location_id': wh.lot_stock_id.id,
            'operating_unit_id': wh.operating_unit_id.id
        }
        line_vals = []
        for line in data.get('products', []):
            lot_id = self.env['stock.production.lot'].search([
                ('product_id', '=', line.get('product_id')),
                ('name', '=', line.get('pallet'))], limit=1).id
            theoretical_qty = self.env['product.product'].get_theoretical_quantity(
                line.get('product_id'),
                line.get('location_id'),
                lot_id=lot_id,
                to_uom=line.get('uom_id'),
            )
            if abs(theoretical_qty - line.get('qty_wms')) > 0.01:
                raise UserError(_("Qty in WMS is different with qty in odoo!"))
            line_vals.append((0, 0, {
                'product_id': line.get('product_id'),
                'location_id': line.get('location_id'),
                "product_qty": line.get('qty_actual'),
                "product_uom_id": line.get('uom_id'),
                "prod_lot_id": lot_id
            }))
        vals['line_ids'] = line_vals
        result = {
            'success': True,
            'ref': self.env['stock.inventory'].create(vals).name}
        count = 1
        return result, count

    def api_post_return_checking(self, data):
        picking = self.env['stock.picking'].search([
            ('name', '=', data['receiving_ref'])], limit=1)
        if picking.state != 'done':
            raise UserError(_("Receiving is not validated!"))
        picking_type_id = picking.picking_type_id.warehouse_id.pick_type_id
        products = data.get('products', [])
        location_id = products and products[0].get('location_id')
        new_picking = picking.copy({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('checking'),
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': _("Return checking of %s") % picking.name,
            'location_id': location_id,
            'location_dest_id': picking_type_id.default_location_dest_id.id})
        new_picking.message_post_with_view(
            'mail.message_origin_link',
            values={'self': new_picking,
                    'origin': picking},
            subtype_id=self.env.ref('mail.mt_note').id)

        for return_line in products:
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == return_line['product_id'])
            if not move:
                raise UserError(
                    _("Selected Receipt Reference doesn't contain product %s" %
                      self.env['product.product'].browse(return_line['product_id']).name))
            elif len(move) > 1:
                move = move[0]
            vals = {
                'product_id': return_line.get('product_id'),
                'product_uom_qty': return_line.get('qty', 0),
                'product_uom': return_line.get('uom_id'),
                'picking_id': new_picking.id,
                'date_expected': fields.Datetime.now(),
                'location_id': location_id,
                'location_dest_id': return_line.get('location_id'),
                'picking_type_id': picking_type_id.default_location_dest_id.id,
                'purchase_line_id': False,
                'warehouse_id': new_picking.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': move.id,
                'procure_method': 'make_to_stock',
                'move_line_ids': [(0, 0, {
                    'product_id': return_line.get('product_id'),
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': return_line.get('location_id'),
                    'product_uom_id': return_line.get('uom_id'),
                    'qty_done': return_line.get('qty', 0),
                    'lot_id': self.env['stock.production.lot'].search([
                        ('product_id', '=', return_line.get('product_id')),
                        ('name', '=', return_line.get('pallet'))], limit=1).id
                })]
            }
            r = move.copy(vals)
            vals = {}
            move_orig_to_link = move.move_dest_ids.mapped(
                'returned_move_ids')
            move_dest_to_link = move.move_orig_ids.mapped(
                'returned_move_ids')
            vals['move_orig_ids'] = [
                (4, m.id) for m in move_orig_to_link | move]
            vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
            r.write(vals)
        new_picking.action_done()
        result = {
            'success': True,
            'ref': new_picking.name}
        count = 1
        return result, count

    def api_post_return_loading(self, data):
        picking = self.env['stock.picking'].search([
            ('name', '=', data['receiving_ref'])], limit=1)
        if picking.state != 'done':
            raise UserError(_("Receiving is not validated!"))
        picking_type_id = picking.picking_type_id.return_picking_type_id
        check_picking_type_id = picking.picking_type_id.warehouse_id.pick_type_id
        products = data.get('products', [])
        new_picking = picking.copy({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('checking'),
            'move_lines': [],
            'picking_type_id': picking_type_id.id,
            'state': 'draft',
            'origin': _("Return of %s") % picking.name,
            'location_id': check_picking_type_id.default_location_dest_id.id,
            'location_dest_id': picking.location_id.id})
        new_picking.message_post_with_view(
            'mail.message_origin_link',
            values={'self': new_picking,
                    'origin': picking},
            subtype_id=self.env.ref('mail.mt_note').id)

        for return_line in products:
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == return_line['product_id'])
            if not move:
                raise UserError(
                    _("Selected Receipt Reference doesn't contain product %s" %
                      self.env['product.product'].browse(return_line['product_id']).name))
            elif len(move) > 1:
                move = move[0]
            vals = {
                'product_id': return_line.get('product_id'),
                'product_uom_qty': return_line.get('qty', 0),
                'product_uom': return_line.get('uom_id'),
                'picking_id': new_picking.id,
                'date_expected': fields.Datetime.now(),
                'location_id': check_picking_type_id.default_location_dest_id.id,
                'location_dest_id': picking.location_id.id,
                'picking_type_id': picking_type_id.default_location_dest_id.id,
                'purchase_line_id': False,
                'warehouse_id': new_picking.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': move.id,
                'procure_method': 'make_to_stock',
                'move_line_ids': [(0, 0, {
                    'product_id': return_line.get('product_id'),
                    'location_id': check_picking_type_id.default_location_dest_id.id,
                    'location_dest_id': picking.location_id.id,
                    'product_uom_id': return_line.get('uom_id'),
                    'qty_done': return_line.get('qty', 0),
                    'lot_id': self.env['stock.production.lot'].search([
                        ('product_id', '=', return_line.get('product_id')),
                        ('name', '=', return_line.get('pallet'))], limit=1).id
                })]
            }
            r = move.copy(vals)
            vals = {}
            move_orig_to_link = move.move_dest_ids.mapped(
                'returned_move_ids')
            move_dest_to_link = move.move_orig_ids.mapped(
                'returned_move_ids')
            vals['move_orig_ids'] = [
                (4, m.id) for m in move_orig_to_link | move]
            vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
            r.write(vals)
        new_picking.action_done()
        result = {
            'success': True,
            'ref': new_picking.name}
        count = 1
        return result, count

    def api_post_return_receipt(self, data):
        picking = self.env['stock.picking'].search([
            ('name', '=', data['delivery_ref'])], limit=1)
        if picking.state != 'done':
            raise UserError(_("Delivery Order is not validated!"))
        picking_type_id = picking.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        products = data.get('products', [])
        location_id = products and products[0].get('location_id')
        new_picking = picking.copy({
            'wms_operator': data.get('operator'),
            'wms_transfer_date': data.get('date'),
            'wms_reference': data.get('receiving'),
            'wms_vehicle': data.get('vehicle'),
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s") % picking.name,
            'location_id': picking.location_dest_id.id,
            'location_dest_id': location_id
        })

        new_picking.message_post_with_view(
            'mail.message_origin_link',
            values={'self': new_picking,
                    'origin': picking},
            subtype_id=self.env.ref('mail.mt_note').id)

        for return_line in products:
            move = picking.move_lines.filtered(
                lambda m: m.product_id.id == return_line['product_id'])
            if not move:
                raise UserError(
                    _("Selected Delivery Reference doesn't contain product %s" %
                      self.env['product.product'].browse(return_line['product_id']).name))
            elif len(move) > 1:
                move = move[0]
            vals = {
                'product_id': return_line.get('product_id'),
                'product_uom_qty': return_line.get('qty', 0),
                'product_uom': return_line.get('uom_id'),
                'picking_id': new_picking.id,
                'date_expected': fields.Datetime.now(),
                'location_id': move.location_dest_id.id,
                'location_dest_id': return_line.get('location_id'),
                'picking_type_id': new_picking.picking_type_id.id,
                'warehouse_id': new_picking.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': move.id,
                'procure_method': 'make_to_stock',
                'move_line_ids': [(0, 0, {
                    'product_id': return_line.get('product_id'),
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': return_line.get('location_id'),
                    'product_uom_id': return_line.get('uom_id'),
                    'qty_done': return_line.get('qty', 0),
                    'lot_id': self.env['stock.production.lot'].search([
                        ('product_id', '=', return_line.get('product_id')),
                        ('name', '=', return_line.get('pallet'))], limit=1).id
                })]

            }
            r = move.copy(vals)
            vals = {}
            move_orig_to_link = move.move_dest_ids.mapped(
                'returned_move_ids')
            move_dest_to_link = move.move_orig_ids.mapped(
                'returned_move_ids')
            vals['move_orig_ids'] = [
                (4, m.id) for m in move_orig_to_link | move]
            vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
            r.write(vals)
        new_picking.action_done()

        result = {
            'success': True,
            'ref': new_picking.name}
        count = 1
        return result, count
