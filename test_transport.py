"""Run with Python and aiohttp; no Home Assistant install required."""
import asyncio
import ast
import importlib.util
import json
from pathlib import Path
from aiohttp import ClientSession, web

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "transport", ROOT / "custom_components/smartrace_connect/client.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


async def main():
    received = []
    connections = []

    async def handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        connections.append(ws)
        async for message in ws:
            if message.type == web.WSMsgType.TEXT:
                received.append(json.loads(message.data))
        return ws

    app = web.Application()
    app.router.add_get("/", handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    site._port = port
    try:
        async with ClientSession() as session:
            client = module.SmartRaceClient(session, "127.0.0.1", port)
            transitions = []
            unsubscribe = client.subscribe(lambda: transitions.append(client.connected))
            assert client.host == "127.0.0.1" and client.port == port
            await client.probe()
            assert not received, "Setup must never send a race command"
            client.start()
            async def wait_for(predicate):
                async with asyncio.timeout(8):
                    while not predicate():
                        await asyncio.sleep(0.01)
            try:
                await wait_for(lambda: client.connected)
                messages = [{"type": "race_control", "data": {"value": value}}
                            for value in ("start", "stop", "esc", "vsc", "reload_weather_settings")]
                messages.append({"type": "race_control", "data": {
                    "value": "assign_penalty", "controller_id": 1,
                    "penalty_type": "time", "penalty_value": 5}})
                await asyncio.gather(*(client.send(p) for p in messages))
                await wait_for(lambda: len(received) == len(messages))
                assert received == messages
                assert len(connections) == 2, "Probe plus ONE persistent command connection"
                await asyncio.sleep(0.1)
                assert not connections[-1].closed, "Connection must remain open after commands"
                await site.stop()
                await connections[-1].close()
                await wait_for(lambda: not client.connected)
                try:
                    await client.send(messages[0])
                except module.CONNECTION_ERRORS:
                    pass
                else:
                    raise AssertionError("Offline command must fail")
                await site.start()
                await wait_for(lambda: client.connected and len(connections) == 3)
                assert received == messages, "Reconnect must not replay old or offline commands"
                await client.send(messages[1])
                await wait_for(lambda: len(received) == 7)
                assert received == messages + [messages[1]]
            finally:
                await client.stop()
            assert not client.connected and client._task is None
            assert transitions == [True, False, True, False], transitions
            unsubscribe()
            assert not client._listeners
            await wait_for(lambda: connections[-1].closed)
            count = len(connections)
            await asyncio.sleep(1.1)
            assert len(connections) == count, "Stopped clients must not reconnect"
    finally:
        await runner.cleanup()
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for path in ROOT.rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print("PASS: syntax, JSON, persistent reuse, disconnect, reconnect, no replay, shutdown, connection notifications, unsubscribe, endpoint")


asyncio.run(main())
