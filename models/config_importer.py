import os
import logging
from .yaml_storage import YamlFileStorage

_logger = logging.getLogger(__name__)


class MinimalConfigImporter:
    """Week 2: Core import functionality"""

    def __init__(self, env):
        self.env = env
        self.storage = YamlFileStorage(env)

    def import_system_configs(self, source_path: str):
        """Import core system configurations with basic validation"""
        try:
            # Check manifest first
            manifest = self.storage.read_yaml(f"{source_path}/manifest.yml")
            if not manifest:
                return {
                    'success': False,
                    'error': 'No manifest file found or invalid manifest'
                }

            # Import in dependency order
            import_order = [
                'ir_config_parameters',
                'res_groups',
                'ir_sequences',
                'module_states',
                'ir_model_data'  # Last because it references other records
            ]

            results = []
            imported_count = 0

            for config_type in import_order:
                try:
                    result = self._import_config_type(config_type, source_path)
                    results.append(result)

                    if result['success']:
                        imported_count += result.get('imported_records', 0)
                    else:
                        # Stop on first failure for MVP
                        return {
                            'success': False,
                            'failed_config_type': config_type,
                            'error': result.get('error'),
                            'imported_count': imported_count
                        }

                except Exception as e:
                    _logger.error(f"Failed to import {config_type}: {str(e)}")
                    return {
                        'success': False,
                        'failed_config_type': config_type,
                        'error': str(e),
                        'imported_count': imported_count
                    }

            _logger.info(
                f"Successfully imported all config types, total records: {imported_count}")

            return {
                'success': True,
                'imported_config_types': len(import_order),
                'total_imported_records': imported_count,
                'results': results
            }

        except Exception as e:
            _logger.error(f"Failed to import system configs: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _import_config_type(self, config_type: str, source_path: str):
        """Import specific configuration type"""
        try:
            file_path = f"{source_path}/{config_type}.yml"
            if not os.path.exists(file_path):
                return {
                    'success': True,
                    'config_type': config_type,
                    'imported_records': 0,
                    'message': 'File not found, skipping'
                }

            data = self.storage.read_yaml(file_path)
            config_data = data.get(config_type, [])

            # Route to appropriate import method
            import_methods = {
                'ir_config_parameters': self._import_config_params,
                'ir_sequences': self._import_sequences,
                'res_groups': self._import_user_groups,
                'ir_model_data': self._import_external_ids,
                'module_states': self._import_module_states
            }

            import_method = import_methods.get(config_type)
            if not import_method:
                return {
                    'success': False,
                    'config_type': config_type,
                    'error': f'No import method for {config_type}'
                }

            imported_records = import_method(config_data)
            _logger.info(
                f"Successfully imported {imported_records} records for {config_type}")

            return {
                'success': True,
                'config_type': config_type,
                'imported_records': imported_records
            }

        except Exception as e:
            _logger.error(
                f"Failed to import config type {config_type}: {str(e)}")
            return {
                'success': False,
                'config_type': config_type,
                'error': str(e)
            }

    def _import_config_params(self, params_data):
        """Import system configuration parameters"""
        imported = 0

        for param_data in params_data:
            try:
                existing = self.env['ir.config_parameter'].search([
                    ('key', '=', param_data['key'])
                ])

                if existing:
                    existing.value = param_data['value']
                else:
                    self.env['ir.config_parameter'].create({
                        'key': param_data['key'],
                        'value': param_data['value']
                    })

                imported += 1
            except Exception as e:
                _logger.warning(
                    f"Failed to import config parameter {param_data.get('key')}: {str(e)}")

        return imported

    def _import_sequences(self, sequences_data):
        """Import number sequences"""
        imported = 0

        for seq_data in sequences_data:
            try:
                existing = self.env['ir.sequence'].search([
                    ('code', '=', seq_data['code'])
                ])

                if existing:
                    # Update existing sequence (but don't update number_next to avoid conflicts)
                    update_data = seq_data.copy()
                    # Remove number_next to avoid conflicts
                    update_data.pop('number_next', None)
                    existing.write(update_data)
                else:
                    # Create new sequence
                    self.env['ir.sequence'].create(seq_data)

                imported += 1
            except Exception as e:
                _logger.warning(
                    f"Failed to import sequence {seq_data.get('code')}: {str(e)}")

        return imported

    def _import_user_groups(self, groups_data):
        """Import user groups (simplified for MVP)"""
        imported = 0

        for group_data in groups_data:
            try:
                existing = self.env['res.groups'].search([
                    ('name', '=', group_data['name'])
                ])

                if not existing:
                    # Create basic group structure
                    # Skip complex relationships for MVP
                    self.env['res.groups'].create({
                        'name': group_data['name']
                    })
                    imported += 1

            except Exception as e:
                _logger.warning(
                    f"Failed to import user group {group_data.get('name')}: {str(e)}")

        return imported

    def _import_external_ids(self, external_ids_data):
        """Import external ID mappings"""
        imported = 0

        for record_data in external_ids_data:
            try:
                existing = self.env['ir.model.data'].search([
                    ('module', '=', record_data['module']),
                    ('name', '=', record_data['name'])
                ])

                if existing:
                    existing.write(record_data)
                else:
                    self.env['ir.model.data'].create(record_data)

                imported += 1
            except Exception as e:
                _logger.warning(
                    f"Failed to import external ID {record_data.get('module')}.{record_data.get('name')}: {str(e)}")

        return imported

    def _import_module_states(self, modules_data):
        """Import module installation states (read-only for MVP)"""
        imported = 0

        # For MVP, we just log the module states but don't modify them
        # as changing module states requires careful dependency management
        for module_data in modules_data:
            try:
                existing = self.env['ir.module.module'].search([
                    ('name', '=', module_data['name'])
                ])

                if existing:
                    current_state = existing.state
                    target_state = module_data['state']

                    if current_state != target_state:
                        _logger.info(
                            f"Module {module_data['name']}: current={current_state}, target={target_state}")

                    imported += 1
                else:
                    _logger.warning(
                        f"Module {module_data['name']} not found in system")

            except Exception as e:
                _logger.warning(
                    f"Failed to check module {module_data.get('name')}: {str(e)}")

        return imported
