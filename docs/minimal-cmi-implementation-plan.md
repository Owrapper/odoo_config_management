# Minimal CMI Implementation Plan for Odoo

## Overview

This document outlines a minimal viable implementation of Configuration Management Initiative (CMI) for Odoo, focused on proving core value with the smallest possible scope. The goal is to create "Drupal drush cex/cim for Odoo" - enabling YAML export/import of Odoo configurations.

## Core Goal

**Enable YAML export/import of Odoo configurations with basic validation**

This addresses the fundamental gap in the Odoo ecosystem: reliable environment synchronization and configuration-as-code capabilities.

## Phase 1: Minimal Viable Product (1-2 weeks)

### 1. Core Components Only

#### Minimal ConfigFactory
```python
class ConfigFactory:
    """Simplified configuration factory for MVP"""
    
    def __init__(self, env):
        self.env = env
        self.storage = YamlFileStorage(env)  # YAML only for MVP
    
    def export_all(self, target_path: str):
        """Export all configurations to YAML"""
        # Focus on just IR model configurations
        return self._export_ir_configs(target_path)
    
    def import_all(self, source_path: str):
        """Import configurations from YAML"""
        return self._import_ir_configs(source_path)
    
    def _export_ir_configs(self, target_path: str):
        """Export core IR model configurations"""
        exporter = MinimalConfigExporter(self.env)
        return exporter.export_system_configs(target_path)
    
    def _import_ir_configs(self, source_path: str):
        """Import core IR model configurations"""
        importer = MinimalConfigImporter(self.env)
        return importer.import_system_configs(source_path)
```

#### Minimal Storage - YAML Only
```python
class YamlFileStorage:
    """Simple YAML file storage for MVP"""
    
    def __init__(self, env):
        self.env = env
    
    def write_yaml(self, file_path: str, data: dict):
        """Write data to YAML file"""
        import yaml
        import os
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)
    
    def read_yaml(self, file_path: str) -> dict:
        """Read data from YAML file"""
        import yaml
        
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def export_ir_model_data(self, target_path: str):
        """Export ir.model.data records as YAML"""
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
        
    def import_ir_model_data(self, source_path: str):
        """Import ir.model.data from YAML"""
        data = self.read_yaml(f'{source_path}/ir_model_data.yml')
        
        for record_data in data.get('ir_model_data', []):
            # Basic import with conflict resolution
            existing = self.env['ir.model.data'].search([
                ('module', '=', record_data['module']),
                ('name', '=', record_data['name'])
            ])
            
            if existing:
                existing.write(record_data)
            else:
                self.env['ir.model.data'].create(record_data)
```

### 2. Target Configuration Scope (Minimal)

**Include these configuration types only:**

#### Core System Configurations
- **`ir.config_parameter`** - System parameters and settings
- **`ir.sequence`** - Number sequences for documents
- **`res.groups`** - User groups and permissions
- **`ir.model.data`** - External ID system for references
- **Basic module states** - Which modules are installed/enabled

