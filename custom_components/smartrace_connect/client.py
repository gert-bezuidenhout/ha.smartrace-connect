"""Direct SmartRace WebSocket transport; no automatic command retries."""
import asyncio
import logging
from contextlib import suppress

from aiohttp import ClientError, WSMsgType

_LOGGER = logging.getLogger(__name__)


class SmartRaceClient:
    def __init__(self, session, host, port):
        self.session = session
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"
        self.lock = asyncio.Lock()
        self._ws = None
        self._task = None
        self._stopping = False
        self._listeners = set()
        self._reported_connected = False

    def subscribe(self, listener):
        """Subscribe to connection transitions; return an unsubscribe callback."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    def _notify_connection(self):
        state = self.connected
        if state == self._reported_connected:
            return
        self._reported_connected = state
        for listener in tuple(self._listeners):
            try:
                listener()
            except Exception:
                _LOGGER.exception("Error updating SmartRace connection listener")

    @property
    def connected(self):
        return self._ws is not None and not self._ws.closed

    def start(self, create_task=asyncio.create_task):
        if self._task is None:
            self._stopping = False
            self._task = create_task(self._run())

    async def stop(self):
        self._stopping = True
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

    async def _run(self):
        delay = 1
        try:
            while not self._stopping:
                ws = None
                try:
                    async with asyncio.timeout(10):
                        ws = await self.session.ws_connect(self.url, heartbeat=30)
                    self._ws = ws
                    self._notify_connection()
                    delay = 1
                    _LOGGER.debug("Connected to SmartRace")
                    # Drain incoming frames so pings, closes and errors are handled.
                    async for message in ws:
                        if message.type == WSMsgType.ERROR:
                            break
                except CONNECTION_ERRORS as err:
                    _LOGGER.debug("SmartRace connection unavailable: %s", err)
                finally:
                    self._ws = None
                    self._notify_connection()
                    if ws is not None:
                        await ws.close()
                if not self._stopping:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 30)
        finally:
            self._ws = None
            self._notify_connection()

    async def probe(self):
        async with asyncio.timeout(10):
            async with self.session.ws_connect(self.url):
                pass

    async def send(self, payload):
        # Serialize presses. Never replay a command after an uncertain delivery.
        async with self.lock:
            ws = self._ws
            if ws is None or ws.closed:
                raise OSError("SmartRace is disconnected; waiting for automatic reconnection")
            async with asyncio.timeout(10):
                await ws.send_json(payload)


CONNECTION_ERRORS = (ClientError, TimeoutError, OSError)
