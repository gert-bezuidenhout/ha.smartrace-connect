"""Set up SmartRace from the Home Assistant interface."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .client import SmartRaceClient, CONNECTION_ERRORS

DATA_SCHEMA = vol.Schema({
    vol.Required("host"): str,
    vol.Required("port"): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
})

def valid_host(value):
    value = str(value).strip()
    if not value or any(c in value for c in "/:?#@ "):
        raise vol.Invalid("Enter an IPv4 address or hostname without a port or scheme")
    return value


class SmartRaceConfigFlow(config_entries.ConfigFlow, domain="smartrace_connect"):
    VERSION = 1

    async def async_step_reconfigure(self, user_input=None):
        """Update the connection while retaining the entry and entity identities."""
        entry = self._get_reconfigure_entry()
        errors = {}
        if user_input is not None:
            try:
                host = valid_host(user_input["host"])
            except vol.Invalid:
                errors["host"] = "invalid_host"
            else:
                port = user_input["port"]
                unique_id = f"{host.lower()}:{port}"
                if any(other.entry_id != entry.entry_id and (
                    other.unique_id == unique_id or (
                        other.data["host"].lower() == host.lower()
                        and other.data["port"] == port
                    )
                ) for other in self._async_current_entries()):
                    errors["base"] = "already_configured"
                else:
                    client = SmartRaceClient(async_get_clientsession(self.hass), host, port)
                    try:
                        await client.probe()
                    except CONNECTION_ERRORS:
                        errors["base"] = "cannot_connect"
                    else:
                        self.hass.config_entries.async_update_entry(entry, unique_id=unique_id)
                        return self.async_update_reload_and_abort(
                            entry, data_updates={"host": host, "port": port},
                            reason="reconfigure_successful",
                        )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                DATA_SCHEMA, user_input if user_input is not None else entry.data
            ),
            errors=errors,
        )

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                host = valid_host(user_input["host"])
            except vol.Invalid:
                errors["host"] = "invalid_host"
            else:
                port = user_input["port"]
                await self.async_set_unique_id(f"{host.lower()}:{port}")
                self._abort_if_unique_id_configured()
                client = SmartRaceClient(async_get_clientsession(self.hass), host, port)
                try:
                    await client.probe()
                except CONNECTION_ERRORS:
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title="SmartRace Connect", data={"host": host, "port": port}
                    )
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
