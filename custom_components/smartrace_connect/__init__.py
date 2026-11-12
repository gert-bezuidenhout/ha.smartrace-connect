"""SmartRace direct control integration."""
from homeassistant.const import Platform, EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .client import SmartRaceClient

DOMAIN = "smartrace_connect"
PLATFORMS = [Platform.BUTTON, Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass, entry):
    if entry.title in ("SmartRace", "SmartRace Direct Control"):
        hass.config_entries.async_update_entry(entry, title="SmartRace Connect")
    client = SmartRaceClient(
        async_get_clientsession(hass), entry.data["host"], entry.data["port"]
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client
    client.start(lambda coro: hass.async_create_background_task(coro, "SmartRace connection"))

    async def async_stop(event):
        await client.stop()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_stop))
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await client.stop()
        hass.data[DOMAIN].pop(entry.entry_id, None)
        raise
    return True


async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop()
        return True
    return False
