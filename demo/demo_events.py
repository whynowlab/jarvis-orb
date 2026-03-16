"""Demo event generator — sends sample brain events to Orb via WebSocket."""

import asyncio
import json
import random
from datetime import datetime, timezone

import websockets

EVENTS = [
    {"type": "session_start", "label": "Session initialized"},
    {"type": "memory_save", "label": "결정: SQLite 유지", "tier": "semantic"},
    {"type": "memory_save", "label": "프로젝트 상태 저장", "tier": "project"},
    {"type": "entity_update", "label": "jarvis-orb: planning → implementing"},
    {"type": "memory_save", "label": "회의 메모 저장", "tier": "episodic"},
    {"type": "memory_contradict", "label": "모순 감지: 이전 결정과 충돌"},
    {"type": "team_dispatch", "label": "strategy 팀 3명 투입"},
    {"type": "memory_save", "label": "배포 절차 기록", "tier": "procedural"},
    {"type": "search", "label": '메모리 검색: "auth module"'},
    {"type": "entity_update", "label": "PR #42: open → merged"},
    {"type": "team_result", "label": "팀 결과: CONDITIONAL GO"},
    {"type": "context_compact", "label": "컨텍스트 73% → 압축 실행"},
    {"type": "memory_save", "label": "선호사항 업데이트", "tier": "semantic"},
]


async def run_demo(ws_url="ws://localhost:9321", interval=3.0):
    """Connect to Orb and send events at intervals."""
    print(f"Connecting to {ws_url}...")

    while True:
        try:
            async with websockets.connect(ws_url) as ws:
                print("Connected to Orb. Sending demo events...")
                print("Press Ctrl+C to stop.\n")

                for event in EVENTS:
                    event["timestamp"] = datetime.now(timezone.utc).isoformat()
                    msg = json.dumps(event, ensure_ascii=False)
                    await ws.send(msg)
                    print(f"  → [{event['type']}] {event['label']}")
                    await asyncio.sleep(interval + random.uniform(-0.5, 1.0))

                # Loop
                print("\n  [Loop] Restarting demo sequence...\n")

        except ConnectionRefusedError:
            print(f"Cannot connect to {ws_url}. Retrying in 3s...")
            await asyncio.sleep(3)
        except websockets.exceptions.ConnectionClosed:
            print("Connection lost. Reconnecting...")
            await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\nDemo stopped.")
