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
    is_product_main_uom = fields.Boolean(
        'Is Product Main UoM', default=False, copy=False)

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
                    if 'factor_product' in values:
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

    uom_name_show = fields.Char(
        'Unit of Measure Name', related='uom_id.name', readonly=False)
    uom_rounding = fields.Float(
        'UoM Rounding', default=0.01, digits=0, related='uom_id.rounding', readonly=False)
    uom_category_id = fields.Many2one(
        'uom.category', 'UoM Category', related='uom_id.category_id', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('uom_name_show') and vals.get('uom_category_id'):
                vals['uom_id'] = self.env['uom.uom'].create({
                    'name': vals['uom_name_show'],
                    'category_id': vals['uom_category_id'],
                    'uom_type': 'bigger',
                    'factor': 1,
                    'rounding': vals.get('uom_rounding', 0.01),
                    'product_tmpl_id': vals['product_tmpl_id'],
                    'is_product_main_uom': True
                }).id
                vals['uom_po_id'] = vals['uom_id']
        return super(InheritProductProduct, self).create(vals_list)

    def write(self, vals):
        to_write = self.env['product.product']
        res = False
        if vals.get('uom_name_show'):
            for product in self:
                if not product.uom_id.product_tmpl_id:
                    vals['uom_id'] = self.env['uom.uom'].create({
                        'name': vals['uom_name_show'],
                        'category_id': vals['uom_category_id'],
                        'uom_type': 'bigger',
                        'factor': 1,
                        'rounding': vals.get('uom_rounding', 0.01),
                        'product_tmpl_id': product.product_tmpl_id.id,
                        'is_product_main_uom': True
                    }).id
                    res = super(InheritProductProduct, self).write(vals)
                else:
                    to_write |= product
        else:
            to_write |= self
        if to_write:
            return super(InheritProductProduct, to_write).write(vals)
        return res


class InheritProductTemplate(models.Model):
    _inherit = 'product.template'

    uom_name_show = fields.Char(
        'Unit of Measure Name', related='uom_id.name', readonly=False)
    uom_rounding = fields.Float(
        'UoM Rounding', default=0.01, digits=0, related='uom_id.rounding', readonly=False)
    uom_category_id = fields.Many2one(
        'uom.category', 'UoM Category', related='uom_id.category_id', readonly=False)

    uom_ids = fields.One2many(
        'uom.uom', 'product_tmpl_id', 'Unit of Measures',
        domain=[('is_product_main_uom', '=', False)])
    uom_main_ids = fields.One2many(
        'uom.uom', 'product_tmpl_id', 'Main Unit of Measures',
        domain=[('is_product_main_uom', '=', True)])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('uom_name_show') and vals.get('uom_category_id'):
                vals['uom_main_ids'] = [(0, 0, {
                    'name': vals['uom_name_show'],
                    'category_id': vals['uom_category_id'],
                    'uom_type': 'bigger',
                    'factor': 1,
                    'rounding': vals.get('uom_rounding', 0.01),
                    'is_product_main_uom': True
                })]
        res = super(InheritProductTemplate, self).create(vals_list)
        for product in res:
            if product.uom_main_ids:
                uom_id = product.uom_main_ids.ids[0]
                product.write({
                    'uom_id': uom_id,
                    'uom_po_id': uom_id,
                })
        return res

    def write(self, vals):
        to_write = self.env['product.template']
        res = False
        if vals.get('uom_name_show'):
            for product in self:
                if not product.uom_id.product_tmpl_id:
                    vals['uom_id'] = self.env['uom.uom'].create({
                        'name': vals['uom_name_show'],
                        'category_id': vals.get('uom_category_id', product.uom_id.category_id.id),
                        'uom_type': 'bigger',
                        'factor': 1,
                        'rounding': vals.get('uom_rounding', 0.01),
                        'product_tmpl_id': product.id,
                        'is_product_main_uom': True
                    }).id
                    res = super(InheritProductTemplate, self).write(vals)
                else:
                    to_write |= product
        else:
            to_write |= self
        if to_write:
            return super(InheritProductTemplate, to_write).write(vals)
        return res
