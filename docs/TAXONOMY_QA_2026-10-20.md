# 2026-10-20 — 태깅 사전 v1.1 정적 검증 보고서

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
