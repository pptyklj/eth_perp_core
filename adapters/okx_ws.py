import asyncio
import json
import logging
from typing import Callable, Optional
import websockets
from core.schemas import Candle

logger = logging.getLogger(__name__)


class OKXWebSocket:
    WS_URL = "wss://ws.okx.com:8443/ws/v5/public"

    def __init__(self, inst_id: str, on_candle: Callable[[Candle], None]):
        self.inst_id = inst_id
        self.on_candle = on_candle
        self.ws = None
        self._running = False

    async def _subscribe(self, websocket):
        msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "candle1m",
                    "instId": self.inst_id,
                }
            ],
        }
        await websocket.send(json.dumps(msg))

    async def _heartbeat(self, websocket):
        while self._running:
            try:
                await websocket.ping()
            except Exception:
                logger.warning("WebSocket ping failed")
                break
            await asyncio.sleep(10)

    async def _handle_message(self, message: str):
        try:
            data = json.loads(message)
            if "data" not in data:
                return
            for item in data.get("data", []):
                ts, o, h, l, c, vol, _, confirm = item
                if int(confirm) != 1:
                    continue
                candle = Candle(
                    ts=int(ts),
                    open=float(o),
                    high=float(h),
                    low=float(l),
                    close=float(c),
                    volume=float(vol),
                    confirm=int(confirm),
                    is_filled=True,
                )
                self.on_candle(candle)
        except Exception as exc:
            logger.error("WS parse error: %s", exc)

    async def _run(self):
        while self._running:
            try:
                async with websockets.connect(self.WS_URL) as websocket:
                    await self._subscribe(websocket)
                    heartbeat_task = asyncio.create_task(self._heartbeat(websocket))
                    async for message in websocket:
                        await self._handle_message(message)
                    heartbeat_task.cancel()
            except Exception as exc:
                logger.warning("WebSocket reconnecting after error: %s", exc)
                await asyncio.sleep(5)

    def start(self):  # pragma: no cover - integration path
        self._running = True
        asyncio.get_event_loop().run_until_complete(self._run())

    def stop(self):  # pragma: no cover - integration path
        self._running = False
