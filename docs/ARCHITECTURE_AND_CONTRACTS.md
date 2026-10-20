> **2026-10-20 변경 참고:** 태깅 정본은 [v1.1 사전](../taxonomy/tag_schema_v1_1.json), [84개 판정 규칙](../taxonomy/tag_rules_v1_1.json). 아래 설명용 JSON은 개략 필드 구조를 보여주는 **부분 예시**로서 P0 계약의 14개 facet 전부를 포함하지 않으므로 validator 입력으로 사용하면 안 된다. 완전한 검증용 JSON은 [합성 fixture](../fixtures/sample_valid_tag_result.json)를 사용할 것.

# 아키텍처 및 RAW↔DERIVED 데이터 계약 v0.1

작성 2026-10-20 | 상태: **설계 제안, 구현/운영 적용 전** | 소유 범위: Analyzer 저장소

## 1. 원칙 / 시스템 경계

```text
P6 (기존 분리 저장소, 권한·동결 설계는 P6가 소유)
Meta → P6 A/B/C Collector → P6 Capture / RAW 관측 DB
                                  │
                                  │ 검증된 read-only snapshot/export (추후 실제 필드 매핑)
                                  ▼
Analyzer (이 저장소)
    synthetic / read-only RAW adapter
           → input/media eligibility + fingerprint
           → n8n trigger + job lease
           → Vision+caption classifier (P0 7축)
           → taxonomy/schema validator
           → DERIVED-only writer transaction
           → DERIVED read-only view → Streamlit/Admin API
```

절대 금지: Analyzer→P6 쓰기, n8n→Meta 재수집/스케줄 변경, F5→AI 호출, API 필드가 누락됐는데 0으로 채우기.

P6 동결 요소: 공식 294개 계정, A/B/C 3 API 레인, limit=4, 일일 2라운드/계정당 최신 3페이지(최대 12개), 최신→누락 복구→과거 백필, 원본·재관측·변경 이력. 별도 승인 없이 바꾸지 않는다.

## 2. 명명 및 원본 소유권

- `post_id`: Instagram 게시물 식별자. 수집기에서 확인된 그대로 저장, 임의 신규 ID 생성 금지.
- `media_id`: 게시물 미디어/캐러셀 자식 식별자. 실제 값 확인 없이 게시물 ID 대입 금지; 없는 경우 source key를 별도 `source_media_key`로 표시.
- `account_id`, `account_username`, `country_code`: P6의 공식 대상 명단 및 수집 근거에서만 획득. 국가를 캡션 언어로 추측하지 않는다.
- `observed_at`: 값이 **조회된 시간**. `posted_at`: 게시물 **작성 시간**. 좋아요 이력의 역사적 시간은 observed_at 기준; 작성일로 역산 금지.
- `like_count`, `comments_count`, `followers_count`: NULL과 0 구분. 수집 필드 미요청/응답 없음도 별도 provenance.
- `media_type`, `media_url`, `thumbnail_url`, `permalink`, `child_order`, `partial_children`: 미디어 출처/캐러셀 구조. 이미지 URL은 영속 다운로드 경로라는 보장이 없으므로 원본 보존과 분석 사용 가능 여부를 분리한다.
- `source_provenance`: source run/observation/response reference, adapter_version, raw schema source, no synthetic/live claims 혼용.

**주의**: 위 필드는 **논리적 adapter 목표**다. P6의 실제 배포 DB 컬럼명이 이것과 동일하다고 확인된 상태가 아니다. raw_v2의 control/capture/raw 역할별 DB와 현재 실제 export 경로/테이블 이름을 확인한 뒤 adapter mapping을 확정한다. 기존 저장소에 없는 컬럼 생성 요구가 아니다.

## 3. 분석 입력 계약 (`analyzer_input_v0_1`)

