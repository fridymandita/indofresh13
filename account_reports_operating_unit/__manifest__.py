# -*- coding: utf-8 -*-
{
    'name': "Operating Unit Accounting Report",

    'summary': """""",

    'description': """""",

    'author': "Arkana, Erlangga <https://erlaangga.github.io>, Joenan",
    'website': "https://arkana.co.id",
    'category': 'Accounting',
    'version': '13.1',
    'license': 'OEEL-1',
    'depends': ['account_reports', 'account_operating_unit'],
    'data': [
        'views/account_report_view.xml',
        'views/report_financial.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'application': True,

}
