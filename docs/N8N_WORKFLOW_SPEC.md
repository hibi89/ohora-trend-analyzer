> **2026-10-20 기준:** 태깅 사전과 판정 규칙 v1.1은 GitHub 등록 완료. [tag_schema_v1_1.json](../taxonomy/tag_schema_v1_1.json), [tag_rules_v1_1.json](../taxonomy/tag_rules_v1_1.json), [검증기](../scripts/validate_taxonomy.py) 및 [QA](TAXONOMY_QA_2026-10-20.md)를 우선한다. **실제 n8n workflow 파일은 아직 없음.**

# n8n Workflow 설계 명세 — 2026-10-21~23 구현용

상태: **노드·분기 설계만 완료 / workflow JSON 및 n8n 실제 실행은 아직 없음**.
상세 계약: [ARCHITECTURE_AND_CONTRACTS.md](ARCHITECTURE_AND_CONTRACTS.md)

## 1. n8n의 역할/범위

P6의 Meta API 호출·스케줄·수집을 **다시 만들지 않는다**. n8n은 기존 RAW의 읽기 전용 export/adapter가 제공한 미디어를 분석해 **DERIVED DB에만** 쓴다.

```text
Manual Trigger / Schedule Trigger(나중에)
  → A. source_readonly_export / synthetic fixture
  → B. normalize + eligible-media filter
  → C. job claim (dedupe / retry lease)
  → D. get image content / resolve accessible URL (권한 준수)
  → E. call VLM (image + caption)
  → F. JSON parse + taxonomy v1.1 validator
  → G. derived-only writer (atomic)
  → H. audit + status + optional report
                      ↘ failure/error log → retry or human review
```

**수동 트리거로 1건 성공**하기 전 Cron 또는 자동 수집 활성화 금지.

## 2. 주요 노드 계약

| 단계 | 입력 | 출력 | 실패 시 정책 |
|---|---|---|---|
| A: Source adapter | read-only snapshot id / fixture path | `analyzer_input_v0_1` 배치 | missing/raw unapproved→STOP |
| B: Normalize/filter | post + media children | 이미지 분석 후보 배열 | VIDEO/REELS→`unsupported_video` 기록 후 이번 주 skip |
| C: Claim | media key + source fingerprint + taxonomy/model/prompt | job id, lease, run eligibility | already_succeeded→LLM 호출 금지 |
| D: Access image | authorized media URL / snapshot byte handle | 이미지 입력, content evidence | expired/403/429→retryable / reason |
| E: VLM | image+caption+fixed 7 facets | untrusted JSON string | budget/rate/model error→bounded retry |
| F: Validator | model output+taxonomy snapshot | validated normalized result | invalid tag/schema→needs_review, DB 태그 기록 금지 |
| G: Writer | validated result+job id | committed run_id, status | transaction 실패→retryable (동일 idempotency key) |
| H: Audit | job+run result | counts, diagnostics | 조회 가능한 실패 기록 보존 |

후보 목록은 P6가 저장한 정보에서 가져온다. 새 게시물 또는 새로운 관측값이 있다는 것만으로 매번 태깅하지 않는다. **이미지/캡션에 실제 변화가 있거나 taxonomy/model/prompt가 바뀌었을 때만 재분석 후보.**

## 3. n8n 실행 환경 주의점

- n8n Cloud/학원 호스팅에서는 사용자의 로컬 Windows 파일이나 `localhost` DB를 직접 읽는 것이 **일반적으로 불가능**. Docker의 localhost는 컨테이너 자신일 수 있음.
- 따라서 **합성 JSON → HTTP adapter → 별도 DERIVED DB** 연결을 먼저 구축하고, 학교 네트워크/권한 확인 후 read-only export 연결을 선택한다.
- 원격 시스템으로 P6 원본 DB 파일 업로드 금지. 대안은 **승인된 최소필드 export, 제한된 read-only API, 또는 승인된 DB read replica**.
- 외부 VLM에는 권한이 있는 이미지/캡션만 전달하고, secrets를 n8n Credentials/.env로 관리. 실행 로그에서 token과 원본 내용을 가린다.
- 노드 명칭과 옵션은 실제 n8n 버전에서 확인. `Execute Command`, 외부 python package나 filesystem nodes의 사용 가능성을 가정하지 않는다.

## 4. 분석 스키마와 검증

