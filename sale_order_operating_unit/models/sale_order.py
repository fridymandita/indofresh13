from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def _get_default_picking_type(self):
    #     # res = super(SaleOrder, self)._default_picking_type()
    #     type_obj = self.env['stock.picking.type']
    #     operating_unit = self.env['res.users'].operating_unit_default_get(
    #         self.env.uid
    #     )
    #     types = type_obj.search([('code', '=', 'incoming'),
    #                              ('warehouse_id.operating_unit_id', '=',
    #                               operating_unit.id)])
        
    #     return types[:1].id
        # return

    READONLY_STATES = {
        'sale': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        states=READONLY_STATES,
        required=True,
        default=lambda self: (self.env['res.users'].
                              operating_unit_default_get(self.env.uid))
    )    

    # picking_type_id = fields.Many2one(
    #     comodel_name='stock.picking.type',
    #     string='Deliver To',
    #     help="This will determine picking type of incoming shipment",
    #     required=True,
    #     states={'confirmed': [('readonly', True)],
    #             'approved': [('readonly', True)],
    #             'done': [('readonly', True)]},
    #     default=lambda self: self._get_default_picking_type(),
    # )

    # @api.constrains('operating_unit_id', 'picking_type_id')
    # def _check_warehouse_operating_unit(self):
    #     for record in self:
    #         picking_type = record.picking_type_id
    #         if not record.picking_type_id:
    #             continue
    #         warehouse = picking_type.warehouse_id
    #         if (picking_type.warehouse_id and
    #                 picking_type.warehouse_id.operating_unit_id and
    #                 record.operating_unit_id and
    #                 warehouse.operating_unit_id != record.operating_unit_id):
    #             raise ValidationError(
    #                 _('Configuration error. The Quotation / Sale Order '
    #                   'and the Warehouse of picking type must belong to the '
    #                   'same Operating Unit.')
    #             )

    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        for record in self:
            if (record.company_id and record.operating_unit_id and
                    record.company_id != record.operating_unit_id.company_id):
                raise ValidationError(
                    _('Configuration error. The Company in the Sale Order '
                      'and in the Operating Unit must be the same.')
                )

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        type_obj = self.env['stock.picking.type']
        if self.operating_unit_id:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id.operating_unit_id', '=',
                                      self.operating_unit_id.id)])
            if types:
                self.picking_type_id = types[:1]
            else:
                raise UserError(
                    _("No Warehouse found with the Operating Unit indicated "
                      "in the Sale Order")
                )

    @api.model
    def _prepare_procurement_values(self):
        picking_vals = super(SaleOrder, self)._prepare_invoice()
        picking_vals['operating_unit_id'] = self.operating_unit_id.id
        return picking_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    operating_unit_id = fields.Many2one(related='order_id.operating_unit_id',
                                        string='Operating Unit')
