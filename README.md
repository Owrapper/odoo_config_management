# Odoo Configuration Management (CMI)

## Overview

This repository provides a minimal viable implementation of the Configuration Management Initiative (CMI) for Odoo. It enables reliable export and import of Odoo system configurations as human-readable YAML files, supporting version control, environment synchronization, and configuration-as-code workflows.

## Features

- **Export system configurations to YAML**
- **Import configurations from YAML files**
- **Basic validation and conflict resolution**
- **CLI commands for automation**
- **Supports dev → staging → production workflows**

## Supported Configuration Types

- `ir.config_parameter` – System parameters and settings
- `ir.sequence` – Number sequences for documents
- `res.groups` – User groups and permissions
- `ir.model.data` – External ID system for references
- Module states – Which modules are installed/enabled

## Getting Started

### Prerequisites

- Odoo 18
- Python dependencies: `pyyaml`, `click`

### Installation

Clone this repository into your Odoo addons directory:

```sh
git clone https://github.com/your-org/odoo_config_management.git
```

Install required Python packages:

```sh
pip install pyyaml click
```

### Usage

#### Export Configurations

```sh
odoo-bin config-export --database=mydb --output=/path/to/configs
```

#### Import Configurations

```sh
odoo-bin config-import --database=mydb --source=/path/to/configs
```

#### Validate Configuration Files

```sh
odoo-bin config-validate --database=mydb --source=/path/to/configs
```

Or use the standalone CLI script:

```sh
python scripts/odoo_config_cli.py export --database=mydb --output=/path/to/configs
python scripts/odoo_config_cli.py import-configs --database=mydb --source=/path/to/configs
python scripts/odoo_config_cli.py validate --database=mydb --source=/path/to/configs
```

## Project Structure

- [`models/`](models/) – Core logic for export/import and YAML storage
- [`cli/`](cli/) – Odoo CLI integration
- [`scripts/`](scripts/) – Standalone CLI script
- [`docs/`](docs/) – Implementation plan and documentation

## Success Criteria

- Export/import round-trip preserves system state
- YAML files are clean, readable, and version-controllable
- Error messages are clear and helpful
- No data loss or corruption on import

## License

LGPL-3.0

## Author

Owrapper.com – [https://owrapper.com](https://owrapper.com)

---

For implementation details, see