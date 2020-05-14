# © 2019 Eficent Business and IT Consulting Services S.L.
# © 2019 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        'Requesting Operating Unit',
        readonly=True,
        states={'draft': [('readonly', False)]})    

    source_operating_unit = fields.Many2one(
        'operating.unit', 'Source Unit')
    
    dest_operating_unit = fields.Many2one('operating.unit', 'Destination Unit')

    antar_cabang = fields.Boolean(string='Antar Cabang', related='picking_type_id.antar_cabang')
 
    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        res = super(StockPicking, self).onchange_picking_type()
        if self.picking_type_id:
            unit = self.picking_type_id.warehouse_id.operating_unit_id
            self.operating_unit_id = unit
            self.source_operating_unit = unit
        return res

    
    def button_validate(self):
        # rec = self.copy()
        picking_type = self.env['stock.picking.type'].search([
                ('operating_unit_id', '=', self.dest_operating_unit.id), ('code', '=', 'incoming')])
        
        if self.dest_operating_unit:
            self.copy({
                'origin': self.name,
                'location_id': self.location_dest_id.id,
                'picking_type_id': picking_type.id, 
                'location_dest_id': picking_type.default_location_dest_id.id,
                'source_operating_unit': self.picking_type_id.operating_unit_id.id,
                'dest_operating_unit': False,
            })

        self = self.with_context({
            'operating_unit' : self.picking_type_id.operating_unit_id.id
        })
        stock = super(StockPicking, self).button_validate()
        return stock
    
    @api.model
    def create(self, vals):
        vals['operating_unit_id'] = self.env['stock.picking.type'].browse(vals['picking_type_id']).\
            warehouse_id.operating_unit_id.id
        return super(StockPicking, self).create(vals)

    # 
    # @api.constrains('operating_unit_id', 'company_id')
    # def _check_company_operating_unit(self):
    #     for rec in self:
    #         if (rec.company_id and rec.operating_unit_id and
    #                 rec.company_id != rec.operating_unit_id.company_id):
    #             raise UserError(
    #                 _('Configuration error. The Company in the Stock Picking '
    #                   'and in the Operating Unit must be the same.')
    #             )

    # 
    # @api.constrains('operating_unit_id', 'picking_type_id')
    # def _check_picking_type_operating_unit(self):
    #     for rec in self:
    #         warehouse = rec.picking_type_id.warehouse_id
    #         if (rec.picking_type_id and rec.operating_unit_id and
    #                 warehouse.operating_unit_id != rec.operating_unit_id):
    #             raise UserError(
    #                 _('Configuration error. The Operating Unit of the picking '
    #                   'must be the same as that of the warehouse of the '
    #                   'Picking Type.')
    #             )
    
    class PickingType(models.Model):
        _inherit = 'stock.picking.type'

        operating_unit_id = fields.Many2one('operating.unit', related='warehouse_id.operating_unit_id', string='Operating Unit')
        antar_cabang = fields.Boolean('Antar Cabang')
        
