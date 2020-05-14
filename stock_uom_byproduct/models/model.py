from odoo import fields, models, api


class UomUom(models.Model):
    _inherit = 'uom.uom'

    
    def _product_id(self):
        for uom in self:
            uom.product_id = uom.product_tmpl_id.product_variant_ids[0]

    
    def _factor_product(self):
        for uom in self:
            if uom.uom_type == 'reference':
                uom.factor_product = 1
            elif uom.uom_type == 'bigger':
                uom.factor_product = uom.product_tmpl_id.uom_id.factor / uom.factor
            else:
                uom.factor_product = uom.factor / uom.product_tmpl_id.uom_id.factor

    product_id = fields.Many2one(
        'product.product', string='Product', compute='_product_id', search='_search_product_id')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    factor_product = fields.Float(
        # force NUMERIC with unlimited precision
        'Product Ratio', compute='_factor_product', digits=0,
        readonly=True, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'product_tmpl_id' in values:
                default_product_uom = self.env['product.template'].browse(
                    values.get('product_tmpl_id')).uom_id
                uom_type = values.get('uom_type')
                values['category_id'] = default_product_uom.category_id.id
                if uom_type == 'reference':
                    values['factor'] = default_product_uom.factor
                else:
                    factor_product = values.pop('factor_product')
                    factor = factor_product if uom_type == 'smaller' else (
                        1 / factor_product)
                    values['factor'] = default_product_uom.factor * factor
        return super(UomUom, self).create(vals_list)

    
    def write(self, values):
        if 'product_tmpl_id' in values:
            default_product_uom = self.env['product.template'].browse(
                values.get('product_tmpl_id'), self and self[0].product_tmpl_id.id or False).uom_id
            uom_type = values.get(
                'uom_type', self and self[0].uom_type or False)
            values['category_id'] = default_product_uom.category_id.id
            if uom_type == 'reference':
                values['factor'] = default_product_uom.factor
            else:
                factor_product = values.pop('factor_product')
                factor = factor_product if uom_type == 'smaller' else (
                    1 / factor_product)
                values['factor'] = default_product_uom.factor * factor
        return super(UomUom, self).write(values)

    def _search_product_id(self, operator, value):
        if operator == '=' and value:
            product = self.env['product.product'].browse(value)
            return [('id', 'in', [product.uom_po_id.id, product.uom_id.id] + product.uom_ids.ids)]
        else:
            return [('id', '=', False)]

    @api.onchange('uom_type')
    def onchange_uom_type(self):
        if self.uom_type == 'reference':
            self.factor_product = 1


class InheritProductProduct(models.Model):
    _inherit = 'product.product'

    
    def _uom_ids(self):
        for product in self:
            product.uom_ids = product.product_tmpl_id.uom_ids

    uom_ids = fields.One2many(
        'uom.uom', compute='_uom_ids', string='Unit of Measures')


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_ids = fields.One2many('uom.uom', 'product_tmpl_id',
                              string='Unit of Measures')
