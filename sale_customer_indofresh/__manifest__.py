# -*- coding: utf-8 -*-
{
    'name': "sale_customer_indofresh",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Arkana",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'operating_unit'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/categ_customer_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}