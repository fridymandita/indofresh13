# -*- coding: utf-8 -*-
{
    'name': "sale_order_operating_unit",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Arkana",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale'
    ],

    # always loaded
    'data': [
        'security/sale_security.xml',
        'views/sale_order_view.xml',
        'views/sale_order_line_view.xml',
        'views/templates.xml',
    ],
}
