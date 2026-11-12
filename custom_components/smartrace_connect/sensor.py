"""Configured SmartRace server endpoint, visible even while disconnected."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SmartRaceServerAddress(entry, hass.data[DOMAIN][entry.entry_id])])


class SmartRaceServerAddress(SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Server address"
    _attr_should_poll = False
    _attr_icon = "mdi:server-network"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, client):
        self._attr_unique_id = f"{entry.entry_id}_server_address"
        self._attr_native_value = f"{client.host}:{client.port}"
        self._attr_extra_state_attributes = {
            "host": client.host, "port": client.port, "websocket_url": client.url,
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name="SmartRace Connect",
            manufacturer="Gert Bezuidenhout", model="SmartRace Connect",
        )
