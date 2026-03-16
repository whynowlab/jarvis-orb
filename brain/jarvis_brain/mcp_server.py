"""Jarvis Brain Lite — MCP Server.

Exposes brain tools via MCP protocol for Claude Code, Cursor, etc.
Every tool call emits a WebSocket event to the Orb.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from .config import DB_PATH
from .memory import MemoryCompiler
from .entities import EntityStore
from .event_emitter import EventEmitter
from .schemas import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

# Global instances
_memory: Optional[MemoryCompiler] = None
_entities: Optional[EntityStore] = None
_emitter: Optional[EventEmitter] = None


async def _ensure_initialized():
    global _memory, _entities, _emitter
    if _memory is None:
        _memory = MemoryCompiler(DB_PATH)
        await _memory.initialize()
    if _entities is None:
        _entities = EntityStore(DB_PATH)
        await _entities.initialize()
    if _emitter is None:
        _emitter = EventEmitter()
        await _emitter.start()


async def memory_save(content: str, memory_type: str = "episodic",
                      project: str = "", tags: str = "", source: str = "") -> str:
    """Save a memory to the brain. Auto-classifies into 4 tiers."""
    await _ensure_initialized()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    entry = MemoryEntry(
        memory_type=MemoryType(memory_type),
        content=content, project=project,
        tags=tag_list, source=source,
    )
    await _memory.save(entry)
    await _emitter.emit("memory_save", f"{content[:50]}...", {"tier": memory_type})
    return f"Saved memory {entry.id} ({memory_type})"


async def memory_search(query: str, limit: int = 10) -> str:
    """Search memories with temporal scoring + observation filtering."""
    await _ensure_initialized()
    results = await _memory.search(query, limit=limit)
    # Filter contradicted/superseded
    filtered = [r for r in results
                if r.verification_status not in ("contradicted",)
                and r.superseded_by is None]
    await _emitter.emit("search", f'검색: "{query}" → {len(filtered)}건')
    lines = []
    for r in filtered:
        lines.append(f"[{r.memory_type.value}] {r.content[:100]} (conf={r.confidence:.2f})")
    return "\n".join(lines) if lines else "No results found."


async def memory_verify(memory_id: str, action: str = "verify") -> str:
    """Verify, supersede, or mark a memory as contradicted."""
    await _ensure_initialized()
    if action == "verify":
        await _memory.verify(memory_id)
        await _emitter.emit("memory_save", f"Verified: {memory_id}")
    elif action == "supersede":
        # Expects format "old_id:new_id"
        parts = memory_id.split(":")
        if len(parts) == 2:
            await _memory.supersede(parts[0], parts[1])
            await _emitter.emit("memory_contradict", f"Superseded: {parts[0]} → {parts[1]}")
    elif action == "contradict":
        parts = memory_id.split(":")
        if len(parts) == 2:
            await _memory.contradict(parts[0], parts[1])
            await _emitter.emit("memory_contradict", f"Contradiction: {parts[0]} ↔ {parts[1]}")
    return f"Done: {action} on {memory_id}"


async def entity_create(entity_type: str, name: str, state: str = "{}") -> str:
    """Create a new entity (person, project, decision, etc.)."""
    await _ensure_initialized()
    initial_state = json.loads(state) if state else {}
    entity = await _entities.create(entity_type, name, initial_state)
    await _emitter.emit("entity_update", f"Created: {name} ({entity_type})")
    return f"Entity {entity.id}: {name} ({entity_type})"


async def entity_update(entity_id: str, new_state: str, reason: str = "") -> str:
    """Update an entity's state (records transition history)."""
    await _ensure_initialized()
    state = json.loads(new_state)
    await _entities.update_state(entity_id, state, reason)
    entity = await _entities.get(entity_id)
    label = f"{entity.name}: {reason}" if entity else f"{entity_id}: {reason}"
    await _emitter.emit("entity_update", label)
    return f"Updated {entity_id}"


async def entity_query(entity_type: str = "", name: str = "") -> str:
    """Query entities by type and/or name."""
    await _ensure_initialized()
    results = await _entities.query(
        entity_type=entity_type or None,
        name=name or None,
    )
    lines = []
    for e in results:
        lines.append(f"[{e.entity_type}] {e.name}: {json.dumps(e.current_state, ensure_ascii=False)}")
    return "\n".join(lines) if lines else "No entities found."


async def entity_link(entity_id: str, memory_id: str) -> str:
    """Link an entity to a memory."""
    await _ensure_initialized()
    await _entities.link_memory(entity_id, memory_id)
    return f"Linked entity {entity_id} ↔ memory {memory_id}"


async def entity_relate(subject_id: str, predicate: str, object_id: str) -> str:
    """Create a relationship between two entities."""
    await _ensure_initialized()
    rel = await _entities.add_relationship(subject_id, predicate, object_id)
    await _emitter.emit("entity_update", f"Relation: {predicate}")
    return f"Relationship {rel.id}: {subject_id} —{predicate}→ {object_id}"


async def distill(messages_json: str, project: str = "") -> str:
    """Extract structured memories from conversation messages."""
    await _ensure_initialized()
    messages = json.loads(messages_json)
    count = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, list):
            content = "\n".join(b.get("text", str(b)) if isinstance(b, dict) else str(b) for b in content)
        if content and len(content) > 20:
            entry = MemoryEntry(
                memory_type=MemoryType.EPISODIC,
                content=content[:500],
                project=project,
                tags=["distilled"],
                confidence=0.8,
                source="distill",
            )
            await _memory.save(entry)
            count += 1
    await _emitter.emit("context_compact", f"Distilled {count} memories")
    return f"Distilled {count} memories from {len(messages)} messages"


# ── CLI Entry Point ──

def main():
    """Run Brain Lite as standalone server."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    async def run():
        await _ensure_initialized()
        logger.info("Jarvis Brain Lite running")
        logger.info("  DB: %s", DB_PATH)
        logger.info("  MCP: ready")
        logger.info("  WebSocket: ws://localhost:%d", _emitter.port)
        # Keep running
        await asyncio.Future()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info("Shutting down")


if __name__ == "__main__":
    main()
