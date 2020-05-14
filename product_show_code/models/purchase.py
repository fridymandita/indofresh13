from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    
    def name_get(self):
        if self._context.get("show_only_code"):
            res = []
            for product in self:
                res.append(
                    (product.id, (product.default_code or product.name)))
            return res
        return super(ProductProduct, self).name_get()
