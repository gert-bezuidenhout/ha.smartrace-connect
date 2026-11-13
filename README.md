# SmartRace Connect for Home Assistant

<img src="custom_components/smartrace_connect/brand/logo.png" alt="SmartRace Connect" width="128" height="128">

[Home Assistant](https://www.home-assistant.io/) is an open-source platform that brings devices, dashboards and automations together, with an emphasis on local control and privacy.

[SmartRace](https://www.smartrace.de/en/) is a slot-car racing app for lap counting, timing, driver and car management, practice, qualifying and races.

This is an independent community integration maintained by Gert Bezuidenhout, not an official SmartRace or Home Assistant product.

Send race-control commands from Home Assistant to SmartRace over your local network.

## What it does

- Start, Stop, ESC, VSC and reload-weather buttons.
- Five-second time-penalty buttons for controllers 1–8.
- Connection indicator and server-address sensor.
- Automatic reconnection and UI reconfiguration when the server address changes.

**Connect sends commands.** [SmartRace Receiver](https://github.com/gert-bezuidenhout/ha.smartrace-receiver) receives race data. They are separate integrations and can be used together.

## Install with HACS

These integrations have not yet been accepted into the default HACS Marketplace catalogue. For now, install through HACS as a custom repository:

1. Install and configure [HACS](https://www.hacs.xyz/docs/use/) in Home Assistant if needed.
2. Open HACS, open its menu and select **Custom repositories**.
3. Add `https://github.com/gert-bezuidenhout/ha.smartrace-connect` with type **Integration**.
4. Find **SmartRace Connect**, download it and restart Home Assistant.
5. Open **Settings > Devices & services > Add integration** and select **SmartRace Connect**.

Once the repository is accepted into the default catalogue, the custom-repository step will no longer be needed. HACS downloads the integration; adding it under Devices & services completes setup. No configuration.yaml changes are required.

## Configure SmartRace

Enable **SmartRace Connect Server** in the main SmartRace app; its required server add-on must be available. Enter the IP address and port shown by SmartRace in the integration setup form. Enter the address without a scheme or port in the address field.

Home Assistant must be able to reach that address on the local network. No MQTT broker or additional intermediary server is needed.

## Use the controls

Open the SmartRace Connect device in Home Assistant and press a button, or add buttons using the dashboard editor. Optional examples are in [dashboard.yaml](dashboard.yaml) and [status-card.yaml](status-card.yaml).

Automations use **Button: Press**, for example:

```yaml
action: button.press
target:
  entity_id: button.smartrace_connect_start
```

Check the actual entity ID on your device if you renamed it or Home Assistant assigned a different one.

## Connection behaviour

ESC and VSC are command buttons, not on/off switches. Their behaviour depends on SmartRace. A successful action means the command was sent, not that the app acknowledged execution. Commands are never queued or automatically retried, avoiding duplicate penalties or toggles after an uncertain connection.

To change the server address or port, use the **Configure** gear on the integration entry (the **Reconfigure** menu remains available). The connection is checked before the new settings are saved.

## Troubleshooting

- **Cannot connect:** ensure Connect Server is running and check its current address/port. Guest-network isolation can prevent access.
- **Command failed:** check SmartRace before retrying; delivery may be uncertain.
- **Integration not listed:** restart Home Assistant after download, refresh the browser and check its logs.
- **Need race data:** install Receiver separately; Connect does not supply lap or race-status data.

The connection uses local, unencrypted WebSocket traffic. Keep the server on a trusted network. Connection testing checks reachability, not a SmartRace identity handshake.

Protocol reference: [SmartRace WebSocket client documentation](https://www.smartrace.de/en/the-smartrace-manual/websocket-client-demo/).

## Updates and removal

Download updates through HACS and restart Home Assistant. Keep the existing integration entry when updating. Older installations should read [MIGRATION.md](MIGRATION.md).

To uninstall, remove the integration entry under Devices & services, remove its download in HACS and restart Home Assistant. Check any automations that used its entities.

## Support and project files

Report problems through [GitHub Issues](https://github.com/gert-bezuidenhout/ha.smartrace-connect/issues), including Home Assistant/integration versions, steps to reproduce and redacted logs.

See [repository file guide](docs/FILES.md) for what is included, and [Marketplace preparation](docs/HACS_SUBMISSION.md) for the maintainer checklist.

## Licence

Project code is licensed under the [MIT licence](LICENSE), copyright Gert Bezuidenhout. Product names and third-party branding remain the property of their respective owners; this project does not imply their endorsement.
