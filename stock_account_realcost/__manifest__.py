# -*- coding: utf-8 -*-
{
    'name': "Inventory Valuation - Real Cost per serial number",

    'summary': """Real cost per serial number for FIFO inventory valuation""",

    'description': """
        When FIFO inventory valuation selected, generated cost will be selected from same serial number with first in
    """,

    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': [
        'stock_account'
    ],

    # always loaded
    'data': [
        'views/view_stock.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
