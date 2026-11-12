"""SmartRace command buttons."""
from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN
from .client import CONNECTION_ERRORS

COMMANDS = (
    ("start", "Start", "mdi:play"),
    ("stop", "Stop", "mdi:stop"),
    ("esc", "ESC", "mdi:car-emergency"),
    ("vsc", "VSC", "mdi:car-speed-limiter"),
    ("reload_weather_settings", "Reload weather settings", "mdi:weather-partly-cloudy"),
)


async def async_setup_entry(hass, entry, async_add_entities):
    client = hass.data[DOMAIN][entry.entry_id]
    entities = [SmartRaceButton(entry, client, key, name, icon,
                {"type": "race_control", "data": {"value": key}})
                for key, name, icon in COMMANDS]
    for controller in range(1, 9):
        entities.append(SmartRaceButton(
            entry, client, f"penalty_{controller}",
            f"Controller {controller} penalty 5 seconds", "mdi:timer-plus",
            {"type": "race_control", "data": {
                "value": "assign_penalty", "controller_id": controller,
                "penalty_type": "time", "penalty_value": 5,
            }},
        ))
    async_add_entities(entities)


class SmartRaceButton(ButtonEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry, client, key, name, icon, payload):
        self.client, self.payload = client, payload
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name="SmartRace Connect",
            manufacturer="Gert Bezuidenhout", model="SmartRace Connect",
        )

    async def async_press(self):
        try:
            await self.client.send(self.payload)
        except CONNECTION_ERRORS as err:
            raise HomeAssistantError(
                "Could not send to SmartRace. Check that its Connect Server is running "
                "and reachable. Delivery may be uncertain; check SmartRace before retrying."
            ) from err
