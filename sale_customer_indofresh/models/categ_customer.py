from odoo import models, fields

class CategCustomer(models.Model):
    _name = 'categ.customer'
    _description = 'Customer Category'

    name = fields.Char(string='Name')