# Jarvis Orb

**See your AI thinking in real time.**

Jarvis Orb gives your AI a memory brain and shows its thought process as a living, breathing orb on your desktop.

- **Brain Lite** — 4-tier memory system with temporal scoring, contradiction detection, entity tracking
- **Orb** — Always-on-top floating visualizer that reacts to brain events in real time

Works with Claude Code, Cursor, and any MCP-compatible tool.

## Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/whynowlab/jarvis-orb/main/install.ps1 | iex
```

**Or download directly:**
[Latest Release](https://github.com/whynowlab/jarvis-orb/releases/latest)

## What happens when you install

1. Brain Lite starts as an MCP server
2. Your AI tool (Claude Code, Cursor) connects to it
3. As you work, memories accumulate automatically
4. The Orb floats on your screen, reacting to every brain event

## Orb Reactions

| Brain Event | Orb Response |
|------------|-------------|
| Memory saved | Particles absorb into orb |
| Contradiction detected | Red/orange pulse |
| Entity state change | Surface ripple |
| Team dispatched | Orb splits into sub-orbs |
| Team result | Sub-orbs merge back |
| Context compressed | Orb shrinks then expands |
| Search | Violet flash |

## Tech

- **Brain**: Python, SQLite, aiosqlite, FTS5
- **Orb**: Tauri (Rust), Three.js, WebGL custom shaders
- **Connection**: WebSocket (Brain → Orb)
- **Size**: ~3MB (not 150MB like Electron)

## License

MIT
