from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    users_ids = fields.Many2many('res.users', string='Salesmen')
    
    operating_unit_ids = fields.Many2many(
        comodel_name='operating.unit',
        string='Operating Unit',
        )
    
    categ_id = fields.Many2one('categ.customer', 'Kategori')
    alamat_pengiriman = fields.Text('Alamat Pengiriman')
    alamat_pajak = fields.Text('Alamat(Pajak)')

    