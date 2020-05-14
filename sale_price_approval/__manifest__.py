{
    'name': 'Sale Pricelist',
    'version': '13.1',
    'category': 'Sales',
    'author': 'Arkana',
    'summary': 'Sale Pricelist',
    'description': """
Sale Pricelist
====================
Setiap SO yg ada harganya di bawah pricelist wajib di validasi oleh manajemen
""",
    'depends': [
        'sale',
    ],
    'data': [
        'security/group.xml',
        'views/view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
