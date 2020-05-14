{
    'name': 'UOM Purchase Product',
    'version': '13.1',
    'category': 'Stock',
    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",
    'summary': 'UOM Purchase Product',
    'description': """
UOM Purchase Product
====================
Tiap Product Beda Uom

""",
    'depends': [
        'stock_uom_byproduct',
        'purchase',
    ],
    'data': [
        'views/view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': True,
}
