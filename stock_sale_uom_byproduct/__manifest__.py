{
    'name': 'UOM Sale Product',
    'version': '13.1',
    'category': 'Stock',
    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",
    'summary': 'UOM Sale Product',
    'description': """
UOM Sale Product
====================
Different UoM for every product
""",
    'depends': [
        'stock_uom_byproduct',
        'sale',
    ],
    'data': [
        'views/view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': True,
}
