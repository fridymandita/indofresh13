# -*- coding: utf-8 -*-
{
    'name': "Credit Limit",

    'summary': """Credit limit for customer
        """,

    'description': """
        Limit utang per customer, ada tenggang waktu, jika lewat tidak bisa invoice lg.
        SO berikutnya akan diblok jika sudah overdue
    """,

    'author': "Arkana, Joenan <joenan@arkana.co.id>",
    'website': "https://arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}