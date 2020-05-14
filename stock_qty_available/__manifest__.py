# -*- coding: utf-8 -*-
{
    'name': "Inventory Report - Show qty available",

    'summary': """QTY Available in Inventory Report""",

    'description': """
        QTY Available in Inventory Report
    """,

    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        'views/view_stock.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
