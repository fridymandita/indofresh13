from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    country_origin = fields.Char('Country Origin')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def api_get_product(self, product_id=False, limit=False, offset=False, order=None):
        field_list = [
            'name',
            'default_code',
            'categ_id',
            'uom_ids',
            'uom_id',
            'weight',
            'volume',
            'country_origin'
        ]
        if product_id:
            result = self.browse(product_id).read(field_list)
            result[0]['uom_ids'] = self.env['uom.uom'].browse(result[0]['uom_ids']).read([
                'name', 'factor_product'])
            count = 1
        else:
            search_list = [['sale_ok', '=', True]]
            product_ids = self.search(
                search_list, limit=limit, offset=offset, order=order)
            result = product_ids.read(field_list)
            uoms = self.env['uom.uom'].browse(
                list(set(y for x in result for y in x['uom_ids']))).read([
                    'name', 'factor_product'])
            for r in result:
                if r['uom_ids']:
                    x = list(filter(
                        lambda x: x['id'] in r['uom_ids'], uoms))
                    r['uom_ids'] = x
            count = len(result)
        return result, count
