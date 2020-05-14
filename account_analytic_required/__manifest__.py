{
    'name': 'Account Analytic Required',
    'version': '13.1',
    'category': 'Accounting',
    'author': 'Arkana',
    'summary': 'Required analytic account for P&L account',
    'description': """
Account Analytic Required
=========================
Required analytic account for P&L account
""",
    'depends': [
        'account_sign',
    ],
    'data': [
        'views/account_move_view.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
