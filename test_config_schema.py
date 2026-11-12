"""Regression test for setup form serialization, without importing HA."""
import ast
import json
from pathlib import Path
import voluptuous as vol
from voluptuous_serialize import convert

root = Path(__file__).parent
source = root / "custom_components/smartrace_connect/config_flow.py"
tree = ast.parse(source.read_text())
schema_nodes = [n for n in tree.body if
                isinstance(n, ast.FunctionDef) and n.name == "valid_host" or
                isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "DATA_SCHEMA" for t in n.targets)]
namespace = {"vol": vol}
exec(compile(ast.Module(body=schema_nodes, type_ignores=[]), str(source), "exec"), namespace)
schema = namespace["DATA_SCHEMA"]
json.dumps(convert(schema))
assert schema({"host": "192.168.1.20", "port": 1234})["port"] == 1234
for port in (0, 65536):
    try:
        schema({"host": "192.168.1.20", "port": port})
    except vol.Invalid:
        pass
    else:
        raise AssertionError("Invalid port accepted")
try:
    convert(vol.Schema({vol.Required("host"): namespace["valid_host"]}))
except ValueError:
    print("Reproduced original failure: custom host validator cannot be serialized")
else:
    raise AssertionError("Expected original schema to fail")
print("PASS: corrected setup form serializes to JSON; port validation passes")
