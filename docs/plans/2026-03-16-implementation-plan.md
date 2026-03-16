# Jarvis Orb — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Brain Lite(MCP 메모리 서버) + Orb(실시간 시각화 데스크탑 앱)를 배포 가능한 독립 제품으로 만든다.

**Architecture:** Brain Lite는 Python MCP 서버로 동작하며 WebSocket으로 이벤트를 emit. Orb는 Tauri(Rust+WebView) 앱으로 Three.js 기반 유기체 구체를 렌더링. 두 컴포넌트는 WebSocket으로 연결. 데모 모드는 Brain 없이 샘플 이벤트로 오브만 동작.

**Tech Stack:** Python 3, aiosqlite, FastMCP, Tauri 2, Three.js, WebSocket, pnpm

---

## Phase 1: 프로젝트 셋업 + 데모 오브

### Task 1: 프로젝트 구조 초기화

**Files:**
- Create: `package.json` (pnpm workspace root)
- Create: `brain/` (Python Brain Lite)
- Create: `orb/` (Tauri + Three.js)
- Create: `.gitignore`

**Step 1: 프로젝트 뼈대 생성**
```
jarvis-brain-visualizer/
├── brain/                  # Python Brain Lite + MCP
│   ├── jarvis_brain/       # 패키지
│   │   ├── __init__.py
│   │   ├── memory.py       # MemoryCompiler (경량)
│   │   ├── retrieval.py    # RetrievalPolicy (temporal)
│   │   ├── entities.py     # EntityStore (경량 KG)
│   │   ├── distiller.py    # MemoryDistiller (경량)
│   │   ├── schemas.py      # 데이터 모델
│   │   ├── mcp_server.py   # FastMCP 서버
│   │   ├── event_emitter.py # WebSocket 이벤트 emit
│   │   └── config.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
├── orb/                    # Tauri 데스크탑 앱
│   ├── src/                # Frontend (Three.js)
│   │   ├── index.html
│   │   ├── main.js         # Three.js orb renderer
│   │   ├── orb.js          # Orb geometry + animations
│   │   ├── events.js       # WebSocket client + event handler
│   │   ├── log.js          # Log panel UI
│   │   └── style.css
│   ├── src-tauri/          # Rust backend
│   │   ├── src/
│   │   │   └── main.rs     # Tauri entry + always-on-top
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json
│   └── package.json
├── demo/                   # 데모 이벤트 생성기
│   └── demo_events.py
├── docs/plans/
├── .gitignore
└── README.md
```

**Step 2: .gitignore 생성**

**Step 3: Commit**

---

### Task 2: Rust + Tauri 설치

**Step 1: Rust 설치**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Step 2: Tauri CLI 설치**
```bash
cargo install tauri-cli
```

**Step 3: 확인**
```bash
cargo --version
cargo tauri --version
```

---

### Task 3: Tauri + Three.js 프로젝트 생성

**Step 1: Tauri 프로젝트 초기화**
```bash
cd orb/
pnpm init
pnpm add three
pnpm add -D @tauri-apps/cli vite
cargo tauri init
```

**Step 2: tauri.conf.json 설정 — Always-on-top + 고정 크기**
```json
{
  "app": {
    "windows": [
      {
        "title": "Jarvis Orb",
        "width": 220,
        "height": 220,
        "resizable": false,
        "alwaysOnTop": true,
        "decorations": false,
        "transparent": true
      }
    ]
  }
}
```

**Step 3: 디자인팀 프로토타입을 index.html로 이식**
디자인팀이 만든 CSS 오브 + gooey 필터 + 로그 패널 코드를 `orb/src/index.html`에 배치.

**Step 4: `pnpm tauri dev`로 창이 뜨는지 확인**

**Step 5: Commit**

---

### Task 4: Three.js 오브 렌더링 (유휴 맥박)

**Files:**
- Create: `orb/src/orb.js`
- Modify: `orb/src/main.js`

**Step 1: Three.js scene + 유기체 구체 생성**
- SphereGeometry + custom shader (블루/퍼플 gradient + 시안 glow)
- 표면 displacement로 찰랑이는 느낌 (noise function)
- idle 상태: scale sine wave (맥박)

**Step 2: 셰이더 색상**
- 베이스: `#00F0FF` (시안) ↔ `#BD00FF` (퍼플) gradient
- 글로우: `#00F0FF` 40% opacity outer glow
- 배경: `#0D0D12` (짙은 다크)

**Step 3: 브라우저에서 오브가 숨쉬듯 움직이는지 확인**

**Step 4: Commit**

---

### Task 5: 오브 이벤트 반응 애니메이션

**Files:**
- Modify: `orb/src/orb.js`
- Create: `orb/src/events.js`

**Step 1: 이벤트별 애니메이션 함수 구현**
```javascript
// events.js
export const OrbAnimations = {
  memory_save: (orb) => { /* 입자 흡수 — 파티클이 오브 중심으로 빨려듦 */ },
  memory_contradict: (orb) => { /* 오렌지/레드 파동 — 색 전환 + ring pulse */ },
  entity_update: (orb) => { /* 표면 파문 — displacement spike */ },
  team_dispatch: (orb) => { /* 조각 분리 — sub orb 3개 분리 */ },
  team_result: (orb) => { /* 합체 — sub orb 복귀 */ },
  context_compact: (orb) => { /* 수축 — scale down + brightness up */ },
  session_start: (orb) => { /* wake-up 글로우 — bloom 확대 */ },
  search: (orb) => { /* 바이올렛 pulse */ },
  idle: (orb) => { /* 기본 맥박 복귀 */ },
};
```

