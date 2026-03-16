"""Tests for Brain Lite — memory + entities + relationships."""
import pytest
import pytest_asyncio

from jarvis_brain.memory import MemoryCompiler
from jarvis_brain.entities import EntityStore
from jarvis_brain.schemas import MemoryEntry, MemoryType


@pytest_asyncio.fixture
async def mc():
    c = MemoryCompiler(db_path=":memory:")
    await c.initialize()
    yield c
    await c.close()


@pytest_asyncio.fixture
async def es():
    s = EntityStore(db_path=":memory:")
    await s.initialize()
    yield s
    await s.close()


class TestMemory:
    @pytest.mark.asyncio
    async def test_save_and_query(self, mc):
        entry = MemoryEntry(memory_type=MemoryType.SEMANTIC, content="Use SQLite")
        await mc.save(entry)
        results = await mc.query(memory_type=MemoryType.SEMANTIC)
        assert len(results) == 1
        assert results[0].content == "Use SQLite"

    @pytest.mark.asyncio
    async def test_observation_fields(self, mc):
        entry = MemoryEntry(memory_type=MemoryType.SEMANTIC, content="Old fact",
                            id="old-1")
        await mc.save(entry)
        await mc.supersede("old-1", "new-1")
        results = await mc.query(memory_type=MemoryType.SEMANTIC)
        assert results[0].superseded_by == "new-1"
        assert results[0].verification_status == "stale"

    @pytest.mark.asyncio
    async def test_contradict(self, mc):
        a = MemoryEntry(id="a", memory_type=MemoryType.SEMANTIC, content="X true")
        b = MemoryEntry(id="b", memory_type=MemoryType.SEMANTIC, content="X false")
        await mc.save(a)
        await mc.save(b)
        await mc.contradict("a", "b")
        results = await mc.query(memory_type=MemoryType.SEMANTIC, limit=10)
        ea = next(r for r in results if r.id == "a")
        assert ea.verification_status == "contradicted"

    @pytest.mark.asyncio
    async def test_search(self, mc):
        await mc.save(MemoryEntry(memory_type=MemoryType.SEMANTIC, content="deploy to vercel"))
        results = await mc.search("deploy")
        assert len(results) >= 1


class TestEntities:
    @pytest.mark.asyncio
    async def test_create_and_get(self, es):
        entity = await es.create("project", "jarvis", {"status": "active"})
        fetched = await es.get(entity.id)
        assert fetched.name == "jarvis"

    @pytest.mark.asyncio
    async def test_state_transition(self, es):
        entity = await es.create("pr", "PR #42", {"status": "open"})
        await es.update_state(entity.id, {"status": "merged"}, "approved")
        history = await es.get_history(entity.id)
        assert len(history) == 1
        assert history[0].to_state["status"] == "merged"

    @pytest.mark.asyncio
    async def test_relationship(self, es):
        p = await es.create("person", "DD")
        proj = await es.create("project", "jarvis-orb")
        rel = await es.add_relationship(p.id, "works_on", proj.id)
        assert rel.predicate == "works_on"
        rels = await es.get_relationships(p.id)
        assert len(rels) == 1

    @pytest.mark.asyncio
    async def test_memory_link(self, es):
        entity = await es.create("decision", "Use SQLite")
        await es.link_memory(entity.id, "mem-001")
        memories = await es.get_linked_memories(entity.id)
        assert "mem-001" in memories
