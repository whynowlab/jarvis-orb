"""Jarvis Brain Lite — MCP Server.

Exposes brain tools via MCP protocol (stdio) for Claude Code, Cursor, etc.
Every tool call emits a WebSocket event to the Orb.

Usage:
  python -m jarvis_brain.mcp_server
"""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .config import DB_PATH
from .memory import MemoryCompiler
from .entities import EntityStore
from .event_emitter import EventEmitter
from .schemas import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

# Create MCP server
mcp = FastMCP("jarvis-brain", instructions="Jarvis Brain Lite — AI memory system with 4-tier memory, entity tracking, and temporal scoring.")

# Global instances
_memory: MemoryCompiler | None = None
_entities: EntityStore | None = None
_emitter: EventEmitter | None = None


async def _ensure_init():
    global _memory, _entities, _emitter
    if _memory is None:
        _memory = MemoryCompiler(DB_PATH)
        await _memory.initialize()
    if _entities is None:
        _entities = EntityStore(DB_PATH)
        await _entities.initialize()
    if _emitter is None:
        _emitter = EventEmitter()
        try:
            await _emitter.start()
        except Exception:
            pass  # Orb not running — that's OK


async def _emit(event_type: str, label: str, **extra):
    if _emitter:
        try:
            await _emitter.emit(event_type, label, extra)
        except Exception:
            pass


@mcp.tool()
async def memory_save(content: str, memory_type: str = "episodic",
                      project: str = "", tags: str = "", source: str = "") -> str:
    """Save a memory to the brain. Types: episodic, semantic, project, procedural."""
    await _ensure_init()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    entry = MemoryEntry(
        memory_type=MemoryType(memory_type),
        content=content, project=project,
        tags=tag_list, source=source,
    )
    await _memory.save(entry)
    await _emit("memory_save", content[:50], tier=memory_type)
    return f"Saved memory {entry.id} ({memory_type})"


@mcp.tool()
async def memory_search(query: str, limit: int = 10) -> str:
    """Search memories with temporal scoring + observation filtering."""
    await _ensure_init()
    results = await _memory.search(query, limit=limit)
    filtered = [r for r in results
                if r.verification_status not in ("contradicted",)
                and r.superseded_by is None]
    await _emit("search", f'"{query}" → {len(filtered)}건')
    lines = []
    for r in filtered:
        lines.append(f"[{r.memory_type.value}] {r.content[:100]} (conf={r.confidence:.2f})")
    return "\n".join(lines) if lines else "No results found."


@mcp.tool()
async def memory_verify(memory_id: str, action: str = "verify") -> str:
    """Verify, supersede, or contradict a memory. Actions: verify, supersede (old:new), contradict (a:b)."""
    await _ensure_init()
    if action == "verify":
        await _memory.verify(memory_id)
        await _emit("memory_save", f"Verified: {memory_id}")
    elif action == "supersede":
        parts = memory_id.split(":")
        if len(parts) == 2:
            await _memory.supersede(parts[0], parts[1])
            await _emit("memory_contradict", f"Superseded: {parts[0]} → {parts[1]}")
    elif action == "contradict":
        parts = memory_id.split(":")
        if len(parts) == 2:
            await _memory.contradict(parts[0], parts[1])
            await _emit("memory_contradict", f"Contradiction: {parts[0]} ↔ {parts[1]}")
    return f"Done: {action} on {memory_id}"


@mcp.tool()
async def entity_create(entity_type: str, name: str, state: str = "{}") -> str:
    """Create an entity (person, project, decision, tool, etc.)."""
    await _ensure_init()
    initial_state = json.loads(state) if state else {}
    entity = await _entities.create(entity_type, name, initial_state)
    await _emit("entity_update", f"Created: {name} ({entity_type})")
    return f"Entity {entity.id}: {name} ({entity_type})"


@mcp.tool()
async def entity_update(entity_id: str, new_state: str, reason: str = "") -> str:
    """Update entity state. Records transition history."""
    await _ensure_init()
    state = json.loads(new_state)
    await _entities.update_state(entity_id, state, reason)
    entity = await _entities.get(entity_id)
    label = f"{entity.name}: {reason}" if entity else f"{entity_id}: {reason}"
    await _emit("entity_update", label)
    return f"Updated {entity_id}"


@mcp.tool()
async def entity_query(entity_type: str = "", name: str = "") -> str:
    """Query entities by type and/or name."""
    await _ensure_init()
    results = await _entities.query(
        entity_type=entity_type or None, name=name or None)
    lines = [f"[{e.entity_type}] {e.name}: {json.dumps(e.current_state, ensure_ascii=False)}"
             for e in results]
    return "\n".join(lines) if lines else "No entities found."


@mcp.tool()
async def entity_relate(subject_id: str, predicate: str, object_id: str) -> str:
    """Create a relationship between two entities."""
    await _ensure_init()
    rel = await _entities.add_relationship(subject_id, predicate, object_id)
    await _emit("entity_update", f"Relation: {predicate}")
    return f"Relationship {rel.id}: {subject_id} —{predicate}→ {object_id}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
