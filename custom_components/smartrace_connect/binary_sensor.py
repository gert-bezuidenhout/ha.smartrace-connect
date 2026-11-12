"""Live SmartRace WebSocket connection status."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from . import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([SmartRaceConnection(entry, hass.data[DOMAIN][entry.entry_id])])


class SmartRaceConnection(BinarySensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Connection"
    _attr_should_poll = False
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, client):
        self.client = client
        self._attr_unique_id = f"{entry.entry_id}_connection"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name="SmartRace Connect",
            manufacturer="Gert Bezuidenhout", model="SmartRace Connect",
        )

    @property
    def is_on(self):
        return self.client.connected

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self.client.subscribe(self._connection_changed))

    @callback
    def _connection_changed(self):
        self.async_write_ha_state()
