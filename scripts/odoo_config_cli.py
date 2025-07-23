#!/usr/bin/env python3
"""
Standalone CLI script for Odoo Configuration Management
Usage: python odoo_config_cli.py --help
"""

import os
import sys
import click
import logging

# Add the module path to Python path
module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, module_path)


@click.group()
@click.option('--log-level', default='INFO', help='Log level (DEBUG, INFO, WARNING, ERROR)')
def cli(log_level):
    """Odoo Configuration Management CLI"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@cli.command()
@click.option('--database', '-d', required=True, help='Database name')
@click.option('--output', '-o', required=True, help='Output directory path')
@click.option('--odoo-path', help='Path to Odoo installation (if not in PYTHONPATH)')
def export(database, output, odoo_path):
    """Export system configurations to YAML files"""
    
    try:
        # Set up Odoo environment
        if odoo_path:
            sys.path.insert(0, odoo_path)
        
        import odoo
        from odoo import registry, api, SUPERUSER_ID
        
        # Initialize Odoo
        odoo.tools.config.parse_config(['-d', database])
        
        # Ensure output directory exists
        os.makedirs(output, exist_ok=True)
        
        with registry(database).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Import our module classes
            from models.config_factory import create_config_factory
            
            factory = create_config_factory(env)
            result = factory.export_all(output)
            
            if result['success']:
                click.echo(f"✓ Exported {result['exported_configs']} config types")
                click.echo(f"✓ Total records: {result['total_records']}")
                click.echo(f"✓ Output: {result['output_path']}")
            else:
                click.echo(f"✗ Export failed: {result.get('error')}")
                sys.exit(1)
                
    except Exception as e:
        click.echo(f"✗ Export failed: {str(e)}")
        logging.exception("Export command failed")
        sys.exit(1)


@cli.command() 
@click.option('--database', '-d', required=True, help='Database name')
@click.option('--source', '-s', required=True, help='Source directory path')
@click.option('--dry-run', is_flag=True, help='Validate only, do not import')
@click.option('--odoo-path', help='Path to Odoo installation (if not in PYTHONPATH)')
def import_configs(database, source, dry_run, odoo_path):
    """Import system configurations from YAML files"""
    
    try:
        # Set up Odoo environment
        if odoo_path:
            sys.path.insert(0, odoo_path)
        
        import odoo
        from odoo import registry, api, SUPERUSER_ID
        
        # Initialize Odoo
        odoo.tools.config.parse_config(['-d', database])
        
        with registry(database).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Import our module classes
            from models.config_factory import create_config_factory
            
            factory = create_config_factory(env)
            
            if dry_run:
                click.echo("Validating configurations (dry run)...")
                
                validation_result = factory.validate_import_path(source)
                
                if validation_result['valid']:
                    click.echo("✓ All required configuration files found")
                    if validation_result.get('missing_optional'):
                        click.echo(f"ℹ Optional files missing: {', '.join(validation_result['missing_optional'])}")
                else:
                    click.echo(f"✗ Validation failed: {validation_result['message']}")
                    sys.exit(1)
            else:
                click.echo("Importing configurations...")
                result = factory.import_all(source)
                
                if result['success']:
                    click.echo(f"✓ Successfully imported {result['imported_config_types']} config types")
                    click.echo(f"✓ Total records: {result['total_imported_records']}")
                else:
                    click.echo(f"✗ Import failed in {result.get('failed_config_type', 'unknown')}")
                    click.echo(f"  Error: {result.get('error')}")
                    sys.exit(1)
                    
    except Exception as e:
        click.echo(f"✗ Import failed: {str(e)}")
        logging.exception("Import command failed")
        sys.exit(1)


@cli.command()
@click.option('--database', '-d', required=True, help='Database name')
@click.option('--source', '-s', required=True, help='Source directory path')
@click.option('--odoo-path', help='Path to Odoo installation (if not in PYTHONPATH)')
def validate(database, source, odoo_path):
    """Validate configuration files without importing"""
    
    try:
        # Set up Odoo environment
        if odoo_path:
            sys.path.insert(0, odoo_path)
        
        import odoo
        from odoo import registry, api, SUPERUSER_ID
        
        # Initialize Odoo
        odoo.tools.config.parse_config(['-d', database])
        
        with registry(database).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            
            # Import our module classes
            from models.config_factory import create_config_factory
            
            factory = create_config_factory(env)
            validation_result = factory.validate_import_path(source)
            
            if validation_result['valid']:
                click.echo(f"✓ {validation_result['message']}")
                if validation_result.get('missing_optional'):
                    click.echo(f"ℹ Optional files missing: {', '.join(validation_result['missing_optional'])}")
            else:
                click.echo(f"✗ {validation_result['message']}")
                sys.exit(1)
                
    except Exception as e:
        click.echo(f"✗ Validation failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()