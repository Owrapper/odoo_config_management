import os
import click
import logging
from odoo.cli.command import Command

_logger = logging.getLogger(__name__)


class ConfigCommand(Command):
    """Configuration management commands for Odoo 18"""
    
    @click.group()
    def config():
        """Configuration management commands"""
        pass
    
    @config.command()
    @click.option('--database', '-d', required=True, help='Database name')
    @click.option('--output', '-o', required=True, help='Output directory path')
    @click.option('--log-level', default='INFO', help='Log level (DEBUG, INFO, WARNING, ERROR)')
    def export(database, output, log_level):
        """Export system configurations to YAML files"""
        
        # Set up logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        
        try:
            from odoo import registry, api, SUPERUSER_ID
            from ..models.config_factory import create_config_factory
            
            # Ensure output directory exists
            os.makedirs(output, exist_ok=True)
            
            with registry(database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                factory = create_config_factory(env)
                result = factory.export_all(output)
                
                if result['success']:
                    click.echo(f"✓ Exported {result['exported_configs']} config types")
                    click.echo(f"✓ Total records: {result['total_records']}")
                    click.echo(f"✓ Output: {result['output_path']}")
                    return 0
                else:
                    click.echo(f"✗ Export failed: {result.get('error')}")
                    return 1
                    
        except Exception as e:
            click.echo(f"✗ Export failed: {str(e)}")
            _logger.exception("Export command failed")
            return 1
    
    @config.command() 
    @click.option('--database', '-d', required=True, help='Database name')
    @click.option('--source', '-s', required=True, help='Source directory path')
    @click.option('--dry-run', is_flag=True, help='Validate only, do not import')
    @click.option('--log-level', default='INFO', help='Log level (DEBUG, INFO, WARNING, ERROR)')
    def import_configs(database, source, dry_run, log_level):
        """Import system configurations from YAML files"""
        
        # Set up logging
        logging.basicConfig(level=getattr(logging, log_level.upper()))
        
        try:
            from odoo import registry, api, SUPERUSER_ID
            from ..models.config_factory import create_config_factory
            
            with registry(database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                factory = create_config_factory(env)
                
                if dry_run:
                    click.echo("Validating configurations (dry run)...")
                    
                    # Basic validation - check files exist and are readable
                    validation_result = factory.validate_import_path(source)
                    
                    if validation_result['valid']:
                        click.echo("✓ All required configuration files found")
                        if validation_result.get('missing_optional'):
                            click.echo(f"ℹ Optional files missing: {', '.join(validation_result['missing_optional'])}")
                        return 0
                    else:
                        click.echo(f"✗ Validation failed: {validation_result['message']}")
                        return 1
                else:
                    click.echo("Importing configurations...")
                    result = factory.import_all(source)
                    
                    if result['success']:
                        click.echo(f"✓ Successfully imported {result['imported_config_types']} config types")
                        click.echo(f"✓ Total records: {result['total_imported_records']}")
                        return 0
                    else:
                        click.echo(f"✗ Import failed in {result.get('failed_config_type', 'unknown')}")
                        click.echo(f"  Error: {result.get('error')}")
                        return 1
                        
        except Exception as e:
            click.echo(f"✗ Import failed: {str(e)}")
            _logger.exception("Import command failed")
            return 1
    
    @config.command()
    @click.option('--database', '-d', required=True, help='Database name')
    @click.option('--source', '-s', required=True, help='Source directory path')
    def validate(database, source):
        """Validate configuration files without importing"""
        
        try:
            from odoo import registry, api, SUPERUSER_ID
            from ..models.config_factory import create_config_factory
            
            with registry(database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                factory = create_config_factory(env)
                validation_result = factory.validate_import_path(source)
                
                if validation_result['valid']:
                    click.echo(f"✓ {validation_result['message']}")
                    if validation_result.get('missing_optional'):
                        click.echo(f"ℹ Optional files missing: {', '.join(validation_result['missing_optional'])}")
                    return 0
                else:
                    click.echo(f"✗ {validation_result['message']}")
                    return 1
                    
        except Exception as e:
            click.echo(f"✗ Validation failed: {str(e)}")
            return 1


# Register the command with Odoo CLI
def load_command():
    """Load the config command into Odoo CLI"""
    return ConfigCommand()