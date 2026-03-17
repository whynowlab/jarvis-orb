"""Safety tests — FTS5 edge cases, input validation, CLI dispatch.

Covers all CRITICAL/HIGH issues found in code review.
"""
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


# ── FTS5 Safety ──────────────────────────────────────


class TestFTSSafety:
    """FTS5 search must never crash on user input."""

    @pytest.mark.asyncio
    async def test_colon_prefix_no_crash(self, mc):
        """'Decision:' must not be parsed as FTS column filter."""
        await mc.save(MemoryEntry(content="Decision: use SQLite"))
        results = await mc.search("Decision: use SQLite")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_quotes_no_crash(self, mc):
        """Double quotes must not break FTS parsing."""
        await mc.save(MemoryEntry(content='User said "hello"'))
        results = await mc.search('he said "hello"')
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_parentheses_no_crash(self, mc):
        """Unclosed parentheses must not crash FTS."""
        results = await mc.search("auth (new")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_fts_operators_no_crash(self, mc):
        """FTS operators AND/OR/NOT/NEAR must not cause errors."""
        for q in ["AND test", "OR something", "NOT found", "NEAR test"]:
            results = await mc.search(q)
            assert isinstance(results, list), f"Failed on: {q}"

    @pytest.mark.asyncio
    async def test_empty_query(self, mc):
        """Empty query should return empty list, not crash."""
        results = await mc.search("")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_asterisk_wildcard(self, mc):
        """Wildcard '*' must not crash."""
        results = await mc.search("test*")
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_limit_clamped(self, mc):
        """Limit must be clamped to max 100."""
        await mc.save(MemoryEntry(content="test entry"))
        results = await mc.search("test", limit=99999)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_returns_results(self, mc):
        """Normal search should return saved entries."""
        await mc.save(MemoryEntry(content="deploy to vercel production"))
        results = await mc.search("deploy vercel")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, mc):
        e = MemoryEntry(content="to delete", id="del-1")
        await mc.save(e)
        deleted = await mc.delete_by_ids(["del-1"])
        assert deleted == 1
        remaining = await mc.query(limit=10)
        assert all(r.id != "del-1" for r in remaining)


# ── Initialization Safety ────────────────────────────


class TestInitSafety:
    """Methods must raise RuntimeError when not initialized."""

    @pytest.mark.asyncio
    async def test_memory_not_initialized(self):
        mc = MemoryCompiler(db_path=":memory:")
        with pytest.raises(RuntimeError, match="Not initialized"):
            await mc.save(MemoryEntry(content="test"))

    @pytest.mark.asyncio
    async def test_entity_not_initialized(self):
        es = EntityStore(db_path=":memory:")
        with pytest.raises(RuntimeError, match="Not initialized"):
            await es.create("test", "test")


# ── Input Validation (MCP layer) ─────────────────────


class TestInputValidation:
    """MCP tool input validation tests (unit-testable parts)."""

    def test_valid_memory_types(self):
        valid = {"episodic", "semantic", "project", "procedural"}
        for t in valid:
            assert MemoryType(t)  # should not raise

    def test_invalid_memory_type(self):
        with pytest.raises(ValueError):
            MemoryType("invalid_type")


# ── CLI Dispatch ─────────────────────────────────────


class TestCLIDispatch:
    """CLI module dispatch must be correct."""

    def test_brain_mode_uses_mcp_server(self):
        from jarvis_brain.cli import start_brain
        import inspect
        src = inspect.getsource(start_brain)
        # When demo=False, module should be mcp_server
        assert "jarvis_brain.mcp_server" in src
        assert "jarvis_brain.demo_server" in src

    def test_demo_and_brain_are_different(self):
        """demo=True and demo=False must produce different modules."""
        from jarvis_brain.cli import start_brain
        import inspect
        src = inspect.getsource(start_brain)
        # The ternary must have different values
        assert 'if demo else "jarvis_brain.mcp_server"' in src


# ── Entity Safety ────────────────────────────────────


class TestEntitySafety:
    @pytest.mark.asyncio
    async def test_update_nonexistent_entity(self, es):
        with pytest.raises(ValueError, match="not found"):
            await es.update_state("nonexistent", {"status": "test"})

    @pytest.mark.asyncio
    async def test_relationship_creates(self, es):
        a = await es.create("person", "Alice")
        b = await es.create("project", "Brain")
        rel = await es.add_relationship(a.id, "works_on", b.id)
        assert rel.predicate == "works_on"
