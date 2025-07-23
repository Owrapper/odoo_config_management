{
    'name': 'Odoo Configuration Management',
    'version': '18.0.1.0.0',
    'category': 'Technical/Configuration',
    'summary': 'Export/Import Odoo configurations as YAML',
    'description': '''
        Configuration Management for Odoo
        ================================
        
        Export and import Odoo system configurations as human-readable YAML files.
        Enables version control, environment synchronization, and configuration-as-code workflows.
        
        Features:
        * Export system configurations to YAML
        * Import configurations from YAML files  
        * CLI commands for automation
        * Basic validation and conflict resolution
        
        Perfect for dev → staging → production workflows.
    ''',
    'author': 'Owrapper.com',
    'website': 'https://owrapper.com',
    'depends': ['base'],
    'external_dependencies': {
        'python': ['pyyaml', 'click']
    },
    'data': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
