# HANDOFF — OHORA Trend Analyzer (새 채팅방 즉시 인수인계)

> **2026-10-20 KST | 최신 상태 요약 (기존 기록보다 우선)**
>
> GitHub `hibi89/ohora-trend-analyzer`, 기본 브랜치 `main`. 신규 저장소에 **설계 문서·태그 사전 원본 스냅샷**만 올렸다. **n8n workflow/AI 태깅 실행/DERIVED DB/관리 대시보드는 모두 미구현이며 실테스트 결과 없음.** 기존 P6 Collector 저장소·실운영 RAW DB·Meta API 호출을 변경하지 않았다.
>
> **새 채팅방에서 먼저 할 일:** `README.md → AGENTS.md → HANDOFF.md → STATUS.md → docs/IMPLEMENTATION_PLAN.md → docs/ARCHITECTURE_AND_CONTRACTS.md → docs/TAXONOMY_DECISIONS.md` 순서로 읽고, repo HEAD를 재확인하라. 이어서 D0 태그 규칙/상태 계약을 결정한 후 D1 synthetic adapter/fixture 개발부터 시작한다. 실제 Meta 호출·운영 DB 접근·외부 AI 이미지 전송은 별도 승인 전 금지.

## 1. 프로젝트의 존재 이유

사용자는 OHORA KDT 2차 프로젝트에서 API 수집 시스템에 시간을 투자해 **원본과 관측 이력을 오래 보존**하도록 했다. 네일 AI 분석·태깅·대시보드의 기준은 개선되어도 원본을 재수집하지 않고 새 기준으로 재분석할 수 있게 만드는 게 핵심 목표다.

- **P6 Collector:** Meta API에서 SNS 원본, 계정/게시물/미디어/시점별 메트릭과 변경 이력 보존.
- **Analyzer (이 repo):** P6의 **승인된 읽기 전용 export**를 이용해 **AI 이미지 태깅 → n8n 자동화 → 별도 DERIVED DB → 내부 관리 UI**.
- **프론트엔드 팀원 화면:** 별도 개발, 공통 read-only 조회 계약만 공유.
- 이번 주는 MVP로 **단일 미디어 E2E + 7축 태깅 + DB 저장 + 조회**가 목표; 트렌드 예측/추천은 이후 확장 가능성으로 제시.

## 2. 태깅 체계와 Astra 의견

- 원본 `taxonomy/tag_schema_v1_0_draft.json`: **F01~F14, 14축, 159개 태그, S01~S04 구조 정보 4개**, 제안 표준. 오호라 **공식 내부 태깅표 아님**.
- P0 분류: **F01 색상, F03 발색·투명도, F05 효과·재질감, F06 기본 기법, F08 패턴, F09 모티프, F10 입체 장식**.
- P1 미평가: F02 F04 F07 F11 F12 F13 F14; 강제 자동 태깅 금지. 구조 S01/S04는 여력 따라 기본 지원, S02/S03 후속.
- Astra 피드백: 시럽/젤리/시어, 그라데이션/옴브레, 크롬/미러 명확 구분. F02/13/14 사진·캡션에서 오판 많으므로 미검증 추측 금지.
- 모델이 판정하지 않은 상태(`not_evaluated`)와 실제 판단불가(`unknown`)를 반드시 구분할 것. 기존 스냅샷은 `not_observed` 사용하므로 **v1.1 상태 규칙 확정/호환 테스트가 첫 과제**.
- 파일: [태깅 원본 설명서](docs/TAXONOMY_ORIGINAL_v1_0_DRAFT.md), [태깅 결정 기록](docs/TAXONOMY_DECISIONS.md), [JSON draft](taxonomy/tag_schema_v1_0_draft.json).
- **주의:** v1.1 파일은 아직 존재하지 않으며, 원본 draft를 최종 동결 파일로 과장하지 않는다.

## 3. 확정된 안전 경계

- P6에 대해 294개 공식 계정, **A/B/C 3 API 레인, limit=4, 하루 2라운드 계정당 3페이지×4 = 최대 12개 최신 수집, 원본·모든 필드 재관측/변경 이력, HISTORY backfill**, 동결된 설계를 존중. 설계 원문: https://github.com/hibi89/ohora-trend-catcher/blob/main/docs/P6_FINAL_COLLECTION_DESIGN_2026-10-20.md
- 이 저장소에서 P6 로직을 고치거나 운영 DB를 갱신하지 않는다. 기존 수집기와 n8n을 역할 분리.
- API 토큰, 실 DB/CSV, 실제 사용자 데이터 등 GitHub 업로드 금지. .gitignore만으로 비밀정보 보호를 보장하지 않으므로 diff 검사.
- P6가 GitHub에서 합성 테스트 PASS를 기록했더라도 **실 Meta 294계정 운영 수집 성공 보장 아님**. 사용자에게 라이브 승인/환경 확인 후 연결.
- n8n 위치(학교 원격/로컬), P6 실제 export 경로/테이블 컬럼, AI 모델 비용/전송 범위, DERIVED DB 저장 제품 **아직 미확정**. 임의 값 확정 금지.

## 4. 일정과 단계 (상태는 STATUS.md가 정본)

| 일정 | 작업 | 현재 상태 |
|---|---|---|
| 10/20(화) | D0 설계 및 태깅 v1.1 확정 | 설계 문서 등록 완료, v1.1 태그 동결 대기 |
| 10/21(수) | D1 P6 read-only adapter/fixture / D2 n8n 시작 | 미구현 |
| 10/22(목) | D2 P0 7축 VLM JSON 검증 | 미구현 |
| 10/23(금) | D3 DERIVED DB와 중복·오류·복구 | 미구현 |
| 10/24(토) | D4 내부 운영 대시보드 | 미구현 |
| 10/25(일) | D5 통합 테스트 및 팀 전달 | 미구현 |
| 11/03(화) | KDT 제출 | 예정 |
| 11/05(목) | KDT 발표 | 예정 |

