# STATUS — OHORA Trend Analyzer

> **최신 검증 문서:** [TAXONOMY_QA_2026-10-20.md](docs/TAXONOMY_QA_2026-10-20.md), [P0 정규화 JSON Schema](taxonomy/p0_tag_result.schema.json), [n8n 인계](docs/TAGGING_INTEGRATION_HANDOFF_v1_1.md). XLSX는 7개 시트 사용자 채팅 첨부이며 GitHub 정본은 JSON.
>
> **2026-10-20 KST — 태깅표 v1.1 완료: JSON Schema 및 36개 로컬 합성 검사 PASS (현재 우선)**
>
> **오늘의 범위: 태깅표·정적 검사·JSON Schema·문서 인수인계. 실제 n8n·AI 이미지 태깅·DERIVED DB·내부 대시보드는 내일 이후.**
>
> 기준 파일: [v1.1 표준 사전](taxonomy/tag_schema_v1_1.json) / [84개 세부 판정 규칙](taxonomy/tag_rules_v1_1.json) / [운영 기준서](docs/TAXONOMY_RULEBOOK_v1_1.md) / [QA 증거](docs/TAXONOMY_QA_2026-10-20.md). 이것은 **팀 프로젝트용 분류안**이며 오호라 공식 내부 기준 또는 실제 AI 정확도 검증 결과가 아니다.

## 다음 채팅방 첫 작업 (2026-10-21)

1. 최신 `main`의 `README.md`·`AGENTS.md`·`HANDOFF.md`·`STATUS.md` 및 새 태깅 파일들을 fetch-back해 버전 일치 확인.
2. 합성 검증 코드 실행: `python scripts/validate_taxonomy.py`, `python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json`, `python -m unittest discover -s tests -v`. **GitHub CI 실제 PASS를 별도 확인**.
3. n8n 호스팅 위치·접근 경로와 P6의 승인된 RAW **read-only export** 방식 결정. 모르면 합성 fixture로 시작.
4. P0 7축 이미지+캡션 분류 n8n 설계에 v1.1 사전·판정 규칙·검증기를 연결. 검증 전 결과는 DERIVED DB에 저장하지 않음.

## 단계별 완료·미완료 현황

| 항목 | 상태 | 증거 / 제한 |
|---|---|---|
| GitHub 신규 분리 저장소 / 설계도 | **완료** | `IMPLEMENTATION_PLAN.md`, `ARCHITECTURE_AND_CONTRACTS.md`, `AGENTS.md` |
| 태깅표 원본 v1.0 보존 | **완료** | `taxonomy/tag_schema_v1_0_draft.json` 유지 |
| **프로젝트용 태깅 사전 v1.1** | **완료** | 14개 F축·159개 원본 태그 ID·S01~S04, 기존 ID/이름·동의어 보존 |
| **P0 7축(84태그) 판정 기준** | **완료** | `taxonomy/tag_rules_v1_1.json`: 모호 용어 경계 규칙 10개 |
| **태깅 JSON 데이터 구조 정적 검사** | **통과** | 기존 159개 ID·명칭 보존 등 GitHub fetch 기반 12개 구조 검사 PASS |
| **태깅 결과 검증 코드** | **등록 완료 / 실행 증거 미확인** | `scripts/validate_taxonomy.py` + `tests/test_tagging_contract.py` 22개 + `tests/test_json_schema_contract.py` 14개, 합계 36개 합성 테스트 |
| **GitHub Actions CI 검사** | **workflow 및 test dependency 등록 / GitHub CI 결과 미확인** | `.github/workflows/taxonomy-check.yml`, `requirements-test.txt`; 로컬 대응코드 36/36 PASS와 구별 |
| 태깅 사전 설명서·QA | **완료** | `docs/TAXONOMY_RULEBOOK_v1_1.md` + `docs/TAXONOMY_QA_2026-10-20.md` |
| P6↔Analyzer 읽기 전용 실제 export 연결 | **미구현/미검증** | P6 운영 DB 소유권 침범 금지 |
| n8n 실제 workflow import/실행 | **미구현** | 10/21 시작 목표 |
| 실제 VLM 이미지 분석 정확도 | **미검증** | 30~50장 권한 확보 검수 필요 |
| DERIVED DB migration / 중복 방지 | **미구현** | 10/23 목표 |
| 내부 개발자 대시보드 | **미구현** | 10/24 목표 |
| 통합 실증 | **미검증** | 10/25 목표 |
| 실 Meta API/토큰 사용/운영 DB 변경 | **이 저장소 작업 중 없음** | 별도 승인 필요 |

