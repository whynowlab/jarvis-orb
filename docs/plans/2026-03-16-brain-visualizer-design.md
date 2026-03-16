# Jarvis Brain Visualizer — Design Document

## Summary

자비스 브레인의 실시간 사고 과정을 시각적 오브젝트 + 이벤트 로그로 보여주는 데스크탑 앱.
배포용 독립 제품. 기존 시스템 연결 아님.

## Core Concept

중앙에 유기체 구체(Siri Orb 스타일)가 AI 브레인 이벤트에 실시간 반응.
ChatGPT/Siri의 반응형 오브젝트 + 실시간 사고 과정 로그의 결합.
"살아있는 AI의 사고 과정이 눈앞에서 보이는 것."

## Confirmed Specifications

### Display
- **형태**: Always-on-top 플로팅 데스크탑 창
- **크기**: 고정 200x200
- **로그**: 기본은 오브만 표시, 클릭 시 최신 로그 펼침
- **용도**: 상시 모니터링 + 쇼케이스/데모

### Visual
- **오브 형태**: 유기체 구체 (Siri Orb 스타일, 물방울처럼 찰랑이는 표면)
- **색상 베이스**: 블루/퍼플 에너지 글로우
- **자비스 터치**: 시안 홀로그래픽 질감 + 투명감
- **상태별 색 전환**:
  - 유휴 → 시안/블루 조용한 맥박
  - 활성 → 시안에서 바이올렛으로 전환
  - 경고/모순 → 오렌지/레드 파동

### Animation (오브 반응 매핑)
| 이벤트 | 반응 |
|--------|------|
| 유휴 | 조용한 맥박 (숨쉬듯) |
| 기억 저장 | 입자가 빨려들어감 |
| 모순 감지 | 빨간/오렌지 파동 |
| 팀 디스패치 | 조각 분리 |
| 결과 수신 | 합체 |
| 컨텍스트 압축 | 수축 |
| 활성 작업 | 시안 → 바이올렛 전환 |

### Tech Stack
- **프레임워크**: Tauri (Rust + WebView)
- **렌더링**: WebGL / Three.js (오브 애니메이션)
- **크로스플랫폼**: macOS / Windows / Linux
- **배포**: 독립 바이너리 (~10MB)

### Architecture (배포용 독립 제품)
- **이벤트 소스**: 범용 API/프로토콜 (특정 시스템 비의존)
  - WebSocket 서버 (외부 시스템이 이벤트 push)
  - 또는 stdin/파일 watch (파이프라인 연결)
  - 데모 모드: 내장 샘플 이벤트 생성기
- **설치**: jarvis 시스템 없이 독립 실행 가능
- **테스트**: 별도 데스크탑에서 진행

### Event Protocol (범용)
```json
{
  "type": "memory_save",
  "label": "결정: SQLite 유지",
  "tier": "semantic",
  "timestamp": "2026-03-16T10:00:00Z"
}
```
지원 이벤트 타입:
- `memory_save` — 기억 저장
- `memory_contradict` — 모순 감지
- `entity_update` — 엔티티 상태 변경
- `team_dispatch` — 팀 디스패치
- `team_result` — 팀 결과 수신
- `context_compact` — 컨텍스트 압축
- `session_start` — 세션 시작
- `idle` — 유휴 상태

### Distribution
- GitHub 오픈소스 (MIT)
- Releases에 macOS/Windows 바이너리
- `brew install jarvis-brain-visualizer` (향후)
- README에 데모 GIF 필수

## References
- [Siri Orb (SmoothUI)](https://smoothui.dev/docs/components/siri-orb)
- [Luminous Energy Sphere (Vecteezy)](https://www.vecteezy.com/video/49072518)
- [Jayse Hansen - Iron Man UI Designer](https://jayse.tv/v2/?portfolio=hud-2-2)
- [JARVIS Color Palette](https://www.color-hex.com/color-palette/80644)