```json
{
  "schema_version": "analyzer_input_v0_1",
  "source_kind": "synthetic_fixture",
  "source_ref": {"post_id": "DEMO_POST_01", "media_id": "DEMO_MEDIA_01", "source_media_key": null,
                 "raw_observation_id": "DEMO_OBS_01"},
  "account": {"account_id": "DEMO_ACCOUNT", "country_code": "JP", "username": "demo_only"},
  "post": {"posted_at": "2026-10-20T00:00:00Z", "caption": "demo",
           "permalink": null, "like_count": 0, "comments_count": null,
           "followers_count": null, "engagement_observed_at": "2026-10-20T00:30:00Z"},
  "media": {"media_type": "IMAGE", "media_url": null, "thumbnail_url": null,
            "child_order": 0, "carousel_partial": false,
            "analysis_image_source": "synthetic_placeholder", "is_accessible": false},
  "provenance": {"adapter_version": "0.1.0", "origin": "fixture", "raw_snapshot_id": "fixture-a"},
  "eligibility": {"status": "blocked_no_image", "reason": "fixture contains no image bytes"}
}
```

이 예시는 **도메인 계약을 확인하는 합성 문서 예시**다. 모델 호출 성공 사례로 취급하지 않는다.

### 입력 필수 검사

1. source id/참조 존재 및 무결성; child image면 부모 post 연결 필수.
2. image 분석 적격: IMAGE 단일/캐러셀 자식에 대해 이미지 실제 접근 가능·전송 허용. VIDEO/REELS 본문은 URL 수집만, 프레임 분석 보류.
3. observed/posted timestamp 분리, ISO-8601 UTC 저장 + KST 표시 시 변환.
4. `NULL`=데이터 없음, `0`=실제 0. 동의어 정규화는 DERIVED에만.
5. 원본 캡션은 P6에 원문 보존; 모델 입력에서 데이터 최소화·필터링 후 별도 `input_hash` 기록.
6. 부분 캐러셀은 부분임을 표시하고 보이는 자식만 독립 태깅; 없는 자식에 '장식 없음' 등 부정 판정 금지.

## 4. 태깅 출력 계약 (`analyzer_tag_result_v0_1`)

```json
{
  "schema_version": "analyzer_tag_result_v0_1",
  "post_id": "DEMO_POST_01",
  "media_id": "DEMO_MEDIA_01",
  "source_observation_id": "DEMO_OBS_01",
  "taxonomy_version": "1.1.0",
  "evaluated_facets": ["F01", "F03", "F05", "F06", "F08", "F09", "F10"],
  "model_id": "TO_BE_DECIDED",
  "prompt_version": "prompt-p0-v0",
  "analyzed_at": "2026-10-21T00:00:00Z",
  "analysis_input_hash": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "is_nail_design": true,
  "review_status": "unreviewed",
  "facet_results": [
    {"facet_id": "F01", "status": "observed", "tag_ids": ["F01.pink"],
     "confidence": null, "evidence_source": "image", "evidence_note": "visible pink area"},
    {"facet_id": "F03", "status": "unknown", "tag_ids": [],
     "confidence": null, "evidence_source": null, "evidence_note": "cannot determine transparency"},
    {"facet_id": "F05", "status": "unknown", "tag_ids": [],
     "confidence": null, "evidence_source": null, "evidence_note": "effect unclear"},
    {"facet_id": "F06", "status": "observed", "tag_ids": ["F06.french"],
     "confidence": null, "evidence_source": "image", "evidence_note": "colored tip"},
    {"facet_id": "F08", "status": "unknown", "tag_ids": [], "confidence": null, "evidence_source": null, "evidence_note": "not identifiable"},
    {"facet_id": "F09", "status": "unknown", "tag_ids": [], "confidence": null, "evidence_source": null, "evidence_note": "not identifiable"},
    {"facet_id": "F10", "status": "unknown", "tag_ids": [], "confidence": null, "evidence_source": null, "evidence_note": "not identifiable"},
    {"facet_id": "F02", "status": "not_evaluated", "tag_ids": [], "confidence": null, "evidence_source": null, "evidence_note": null}
  ],
  "structure": {"S01": null, "S02": null, "S03": null, "S04": null},
  "source_provenance": {"origin": "fixture"},
  "model_raw_response_ref": null
}
```

