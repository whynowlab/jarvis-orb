<div align="center">

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/assets/demo.gif">
  <img src="https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/assets/demo.gif" alt="Jarvis Orb" width="280">
</picture>

<sub>Actual footage. Not a mockup.</sub>

<br><br>

# Jarvis Orb

### Not a tool. A presence.

*It remembers your decisions. It tracks your world. It glows on your desktop, alive.*

<br>

[![Stars](https://img.shields.io/github/stars/whynowlab/jarvis-orb?style=flat&color=4A9EBF&label=Stars)](https://github.com/whynowlab/jarvis-orb/stargazers)
[![Release](https://img.shields.io/github/v/release/whynowlab/jarvis-orb?color=6B4FA0&label=Release)](https://github.com/whynowlab/jarvis-orb/releases)
[![License](https://img.shields.io/badge/License-MIT-white)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-ready-white)]()
[![Windows](https://img.shields.io/badge/Windows-ready-white)]()

[Website](https://jarvis-brain-visualizer.vercel.app) · [Download](https://github.com/whynowlab/jarvis-orb/releases/latest) · [Report Bug](https://github.com/whynowlab/jarvis-orb/issues)

**English** | [한국어](README.ko.md)

</div>

---

## The Problem

Every session, your AI starts over. Your decisions, your preferences, your project context — gone. You explain yourself again. And again. And again.

- "We decided to use SQLite." → Three days later, it suggests PostgreSQL.
- "This PR was merged yesterday." → It doesn't know. It never remembers state.
- "What was the architecture decision?" → Gone. The session ended.

## The Solution

**Jarvis Orb** gives your AI a persistent brain and shows its thought process as a living orb on your desktop.

[![jarvis-orb MCP server](https://glama.ai/mcp/servers/whynowlab/jarvis-orb/badges/card.svg)](https://glama.ai/mcp/servers/whynowlab/jarvis-orb)

| | Without Jarvis Orb | With Jarvis Orb |
|---|---|---|
| **Context** | Every session starts from zero | Carries over automatically |
| **Decisions** | Reversed decisions come back | Contradictions detected and filtered |
| **State** | "What's the status?" → guess | Exact state + transition history |
| **Visibility** | No idea what it's thinking | Every thought, live on your screen |

## Install

**macOS (Apple Silicon) / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash
```

> Requires Apple Silicon (M1/M2/M3/M4). Use the terminal command above for the smoothest install experience.

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.ps1 | iex
```

That's it. Brain starts. Orb floats. Claude Code connects.

**Verify your install:**
```bash
jarvis-orb --doctor
```

### Supported Platforms

| Platform | Brain (MCP) | Orb (Desktop) |
|----------|-------------|---------------|
| macOS Apple Silicon (M1+) | Yes | Yes |
| macOS Intel | Yes | Yes |
| Windows x64 | Yes | Yes |
| Linux | Yes | Not yet |

### Cursor / Windsurf Setup

Add to your MCP config (`~/.cursor/mcp.json` or equivalent):
```json
{
  "mcpServers": {
    "jarvis-brain": {
      "command": "python3",
      "args": ["-m", "jarvis_brain.mcp_server"],
      "env": {
        "PYTHONPATH": "~/.jarvis-orb/lib:~/.jarvis-orb"
      }
    }
  }
}
```

### Uninstall

```bash
# Remove Brain + data
rm -rf ~/.jarvis-orb

# Remove from Claude Code
claude mcp remove jarvis-brain

# Remove Orb app (macOS)
rm -rf "/Applications/Jarvis Orb.app"

# Remove PATH entry from ~/.zshrc or ~/.bashrc
# Delete the line: export PATH="$HOME/.jarvis-orb/bin:$PATH"
```

---

## Brain Lite

> Watch it think.

| # | Feature | Description |
|---|---------|-------------|
| 01 | **4-Tier Memory** | Episodic, semantic, project, procedural — auto-classified and ranked by recency |
| 02 | **Temporal Scoring** | 30-day half-life decay. Recent memories surface first. Old context fades naturally |
| 03 | **Contradiction Detection** | Conflicting memories flagged. Superseded decisions marked stale. Only truth surfaces |
| 04 | **Entity Tracking** | Projects, PRs, decisions tracked as objects with full state transition history |
| 05 | **Relationship Storage** | People → projects → decisions connected as a lightweight knowledge graph |
| 06 | **FTS5 Search** | Full-text search across all memories with observation filtering |

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

Works with **Claude Code**, **Cursor**, and any MCP-compatible tool.

---

## Orb

> Every thought, visible.

The orb is not decorative. It shows you what the brain is doing, in real time.

| Brain Event | Orb Response |
|------------|-------------|
| Memory saved | Particles absorb into orb |
| Contradiction detected | Red/orange pulse wave |
| Entity state changed | Cyan flash + scale pulse |
| Search executed | Violet color shift |
| Context compressed | Shrink, brighten, expand |
| Team dispatched | Orb splits into sub-orbs |

3MB desktop app. Always-on-top. Draggable. Click to see logs.

---

## In Practice

**Monday morning standup** — *"What did we work on last week?"*
Brain searches episodic memories with temporal scoring. Returns a ranked summary. No digging through chat history.

**Mid-project contradiction** — *"We should use Redis for caching."*
Brain detects this contradicts a previous decision. Flags the conflict. The orb pulses red. You see it happening.

**New session, no context loss** — *"Continue where we left off."*
Brain loads project state, recent decisions, and your preferences. No re-explaining.

---

## Architecture

```
Claude Code / Cursor
     ↕  MCP (stdio)
Brain Lite  —  Python · aiosqlite · FTS5 · ~/.jarvis-orb/brain.db
     ↕  WebSocket
Orb  —  Tauri · Three.js · WebGL · 3MB · Always-on-top
```

| | |
|---|---|
| **3MB** | App size. Not 150MB. |
| **7** | MCP tools. Memory, entities, search. |
| **0** | Cloud dependencies. Everything local. |

---

## Origin

Jarvis Orb was extracted from a working AI control plane — **Jarvis** — running 19 modules, a knowledge graph with 100+ entities, 500+ memories, and 22 agent teams. This is the lightweight, open-source version of that brain.

> *"I built a personal AI operating system. After months of using it, I realized the core — the brain and the visualization — should be available to everyone."*

---

## Roadmap

- **Orb Customization** — Custom orb skins, color themes, animation profiles
- **Brain Pro** — Advanced memory with full knowledge graph, multi-model routing, autonomous reasoning loop
- **Auto-update** — Seamless in-app updates
- **Plugin System** — Extend Brain with custom MCP tools

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
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

<br>

**Your AI will start remembering.**

[Website](https://jarvis-brain-visualizer.vercel.app) · [Download](https://github.com/whynowlab/jarvis-orb/releases/latest) · [GitHub](https://github.com/whynowlab/jarvis-orb)

<br>

</div>