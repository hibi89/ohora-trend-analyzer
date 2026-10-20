# 2026-10-20 — 태깅표 v1.1 추가 검증·연동 준비 작업

> **현재 기준:** 기존 v1.1 14축/159개 태그 ID는 변경하지 않음. 오늘 추가 작업은 모델 응답·정규화 계약, 합성 회귀, QA 준비만 진행. **n8n·P6 RAW 운영 DB·실 Meta API·외부 AI 실행/과금 없음.**

## 1. 기존 36개 회귀 이후 발견한 결함

- 기존 Python 출력 검증기는 `schema_version` 누락과 정의되지 않은 필드를 허용한 반면, JSON Schema는 거부했다.
- 미평가 축 `not_evaluated`의 빈 문자열 근거/분석 범위에 대해 검증기가 서로 다른 결론을 내렸다.
- JSON 파서 기본 동작이 **중복된 JSON 키를 마지막 값으로 덮고 NaN/Infinity를 허용**할 수 있었다.
- 잘못된 `evidence_source` 자료형이 모델의 JSON 응답에서 발생할 때 예외가 날 가능성이 있었다.

**수정:** Python 검증기·JSON Schema 계약 일치, 중복 키/비표준 상수 엄격 거부, 정의되지 않은 루트/축 필드 차단, 미평가 축의 허위 근거/범위 거부. 태그의 의미/ID/한영일 명칭은 변경하지 않음.

## 2. 오늘 추가한 순수 오프라인 기능

| 경로 | 담당 역할 | 완료 범위 |
|---|---|---|
| `scripts/validate_taxonomy.py` | v1.1 사전 정합성 + 최종 14축 결과 안전 검증 | **보강** |
| `taxonomy/p0_tag_result.schema.json` | 저장 직전 정규화 결과 JSON Schema | **보강** |
| `scripts/validate_model_output.py` | 모델에게 요청하는 **7축 소형 응답** 검사, 미등록 코드/가짜 소스 ID 거부 | **신규** |
| `scripts/normalize_p0_result.py` | 모델 7축 + 신뢰된 실행 식별정보 결합 → P1 7축을 `not_evaluated`로 채운 14축 DERIVED 결과 | **신규**, DB 쓰기 없음 |
| `fixtures/sample_p0_model_output.json` | 가상 7축 모델 응답 | **신규**, 실제 이미지 근거 아님 |
| `docs/P0_VISION_PROMPT_CONTRACT_v1_1.md` | 시각 판정 우선, SNS 캡션은 비신뢰 데이터, 모델 응답에 ID·국가 삽입 금지 | **신규** |
| `docs/TAGGING_IMAGE_QA_PROTOCOL_v1_1.md` | 승인된 실사진 30~50장 품질 검수 프로토콜 | **신규**, 사람 평가 미실시 |
| `fixtures/human_review_template.csv` | 개인·계정 정보 없는 빈 13열 수동 QA 기록 양식 | **신규** |
| `.github/workflows/taxonomy-check.yml` | 새로운 model-output validator와 모든 synthetic tests를 CI 대상으로 편입 | **갱신**, 원격 CI 확인 필요 |

## 3. 테스트 사실과 한계

- 기존 등록된 합성 검증 **36건**.
- 경계 조건을 확장한 추가 테스트 **16건** → 52건.
- 새 모델 7축 JSON 검사 합성 테스트 **20건** → 72건.
- 모델 출력의 신뢰된 식별정보 결합 및 14축 정규화 테스트 **13건** → **총 85개 테스트**.
- 이번 작업 환경의 **로컬 대응 구현**에서 Python unittest **85/85 PASS**, 양쪽 CLI schema/모델 샘플 검증 성공.
- GitHub 저장소 파일은 연결된 GitHub 도구로 개별 게시·수정·재조회할 수 있으나, 컨테이너 네트워크 DNS 제한으로 **GitHub 저장소를 직접 git clone해 실행한 85개 테스트는 아니다**.
- GitHub commit statuses는 빈 결과였고 push에 대한 Actions 실제 성공 로그도 확인되지 않았다. **GitHub CI PASS 주장 금지**.
- JSON Schema는 **최종 정규화된 결과용**이며 n8n 모델 Structured Output 기능이 이 스키마 전체를 지원한다고 가정하지 않는다.
- 85/85라는 수치는 **스키마·논리·에러 분기 합성 테스트 성공**이지, AI가 네일 사진에서 정확히 태그를 추출한다는 뜻이 아니다.

## 4. 내일 첫 작업 순서

1. 실제 GitHub 체크아웃 또는 GitHub Actions에서 다음 명령을 재실행하고 PASS 확인:
   ```bash
   python -m pip install -r requirements-test.txt
   python scripts/validate_taxonomy.py
   python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
   python -m scripts.validate_model_output --input fixtures/sample_p0_model_output.json
   python -m unittest discover -s tests -v
   ```
2. n8n 인스턴스(학교/로컬), AI 모델/요금/이미지 전송 권한, P6 read-only export 경로 확인.
3. **1개 승인된 이미지**로 Model P0 JSON → `validate_model_output` → `normalize_p0_output` → `check_result`/JSON Schema → DERIVED 개발 DB 쓰기 → 읽기 전용 UI의 순서로 실제 E2E 구현.
4. 모델 출력이 `is_nail_design=false`이면 `non_nail` 작업 상태로 종료, 14축 가짜 태그 생성하지 않는다.
5. 30~50장 사람이 검수해 실제 정확도·경계 모호성·country별 편향 평가. 이전의 원본 RAW, Meta quota, 수집기 스케줄 정책을 건드리지 않음.

## 5. 공개범위 및 비밀정보

- 연결된 GitHub 검색에서 이 저장소는 **public**으로 확인됨. 실제 이미지·고객 계정 리스트·Meta 토큰·DB 원본·.env 파일을 올리지 않는다.
- QA용 fixture/CSV는 가상 ID 또는 헤더만 포함하고, 허가받은 실데이터는 별도 보호된 위치에서만 사용.
- 민감한 게시물 캡션은 프롬프트의 명령이 아닌 **분석 대상 데이터**로만 취급한다.

**마감 이후에도 사용 가능한 점:** 원본 14축·159개 사전은 안정적으로 보존하면서 더 나은 모델·프롬프트만 바꿔 재분석할 수 있다. 이를 위해 RAW/DERIVED 데이터는 물리적으로 분리한다.
