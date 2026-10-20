> **2026-10-20 최종 점검 추가 (최신 정보):** v1.1 사전·84개 판정 규칙·[정규화 JSON Schema](../taxonomy/p0_tag_result.schema.json)·22개 기존 검사(기본 16+잘못된 JSON 자료형/상태 근거 6)·JSON Schema 테스트 14개, 총 **36개 합성 테스트의 로컬 동등코드 실행 PASS**. GitHub Actions 실행 로그/완료 상태는 **미확인**. 원본/미디어 실데이터·Meta·n8n·운영 DB 접근은 없음. 세부 [통합 인수인계](TAGGING_INTEGRATION_HANDOFF_v1_1.md).\n\n# 2026-10-20 — 태깅 사전 v1.1 정적 검증 보고서

> **후속 검증 최신 기준:** [2026-10-20 추가 QA 보고](TAGGING_QA_EXTENSION_2026-10-20.md)에 로컬 대응 구현 합성 **85/85 PASS**와 model-output→14축 정규화 파일이 기록돼 있다. 아래 36건 표기는 **당일 초기 단계의 이력**이며 최신 합계가 아님. GitHub Actions 원격 실행/실 네일 이미지 모델 정확도는 여전히 미확인.


> **범위:** 팀 프로젝트용 태깅표/검증 계약. 실 이미지 AI 판정·n8n/Meta/API/DB 운영 검증 아님.

## 확정한 데이터 사전 기준
- `taxonomy/tag_schema_v1_1.json`: 14개 대분류 F01~F14 및 기존 159개 불변 태그 ID/표시명/동의어.
- `taxonomy/tag_rules_v1_1.json`: 이번 주 우선 구현 7축 F01,F03,F05,F06,F08,F09,F10에 속한 84개 태그의 시각 판정 기준과 경계 규칙 10개.
- P1 7축 F02,F04,F07,F11,F12,F13,F14는 사전에는 유지하지만 P0 성공 응답에서 `not_evaluated`.
- 디자인 관계 정보 S01~S04는 사전에서 유지; 실제 모델 구현 수준은 미정이며 미구현 기능을 이미 분석 완료로 표시하지 않는다.
- 결과 상태: `observed`, `unknown`, `not_applicable`, `not_evaluated`. 기존 v1.0-draft의 `not_observed`는 중의적이므로 맥락 없이 변환하지 않는다.
- `input_unavailable`, `non_nail`, `unsupported_video`는 facet 태그가 아닌 **작업 단위 상태**다.

## 실행 및 정적 검증 실적

1. 기존 v1.0-draft와 v1.1의 159개 `tag_id`/slug/한국어·영어·일본어 라벨/동의어/active 상태 모두 **변경 없이 보존**.
2. facet 14개, 전체 태그 159개, P0 7축, P0 태그 84개, P1 7축 확인.
3. 각 tag_id의 축 prefix, 중복 ID, 축 내 alias 충돌 검사 통과.
4. v1.1과 판정 규칙 파일의 버전 `1.1.0` 일치, P0 84개 전부 규칙 존재, 혼동 규칙 10개 존재 확인.
5. 성공 결과 예시에서 총 14축 각 한 행을 유지하고 P0 미평가 오류/P1 허위 평가가 없는지 정적 검사 통과.
6. 이전 채팅에서 로컬 `verify_tagging_v1_1.py` 실행 결과: `PASS: 14 facets, 159 unchanged IDs/labels, 84 P0 definitions, 10 ambiguity rules, 4 status enum, no scoped alias collisions`.
7. 이번 세션에서 GitHub 파일을 다시 읽어 시행한 **12개 구조 항목 전부 통과**.
8. `scripts/validate_taxonomy.py`, `tests/test_tagging_contract.py`(합성 테스트 16개), `fixtures/sample_valid_tag_result.json`, `.github/workflows/taxonomy-check.yml`을 등록했다.

**검증 상태 구분:** 위 12개는 연결된 GitHub 파일에 대한 정적 데이터 비교 검사이다. 새로 업로드한 Python 테스트 16개가 **GitHub Actions에서 통과했다는 증거는 아직 없음**. 컨테이너에서 GitHub `git clone` 시 DNS를 해석할 수 없어 GitHub 체크아웃 실행을 진행하지 못했다. GitHub commit combined statuses 조회는 빈 목록이었으며 PASS로 추정하지 않는다.

