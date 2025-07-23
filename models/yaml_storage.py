import yaml
import os
import logging

_logger = logging.getLogger(__name__)


class YamlFileStorage:
    """Simple YAML file storage for MVP"""

    def __init__(self, env):
        self.env = env

    def write_yaml(self, file_path: str, data: dict):
        """Write data to YAML file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)

            _logger.info(f"Successfully wrote YAML file: {file_path}")
        except Exception as e:
            _logger.error(f"Failed to write YAML file {file_path}: {str(e)}")
            raise

    def read_yaml(self, file_path: str) -> dict:
        """Read data from YAML file"""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                if data is None:
                    return {}
                return data
        except FileNotFoundError:
            _logger.warning(f"YAML file not found: {file_path}")
            return {}
        except Exception as e:
            _logger.error(f"Failed to read YAML file {file_path}: {str(e)}")
            raise

    def export_ir_model_data(self, target_path: str):
        """Export ir.model.data records as YAML"""
        try:
            ir_data = self.env['ir.model.data'].search([])

            data = []
            for record in ir_data:
                data.append({
                    'module': record.module,
                    'name': record.name,
                    'model': record.model,
                    'res_id': record.res_id,
                    'noupdate': record.noupdate
                })

            self.write_yaml(f'{target_path}/ir_model_data.yml', {
                'ir_model_data': data
            })

            _logger.info(f"Exported {len(data)} ir.model.data records")
            return len(data)

        except Exception as e:
            _logger.error(f"Failed to export ir.model.data: {str(e)}")
            raise

    def import_ir_model_data(self, source_path: str):
        """Import ir.model.data from YAML"""
        try:
            data = self.read_yaml(f'{source_path}/ir_model_data.yml')
            imported_count = 0

            for record_data in data.get('ir_model_data', []):
                existing = self.env['ir.model.data'].search([
                    ('module', '=', record_data['module']),
                    ('name', '=', record_data['name'])
                ])

                if existing:
                    existing.write(record_data)
                else:
                    self.env['ir.model.data'].create(record_data)

                imported_count += 1

            _logger.info(f"Imported {imported_count} ir.model.data records")
            return imported_count

        except Exception as e:
            _logger.error(f"Failed to import ir.model.data: {str(e)}")
            raise
