# Repository files

Only `custom_components/smartrace_connect/` is installed as integration runtime code. The remaining files support installation, documentation and development.

| File or folder | Purpose |
| --- | --- |
| `custom_components/smartrace_connect/` | Integration implementation loaded by Home Assistant. |
| `manifest.json` inside that folder | Integration identity, version, dependencies and support links. |
| `__init__.py` | Setup, reload and shutdown lifecycle. |
| `config_flow.py` | Setup/settings forms in Home Assistant. |
| `sensor.py`, `binary_sensor.py`, `button.py` | Sensors, diagnostic/connection indicators and buttons. |
| `strings.json`, `translations/en.json` | User-facing form text. |
| `brand/` | Integration icon and logo. |
| `hacs.json` | HACS repository metadata. |
| `README.md` | Installation, features and troubleshooting. |
| `MIGRATION.md` | Guidance for users upgrading older setups; unnecessary for fresh installations. |
| `LICENSE` | MIT licence for the project code. |
| `.gitignore` | Keeps local caches, logs and secrets out of future commits. |
| `.github/workflows/validate.yaml` | Automated HACS and Hassfest checks. |
| `docs/HACS_SUBMISSION.md` | Maintainer checklist for later Marketplace submission. |
| `client.py` | WebSocket transport and reconnect handling. |
| `dashboard.yaml`, `status-card.yaml` | Optional dashboard examples, not required for installation. |
| `test_*.py` | Developer checks for transport, setup schema and reconfiguration. |

