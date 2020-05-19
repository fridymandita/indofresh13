from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    api_write_date = fields.Datetime(string='Latest Change of QT fields')

    def write(self, values):
        if (values.get('name') or values.get('login') or
                values.get('password')):
            values['api_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(values)
