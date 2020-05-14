# -*- coding: utf-8 -*-
{
    'name': "Purchase - Advance Invoice",

    'summary': """Create advance invoice from PO""",

    'description': """
        Create advance invoice from PO
    """,

    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'sale',
    ],

    # always loaded
    'data': [
        'views/view_purchase.xml',
        'wizard/view_wizard_purchase_advance.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
