# Jarvis Orb — Design Document

## Summary

Jarvis Orb = **Brain Lite(경량 AI 메모리 브레인)** + **Orb(실시간 시각화)**.
설치하면 AI 메모리 시스템이 작동하고, 그 활동이 오브로 보인다.
배포용 독립 제품. 크로스플랫폼 (macOS/Windows/Linux).

## Product: What Users Get

사용자가 Jarvis Orb를 설치하면:
1. **Brain Lite** — MCP 서버로 동작하는 경량 메모리 브레인
2. **Orb** — 브레인 활동을 실시간으로 보여주는 Always-on-top 플로팅 창

"AI가 건망증을 치료받고, 그 과정이 눈에 보인다."

---

## Part 1: Brain Lite

### 포함
| 기능 | 설명 |
|------|------|
| 4계층 메모리 | episodic, semantic, project, procedural |
| Temporal scoring | 30일 반감기, 최근 기억 우선 |
| Observation 메타데이터 | superseded_by, contradicted_by, verification_status |
| 모순/대체 감지 | 틀린 기억 자동 필터링 |
| FTS5 검색 | 전문 검색 |
| 엔티티 + 관계 저장 | 사람/프로젝트/결정 간 관계 (경량 KG) |
| MCP 서버 | Claude Code, Cursor, Gemini 등에서 호출 |

### 제외 (대표님 풀 시스템 전용)
- Knowledge Graph 시각화 (그래프 뷰)
- 22개 팀 디스패치 / 오케스트레이터
- 모델 라우터 / 예산 관리
- 자율 판단 루프 (OTPAVLA)
- 정책 엔진 / 신뢰 레벨
- 스킬 체이닝 / Plan Ledger

### MCP Tools (Brain Lite가 노출하는 도구)
```
memory_save     — 기억 저장 (자동 계층 분류)
memory_search   — 시간 가중 + observation 필터링 검색
memory_verify   — 기억 검증/대체/모순 표시
entity_create   — 엔티티 생성 (person, project, decision 등)
entity_update   — 엔티티 상태 변경 + transition 기록
entity_query    — 엔티티 조회 + 관계 탐색
entity_link     — 엔티티 ↔ 메모리 연결
distill         — 대화 → 구조화 기억 추출
```

### Storage
- SQLite 단일 파일 (`~/.jarvis-orb/brain.db`)
- 서버 없음, 클라우드 없음
- 포터블 (파일 복사로 이동 가능)

---

## Part 2: Orb (시각화)

### Display
- **형태**: Always-on-top 플로팅 데스크탑 창
- **크기**: 고정 200x200
- **로그**: 기본은 오브만, 클릭 시 최신 로그 펼침
- **용도**: 상시 모니터링 + 쇼케이스/데모

### Visual
- **오브 형태**: 유기체 구체 (Siri Orb 스타일)
- **색상 베이스**: 블루/퍼플 에너지 글로우
- **자비스 터치**: 시안 홀로그래픽 질감 + 투명감
- **상태별 색 전환**:
  - 유휴 → 시안/블루 맥박
  - 활성 → 시안 → 바이올렛 전환
  - 경고/모순 → 오렌지/레드 파동

### Animation (오브 반응 매핑)
| Brain 이벤트 | 오브 반응 |
|-------------|----------|
| 유휴 | 조용한 맥박 (숨쉬듯) |
| 기억 저장 | 입자 흡수 |
| 모순 감지 | 오렌지/레드 파동 |
| 엔티티 변경 | 표면 파문 |
| 관계 생성 | 시안 링 flash |
| 검색 실행 | 바이올렛 pulse |
| 증류 실행 | 수축 후 팽창 |
| 세션 시작 | wake-up 글로우 |

### Orb ↔ Brain 연결
- Orb는 Brain Lite의 이벤트를 구독
- Brain이 동작할 때마다 이벤트 emit → Orb가 반응
- 데모 모드: Brain 없이 샘플 이벤트로 오브만 동작

---

## Part 3: Tech Stack

| 레이어 | 기술 | 이유 |
|--------|------|------|
| Brain Lite | Python + aiosqlite + FTS5 | 기존 검증된 코드 재사용 |
| MCP 서버 | FastMCP (Python) | Claude Code/Cursor 호환 |
| Orb 앱 | Tauri (Rust + WebView) | 가벼운 크로스플랫폼 (~10MB) |
| 오브 렌더링 | Three.js + WebGL | 셰이더 기반 유기체 구체 |
| 이벤트 전달 | WebSocket (Brain → Orb) | 실시간, 범용 |
| 패키징 | Tauri bundler | macOS .dmg / Windows .msi / Linux .AppImage |

### Architecture
```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Brain Lite    │ ──────────────────→ │    Orb (Tauri)  │
│  (Python MCP)   │     events          │  Three.js WebGL │
│                 │                     │  Always-on-top  │
│  brain.db       │                     │  200x200 float  │
│  (SQLite)       │ ←── MCP calls ──── │                 │
└─────────────────┘   Claude/Cursor     └─────────────────┘
```

### Demo Mode
Brain 없이 Orb만 실행 가능:
```bash
jarvis-orb --demo  # 샘플 이벤트로 오브 애니메이션만
jarvis-orb         # Brain + Orb 전체 실행
```

---

## Part 4: Distribution

- **이름**: Jarvis Orb
- **레포**: `github.com/dd/jarvis-orb` (가칭)
- **라이선스**: MIT
- **설치**: Releases에서 바이너리 다운로드 또는 brew/winget
- **README**: 데모 GIF 필수 (오브가 반응하는 15초 영상)

### Install Flow
```bash
# macOS
brew install jarvis-orb

# Windows
winget install jarvis-orb

# 또는 직접 다운로드
# → 실행하면 Brain Lite 자동 시작 + Orb 창 뜸
# → Claude Code에서 MCP 서버로 자동 연결
```

---

## References
- [Siri Orb (SmoothUI)](https://smoothui.dev/docs/components/siri-orb)
- [Luminous Energy Sphere (Vecteezy)](https://www.vecteezy.com/video/49072518)
- [Jayse Hansen - Iron Man UI Designer](https://jayse.tv/v2/?portfolio=hud-2-2)
- [JARVIS Color Palette](https://www.color-hex.com/color-palette/80644)
- [SwiftUI Orb (GitHub)](https://github.com/metasidd/Orb)
