{
    'name': 'Odoo Rest API - Indofresh WMS Integration',
    'version': '13.0.0',
    'author': 'ARKANA SOLUSI DIGITAL',
    'category': 'Backend',
    'website': 'https://www.arkana.co.id/',
    'summary': 'Restful Api Service',
    'description': '''
API for integration with largo
''',
    'external_dependencies': {
        'python': [
            'pyjwt'
        ],
    },
    'depends': [
        'base',
        'product',
        'stock',
        'sale',
        'purchase',
        'stock_uom_byproduct'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/refresh_token.xml',
        'views/view_stock.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
