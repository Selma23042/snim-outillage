{
    'name': 'Module Test DevOps',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Maintenance',
    'summary': 'Module de test pour pipeline DevOps',
    'description': 'Module créé pour valider le pipeline CI/CD Jenkins',
    'author': 'Salma',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/instrument_views.xml',
        'views/fiche_vie_views.xml',
        'views/reforme_views.xml',
        'views/menu_views.xml',
        'report/fiche_vie_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'module_test_devops/static/src/css/snim.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}