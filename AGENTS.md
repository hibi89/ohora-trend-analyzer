> **2026-10-28 해총 전 저장소 최상위 공통 운영 공지 (소유자 승인):** [개발 가속·로컬검증·병목제거 통합 정본](https://github.com/hibi89/hackathon-command-center-2026/blob/main/docs/DEV_ACCELERATION_AND_VERIFICATION_20261028.md) 확인. 현 시점 활성은 **KIC(+DL)·PayPal·UGREEN·LA 4개**만이다. 이 프로젝트는 **임시 개발 대기**(폐기·기존 기록 삭제 아님)로, 소유자의 재개 지시 없이 `ㄱ`만으로 신규 개발·CI·배포를 진행하지 않는다. 활성 프로젝트 일반 기능 구현은 **GPT-6 Instant**, 최초 설계·난제·해총 독립검수는 높은 추론. 파일 단위 GitHub 반복·다수 상태 문서 갱신·동일 SHA 반복 조회를 줄이고, 기능 단위 검증/정확한 PASS·FAIL·SKIP·커밋 SHA만 보고한다. 기존 제품 설계 동결, 외부 승인, 보안·고객데이터/원본·출시 게이트는 그대로 유지. 이 공지는 운영 통지이며 기능 완성 선언이 아니다.

> **2026-10-20 최신 개발 규칙:** [HANDOFF.md](HANDOFF.md), [STATUS.md](STATUS.md), [smoke 안내](docs/TAGGING_SMOKE_RUNBOOK_2026-10-20.md)를 먼저 읽어라. 97개 합성 테스트는 **GitHub에 정의**, 현재 HEAD 원격 CI 성공은 미확인. `observed/not_applicable`는 이미지 근거 필수. JSON 태깅 파일을 AI가 직접 만든 source post_id 등과 섞지 말고 신뢰된 실행 정보와 정규화하라. 실제 n8n/Meta/운영 DB 변경은 다음 단계 별도.

# AGENTS — OHORA Trend Analyzer

> **2026-10-20 추가 품질 작업 지침:** v1.1 태깅 분석 연동 시 `scripts/validate_model_output.py` → `scripts/normalize_p0_result.py` → 최종 `scripts/validate_taxonomy.py` / `taxonomy/p0_tag_result.schema.json` 검증 계약을 유지한다. 모델에게 ID·국가·관측시각·model_id를 생성시키지 말고, 신뢰된 실행/수집 정보만 결합한다. 7축 모델 응답과 14축 저장용 응답을 혼동하지 않는다. 현재 순수 Python 정규화·검증만 오프라인 구현됐으며 **n8n 실행/DERIVED DB 저장·실 이미지 정확도 검증은 미구현**. [최신 QA](docs/TAGGING_QA_EXTENSION_2026-10-20.md)와 [HANDOFF](HANDOFF.md) 우선.


> **2026-10-20 KST:** 설계가 먼저다. README/HANDOFF/STATUS/계약을 확인하지 않고 코드부터 작성하지 않는다.

## 1. 최상위 작업 목표

- 별도 저장소에서 n8n 기반 AI 이미지 태깅 → DERIVED 데이터 저장 → 읽기 전용 내부 대시보드까지 이어지는 **MVP**를 완성한다.
- 기존 [P6 RAW 수집기](https://github.com/hibi89/ohora-trend-catcher)는 독립 시스템이며, 이 저장소에서 구현을 중복하거나 정책을 바꾸지 않는다.
- **원본 API 응답, 관측 이력, 수집 메타데이터는 P6 소유**. 분석 결과, 분류 사전, 모델 실행 이력, 검수 결과는 Analyzer 소유.
- 11/03 제출 및 11/05 발표에 맞추며, 기능 확장보다 수집된 1건의 검증 가능한 E2E를 우선한다.

## 2. 금지/승인 경계

1. 사용자 별도 승인 전 **실 Meta API 호출, 토큰 사용, P6 운영 DB 갱신, 수집기 스케줄러 변경, P6 main 병합, 실제 계정 294개 무인 수집 활성화 금지**.
2. P6 동결 정책 **3 API 레인 A/B/C, limit=4, 2라운드/일, 각 계정 최신 3페이지×4개, 원본/변경 이력, 백필**을 바꾸지 않는다. 관련 [설계 원문](https://github.com/hibi89/ohora-trend-catcher/blob/main/docs/P6_FINAL_COLLECTION_DESIGN_2026-10-20.md)과 [동결 공지](https://github.com/hibi89/ohora-trend-catcher/blob/main/DESIGN_FREEZE_NOTICE.md) 먼저 확인한다.
3. 운영 P6 DB를 Analyzer 또는 n8n이 직접 쓰지 않는다. 읽기 전용 복제본 또는 P6가 정의·검증한 읽기 전용 export/adapter를 사용한다. SQLite 실운영 DB 파일을 n8n에서 직접 열지 않는다.
4. 실제 API 토큰, .env, 계정 인증 정보, Meta 응답 전문, 실수집 원본 CSV/DB, 사용자 개인정보, 미디어 파일을 Git에 커밋하지 않는다. 외부 AI 모델 전송 전에 데이터 범위·권한·비용을 승인받는다.
5. 새 GitHub 작업은 이 저장소에만. P6를 고치고 싶으면 먼저 영향·근거·대안 보고 후 명시 승인 요청.
6. P6의 합성 CI 통과를 실계정 API 연동·운영 검증 완료로 표현하지 않는다.

## 3. 분류/분석 계약

- 기준 사전: `taxonomy/tag_schema_v1_1.json`(14축, 159태그, S01~S04) + `taxonomy/tag_rules_v1_1.json`(P0 84개 판정 기준). 기존 v1.0-draft는 원본 보존. **팀 프로젝트 표준 v1.1이며 오호라 공식 내부 표준은 아님.**
- Astra 피드백: F01/F03/F05/F06/F08/F09/F10 **P0 7축**만 우선; 시어/시럽/젤리, 그라데이션/옴브레, 크롬/미러 경계 규칙; F02/F13/F14 등은 충분한 근거 없으면 unknown. `docs/TAXONOMY_DECISIONS.md` 참고.
- 값은 표시명 대신 불변 tag_id로 저장. 모델 출력은 사전 존재 여부·축 적합성·상태 조합으로 검증.
- `observed`/`unknown`/`not_applicable`/`not_evaluated`: **미실행과 판단불가를 구별**. 기존 draft의 `not_observed`는 의미가 모호하므로 자동 변환 금지. 결과는 `scripts/validate_taxonomy.py`의 계약 검사 통과 후만 저장.
- 분류할 수 없으면 빈 태그+정확한 상태; 사진에 보이지 않는 재료/공정/브랜드/오호라 상품을 상상하지 않는다.
- RAW는 원본 기록, DERIVED는 버전 있는 재실행 가능한 해석. 재분석 때 과거 결과 덮어쓰기 금지.
- 모델 self-reported confidence는 실제 정확도 확률이 아니다.
- taxonomy/model/prompt/분석 입력 식별자/미디어 ID/분석 시각/응답·정규화 결과를 버전 기록.

## 4. 구현 방법

- 모든 작업은 **작고 되돌릴 수 있는 단위**로 진행한다: 설계 계약 → 합성 fixture → 오프라인 검사 → 부분 기능 → E2E.
- n8n 프로세스가 파일 시스템 접근이 가능한지, hosted 여부, 버전, 자격증명 저장소, P6 export 호출 경로는 **확인 전 가정하지 않는다**.
- F5/페이지 조회로 AI 모델 재호출 금지. 내부 대시보드는 DERIVED DB 조회 전용.
- 실패/중복/모델 오류/요금 제한에서 fail-closed, 재시도 횟수 제한, 실행 상태와 오류 기록. 리플레이 재실행 가능해야 한다.
- API·DB 비동기 경계의 실제 상태(확인/미검증/차단)를 문서에 표시.
- 동시에 두 작업자가 같은 파일을 수정하지 않는다. 병렬 작업 시 독립 브랜치 또는 직렬 작업; 워크트리/머지 사용 강요 금지. main 푸시 전에 diff·비밀정보 검사.

## 5. 채팅방 교체/인수인계 프로토콜

1. 새 작업 시작: `README.md`, `AGENTS.md`, `HANDOFF.md`, `STATUS.md` 및 해당 단계 설계서 읽기.
2. 개발 전: 저장소 브랜치/HEAD/파일 상태 재조회, 중복 작업 확인.
3. 각 의미 있는 작업 단위 후: 실행 코드/테스트/결과/미검증/다음 1~3개 작업/롤백 경로를 `HANDOFF.md`와 `STATUS.md` **함께** 업데이트.
4. 문서만 커밋되었으면 **설계 완료**로만 표시; 구현·n8n import·실운영은 별도 검증.
5. 완료 보고 전 GitHub에서 두 파일을 다시 fetch하여 변경이 현재 HEAD에 반영됐는지 검증하고 SHA 제공.
6. 동일 실패를 같은 방법으로 2회 이상 반복하지 말고 원인과 대안 기록.
7. 사용자 입력 `ㄱ`/`3`/`.` 등의 단축 명령은 새 채팅방에서 사용자가 명시적으로 재확인하면 따른다. 본 문서만으로 임의 반복·백그라운드 실행하지 않는다.

## 6. 현재 우선순위

`docs/IMPLEMENTATION_PLAN.md`의 D0 태깅 기준 v1.1 발행 이후, D1 오프라인 fixture/연동 검증 → D2 n8n → D3 DERIVED DB → D4 내부 UI → D5 통합 검수 순서로 진행. 코드 파일 등록과 실제 실행/AI 정확도 검증은 구분한다. 사용자 승인 없는 운영 접속은 미완료 항목으로 남긴다.
