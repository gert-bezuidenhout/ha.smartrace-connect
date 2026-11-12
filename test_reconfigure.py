"""Exercise reconfiguration decisions using a minimal HA flow harness."""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import voluptuous as vol
from voluptuous_serialize import convert

tree = ast.parse((Path(__file__).parent / "custom_components/smartrace_connect/config_flow.py").read_text())
tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
entry = SimpleNamespace(entry_id="stable-id", unique_id="old:1234", data={"host": "old", "port": 1234})
others = [entry]
probes = []

class Base:
    def __init_subclass__(cls, **kwargs): pass
    def _get_reconfigure_entry(self): return entry
    def _async_current_entries(self): return others
    def add_suggested_values_to_schema(self, schema, data):
        convert(schema)
        self.suggested = data
        return schema
    def async_show_form(self, **kwargs): return kwargs
    def async_update_reload_and_abort(self, target, data_updates, reason):
        assert target is entry
        target.data.update(data_updates)
        return {"reason": reason}

class Client:
    fail = False
    def __init__(self, session, host, port): self.address = (host, port)
    async def probe(self):
        probes.append(self.address)
        if self.fail: raise OSError("Offline")

namespace = {"vol": vol, "config_entries": SimpleNamespace(ConfigFlow=Base),
             "SmartRaceClient": Client, "CONNECTION_ERRORS": (OSError,),
             "async_get_clientsession": lambda hass: None}
exec(compile(tree, "config_flow.py", "exec"), namespace)
flow = namespace["SmartRaceConfigFlow"]()
flow.hass = SimpleNamespace(config_entries=SimpleNamespace(
    async_update_entry=lambda target, **values: [setattr(target, k, v) for k, v in values.items()]))

async def main():
    result = await flow.async_step_reconfigure()
    assert result["step_id"] == "reconfigure" and flow.suggested == entry.data
    result = await flow.async_step_reconfigure({"host": "ws://bad", "port": 1234})
    assert result["errors"] == {"host": "invalid_host"} and not probes
    Client.fail = True
    result = await flow.async_step_reconfigure({"host": "new", "port": 4321})
    assert result["errors"] == {"base": "cannot_connect"}
    assert entry.data == {"host": "old", "port": 1234} and entry.unique_id == "old:1234"
    Client.fail = False
    others.append(SimpleNamespace(entry_id="other", unique_id="new:4321", data={"host": "new", "port": 4321}))
    result = await flow.async_step_reconfigure({"host": "new", "port": 4321})
    assert result["errors"] == {"base": "already_configured"}
    others.pop()
    result = await flow.async_step_reconfigure({"host": " new ", "port": 4321})
    assert result["reason"] == "reconfigure_successful"
    assert entry.entry_id == "stable-id" and entry.data == {"host": "new", "port": 4321}
    assert entry.unique_id == "new:4321"
    result = await flow.async_step_reconfigure({"host": "new", "port": 4321})
    assert result["reason"] == "reconfigure_successful"
    print("PASS: form, validation, failed connection preserves settings, duplicates, successful update, unchanged address")

asyncio.run(main())