**Step 2: 키보드로 테스트 (1=memory_save, 2=contradict, 3=dispatch...)**

**Step 3: Commit**

---

### Task 6: 로그 패널 (클릭 토글)

**Files:**
- Create: `orb/src/log.js`
- Modify: `orb/src/index.html`

**Step 1: 오브 클릭 시 로그 패널 토글**
- 기본: 오브만 (200x200)
- 클릭: 아래로 확장 (200x400), 최신 로그 5줄 표시
- 다시 클릭: 축소

**Step 2: 로그 라인 포맷**
```
[MEMORY] 결정: SQLite 유지 → semantic
[ENTITY] jarvis-brain: planning → implementing
[ALERT] 모순 감지: 이전 기억과 충돌
```

**Step 3: Commit**

---

### Task 7: 데모 모드

**Files:**
- Create: `demo/demo_events.py`

**Step 1: 샘플 이벤트를 시간차로 emit하는 스크립트**
```python
# 3초마다 랜덤 이벤트 → WebSocket으로 전송
events = [
    {"type": "session_start", "label": "Session initialized"},
    {"type": "memory_save", "label": "결정: SQLite 유지", "tier": "semantic"},
    {"type": "entity_update", "label": "jarvis-brain: planning → implementing"},
    {"type": "memory_contradict", "label": "모순 감지: 이전 기억과 충돌"},
    {"type": "team_dispatch", "label": "strategy 팀 3명 투입"},
    {"type": "team_result", "label": "팀 결과 수신: CONDITIONAL GO"},
    {"type": "context_compact", "label": "컨텍스트 73% → 압축 실행"},
]
```

**Step 2: `jarvis-orb --demo`로 데모 이벤트 + 오브 연동 확인**

**Step 3: Commit**

---

## Phase 2: Brain Lite (MCP 서버)

### Task 8: Brain Lite 스키마 + 메모리

**Files:**
- Create: `brain/jarvis_brain/schemas.py`
- Create: `brain/jarvis_brain/memory.py`
- Create: `brain/tests/test_memory.py`

**Step 1: 기존 jarvis schemas.py/memory_compiler.py에서 경량 버전 추출**
- MemoryEntry (4계층 + observation 메타데이터)
- MemoryCompiler (save, query, search, supersede, contradict, verify)
- Temporal scoring (30일 반감기)
- FTS5 검색

**Step 2: 테스트 작성 + 통과**

**Step 3: Commit**

---

### Task 9: Brain Lite 엔티티 + 관계

**Files:**
- Create: `brain/jarvis_brain/entities.py`
- Create: `brain/tests/test_entities.py`

**Step 1: 기존 entity_store.py에서 경량 버전 추출**
- Entity, EntityTransition
- create, update_state, get_history, link_memory, query
- 관계형 저장 (entity_relationships 테이블 추가)

**Step 2: 테스트 작성 + 통과**

**Step 3: Commit**

---

### Task 10: Brain Lite MCP 서버

**Files:**
- Create: `brain/jarvis_brain/mcp_server.py`
- Create: `brain/jarvis_brain/event_emitter.py`

**Step 1: FastMCP 서버 구현**
```python
# MCP Tools:
# memory_save, memory_search, memory_verify
# entity_create, entity_update, entity_query, entity_link
# distill
```

**Step 2: event_emitter — 모든 MCP 호출 시 WebSocket으로 이벤트 emit**
```python
# memory_save 호출 시 → {"type": "memory_save", "label": "...", "tier": "..."} emit
# → Orb가 이 이벤트를 받아서 애니메이션 반응
```

**Step 3: Commit**

---

### Task 11: Brain ↔ Orb 연결

**Step 1: Brain의 WebSocket 서버 + Orb의 WebSocket 클라이언트 연결**

**Step 2: 실제 MCP 호출 → 오브 반응 end-to-end 테스트**
```bash
# 터미널 1: Brain 시작
python -m jarvis_brain.mcp_server

# 터미널 2: Orb 시작
cd orb && pnpm tauri dev

# 터미널 3: 테스트 이벤트
python -c "from jarvis_brain.mcp_server import ...; memory_save(...)"
# → Orb에서 입자 흡수 애니메이션 발생 확인
```

**Step 3: Commit**

---

## Phase 3: 패키징 + 배포

### Task 12: Tauri 빌드 + 바이너리

**Step 1: macOS .dmg 빌드**
```bash
cd orb && pnpm tauri build
```

**Step 2: Windows .msi 빌드 (CI에서)**

**Step 3: GitHub Releases에 업로드**

---

### Task 13: README + 데모 GIF

**Step 1: 데모 모드로 오브 녹화 (15초 GIF)**
**Step 2: README 작성 (설치 → 스크린샷 → 사용법)**
**Step 3: Commit + 공개**

---

## Phase 4: QA + 팀 검증

### Task 14: 전략팀 리뷰
```bash
dispatch-team.sh strategy --task "Jarvis Orb 최종 제품 리뷰"
```

### Task 15: 코드리뷰팀
```bash
dispatch-team.sh code-review --task "Jarvis Orb 전체 코드 리뷰"
```

### Task 16: QA 게이트
```bash
dispatch-team.sh qa-gate --task "Jarvis Orb 배포 전 QA 검증"
```

---

## Execution Order

```
Phase 1 (데모 오브): Task 1-7 — 눈에 보이는 것 먼저
Phase 2 (Brain Lite): Task 8-11 — 실제 두뇌 연결
Phase 3 (패키징): Task 12-13 — 배포
Phase 4 (QA): Task 14-16 — 팀 검증
```

Phase 1 완료 시점에 데모 가능. Phase 2 완료 시점에 제품 동작. Phase 3에서 배포.