- P0: F01, F03, F05, F06, F08, F09, F10.
- 나머지 축은 `not_evaluated` 명시.
- source provenance: RAW observation/ref + media id + image inspection status + captions separately.
- normalized `facet_results`: allowed `tag_id`, matching facet, `observed`→tag IDs 존재, `unknown`/NA/미평가→빈 배열.
- AI 원문 JSON은 untrusted input: JSON 파싱 성공만으로 저장하지 말고 whitelist/enum/length/관계 검사 통과 필요.
- 모델이 사진이 아닌 캡션을 근거로 태그를 붙이면 `evidence_source=caption`; 추정 정보의 검수 대상 분리.
- 분류용 프롬프트/결과/validator는 버전 관리.
- 크롬과 미러처럼 **다른 축**이면 동시 태깅 가능(단 F04는 P1이라 이번 주 미평가).
- v1.0-draft의 not_observed는 모호하므로 v1.1의 not_evaluated로 자동 일괄치환하지 않는다. v1.1 상태 계약 및 검증 코드는 저장소에 등록했으며, 실제 Python 회귀·n8n 사용 검증은 후속.

## 5. Idempotency와 실패 복구

- `dedupe_key`는 source media, 실제 이미지/캡션 fingerprint, taxonomy/model/prompt 버전을 결합. 외부 이미지 URL 만료/회전과 컨텐츠 변경을 혼동하지 말 것.
- `analysis_jobs` status: pending→leased→succeeded / retryable_failed / terminal_failed / needs_review / unsupported.
- 같은 key의 유효 succeeded가 있으면 skip_model; 사용자 명시 재분석은 new version/key/run.
- 성공 저장은 트랜잭션 처리, 오류 시 어느 단계에서 실패했는지 구분. 외부 모델 호출 후 DB 쓰기 실패 시 같은 이미지로 재호출하기 전에 검증 가능한 durable AI 응답 스냅샷이 있으면 이를 재사용한다.
- retry 정책 제안: 429/5xx/일시적 네트워크는 제한 횟수+백오프; 400/권한·스키마 오류는 즉시 분기. 실제 API 제한/비용 확인 후 수치 확정.
- `Error Trigger`/분기에서 `job_id`, `stage`, `error_code`, `retry_after`, `sensitive_redacted_message`, 실행 시각 기록.
- n8n 합성 fixture 기반 로직 개발은 사용자 계획에 따라 2026-10-21부터 가능하다. 단, 실제 Meta 호출·유료 외부 AI 요청·실데이터 전송·운영 DB 변경은 별도 승인/예산 확인 전 금지.

## 6. import/export 파일 계획

```text
workflows/
  README.md                         # import/credential/config 방법
  p0-tagging.workflow.json          # 실제 n8n에서 export한 파일 (미작성)
  sample-trigger.workflow.json      # 선택: 합성 데이터 전용
config/
  taxonomy_version.json             # 사전 버전 동결 후 (미작성)
fixtures/
  synthetic_single_image.json       # 추후 생성
  synthetic_carousel_partial.json   # 추후 생성
tests/
  test_taxonomy_validator.py        # 추후 생성
```

n8n workflow에는 실제 API 키, 민감 Headers, 실 URL, 내부 DB 접속 문자열을 포함하지 않는다.

## 7. 완료 기준과 필수 테스트

- [ ] n8n 환경/version/network/credentials storage 확인
- [ ] 합성 이미지 1건 분류 정상·schema validator 통과
- [ ] 캐러셀 2장 개별 분석 및 post 연결
- [ ] F03 syrup/jelly/sheer 등 경계 판정 기준 prompt 적용
- [ ] unknown/NA/not_evaluated 구분 검증
- [ ] like_count=0, comments_count=NULL 값 변조 없음
- [ ] VIDEO는 파일 다운로드/프레임 분석 없이 지원 제외 상태 기록
- [ ] 중복 실행 시 외부 AI 요청 추가 0회
- [ ] invalid tag 반환 시 DERIVED 태그 저장 0건
- [ ] 모델 429/이미지 만료/DB 저장 실패→중단/복구
- [ ] 원본 DB·스냅샷 해시 변화 없음
- [ ] n8n import와 실제 실행 증거 기록 (워크플로 파일만으로 통과 주장 불가)

## 8. 첫 구현 작업자에게

첫 작업은 **실 API가 아니라 합성 source fixture + taxonomy whitelist 검사기**다. P6 운영 DB와 Meta 토큰 연결부터 시작하지 않는다. 성공한 합성 결과가 DB에 저장되면 그때 사용자에게 실수집 export 연결 승인과 인터페이스를 요청한다.
