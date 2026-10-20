# STATUS — OHORA Trend Analyzer

> **현재 확인 시점: 2026-10-20 KST / 설계·인수인계 문서 등록 완료 (기능은 미구현)**
>
> **요약: GitHub 신규 저장소 초기화 및 설계 문서 등록 완료(구현 시작 전). n8n workflow, 태깅 실행 코드, DERIVED DB migration, 대시보드는 아직 구현/검증되지 않았음.** 이 저장소의 설계 작업은 기존 P6 collector 완료·실운영 검증의 증거가 아니다.

## 0. 다음 채팅방 첫 작업

1. 이 저장소 `main` 최신 HEAD 재조회 후 `README.md`, `AGENTS.md`, `HANDOFF.md`, `STATUS.md` 읽기.
2. `docs/TAXONOMY_DECISIONS.md`의 `not_observed` / `not_evaluated` 계약 차이를 검토하고 검증 규칙 확정.
3. P6 실제 **읽기 전용 export** 가능 여부 및 n8n 실행 환경 확인(불명확하면 synthetic fixture부터).
4. 합성 네일 media 1건의 `analyzer_input_v0_1` fixture/validator 만드는 **최소 구현** 시작. 사용자 승인 없는 Meta/API/운영 DB 실연동 금지.

## 1. 단계별 현황

| 작업 | 상태 | 근거 / 한계 |
|---|---|---|
| 신규 GitHub 저장소 `hibi89/ohora-trend-analyzer` | **완료** | main README 생성 및 문서 커밋 |
| 기초 개발 규칙·RAW 쓰기 금지 `AGENTS.md` | **문서화** | 보안·승인 규칙. 기술적 배포 정책/분기 보호 별개 |
| 원본 taxonomy v1.0-draft 스냅샷 | **파일 등록·파싱 확인** | JSON의 F01~F14, 159 tag, S01~S04; v1.1 확정 아님 |
| 분류 판정·Astra 의견 | **설계** | 모호한 용어 경계와 7축 P0 제안, 모델 테스트 전 |
| P6↔Analyzer 논리 데이터 계약 | **설계** | 실제 P6 export·필드별 매핑·권한 검증 미완료 |
| n8n 노드/에러/중복 처리 설계 | **설계** | 실제 workflow JSON/인스턴스 import 없음 |
| DERIVED DB schema 및 migration | **미구현** | 논리 테이블/키만 문서화 |
| AI 비전 태깅 7축 실행 | **미구현** | 모델/비용/이미지 전송 환경 미확정 |
| 내부 관리자 대시보드 | **미구현** | 화면 사양만 문서화 |
| E2E 자동화·장애 복구 테스트 | **미검증** | 합성 fixture/실행 전 |
| 실제 P6 RAW 읽기 및 294계정 수집 | **이 저장소에서 미검증** | P6 동결 설계는 별도. 독립 repo 상태 별도 조회 필요 |
| Meta 라이브 실행·운영 DB 변경 | **이 저장소에서는 0건, 미승인** | 승인 없는 호출/쓰기 금지 |
| 11/03 최종 제출 / 11/05 발표 | **미래 마감** | 진행률 100%로 주장 금지 |

## 2. 변경·보존 규칙

- P6 RAW와 Analyzer DERIVED는 물리적·논리적 분리. 원본값 덮어쓰기 금지.
- n8n은 태깅만. 이미 수집된 Meta API 게시물 다시 긁지 않는다.
- `taxonomy/tag_schema_v1_0_draft.json`은 보존용. v1.1은 별도 신규 파일로 추가.
- 성능/정확도 수치, 실제 운영 처리량, AI 분류 정확도는 현재 검증되지 않음.
- 모델 판단과 원본 캡션·계정 국가·좋아요 관측 시점 분리.
- 라이브 실환경 테스트에는 별도 승인 필요.

## 3. 검증 기록 (현재)

- **수행함**: GitHub 연결 저장소 확인, 신규 파일 생성. 태그 JSON parse 및 14 categories/159 tags 개수 확인. 기존 JSON을 snapshot으로 복사.
- **수행하지 않음**: 원격 저장소 전체 Git clone 및 테스트 실행, n8n workflow import, DB migration, VLM 테스트, 실 Media/Meta 접근.
- **필수 후속**: GitHub에서 `README/AGENTS/HANDOFF/STATUS` 및 중요 설계 문서 fetch-back, 최신 내용/링크 검사.

## 4. 오늘~주말 작업

- 10/20: D0 설계·태그 상태 결정.
- 10/21: D1 read-only adapter/fixture, D2 n8n 시작.
- 10/22: D2 분류 모델+스키마 검증.
- 10/23: D3 DERIVED 저장 및 재시도/중복.
- 10/24: D4 내부 read-only 대시보드.
- 10/25: D5 통합/회귀 테스트와 팀 인계.

상세 일정·DoD는 [IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md) 참조.

## 5. 운영/결정 필요 질문

1. n8n은 학원 원격 서버인지 로컬 인스턴스인지? 버전·HTTP 접근 경로는?
2. P6에서 준비되는 **읽기 전용 스냅샷/내보내기** 구조는 무엇인지?
3. DERIVED DB 개발용 저장 매체는 SQLite 로컬 / Supabase / Postgres 중 무엇인지?
4. LLM/VLM 선택·자격증명 저장·이미지 외부 전송 승인 범위는?
5. v1.1에서 `not_evaluated` 도입 후 구버전 `not_observed` 어떻게 처리할지?

## 6. 다음 상태 갱신 규칙

실제 테스트할 때 명령, 실행 환경, PASS 수치, output sample, 영향 파일, 운영 미검증, rollback을 기록한다. 중요한 변경은 `HANDOFF.md`와 이 파일을 **같은 작업 세션**에 업데이트한다.
