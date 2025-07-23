import logging
from datetime import datetime
from .yaml_storage import YamlFileStorage

_logger = logging.getLogger(__name__)


class MinimalConfigExporter:
    """Week 1: Core export functionality"""

    def __init__(self, env):
        self.env = env
        self.storage = YamlFileStorage(env)

    def export_system_configs(self, output_path: str):
        """Export core system configurations only"""
        try:
            configs = {
                'ir_config_parameters': self._export_config_params(),
                'ir_sequences': self._export_sequences(),
                'res_groups': self._export_user_groups(),
                'ir_model_data': self._export_external_ids(),
                'module_states': self._export_module_states()
            }

            # Write each config type to separate YAML file
            for config_type, data in configs.items():
                file_path = f"{output_path}/{config_type}.yml"
                self.storage.write_yaml(file_path, {config_type: data})

            # Create export manifest
            manifest = {
                'export_date': datetime.now().isoformat(),
                'odoo_version': self._get_odoo_version(),
                'database_uuid': self._get_database_uuid(),
                'config_types': list(configs.keys()),
                'total_records': sum(len(data) for data in configs.values())
            }

            self.storage.write_yaml(f"{output_path}/manifest.yml", manifest)

            _logger.info(
                f"Successfully exported {len(configs)} config types with {manifest['total_records']} total records")

            return {
                'success': True,
                'exported_configs': len(configs),
                'total_records': manifest['total_records'],
                'output_path': output_path
            }

        except Exception as e:
            _logger.error(f"Failed to export system configs: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _export_config_params(self):
        """Export system configuration parameters"""
        try:
            params = self.env['ir.config_parameter'].search([])
            data = [
                {
                    'key': param.key,
                    'value': param.value
                }
                for param in params
            ]
            _logger.info(f"Exported {len(data)} config parameters")
            return data
        except Exception as e:
            _logger.error(f"Failed to export config parameters: {str(e)}")
            raise

    def _export_sequences(self):
        """Export number sequences"""
        try:
            sequences = self.env['ir.sequence'].search([])
            data = [
                {
                    'name': seq.name,
                    'code': seq.code,
                    'prefix': seq.prefix,
                    'suffix': seq.suffix,
                    'padding': seq.padding,
                    'number_next': seq.number_next,
                    'number_increment': seq.number_increment,
                    'active': seq.active
                }
                for seq in sequences
            ]
            _logger.info(f"Exported {len(data)} sequences")
            return data
        except Exception as e:
            _logger.error(f"Failed to export sequences: {str(e)}")
            raise

    def _export_user_groups(self):
        """Export user groups"""
        try:
            groups = self.env['res.groups'].search([])
            data = []

            for group in groups:
                group_data = {
                    'name': group.name,
                    'category_id': group.category_id.complete_name if group.category_id else None,
                    'implied_ids': [],
                    'users': [u.login for u in group.users]
                }

                # Get external IDs for implied groups
                for implied_group in group.implied_ids:
                    external_id = self.env['ir.model.data'].search([
                        ('model', '=', 'res.groups'),
                        ('res_id', '=', implied_group.id)
                    ], limit=1)
                    if external_id:
                        group_data['implied_ids'].append(
                            f"{external_id.module}.{external_id.name}")

                data.append(group_data)

            _logger.info(f"Exported {len(data)} user groups")
            return data
        except Exception as e:
            _logger.error(f"Failed to export user groups: {str(e)}")
            raise

    def _export_external_ids(self):
        """Export external ID mappings"""
        try:
            ir_data = self.env['ir.model.data'].search([])
            data = [
                {
                    'module': record.module,
                    'name': record.name,
                    'model': record.model,
                    'res_id': record.res_id,
                    'noupdate': record.noupdate
                }
                for record in ir_data
            ]
            _logger.info(f"Exported {len(data)} external IDs")
            return data
        except Exception as e:
            _logger.error(f"Failed to export external IDs: {str(e)}")
            raise

    def _export_module_states(self):
        """Export module installation states"""
        try:
            modules = self.env['ir.module.module'].search([])
            data = [
                {
                    'name': module.name,
                    'state': module.state,
                    'auto_install': module.auto_install,
                    'sequence': module.sequence
                }
                for module in modules
                if module.state in ['installed', 'to_install', 'to_upgrade']
            ]
            _logger.info(f"Exported {len(data)} module states")
            return data
        except Exception as e:
            _logger.error(f"Failed to export module states: {str(e)}")
            raise

    def _get_odoo_version(self):
        """Get Odoo version"""
        try:
            import odoo
            return odoo.release.version
        except:
            return "18.0"

    def _get_database_uuid(self):
        """Get database UUID"""
        try:
            db_uuid = self.env['ir.config_parameter'].sudo(
            ).get_param('database.uuid')
            if not db_uuid:
                # Generate and store UUID if not exists
                import uuid
                db_uuid = str(uuid.uuid4())
                self.env['ir.config_parameter'].sudo(
                ).set_param('database.uuid', db_uuid)
            return db_uuid
        except:
            return None