**예시는 필드 형식만 보여주며 실제 AI 판정/테스트 PASS 증거 아님.** 실제 validator는 모든 14축에 대한 상태 1개씩을 요구하는 방식 또는 `evaluated_facets`+미포함=not_evaluated 방식 중 하나를 **결정 후 강제**해야 한다. 기본 권고는 모든 14축의 facet row를 생성해 빈 항목을 오해하지 않도록 하는 방식이다. F07는 F06.french와 연동하되 이번 주에 미평가라면 **우선 not_evaluated**로 남기고 가짜 not_applicable을 만들지 않는다.

### 상태 정의 (제안 v1.1 목표)

| 상태 | 정의 | tag_ids | 예시 |
|---|---|---|---|
| `observed` | 평가했고 근거로 확인 | 1개 이상 | 이미지에 프렌치 팁 보임 |
| `unknown` | 평가했지만 판단 불가 | 빈 배열 | 조명 때문에 크롬/쉬머 판정 못 함 |
| `not_applicable` | 평가했고 논리적으로 해당 없음 | 빈 배열 | 프렌치 아니며 F07 검토 수행 |
| `not_evaluated` | 해당 축을 이번 실행에서 검사하지 않음 | 빈 배열 | P0만 실행, F13 미실행 |

**원본 draft JSON의 `not_observed`는 '미분석/이미지 미관측'을 함께 표현**한다. 이를 무조건 `not_evaluated`로 매핑하지 않는다. v1.1 동결 시 `not_evaluated`와 `input_unavailable`(job-level 처리 상태)를 분리하고 호환 변환 테스트를 만든다. 기존 draft JSON은 이 합의 전까지 수정 금지.

### 태그 검증 조건

- 모든 tag_id는 사전에 존재, 해당 facet prefix 동일. 이름·동의어/자유 텍스트의 DB 태그 직접 저장 금지.
- `observed`=nonempty, `unknown/NA/not_evaluated`=empty, `confidence`은 null 또는 0..1 유한 실수; `evidence_source`의 출처를 이미지/캡션/둘 다/검수 중 하나로 기록.
- AI 제안의 금속 재료/시술 공정/제품 라인업·SKU 추정 금지. 이미지가 없으면 태그 대신 job-level 실패/보류 상태.
- hallucinated tag, 중복 tag_id, 잘못된 facet 매핑, 누락/과도한 JSON, 텍스트/비JSON 출력 차단; 안전한 재시도·human review 경로.
- confidence는 모델 내부 추정치일 뿐 보정된 정확도 아님.

## 5. DERIVED DB 논리 스키마 (SQL 구현 전 초안)

**DB는 P6와 물리적으로 분리**. 초기 SQLite(로컬) 또는 승인된 서비스형 DB 중 환경 확인 후 선택. 테이블/PK/FK/유니크 키는 migration 코드로 명시한다.

