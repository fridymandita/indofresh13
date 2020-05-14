# Copyright 2019 ARKANA (<https://www.arkana.co.id>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report docx",

    'summary': "Base module to create docx report",
    'author': 'Fadhlullah <ifadhf@gmail.com>',
    'website': "https://www.arkana.co.id",
    'category': 'Reporting',
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'docxtpl',
            'docx',
        ],
    },
    'depends': [
        'base', 'web',
    ],
    'data': [
        'views/webclient_templates.xml',
        'demo/report.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