#### Implementation Focus
```python
class MinimalConfigExporter:
    """Week 1: Core export functionality"""
    
    def __init__(self, env):
        self.env = env
        self.storage = YamlFileStorage(env)
    
    def export_system_configs(self, output_path: str):
        """Export core system configurations only"""
        
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
        
        return {
            'success': True,
            'exported_configs': len(configs),
            'total_records': manifest['total_records'],
            'output_path': output_path
        }
    
    def _export_config_params(self):
        """Export system configuration parameters"""
        params = self.env['ir.config_parameter'].search([])
        return [
            {
                'key': param.key,
                'value': param.value
            }
            for param in params
        ]
    
    def _export_sequences(self):
        """Export number sequences"""
        sequences = self.env['ir.sequence'].search([])
        return [
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
    
    def _export_user_groups(self):
        """Export user groups"""
        groups = self.env['res.groups'].search([])
        return [
            {
                'name': group.name,
                'category_id': group.category_id.xml_id if group.category_id else None,
                'implied_ids': [g.xml_id for g in group.implied_ids if g.xml_id],
                'users': [u.login for u in group.users]
            }
            for group in groups
        ]
    
    def _export_external_ids(self):
        """Export external ID mappings"""
        ir_data = self.env['ir.model.data'].search([])
        return [
            {
                'module': record.module,
                'name': record.name,
                'model': record.model,
                'res_id': record.res_id,
                'noupdate': record.noupdate
            }
            for record in ir_data
        ]
    
    def _export_module_states(self):
        """Export module installation states"""
        modules = self.env['ir.module.module'].search([])
        return [
            {
                'name': module.name,
                'state': module.state,
                'auto_install': module.auto_install,
                'sequence': module.sequence
            }
            for module in modules
            if module.state in ['installed', 'to_install', 'to_upgrade']
        ]

class MinimalConfigImporter:
    """Week 2: Core import functionality"""
    
    def __init__(self, env):
        self.env = env
        self.storage = YamlFileStorage(env)
    
    def import_system_configs(self, source_path: str):
        """Import core system configurations with basic validation"""
        
        # Check manifest first
        manifest = self.storage.read_yaml(f"{source_path}/manifest.yml")
        
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
                return {
                    'success': False,
                    'failed_config_type': config_type,
                    'error': str(e),
                    'imported_count': imported_count
                }
        
        return {
            'success': True,
            'imported_config_types': len(import_order),
            'total_imported_records': imported_count,
            'results': results
        }
    
    def _import_config_type(self, config_type: str, source_path: str):
        """Import specific configuration type"""
        
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
        
        try:
            imported_records = import_method(config_data)
            return {
                'success': True,
                'config_type': config_type,
                'imported_records': imported_records
            }
        except Exception as e:
            return {
                'success': False,
                'config_type': config_type,
                'error': str(e)
            }
    
    def _import_config_params(self, params_data):
        """Import system configuration parameters"""
        imported = 0
        
        for param_data in params_data:
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
        
        return imported
    
    def _import_sequences(self, sequences_data):
        """Import number sequences"""
        imported = 0
        
        for seq_data in sequences_data:
            existing = self.env['ir.sequence'].search([
                ('code', '=', seq_data['code'])
            ])
            
            if existing:
                # Update existing sequence
                existing.write({
                    'name': seq_data['name'],
                    'prefix': seq_data['prefix'],
                    'suffix': seq_data['suffix'],
                    'padding': seq_data['padding'],
                    'number_increment': seq_data['number_increment'],
                    'active': seq_data['active']
                    # Note: Don't update number_next to avoid conflicts
                })
            else:
                # Create new sequence
                self.env['ir.sequence'].create(seq_data)
            
            imported += 1
        
        return imported
    
    def _import_user_groups(self, groups_data):
        """Import user groups (simplified for MVP)"""
        imported = 0
        
        for group_data in groups_data:
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
        
        return imported
```

**Skip for MVP:**
- Complex business configurations (sale settings, inventory rules)
- Custom fields and models
- Workflow and automation configurations  
- Integration and webhook settings
- Advanced permissions and access controls

### 3. Simple CLI Commands

#### Command Structure
```bash
# Export command
odoo-bin config-export --database=mydb --output=/path/to/configs

# Import command  
odoo-bin config-import --database=mydb --source=/path/to/configs

# Optional: Validation command
odoo-bin config-validate --source=/path/to/configs
```

