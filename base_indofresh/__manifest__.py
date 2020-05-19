# -*- coding: utf-8 -*-
{
    'name': "base_indofresh",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_analytic_required',
        # 'account_indofresh',
        # 'account_operating_unit',
        # 'account_reports_operating_unit',
        'account_sign',
        # 'analytic_operating_unit',
        # 'operating_unit',
        'product_show_code',
        'purchase_advance',
        'purchase_currency',
        # 'purchase_operating_unit',
        'report_docx',
        'rest_api',
        'sale_credit_limit',
        # 'sale_customer_indofresh',
        # 'sale_order_operating_unit',
        'sale_price_approval',
        # 'sales_team_operating_unit',
        'stock_account_realcost',
        'stock_account_uom_byproduct',
        'stock_adjustment_lock',
        # 'stock_operating_unit',
        'stock_purchase_uom_byproduct',
        'stock_qty_available',
        'stock_sale_uom_byproduct',
        'stock_uom_byproduct',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