## 로컬/CI 필수 실행 명령

```bash
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m unittest discover -s tests -v
```

위 명령은 **외부 API/DB 접근 없는 구조 검증**이다. CI가 실행 가능하면 `.github/workflows/taxonomy-check.yml`의 작업 결과를 직접 확인해야 한다.

## 아직 검증하지 않은 것

- 실제 네일 이미지에 대한 AI 모델 태깅 정확도·재현율·국가별 편차·모호한 태그의 실무 합의.
- 실제 n8n 워크플로 구성과 VLM 호출 결과, 운영용 JSON Validator 연동.
- 오호라 내부 공식 분류표, 일본어 전체 159개 정식 표기, 실제 실무자 승인.
- P6 운영 RAW export 규격·실 Meta 토큰·운영 DB 변경/배포.

## 10/21 시작 시 우선 행동

1. `HANDOFF.md`, `STATUS.md`, 이 파일과 `taxonomy/tag_schema_v1_1.json`, `taxonomy/tag_rules_v1_1.json`을 읽어 최신 기준을 복원.
2. Python 오프라인 16개 테스트와 CI 결과 확인. 실패 시 원인만 최소 수정하고 재검증.
3. P6 수집기의 승인된 읽기 전용 export/합성 fixture로 n8n 테스트. 원본 DB를 쓰지 말 것.
4. n8n의 AI JSON 응답은 14축 결과를 내되 우선 7축만 평가하고, `scripts/validate_taxonomy.py`와 동일 계약으로 검사한 뒤 별도 DERIVED DB에 기록.
5. 실사진 30~50장에 대한 사람 검수는 접근권한 확보 후 진행하며 그 전까지 모델 정확도 주장 금지.

## 인계 주의

**데이터 사전 기준 v1.1 등록 완료 ≠ 분석 엔진 완성 ≠ 오호라 실무 검증.** 태그 사전 JSON은 나중에 버전업 가능하고, Meta RAW는 P6의 별도 저장소에서 변경하지 않는다.

## 2026-10-20 추가 검증 상세 (이번 작업)

- 로컬 별도 작업 디렉터리에서 GitHub 태깅 검사 함수 및 합성 테스트를 대응 구현해 재현: `python -m unittest discover -s tests -v` → **36/36 PASS** (22개 결과 검증 + 14개 JSON Schema 규격 검사). 같은 local fixture/스키마로 `python scripts/validate_taxonomy.py` 및 `--result fixtures/sample_valid_tag_result.json` PASS.
- 실제 GitHub 저장소를 로컬에서 클론해 검사한 결과는 아니다(네트워크 DNS 제한). 등록된 최신 소스 17파일 GitHub fetch-back 및 JSON 구조 검사로 정합성 검토.
- GitHub 파일 기준 재확인: F01~F14 정확히 14축, 159개 태그 ID 전수 불변/유일, P0 7축·84개 규칙, 14축 결과 계약, 36개 테스트 함수, 14개 JSON Schema 중복방지 조건, 원본 v1.0 보존.
- 잘못된 `facet_id`/`status` 자료형의 예외 중단 방지, `not_applicable`의 부재 판단 이유 필수, `not_evaluated` 근거 주장 차단.
- 팀원용 XLSX 최종본은 7개 시트(기존 5개 + S01~S04 구조 4개 + 오호라 공개몰 분류 대응표)로 갱신해 사용자 채팅 첨부로 제공. **XLSX 파일 자체는 GitHub에 미등록**; 개발 표준 정본은 JSON과 기준서.
- P0 JSON Schema는 **정규화 결과 검증용**으로서 n8n의 모든 Structured Output 구현에서 그대로 동작한다는 보장은 없다. 내일 실제 n8n 환경과 검증 어댑터를 확인해야 한다.
- 이미지 태깅 품질, 294계정 실수집, DERIVED DB 실저장, 유료 외부 AI 실행 및 Github Actions CI PASS는 **여전히 미검증**.
