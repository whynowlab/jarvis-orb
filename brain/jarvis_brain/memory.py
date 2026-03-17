"""Jarvis Brain Lite — Memory Compiler.

4-tier memory with FTS5, temporal scoring, observation metadata.
Extracted from ~/.claude/jarvis/memory_compiler.py (lightweight).
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

import aiosqlite

from .config import DB_PATH, ensure_dirs
from .schemas import MemoryEntry, MemoryType

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    project TEXT NOT NULL DEFAULT '',
    tags TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL DEFAULT 1.0,
    source TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    last_validated TEXT NOT NULL,
    ttl_days INTEGER NOT NULL DEFAULT 90,
    superseded_by TEXT DEFAULT NULL,
    contradicted_by TEXT DEFAULT NULL,
    verification_status TEXT NOT NULL DEFAULT 'unverified'
)
"""

_CREATE_FTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    id UNINDEXED, content, project, tags,
    memory_type UNINDEXED, content=memories, content_rowid=rowid
)
"""

_FTS_TRIGGERS = [
    """CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
        INSERT INTO memories_fts(rowid, id, content, project, tags, memory_type)
        VALUES (new.rowid, new.id, new.content, new.project, new.tags, new.memory_type);
    END""",
    """CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, id, content, project, tags, memory_type)
        VALUES ('delete', old.rowid, old.id, old.content, old.project, old.tags, old.memory_type);
    END""",
    """CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, id, content, project, tags, memory_type)
        VALUES ('delete', old.rowid, old.id, old.content, old.project, old.tags, old.memory_type);
        INSERT INTO memories_fts(rowid, id, content, project, tags, memory_type)
        VALUES (new.rowid, new.id, new.content, new.project, new.tags, new.memory_type);
    END""",
]


class MemoryCompiler:
    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = db_path if db_path == ":memory:" else Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        if isinstance(self.db_path, Path):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(str(self.db_path))
        self._db.row_factory = aiosqlite.Row
        await self._db.execute(_CREATE_TABLE)
        await self._db.execute(_CREATE_FTS)
        for t in _FTS_TRIGGERS:
            await self._db.execute(t)
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

    def _ensure_db(self):
        if self._db is None:
            raise RuntimeError("Not initialized. Call initialize() first.")

    async def save(self, entry: MemoryEntry) -> None:
        self._ensure_db()
        await self._db.execute(
            """INSERT OR REPLACE INTO memories
               (id, memory_type, content, project, tags, confidence,
                source, created_at, last_validated, ttl_days,
                superseded_by, contradicted_by, verification_status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (entry.id, entry.memory_type.value, entry.content, entry.project,
             json.dumps(entry.tags), entry.confidence, entry.source,
             entry.created_at.isoformat(), entry.last_validated.isoformat(),
             entry.ttl_days, entry.superseded_by, entry.contradicted_by,
             entry.verification_status),
        )
        await self._db.commit()

    async def query(self, memory_type: Optional[MemoryType] = None,
                    project: Optional[str] = None, limit: int = 50) -> List[MemoryEntry]:
        self._ensure_db()
        clauses, params = [], []
        if memory_type:
            clauses.append("memory_type = ?"); params.append(memory_type.value)
        if project:
            clauses.append("project = ?"); params.append(project)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM memories {where} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        cursor = await self._db.execute(sql, params)
        return [self._row_to_entry(r) for r in await cursor.fetchall()]

    @staticmethod
    def _sanitize_fts_query(query: str) -> str:
        """Sanitize user input for FTS5 MATCH: strip special syntax, keep words."""
        # Remove FTS5 special chars: " ( ) * : ^
        cleaned = re.sub(r'[":()^*]', ' ', query)
        # Collapse whitespace
        tokens = cleaned.split()
        if not tokens:
            return '""'
        # Join as space-separated terms (implicit AND in FTS5)
        return " ".join(tokens)

    async def search(self, query: str, limit: int = 20) -> List[MemoryEntry]:
        self._ensure_db()
        safe_query = self._sanitize_fts_query(query)
        if not safe_query:
            return []
        sql = """SELECT m.* FROM memories m
                 WHERE m.rowid IN (
                     SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?
                 )
                 ORDER BY m.created_at DESC LIMIT ?"""
        try:
            cursor = await self._db.execute(sql, (safe_query, min(limit, 100)))
            return [self._row_to_entry(r) for r in await cursor.fetchall()]
        except Exception:
            return []

    async def delete_by_ids(self, ids: List[str]) -> int:
        """Delete memories by their IDs."""
        self._ensure_db()
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        await self._db.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", ids)
        await self._db.commit()
        return len(ids)

    async def supersede(self, old_id: str, new_id: str) -> None:
        self._ensure_db()
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE memories SET superseded_by=?, verification_status='stale', last_validated=? WHERE id=?",
            (new_id, now, old_id))
        await self._db.commit()

    async def contradict(self, id_a: str, id_b: str) -> None:
        self._ensure_db()
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE memories SET contradicted_by=?, verification_status='contradicted', last_validated=? WHERE id=?",
            (id_b, now, id_a))
        await self._db.execute(
            "UPDATE memories SET contradicted_by=?, verification_status='contradicted', last_validated=? WHERE id=?",
            (id_a, now, id_b))
        await self._db.commit()

    async def verify(self, memory_id: str) -> None:
        self._ensure_db()
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE memories SET verification_status='verified', last_validated=? WHERE id=?",
            (now, memory_id))
        await self._db.commit()

    @staticmethod
    def _row_to_entry(row: aiosqlite.Row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"], memory_type=MemoryType(row["memory_type"]),
            content=row["content"], project=row["project"],
            tags=json.loads(row["tags"]), confidence=row["confidence"],
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_validated=datetime.fromisoformat(row["last_validated"]),
            ttl_days=row["ttl_days"], superseded_by=row["superseded_by"],
            contradicted_by=row["contradicted_by"],
            verification_status=row["verification_status"],
        )
