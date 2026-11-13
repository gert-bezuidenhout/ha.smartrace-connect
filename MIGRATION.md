# Upgrade from smartrace_control

For v1.0.6 or earlier, the integration domain changed to smartrace_connect. Back up Home Assistant and note your server address, port and entity IDs. Remove the old integration entry while its files are still installed, then remove its old custom_components/smartrace_control folder. Install SmartRace Connect through HACS, restart and add it with your server details.

Check dashboard and automation references against the new entities. Device-based automations must select the new device. History and old configuration entries are not automatically transferred.

For updates within smartrace_connect, keep the integration entry and update through HACS.