## v1.1 적용 규칙

- 모든 14축은 **사전에서 유지**. 이번 P0에서 **F01·F03·F05·F06·F08·F09·F10만 평가**하고 F02·F04·F07·F11·F12·F13·F14는 `not_evaluated`.
- 성공한 P0 이미지 결과에 14개 `facet_results` 존재. `observed`는 태그+근거, `unknown`은 평가했으나 판단불가, `not_applicable`는 충분한 관측 범위 내 해당 없음, `not_evaluated`는 미평가. 기존 `not_observed` 자동치환 금지.
- 이미지 접근불가·비네일·분석 미지원 영상은 **job-level** 처리 상태. 잘못된 가짜 facet 생성 금지.
- RAW 수집기(P6)와 n8n/DERIVED 분리. API 원본/관측 시간/미디어 식별자 훼손 금지. `post_id` ≠ `media_id` ≠ 이후 디자인 클러스터 ID.
- 사용된 모델·프롬프트·taxonomy 버전·분석 시간·입력 해시·근거를 파생 분석 결과에 기록.
- F5/필터/카드 조회는 저장된 DB만 사용하고 AI 분석·Meta 호출을 재실행하지 않는다.
- P6 동결 요건(공식 294계정, 3 API 레인, limit=4, 최신 2라운드, 원본 이력)은 별도 저장소 관할. **이 저장소에서 변경 금지**.

## 오늘 실시한 검증 / 한계

- 로컬 사전 `verify_tagging_v1_1.py` 구조 검사 PASS, 대응 검증기 22개+JSON Schema 14개 **로컬 합성 검사 36/36 PASS**. GitHub 최신 파일을 다시 읽어 17개 파일 존재 및 14축/159 ID/84 규칙/36 테스트 함수 확인.
- 로컬 별도 작업공간의 GitHub 대응 검증 코드 + JSON Schema 회귀 **36/36 PASS**. GitHub Actions에서 실제 해당 커밋의 **CI 실행 완료/성공 증거는 아직 없음**. 임의 PASS 주장 금지.
- 컨테이너의 `git clone`은 `Could not resolve host: github.com` 실패. 같은 네트워크 방식 반복 금지; GitHub Actions 또는 사용자의 로컬 환경에서 검증.
- 타인의 GitHub 파일·실제 사진·오호라 내부 분류에 대한 확인 없이 공식 표준으로 주장하지 않는다.

## 향후 일정

| 날짜 | 목표 |
|---|---|
| 10/20(화) | D0 태깅 사전 v1.1·규칙·정적 검증·인수인계 **완료** |
| 10/21(수) | D1 읽기 전용 adapter/fixture, D2 n8n 기본 연결 시작 |
| 10/22(목) | P0 이미지+캡션 태깅 JSON 흐름 |
| 10/23(금) | DERIVED 저장 및 재실행/실패 안전성 |
| 10/24(토) | 최소 내부 대시보드 |
| 10/25(일) | 통합·팀원 인수인계 |
| 11/03(화) | 제출 / 11/05(목) 발표 |

## 다음 갱신 규칙

작업마다 변경 파일, 커밋 SHA, 실행 명령, 실제 PASS 증거, 위험과 롤백, 다음 최소 작업을 `HANDOFF.md`와 `STATUS.md`에 같은 작업 세션으로 남기고 GitHub fetch-back 검증할 것. **태깅 기준 등록과 모델 구현 완료를 혼동하지 말 것**.
