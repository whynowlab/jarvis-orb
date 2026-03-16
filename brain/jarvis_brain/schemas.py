"""Jarvis Brain Lite — Data Schemas."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROJECT = "project"
    PROCEDURAL = "procedural"


@dataclass
class MemoryEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memory_type: MemoryType = MemoryType.EPISODIC
    content: str = ""
    project: str = ""
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0
    source: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_validated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_days: int = 90
    superseded_by: Optional[str] = None
    contradicted_by: Optional[str] = None
    verification_status: str = "unverified"


@dataclass
class Entity:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    entity_type: str = ""
    name: str = ""
    current_state: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_updated: str = ""


@dataclass
class EntityTransition:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    entity_id: str = ""
    from_state: Dict[str, Any] = field(default_factory=dict)
    to_state: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    timestamp: str = ""


@dataclass
class Relationship:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    subject_id: str = ""
    predicate: str = ""
    object_id: str = ""
    confidence: float = 1.0
    created_at: str = ""
