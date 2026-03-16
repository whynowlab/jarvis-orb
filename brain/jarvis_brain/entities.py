"""Jarvis Brain Lite — Entity Store with relationships.

Lightweight KG: entities + transitions + relationships + memory links.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from .config import DB_PATH
from .schemas import Entity, EntityTransition, Relationship

_CREATE_ENTITIES = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    name TEXT NOT NULL,
    current_state TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    last_updated TEXT NOT NULL
)"""

_CREATE_TRANSITIONS = """
CREATE TABLE IF NOT EXISTS entity_transitions (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    from_state TEXT NOT NULL DEFAULT '{}',
    to_state TEXT NOT NULL DEFAULT '{}',
    reason TEXT NOT NULL DEFAULT '',
    timestamp TEXT NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)"""

_CREATE_MEMORY_LINKS = """
CREATE TABLE IF NOT EXISTS entity_memory_links (
    entity_id TEXT NOT NULL,
    memory_id TEXT NOT NULL,
    linked_at TEXT NOT NULL,
    UNIQUE(entity_id, memory_id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
)"""

_CREATE_RELATIONSHIPS = """
CREATE TABLE IF NOT EXISTS relationships (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 1.0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES entities(id),
    FOREIGN KEY (object_id) REFERENCES entities(id)
)"""


class EntityStore:
    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = db_path if db_path == ":memory:" else Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA foreign_keys = ON")
        for sql in [_CREATE_ENTITIES, _CREATE_TRANSITIONS, _CREATE_MEMORY_LINKS, _CREATE_RELATIONSHIPS]:
            await self._db.execute(sql)
        await self._db.commit()

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, *exc):
        await self.close()

    async def create(self, entity_type: str, name: str,
                     initial_state: Dict[str, Any] = None) -> Entity:
        assert self._db
        now = datetime.now(timezone.utc).isoformat()
        entity = Entity(
            id=str(uuid.uuid4())[:8], entity_type=entity_type, name=name,
            current_state=initial_state or {}, created_at=now, last_updated=now,
        )
        await self._db.execute(
            "INSERT INTO entities (id, entity_type, name, current_state, created_at, last_updated) VALUES (?,?,?,?,?,?)",
            (entity.id, entity.entity_type, entity.name,
             json.dumps(entity.current_state), entity.created_at, entity.last_updated))
        await self._db.commit()
        return entity

    async def get(self, entity_id: str) -> Optional[Entity]:
        assert self._db
        cursor = await self._db.execute("SELECT * FROM entities WHERE id=?", (entity_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return Entity(id=row["id"], entity_type=row["entity_type"], name=row["name"],
                      current_state=json.loads(row["current_state"]),
                      created_at=row["created_at"], last_updated=row["last_updated"])

    async def update_state(self, entity_id: str, new_state: Dict[str, Any], reason: str = "") -> None:
        assert self._db
        entity = await self.get(entity_id)
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")
        now = datetime.now(timezone.utc).isoformat()
        tid = str(uuid.uuid4())[:8]
        await self._db.execute(
            "INSERT INTO entity_transitions (id, entity_id, from_state, to_state, reason, timestamp) VALUES (?,?,?,?,?,?)",
            (tid, entity_id, json.dumps(entity.current_state), json.dumps(new_state), reason, now))
        await self._db.execute(
            "UPDATE entities SET current_state=?, last_updated=? WHERE id=?",
            (json.dumps(new_state), now, entity_id))
        await self._db.commit()

    async def get_history(self, entity_id: str) -> List[EntityTransition]:
        assert self._db
        cursor = await self._db.execute(
            "SELECT * FROM entity_transitions WHERE entity_id=? ORDER BY timestamp", (entity_id,))
        rows = await cursor.fetchall()
        return [EntityTransition(id=r["id"], entity_id=r["entity_id"],
                from_state=json.loads(r["from_state"]), to_state=json.loads(r["to_state"]),
                reason=r["reason"], timestamp=r["timestamp"]) for r in rows]

    async def link_memory(self, entity_id: str, memory_id: str) -> None:
        assert self._db
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT OR IGNORE INTO entity_memory_links (entity_id, memory_id, linked_at) VALUES (?,?,?)",
            (entity_id, memory_id, now))
        await self._db.commit()

    async def get_linked_memories(self, entity_id: str) -> List[str]:
        assert self._db
        cursor = await self._db.execute(
            "SELECT memory_id FROM entity_memory_links WHERE entity_id=?", (entity_id,))
        return [r["memory_id"] for r in await cursor.fetchall()]

    async def add_relationship(self, subject_id: str, predicate: str,
                                object_id: str, confidence: float = 1.0) -> Relationship:
        assert self._db
        now = datetime.now(timezone.utc).isoformat()
        rel = Relationship(id=str(uuid.uuid4())[:8], subject_id=subject_id,
                           predicate=predicate, object_id=object_id,
                           confidence=confidence, created_at=now)
        await self._db.execute(
            "INSERT INTO relationships (id, subject_id, predicate, object_id, confidence, created_at) VALUES (?,?,?,?,?,?)",
            (rel.id, rel.subject_id, rel.predicate, rel.object_id, rel.confidence, rel.created_at))
        await self._db.commit()
        return rel

    async def get_relationships(self, entity_id: str) -> List[Relationship]:
        assert self._db
        cursor = await self._db.execute(
            "SELECT * FROM relationships WHERE subject_id=? OR object_id=?",
            (entity_id, entity_id))
        return [Relationship(id=r["id"], subject_id=r["subject_id"], predicate=r["predicate"],
                object_id=r["object_id"], confidence=r["confidence"],
                created_at=r["created_at"]) for r in await cursor.fetchall()]

    async def query(self, entity_type: str = None, name: str = None,
                    limit: int = 50) -> List[Entity]:
        assert self._db
        clauses, params = [], []
        if entity_type:
            clauses.append("entity_type=?"); params.append(entity_type)
        if name:
            clauses.append("name=?"); params.append(name)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        cursor = await self._db.execute(
            f"SELECT * FROM entities {where} ORDER BY last_updated DESC LIMIT ?",
            params + [limit])
        rows = await cursor.fetchall()
        return [Entity(id=r["id"], entity_type=r["entity_type"], name=r["name"],
                current_state=json.loads(r["current_state"]),
                created_at=r["created_at"], last_updated=r["last_updated"]) for r in rows]
