# Tagging v1.1 — 오프라인 검사 및 내일 n8n 인수인계 (2026-10-20)

> **범위:** 태그 규격 검사·7축 모델 출력 형식·14축 파생 결과 형식의 합성 테스트 전용. Meta 호출/이미지 AI 호출/DB 저장/n8n 실행이 없다. 오호라 내부 공식 규칙이 아닌 프로젝트용 태그 표준 v1.1이다.

## 1. 단 하나의 사전 점검 명령

GitHub 저장소 루트에서 Python 3.11 이상 환경:

```bash
python -m pip install -r requirements-test.txt
python -m scripts.smoke_p0_pipeline
```

성공 시 기대 로그:

```text
PASS: synthetic P0 seven-facet proposal -> trusted normalization -> 14-facet Python and JSON Schema validation; no AI, n8n or DB activity
```

**원리**

```text
fixtures/sample_p0_model_output.json          [합성 7축]
fixtures/sample_trusted_execution_context.json [합성/신뢰된 작업 메타]
   │
   ▼
scripts/validate_model_output.py               [모델 태그 ID·근거·status 검사]
   ▼
scripts/normalize_p0_result.py                 [7축+신뢰된 ID/모델/시간 → 14축]
   ▼
scripts/validate_taxonomy.py                   [구조·태그 whitelist·출처 검사]
   ▼
taxonomy/p0_tag_result.schema.json             [최종 정규화 JSON Schema 검사]
   ▼
stdout PASS 또는 FAIL                            [파일/DB 미변경]
```

가상 정규화 결과를 화면에 보고 싶다면:

```bash
python -m scripts.smoke_p0_pipeline --print-result
```

출력은 실 Meta 게시물이나 실제 모델 결과가 아니며 `SYNTHETIC_` ID와 고정된 가상 관측값만 포함한다.

## 2. 전체 합성 회귀 검사

```bash
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m scripts.validate_model_output --input fixtures/sample_p0_model_output.json
python -m scripts.smoke_p0_pipeline
python -m unittest discover -s tests -v
```

**최신 테스트 함수 정의 기준 총 97개**

| 모듈 | test_* 함수 수 |
|---|---:|
| `tests/test_tagging_contract.py` | 35 |
| `tests/test_json_schema_contract.py` | 23 |
| `tests/test_model_output_contract.py` | 21 |
| `tests/test_normalize_p0_result.py` | 13 |
| `tests/test_smoke_p0_pipeline.py` | 5 |
| **합계** | **97** |

**주의:** 97개는 GitHub 코드에 **등록된 테스트 수**이다. **최신 97개가 원격 GitHub Actions에서 실행되어 PASS했다는 증거는 아직 없다.** 이전의 로컬 대응 코드 85/85 PASS는 이전 커밋의 별도 검증이며 신규 97개에 자동 승계할 수 없다.

## 3. CI가 왜 아직 미확인인가

- CI workflow: `.github/workflows/taxonomy-check.yml`, `push(main)`/PR/수동 실행 트리거.
- GitHub 연결 도구는 이번 `main` push에 대한 workflow run 상태를 확인할 수 없었고 commit status 조회 결과가 비어 있었다.
- 컨테이너의 github.com DNS가 작동하지 않아 `git clone`로 해당 최신 HEAD를 직접 체크아웃해 실행하지 못했다.
- 따라서 위 97개를 실제 실행했다는 표현을 사용하지 않는다.

**확인 방법:** GitHub 저장소 → Actions → `Taxonomy v1.1 offline contract checks` 실행 기록을 보고 `main` HEAD의 4개 단계(Install/Taxonomy/Model/Smoke/Unit tests) 통과 여부와 실패 로그를 확인. 실행 기록이 없다면 워크플로 승인/활성화 여부 또는 `workflow_dispatch` 수동 실행 가능 여부를 확인한다. 사용자 승인 없이 Meta/API를 호출할 일은 없다.

## 4. 가장 중요한 데이터 안전성

- `taxonomy/tag_schema_v1_1.json`은 **14축·159개 태그 코드 불변**.
- P0는 F01,F03,F05,F06,F08,F09,F10의 **7축 84태그만 평가**.
- P1 미실행 일곱 축은 `not_evaluated`, 모델 임의 추가 금지.
- AI가 만든 게시물 ID/국가/모델 버전/분석 시간 등은 신뢰하지 않고 실행기가 채운다.
- `observed` 또는 `not_applicable`에는 **이미지 근거**가 필요. 캡션 주장만으로 실제 요소 존재/부재를 단정하지 않는다.
- `unknown`: 판단 실패, `not_applicable`: 관측 범위 내 해당 없음, `not_evaluated`: 아예 검사하지 않음.
- 비네일은 14축 태깅 결과가 아니라 **job-level `non_nail`**. 동영상 프레임 분석은 이번 MVP 범위 밖.
- n8n과 모델 output parser가 실패 시 DERIVED에 가짜 완료 레코드를 저장하지 않도록 fail-closed 처리.

## 5. 다음 작업 순서

1. **원격 CI 실제 97개 실행/통과 확인**, 실패하면 해당 테스트만 원인 수정.
2. P6 운영 RAW가 아닌 synthetic fixture에서 n8n Manual Trigger 시작.
3. n8n 환경(학원 원격/로컬), 이미지 접근/전송 허용 범위, VLM 모델·요금/자격증명 보관 확인.
4. 코드로 이미 정해진 모델 7축 → validator → normalize → final validator 호출을 검증된 방식으로 연동. n8n 실행 환경에서 Python 코드를 직접 사용할 수 있다고 가정하지 않는다.
5. 별도 DERIVED DB에는 성공 검증 결과만 저장. 운영 RAW 수정 금지. F5는 DB만 조회.
6. 승인된 실제 이미지 30~50장에 대한 사람 검수는 별도 품질 평가. 오호라 공식 내부 표준 승인과 혼동 금지.

## 6. 롤백 및 책임

- 오늘 수정한 영역: `scripts/validate_taxonomy.py`, `scripts/validate_model_output.py`, `taxonomy/p0_tag_result.schema.json`의 **출처 판정 강화**와 테스트, `scripts/smoke_p0_pipeline.py` 및 합성 fixture·문서.
- **RAW·P6·n8n·실 AI API·운영 DB 수정 없음**.
- 문제가 생기면 GitHub 해당 커밋들만 revert하고, v1.1 사전/159개 tag_id는 유지. 멋대로 taxonomy 의미 변경 금지.