#### CLI Implementation
```python
import click
from odoo.cli import Command

class ConfigCommand(Command):
    """Minimal configuration management commands"""
    
    @click.group()
    def config():
        """Configuration management commands"""
        pass
    
    @config.command()
    @click.option('--database', required=True, help='Database name')
    @click.option('--output', required=True, help='Output directory path')
    def export(database, output):
        """Export system configurations to YAML files"""
        
        try:
            from odoo import registry, api, SUPERUSER_ID
            
            with registry(database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                factory = ConfigFactory(env)
                result = factory.export_all(output)
                
                if result['success']:
                    click.echo(f"✓ Exported {result['exported_configs']} config types")
                    click.echo(f"✓ Total records: {result['total_records']}")
                    click.echo(f"✓ Output: {result['output_path']}")
                else:
                    click.echo(f"✗ Export failed: {result.get('error')}")
                    return 1
                    
        except Exception as e:
            click.echo(f"✗ Export failed: {str(e)}")
            return 1
        
        return 0
    
    @config.command() 
    @click.option('--database', required=True, help='Database name')
    @click.option('--source', required=True, help='Source directory path')
    @click.option('--dry-run', is_flag=True, help='Validate only, do not import')
    def import_configs(database, source, dry_run):
        """Import system configurations from YAML files"""
        
        try:
            from odoo import registry, api, SUPERUSER_ID
            
            with registry(database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                factory = ConfigFactory(env)
                
                if dry_run:
                    click.echo("Validating configurations (dry run)...")
                    # Basic validation - check files exist and are readable
                    config_types = [
                        'ir_config_parameters', 'ir_sequences', 
                        'res_groups', 'ir_model_data', 'module_states'
                    ]
                    
                    missing_files = []
                    for config_type in config_types:
                        file_path = f"{source}/{config_type}.yml"
                        if not os.path.exists(file_path):
                            missing_files.append(file_path)
                    
                    if missing_files:
                        click.echo(f"✗ Missing files: {missing_files}")
                        return 1
                    else:
                        click.echo("✓ All configuration files found")
                        return 0
                else:
                    click.echo("Importing configurations...")
                    result = factory.import_all(source)
                    
                    if result['success']:
                        click.echo(f"✓ Successfully imported {result['imported_config_types']} config types")
                        click.echo(f"✓ Total records: {result['total_imported_records']}")
                    else:
                        click.echo(f"✗ Import failed in {result['failed_config_type']}")
                        click.echo(f"  Error: {result.get('error')}")
                        return 1
                        
        except Exception as e:
            click.echo(f"✗ Import failed: {str(e)}")
            return 1
        
        return 0
```

## Success Criteria for MVP

### Core Requirements
✅ **Export system configs to human-readable YAML**
- All core system configurations exportable
- YAML format is clean and readable
- Export includes manifest with metadata

✅ **Import configs to recreate system state**  
- Can import exported configurations to fresh instance
- Basic conflict resolution (update existing, create new)
- Import validates file structure before processing

✅ **Basic validation (no broken references)**
- Import fails gracefully on invalid data
- External ID references are preserved
- No database corruption from bad imports

✅ **Works with dev → staging workflow**
- Export from development instance
- Import to staging instance  
- Core functionality preserved

### Additional Success Indicators
- **File structure is intuitive** - developers can read/modify YAML files
- **Error messages are helpful** - clear indication of what went wrong
- **Performance is acceptable** - export/import completes in reasonable time
- **No data loss** - import preserves all exported information

## What This Proves

### Immediate Value
- **Odoo configurations become version-controllable**
  - Store configuration changes in git
  - Track who changed what and when
  - Branch and merge configuration changes

- **Environment synchronization becomes possible**
  - Reliable dev → staging → production workflow
  - Consistent configuration across environments
  - Automated deployment of configuration changes

- **Manual configuration copying eliminated**
  - No more manual recreation of settings
  - Reduced human error in environment setup
  - Faster environment provisioning

### Technical Validation
- **Proves there's demand for Odoo configuration management**
  - Community adoption metrics
  - Implementation partner usage
  - User feedback and feature requests

- **Tests YAML as the right format choice**
  - Readability and editability
  - Git diff friendliness
  - Tool ecosystem compatibility

- **Validates the export/import workflow**
  - Reliability of round-trip operations
  - Performance characteristics
  - Integration points with existing tools

## Module Naming and Structure

### Recommended Module Name: `odoo_config_management`

**Why this works best:**
- Clear, descriptive purpose
- Follows Odoo naming conventions (`module_description`)
- Professional and enterprise-ready
- Easy to find in app store/repositories
- Matches technical terminology (CMI = Configuration Management Initiative)

### Alternative Names Considered:

**Technical Focus:**
- `configuration_sync` - Emphasizes synchronization capability
- `config_export_import` - Direct description of functionality  
- `system_config_manager` - Broader system management scope

**Community/Ecosystem Focus:**
- `odoo_cmi` - Direct reference to Configuration Management Initiative
- `config_as_code` - Modern DevOps terminology
- `environment_sync` - Emphasizes use case

**Marketplace Appeal:**
- `configuration_toolkit` - Suggests comprehensive toolset
- `config_master` - Simple, memorable
- `odoo_devops_config` - Appeals to DevOps audience

