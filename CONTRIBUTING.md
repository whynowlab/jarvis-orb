# Contributing to Jarvis Orb

Thanks for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/whynowlab/jarvis-orb.git
cd jarvis-orb
```

### Brain (Python)

```bash
cd brain
uv venv .venv && source .venv/bin/activate
uv pip install aiosqlite websockets mcp pytest pytest-asyncio
python -m pytest tests/ -v
```

### Orb (Tauri + Three.js)

```bash
cd orb
pnpm install
pnpm tauri dev
```

## Pull Requests

1. Fork the repo and create a feature branch
2. Make your changes
3. Run tests: `cd brain && python -m pytest tests/ -v`
4. Submit a PR with a clear description

## Reporting Bugs

Open an issue at [GitHub Issues](https://github.com/whynowlab/jarvis-orb/issues) with:
- Steps to reproduce
- Expected vs actual behavior
- OS and Python version

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
