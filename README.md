# SmartRace Connect for Home Assistant

An unofficial custom integration. Home Assistant sends JSON directly to SmartRace's Connect Server using a WebSocket. No MQTT, Node-RED, additional server, browser permission changes, or extra Python packages are required.

## Install

1. Unzip this package on your computer.
2. Copy the entire `smartrace_connect` folder inside `custom_components` into Home Assistant's `/config/custom_components/` folder. Create `custom_components` if needed. The result must be `/config/custom_components/smartrace_connect/manifest.json`, with the other Python files beside it. Use your existing Samba share, Studio Code Server, or file editor that supports folder uploads. Do not put the folder under `www`.
3. Restart Home Assistant.
4. In the main SmartRace app, enable/start **SmartRace Connect Server**. Its paid server add-on must be available. Note the IP address and port shown by SmartRace; there is deliberately no assumed default port.
5. In Home Assistant open **Settings > Devices & services > Add integration**, search for **SmartRace Connect**, and enter that IP address and port. Enter only the address in the address field, without `ws://` or the port.
6. Open the new SmartRace device. Try a button while watching SmartRace. Start with the track idle and use Start/Stop only when ready to test their effects.

If the integration is missing from the list, refresh your browser after the Home Assistant restart and check Settings > System > Logs for `smartrace_connect` errors.

## Included controls

- Start, Stop, ESC, VSC, and Reload weather settings.
- A five-second time penalty button for each controller, 1–8.

These send the exact command forms in the official demo. ESC/VSC are command buttons rather than on/off switches: the public example does not establish separate on/off commands. Race-state behavior and required feature add-ons are controlled by SmartRace. Stop is not represented as an emergency power cutoff.

Analog sensor injection is intentionally excluded from the normal race dashboard; it is not required to control a digital race.

## Dashboard

Edit a dashboard, add a **Manual** card, and paste `dashboard.yaml`. The example assumes the generated entity IDs are `button.smartrace_start`, `button.smartrace_stop`, `button.smartrace_esc`, and `button.smartrace_vsc`. Confirm them on your SmartRace device page and replace them in the example if Home Assistant assigned different IDs. You can also add the buttons directly using the dashboard editor.

## Automations

Use **Button: Press** as an action and select the desired SmartRace button. Equivalent action YAML:

```yaml
action: button.press
target:
  entity_id: button.smartrace_start
```

No `configuration.yaml` changes are needed.

## Connection and delivery

The integration opens one persistent WebSocket connection at startup and reuses it for every button press. Incoming messages are drained and standard WebSocket heartbeat checks detect an unresponsive server. After a disconnect it reconnects automatically, with retry delays increasing from one second to a maximum of 30 seconds. Removing/reloading the integration, changing its address, or stopping Home Assistant closes the connection cleanly. The official demo sends commands without an application login or initial registration, and this integration follows it. Commands are serialized and never automatically retried, to avoid repeating a penalty or toggle after uncertain delivery. A successful press means the message was sent, not that SmartRace confirmed execution: the public demo specifies no command acknowledgement. There is no race-state sensor in this package. A Connection binary sensor tracks the live WebSocket and a Server address sensor shows the configured endpoint. Button presses while disconnected report an error; commands are never queued for later execution.

Home Assistant must reach the SmartRace device on its LAN IP and displayed port; guest Wi-Fi isolation can prevent this. Reserve the SmartRace device's IP in your router if possible. Commands use unencrypted `ws://` on your local network. Do not expose this server to the internet. Browser mixed-content restrictions do not apply to these server-side connections.

If the address or port changes, open Settings > Devices & services > SmartRace Connect, open the three-dot menu for the SmartRace entry, and select Reconfigure. Enter the new address and port, then submit. The new connection is checked before saving and the integration reloads automatically. Existing buttons, dashboard references, and automations are retained. If the check fails, the saved connection remains unchanged.

## Validation and limits

The package includes transport tests using a local mock WebSocket server. It has not been tested inside your Home Assistant installation or against your live SmartRace server. A listening WebSocket endpoint is checked during setup; this is a reachability check, not a verified SmartRace identity handshake.

Protocol reference: https://tools.smartrace.de/websocket-client/ and its linked `js/main.js`.
Manual: https://www.smartrace.de/en/the-smartrace-manual/websocket-client-demo/

## Remove

Remove the integration under Devices & services, delete `/config/custom_components/smartrace_connect`, and restart Home Assistant.

## Upgrade from smartrace_control (v1.0.6 or earlier)

This version changes the integration domain as well as its folder name. Home Assistant does not automatically move the old integration entry to a new domain. Do not simply rename the installed folder while leaving the old entry configured.

1. Make a Home Assistant backup. Note the existing server address/port and entity IDs from the SmartRace device page, including any disabled entities or customizations you want to retain.
2. While the old integration files are still installed, remove its SmartRace entry in Settings > Devices & services. This stops its connection and removes its registered entities. Historical data migration is not included.
3. Remove the old `/config/custom_components/smartrace_control/` folder. Copy this package's `smartrace_connect` folder to `/config/custom_components/smartrace_connect/`.
4. Restart Home Assistant.
5. Add **SmartRace Connect** again with the recorded address and port.
6. Compare the new entity IDs with your recorded IDs. Use each entity's settings to restore its previous entity ID where needed, then verify dashboard and automation references. New default entity IDs may start with `smartrace_connect_` because the device is named SmartRace Connect. The included YAML examples use that prefix; verify the actual IDs.

The connection, server-address sensors, persistent WebSocket, reconfiguration, supplied logo, and device attribution are included. Stored entry/device identifiers change with this domain migration; retaining the old config entry, history links, and device-based automation references is not automatic. Update device-based automations to select the new device.