### Module Manifest Structure:
```python
# odoo_config_management/__manifest__.py
{
    'name': 'Odoo Configuration Management',
    'version': '1.0.0',
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
    'installable': True,
    'auto_install': False,
    'application': True,
}
```

## Implementation Timeline

### Week 1: Core Export Functionality
- [ ] Set up basic module structure
- [ ] Implement `YamlFileStorage` class
- [ ] Implement `MinimalConfigExporter` 
- [ ] Create CLI export command
- [ ] Test export functionality with demo data

### Week 2: Core Import Functionality
- [ ] Implement `MinimalConfigImporter`
- [ ] Add basic validation and error handling
- [ ] Create CLI import command
- [ ] Test round-trip export/import workflow
- [ ] Document usage and limitations

### Testing Strategy
1. **Fresh Odoo instance**: Export → Import to new instance → Compare
2. **Configured demo instance**: Export → Import → Verify functionality  
3. **Simple module installation**: Export → Import → Test module works
4. **User workflow testing**: Real implementation partner usage

## Success Metrics

### Quantitative Metrics
- **Export completeness**: Can recreate >90% of basic system state
- **Import reliability**: <5% failure rate on valid configurations
- **Performance**: Export/import completes in <2 minutes for typical instance
- **File size**: YAML files are reasonable size (<10MB for typical export)

### Qualitative Metrics  
- **User adoption**: Implementation partners start using it regularly
- **Community feedback**: Positive response from Odoo community forums
- **Use case validation**: Solves real problems users are experiencing
- **Extension requests**: Users ask for additional configuration types

## What This Enables Next

### Phase 2 Additions Become Obvious
Based on user feedback and usage patterns:

- **Schema validation** (users hit validation errors frequently)
- **More configuration types** (users request specific configs like views, reports)
- **Event system** (users want to react to config changes)
- **Advanced dependency handling** (users encounter dependency conflicts)

### Integration Opportunities
- **CI/CD integration** (automated export/import in deployment pipelines)
- **Backup/restore workflows** (configuration backup alongside data backup)
- **Multi-instance management** (configuration sharing across instances)
- **Template marketplace** (sharing configuration templates)

## Why This Minimal Approach Works

### 1. Immediate ROI
- Solves real pain point that every Odoo implementation faces
- Provides value from day one of usage
- Clear before/after improvement in workflow

### 2. Proof of Concept
- Validates core architecture decisions before heavy investment
- Tests market demand with minimal resource commitment
- Identifies technical challenges early

### 3. Community Building
- Gets early adopters involved in feedback and improvement
- Creates network effects as more users adopt
- Establishes reputation and credibility in Odoo ecosystem

### 4. Foundation for Growth
- Everything else builds on this proven base
- Technical architecture scales to more complex features
- User base grows organically from satisfied early adopters

## Integration with Transformation System

### Current State Capture
```python
# MVP enables basic state capture
def capture_current_state(instance_id: str):
    factory = ConfigFactory(env)
    
    # Export current configuration state
    temp_export_path = f"/tmp/state_capture_{instance_id}"
    export_result = factory.export_all(temp_export_path)
    
    # Return structured state data
    return {
        'instance_id': instance_id,
        'timestamp': datetime.now().isoformat(),
        'config_state': load_yaml_configs(temp_export_path),
        'export_metadata': export_result
    }
```

### Configuration Change Application
```python
# MVP enables basic config change application  
def apply_config_changes(changes: dict):
    # Generate temporary YAML files with changes
    temp_import_path = generate_config_files(changes)
    
    # Use CMI import to apply changes
    factory = ConfigFactory(env)
    import_result = factory.import_all(temp_import_path)
    
    return import_result
```

**Most importantly**: This minimal version focuses on the **80% use case** - basic system configuration synchronization - which is exactly what's missing in the Odoo ecosystem today.

The MVP provides immediate value while laying the foundation for more advanced transformation capabilities. It proves the concept, builds the user base, and validates the technical approach before significant additional investment.

---

*Implementation Plan Document*
*Target: 1-2 week MVP development*
*Focus: Core export/import functionality with YAML format*