"""Jarvis Brain Lite — WebSocket Event Emitter.

Emits brain events to connected Orb clients.
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Set

import websockets
from websockets.server import WebSocketServerProtocol

from .config import WS_PORT

logger = logging.getLogger(__name__)


class EventEmitter:
    """WebSocket server that broadcasts brain events to Orb clients."""

    def __init__(self, port: int = WS_PORT) -> None:
        self.port = port
        self._clients: Set[WebSocketServerProtocol] = set()
        self._server = None

    async def start(self) -> None:
        self._server = await websockets.serve(
            self._handler, "localhost", self.port)
        logger.info("EventEmitter listening on ws://localhost:%d", self.port)

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def _handler(self, ws: WebSocketServerProtocol) -> None:
        self._clients.add(ws)
        logger.info("Orb connected (%d clients)", len(self._clients))
        try:
            await ws.wait_closed()
        finally:
            self._clients.discard(ws)
            logger.info("Orb disconnected (%d clients)", len(self._clients))

    async def emit(self, event_type: str, label: str = "",
                   extra: Dict[str, Any] = None) -> None:
        """Broadcast an event to all connected Orb clients."""
        event = {
            "type": event_type,
            "label": label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(extra or {}),
        }
        message = json.dumps(event, ensure_ascii=False)
        if self._clients:
            await asyncio.gather(
                *[c.send(message) for c in self._clients],
                return_exceptions=True,
            )

    @property
    def client_count(self) -> int:
        return len(self._clients)
