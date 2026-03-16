<div align="center">

# Jarvis Orb

### Watch it think.

*A brain that remembers. An orb that breathes.*

<br>

<img src="assets/demo.gif" alt="Jarvis Orb Demo" width="320">

<br><br>

[![GitHub Stars](https://img.shields.io/github/stars/whynowlab/jarvis-orb?style=flat&color=4A9EBF)](https://github.com/whynowlab/jarvis-orb/stargazers)
[![Release](https://img.shields.io/github/v/release/whynowlab/jarvis-orb?color=6B4FA0)](https://github.com/whynowlab/jarvis-orb/releases)
[![License](https://img.shields.io/badge/license-MIT-white)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-white)](https://github.com/whynowlab/jarvis-orb/releases)

**English** | [한국어](README.ko.md)

</div>

---

Every session, your AI starts over. Your decisions, your preferences, your project context — gone.

**Jarvis Orb** gives your AI a persistent brain and shows its thought process as a living orb on your desktop.

- **Brain Lite** — 4-tier memory, entity tracking, contradiction detection, temporal scoring
- **Orb** — Always-on-top floating visualizer that reacts to brain events in real time
- **MCP** — Works with Claude Code, Cursor, and any MCP-compatible tool

## Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.ps1 | iex
```

**Or download directly** → [Latest Release](https://github.com/whynowlab/jarvis-orb/releases/latest)

That's it. Brain starts, Orb floats, Claude Code connects.

## How It Works

```
┌──────────────┐     MCP      ┌──────────────┐    WebSocket    ┌──────────┐
│  Claude Code │ ──────────── │  Brain Lite   │ ──────────────  │   Orb    │
│  / Cursor    │   tool calls │  (Python)     │    events       │ (Tauri)  │
│              │              │               │                 │          │
│  You work.   │              │  It remembers.│                 │ You see. │
└──────────────┘              └──────────────┘                  └──────────┘
                                    │
                              ~/.jarvis-orb/
                               brain.db (SQLite)
```

You work in Claude Code as usual. Brain Lite runs as an MCP server — saving memories, tracking entities, detecting contradictions. The Orb floats on your screen, reacting to every brain event in real time.

## Brain Lite

| Feature | Description |
|---------|-------------|
| **4-Tier Memory** | Episodic, semantic, project, procedural — auto-classified |
| **Temporal Scoring** | Recent memories rank higher (30-day half-life decay) |
| **Observation Metadata** | Every memory tagged: verified, stale, or contradicted |
| **Contradiction Detection** | Conflicting memories auto-filtered from search results |
| **Entity Tracking** | Projects, PRs, decisions tracked as objects with state history |
| **Relationship Storage** | People → projects → decisions connected as a lightweight knowledge graph |
| **FTS5 Search** | Full-text search across all memories |

### MCP Tools

```
memory_save      Save a memory (auto-classified into 4 tiers)
memory_search    Search with temporal scoring + contradiction filtering
memory_verify    Mark memories as verified, superseded, or contradicted
entity_create    Track a project, person, decision, or tool
entity_update    Update entity state (records transition history)
entity_query     Query entities by type or name
entity_relate    Create relationships between entities
```

## Orb Reactions

The orb is not decorative. It shows you what the brain is doing.

| Brain Event | Orb Response |
|------------|-------------|
| Memory saved | Particles absorb into orb |
| Contradiction detected | Red/orange pulse |
| Entity state change | Cyan flash + scale pulse |
| Search executed | Violet color shift |
| Context compressed | Orb shrinks then expands |
| Session start | Wake-up glow |

## Tech

| Layer | Tech | Why |
|-------|------|-----|
| Brain | Python, aiosqlite, FTS5 | Proven, zero-config, single file DB |
| MCP | FastMCP (stdio) | Claude Code / Cursor native |
| Orb | Tauri 2, Three.js, WebGL | 3MB not 150MB. Custom shaders. |
| Connection | WebSocket | Real-time, bidirectional |
| Build | GitHub Actions | macOS + Windows on every tag |

## Philosophy

Built from a real system. The author's personal AI control plane — Jarvis — runs 19 modules, a knowledge graph with 100+ entities, 500+ memories, and 22 agent teams. Jarvis Orb is the lightweight, open version of that brain.

We believe AI should remember you, understand your context, and show you it's thinking. Not start over every session.

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
# Dev setup
git clone https://github.com/whynowlab/jarvis-orb.git
cd jarvis-orb

# Brain
cd brain && uv venv .venv && source .venv/bin/activate
uv pip install aiosqlite websockets mcp pytest pytest-asyncio
python -m pytest tests/ -v

# Orb
cd ../orb && pnpm install && pnpm tauri dev
```

## License

MIT

---

<div align="center">

**Not a tool. A presence.**

*It remembers your decisions. It tracks your world. It glows on your desktop, alive.*

<br>

[Install](https://github.com/whynowlab/jarvis-orb/releases/latest) · [Landing Page](https://jarvis-orb.vercel.app) · [Report Bug](https://github.com/whynowlab/jarvis-orb/issues)

</div>
