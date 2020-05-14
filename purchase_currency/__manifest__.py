# -*- coding: utf-8 -*-
{
    'name': "Purchase - Input Currency Rate",

    'summary': """Currency Rate on PO""",

    'description': """
        Currency Rate on PO
    """,

    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/view_purchase.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
