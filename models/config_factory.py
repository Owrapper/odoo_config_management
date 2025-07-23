import logging
from odoo import models, api
from .yaml_storage import YamlFileStorage
from .config_exporter import MinimalConfigExporter
from .config_importer import MinimalConfigImporter

_logger = logging.getLogger(__name__)


class ConfigFactory(models.TransientModel):
    """Simplified configuration factory for MVP"""
    _name = 'config.factory'
    _description = 'Configuration Management Factory'
    
    def __init__(self, env):
        if hasattr(env, 'registry'):
            # Called from Odoo model context
            super(ConfigFactory, self).__init__(env)
        else:
            # Called directly from CLI
            self.env = env
        self.storage = YamlFileStorage(self.env)
    
    @api.model
    def export_all(self, target_path: str):
        """Export all configurations to YAML"""
        try:
            _logger.info(f"Starting configuration export to: {target_path}")
            result = self._export_ir_configs(target_path)
            _logger.info(f"Configuration export completed successfully")
            return result
        except Exception as e:
            _logger.error(f"Configuration export failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @api.model
    def import_all(self, source_path: str):
        """Import configurations from YAML"""
        try:
            _logger.info(f"Starting configuration import from: {source_path}")
            result = self._import_ir_configs(source_path)
            _logger.info(f"Configuration import completed successfully")
            return result
        except Exception as e:
            _logger.error(f"Configuration import failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _export_ir_configs(self, target_path: str):
        """Export core IR model configurations"""
        exporter = MinimalConfigExporter(self.env)
        return exporter.export_system_configs(target_path)
    
    def _import_ir_configs(self, source_path: str):
        """Import core IR model configurations"""
        importer = MinimalConfigImporter(self.env)
        return importer.import_system_configs(source_path)
    
    @api.model
    def validate_export_path(self, path: str):
        """Validate export path is writable"""
        import os
        try:
            # Check if directory exists or can be created
            os.makedirs(path, exist_ok=True)
            
            # Check if we can write to the directory
            test_file = os.path.join(path, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            
            return {
                'valid': True,
                'message': 'Export path is valid and writable'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Export path validation failed: {str(e)}'
            }
    
    @api.model
    def validate_import_path(self, path: str):
        """Validate import path has required files"""
        import os
        
        required_files = [
            'manifest.yml'
        ]
        
        optional_files = [
            'ir_config_parameters.yml',
            'ir_sequences.yml',
            'res_groups.yml',
            'ir_model_data.yml',
            'module_states.yml'
        ]
        
        missing_required = []
        missing_optional = []
        
        for file_name in required_files:
            file_path = os.path.join(path, file_name)
            if not os.path.exists(file_path):
                missing_required.append(file_name)
        
        for file_name in optional_files:
            file_path = os.path.join(path, file_name)
            if not os.path.exists(file_path):
                missing_optional.append(file_name)
        
        if missing_required:
            return {
                'valid': False,
                'message': f'Required files missing: {", ".join(missing_required)}'
            }
        
        return {
            'valid': True,
            'message': 'Import path is valid',
            'missing_optional': missing_optional
        }


# Helper function for CLI usage
def create_config_factory(env):
    """Create ConfigFactory instance for CLI usage"""
    return ConfigFactory(env)