## 5. 개발할 구조

```
P6 RAW Collector (다른 repo, 사용자 동결)
           ↓ read-only export/clone/validated adapter
         n8n
           ↓ image+caption → P0 7-facet VLM
      schema validator
           ↓ taxonomy/code/status validation
     DERIVED DB ONLY
           ↓ read-only API/view
       운영 대시보드
```

- 기본 분석 단위는 **post가 아니라 media**. 1개 post에 캐러셀 여러 장.
- 영상/릴스 **URL/thumbnail/permalink 보존**은 P6; Analyzer의 프레임/동영상 분석은 이번 주 미구현·후속.
- source data의 likes/댓글이 바뀌어도 네일 디자인이 동일하면 Vision AI 재분석 불필요.
- idempotency: media content/caption fingerprint + taxonomy/model/prompt version, DB unique key/claim/lease; 동일 성공 분석 재호출 금지.
- 모델 결과 JSON을 절대 검증 없이 저장하지 않음. 알 수 없는 코드 격리.
- UI F5/조회 시 n8n/Meta 호출 없음.
- `docs/ARCHITECTURE_AND_CONTRACTS.md`의 예시 JSON은 **합성 예시**이며 진짜 기능이나 모델 판정 결과 아님.

## 6. 다음 작업: 구체적인 첫 3단위

### Task A (D0) — 태깅 v1.1 규칙 합의
- `docs/TAXONOMY_DECISIONS.md`의 상태값: `observed`, `unknown`, `not_applicable`, `not_evaluated` 구분.
- 기존 JSON `not_observed` 호환성 검토; 새 v1.1 파일 작성 시 파일명/버전 변경, 기존 원본 그대로 보존.
- F03/F05/F06 경계가 validator로 검증 가능한 것과 프롬프트 사례로만 가능한 것을 구분.
- 납품: decisions 확정, 스키마 신규, schema static tests(합성).

### Task B (D1) — synthetic normalized input
- `fixtures/synthetic_single_image.json` 및 `synthetic_carousel_partial.json` 생성(허구 계정/게시물 ID, 실 URL 금지).
- Python 경량 adapter/validator 코드를 작성하고 DB 없음 상태에서 input/output 검증.
- P6 실제 스키마/호출 경로를 확인할 때까지 **실운영 원본 접근 없음**.
- 납품: sample JSON, parser/validator 테스트 커맨드+PASS.

### Task C (D2) — n8n import와 최초 1건
- 학교 n8n 환경·외부 AI 접근 승인 확인.
- Manual Trigger → fixture/read-only adapter → Vision AI → validator → DERIVED test DB.
- 첫 1건 성공 후에만 Loop/스케줄·배치 적용.
- 납품: `workflows/p0-tagging.workflow.json`, import 절차, 성공·실패 실행 결과·비용·운영 미검증 기록.

**다음 실행은 이 세 작업 중 A부터.** 사용자 명시 요청 또는 새 채팅방에서 `ㄱ` 등을 받으면 진행하되, 실 Meta·운영 DB·외부 API 과금은 매번 승인 경계 확인.

## 7. 저장소 주요 문서 인덱스

- [README](README.md): 빠른 안내 및 시작 순서
- [AGENTS](AGENTS.md): 작업 금지/수정 정책
- [STATUS](STATUS.md): 실제 단계/검증 상태
- [구현 일정](docs/IMPLEMENTATION_PLAN.md): D0~D5 완료 기준·컷라인
- [데이터 계약](docs/ARCHITECTURE_AND_CONTRACTS.md): RAW↔DERIVED 분리/JSON/상태/DB
- [태깅 규칙](docs/TAXONOMY_DECISIONS.md): 14축·7축·Astra 보완·v1.1 gate
- [n8n 설계](docs/N8N_WORKFLOW_SPEC.md): 노드·오류·중복·비용·검증
- [주말 관리 UI](docs/INTERNAL_DASHBOARD_SPEC.md): 미디어 카드·태그·오류/로그 조회

## 8. 채팅방 전환용 1분 프롬프트

> `hibi89/ohora-trend-analyzer`를 GitHub에서 직접 확인해 이어받아라. `main`의 README/AGENTS/HANDOFF/STATUS 및 IMPLEMENTATION_PLAN/ARCHITECTURE_AND_CONTRACTS/TAXONOMY_DECISIONS/N8N_WORKFLOW_SPEC을 읽고, 실제 HEAD와 완료·미완료를 구분해라. 본 저장소는 P6와 별도 태깅/n8n/파생 DB/관리 UI이며 원본 RAW는 읽기 전용. 14축·159태그 유지, P0 7축(F01 F03 F05 F06 F08 F09 F10). D0 v1.1 상태/경계 규칙부터 작은 오프라인 테스트 단위로 개발하고, 매 단계 HANDOFF·STATUS를 갱신하라. 실 Meta 호출·운영 DB 변경·비밀정보 업로드·P6 설계 수정은 별도 승인 없이 하지 마라.`

## 9. 변경 시 필수 로그 템플릿

```text
작업 일시/브랜치/커밋:
목표/변경 파일:
완료한 기능:
검증 명령/테스트 PASS/환경:
미검증/실운영 차단:
영향 DB 또는 API 호출:
롤백 방법:
바로 다음 최소 작업:
HANDOFF.md/STATUS.md 동기화 확인:
```

**프로젝트 숫자 단축 ID:** 이 저장소에 대한 등록부/BOOK 매핑을 확인하지 못했으므로 **미배정**. P6 번호를 그대로 재사용하지 않는다.
