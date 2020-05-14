{
    'name': 'UOM Account Product',
    'version': '13.1',
    'category': 'Stock',
    'author': "Arkana, Fadhlullah <fadhlullah@arkana.co.id>",
    'website': "https://arkana.co.id",
    'summary': 'UOM Account Product',
    'description': """
UOM Account Product
====================
Tiap Product Beda Uom

""",
    'depends': [
        'stock_uom_byproduct',
        'sale',
    ],
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'application': True,
    'installable': True,
    'auto_install': True,
}
