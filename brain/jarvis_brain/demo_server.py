"""Standalone WebSocket server for demo/testing.

Runs Brain Lite's WebSocket server and sends demo events.
Usage: python -m jarvis_brain.demo_server
"""

import asyncio
import json
import random
from datetime import datetime, timezone

import websockets
from websockets.server import WebSocketServerProtocol

from .config import WS_PORT

clients: set[WebSocketServerProtocol] = set()

EVENTS = [
    {"type": "session_start", "label": "Session initialized"},
    {"type": "memory_save", "label": "Decision: Use SQLite", "tier": "semantic"},
    {"type": "memory_save", "label": "Project state saved", "tier": "project"},
    {"type": "entity_update", "label": "jarvis-orb: planning → implementing"},
    {"type": "memory_save", "label": "Meeting notes saved", "tier": "episodic"},
    {"type": "memory_contradict", "label": "Contradiction detected: conflicts with prior decision"},
    {"type": "team_dispatch", "label": "strategy team dispatched (3 agents)"},
    {"type": "memory_save", "label": "Deploy procedure recorded", "tier": "procedural"},
    {"type": "search", "label": 'Memory search: "auth module"'},
    {"type": "entity_update", "label": "PR #42: open → merged"},
    {"type": "team_result", "label": "Team result: CONDITIONAL GO"},
    {"type": "context_compact", "label": "Context 73% → compaction triggered"},
    {"type": "memory_save", "label": "Preference updated", "tier": "semantic"},
]


async def handler(ws: WebSocketServerProtocol, path: str = "/"):
    clients.add(ws)
    print(f"[Orb connected] ({len(clients)} clients)")
    try:
        await ws.wait_closed()
    finally:
        clients.discard(ws)
        print(f"[Orb disconnected] ({len(clients)} clients)")


async def broadcast(event: dict):
    if not clients:
        return
    msg = json.dumps(event, ensure_ascii=False)
    await asyncio.gather(*[c.send(msg) for c in clients], return_exceptions=True)


async def demo_loop(interval: float = 3.0):
    """Send demo events in a loop."""
    print(f"\nDemo mode: sending events every ~{interval}s")
    print("Waiting for Orb to connect...\n")

    while True:
        if clients:
            event = random.choice(EVENTS).copy()
            event["timestamp"] = datetime.now(timezone.utc).isoformat()
            await broadcast(event)
            print(f"  → [{event['type']}] {event['label']}")

        await asyncio.sleep(interval + random.uniform(-0.5, 1.0))


async def main():
    print(f"Jarvis Brain — Demo Server")
    print(f"WebSocket: ws://localhost:{WS_PORT}")
    print(f"Start the Orb app, then events will flow.\n")

    server = await websockets.serve(handler, "localhost", WS_PORT)
    await demo_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