| 논리 테이블 | 목적 / 핵심 필드 | 갱신 방식 |
|---|---|---|
| `taxonomy_versions` | taxonomy_version, file hash, frozen_at, reviewed_by, note | 버전 추가만 |
| `tag_dictionary` | taxonomy_version, tag_id, facet_id, ko/en/ja label, aliases, definition | 스냅샷+새 버전 |
| `source_media_refs` | source key, post_id, media_id?, raw observation ref, last_seen_at, media kind, country | 원본의 읽기 전용 참조 캐시, 민감값 최소 |
| `analysis_jobs` | job_id, media key, status, lease_owner/expiry, attempts, input fingerprint, last_error | 상태 전이/복구 |
| `analysis_runs` | run_id, job_id, taxonomy/model/prompt, input_hash, analyzed_at, raw_model_output_ref, validator_version | **append-only** |
| `facet_results` | run_id+facet_id, status, normalized tag ids, evidence, model confidence | 불변 실행 결과 |
| `structure_results` | run_id, S01~S04; 이번주에는 미평가 NULL 및 이유 | 실행 결과에 종속 |
| `review_events` | run_id, reviewer, old/new, reason, timestamp | append-only, 원출력 보존 |
| `pipeline_events` | event_id, job_id/run_id, stage, status, timestamp, error_class, safe_message | append-only |
| `current_analysis_view` | 미디어별 가장 최근 검증 통과·선택된 모델 결과 | 파생 조회 뷰 |

### 중복/재분석 키 (필수)

- 미디어별 `source_media_key`, `media_id`, 버전은 별도로 검증.
- 작업 dedupe key 제안: SHA256(`source_media_key` + `image_content_fingerprint` + `normalized_caption_fingerprint` + `taxonomy_version` + `model_id` + `prompt_version`). fingerprint의 사용 가능성과 권한은 실제 어댑터에서 확인한다.
- **오직 좋아요/댓글 수가 바뀐 것만으로 AI 이미지 태깅 다시 실행하지 않는다.**
- URL 만료/변경 자체가 곧 이미지 내용 변경은 아니다. 콘텐츠 해시 없이 미디어 동일성을 확정하지 말고 '미확인 fingerprint'를 구분한다.
- 동일 dedupe key에 완료된 유효 분석 결과가 있으면 AI 재호출 없이 결과 조회. 이전 실패는 재시도 정책에 따라 새 `run_id`로 실행.
- 상태 전이: `pending → leased → succeeded | retryable_failed | terminal_failed | needs_review | unsupported`. 임대 만료/프로세스 재시작 대응 설계.
- 다중 worker가 붙을 가능성이 있다면 **단일 writer 또는 DB transaction+UNIQUE 제약**으로 race를 방지한다.

## 6. 저장·조회·재분석 분리

- **수집**: P6가 수행. 운영 데이터 직접 수정 불가.
- **분석**: n8n이 새 작업 요청. job worker만 외부 AI 호출 가능.
- **조회**: 대시보드는 DERIVED 읽기 전용 endpoint 사용. RAW 리치 지표가 필요한 경우 읽기 전용 join/export snapshot 기반.
- **재분석**: 명시적 모델/버전 변경 또는 승인된 재시도 작업만 수행; 이전 결과 보존·검수 이력 추가.
- **영상/릴스**: URL/thumbnail/permalink 메타 유지; 이번 버전 프레임 분석 구현·검증되지 않음.

## 7. 환경·연결 미확정 사항

- P6 실제 RAW DB 파일명/테이블/view/export 형태 및 신뢰성 있는 읽기 경로.
- n8n 실행 환경이 로컬, 강의실 원격, Docker 중 어디인지 / 네트워크 격리.
- AI 제공자/비용/영상·이미지 외부 전송 적정성.
- SQLite 로컬만 사용 vs Supabase/별도 Postgres 계정·권한. **원격 n8n이 Windows SQLite를 직접 읽을 수 있다고 가정 금지.**
- 원본 이미지 URL 만료·접근 제약, 저장/다운로드 법적 권한·비용.
- P6 운영 연결·실 Meta 테스트 및 실운영 변경은 사용자의 별도 명시 승인 필요.

## 8. 향후 확장 지점

14축 전체 평가, S02/S03 네일별 관계, 이미지 임베딩·디자인 클러스터 ID, 공개몰 분류/상품 SKU, 일본·한국·미국 비교, 게시물 지표 시계열/트렌드 점수, 영상 프레임 분석. 설계상 필드가 존재한다는 이유로 이미 구현됐다고 주장 금지.
