from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def api_get_partner(self, partner_id=False, partner_type='customer', limit=False, offset=False, order=None):
        field_list = [
            'name',
            'street',
            'street2',
            'city',
            'state_id',
            'zip',
        ]
        if partner_id:
            result = self.browse(partner_id).read(field_list)
            count = 1
        else:
            search_list = [
                ('active', '=', True),
                (partner_type + '_rank', '>', 0)
            ]
            partner_ids = self.search(
                search_list, limit=limit, offset=offset, order=order)
            result = partner_ids.read(field_list)
            count = len(result)
        return result, count
