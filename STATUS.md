# STATUS — OHORA Trend Analyzer

> **2026-10-22 KST · 프로젝트 번호 p8 확정:** Analyzer(`hibi89/ohora-trend-analyzer`)는 **p8: n8n 분석 자동화·AI 태깅·DERIVED DB·읽기 전용 대시보드/Sheets 활용** 전담. 기존 P6(`hibi89/ohora-trend-catcher`)는 **p6: Meta 수집·RAW/Capture·SQLite·수집 tick** 전담을 유지한다. 사용자 승인으로 **p6/p8 투트랙** 진행하며 저장소 병합·코드 이관 없음. 번호 정본: [BOOK.md](https://github.com/hibi89/project-book/blob/main/BOOK.md). p8의 다음 실제 구현 단위는 [Issue #1](https://github.com/hibi89/ohora-trend-analyzer/issues/1) 합성 1건→태깅 검증→별도 DERIVED SQLite→조회; 현재 여전히 **구현 대기**, 실제 n8n·VLM·운영 데이터·Sheets 미실행.


> **2026-10-22 KST · 승인된 저장소 경계 / 개발 대기:** 수집 Meta·RAW·Capture·SQLite·수집용 n8n tick은 P6 `ohora-trend-catcher`가 계속 소유. **본 Analyzer는 분석용 n8n·AI 7축 검증/14축 정규화·독립 DERIVED DB·읽기 전용 내부 대시보드 전담**. 기존 팀 프론트 `ohora-nail-intelligence-v4`는 표현 계층으로 유지. 상세: [approved boundaries and first E2E](docs/APPROVED_REPO_BOUNDARIES_AND_FIRST_E2E_2026-10-22.md); 다음 실제 구현 단위: [Analyzer D1 Issue #1](https://github.com/hibi89/ohora-trend-analyzer/issues/1). **이번 단계는 설계 의사결정 GitHub 기록만 완료**, n8n 실행/DERIVED writer/운영 데이터/Google Sheets 쓰기/유료 AI 호출 0. P6 `1417a8e` CI 6/6 통과 기록과 Analyzer 자체 미검증 97개 테스트는 별개의 상태. P6 Sheets manual pilot JSON은 동기화 참고 자산으로 보존, Analyzer와 이중 활성화하지 않음. Media adapter는 관측행 exporter와 별도 검증 필요.


> **최종 갱신: 2026-10-20 KST, 오늘 태깅표 추가 품질 점검 완료.** GitHub `hibi89/ohora-trend-analyzer`의 `main` 기준. **n8n·유료 VLM/Meta 실호출·운영 RAW/DERIVED DB 변경 없음.**
>
> **현 상태: 태깅 사전 v1.1과 합성 검증 코드 등록 완료. 최신 Python 테스트 97개가 저장소에 정의되어 있으나 GitHub Actions 최신 CI 통과는 확인되지 않았다.** 과거 로컬 대응 코드의 85/85 PASS는 이전 버전 이력이며, 이번 추가된 97개가 실행·통과했다는 증거가 아니다.

## 프로젝트 목적

기존 [P6 원본 수집기](https://github.com/hibi89/ohora-trend-catcher)에서 수집한 Instagram 원본·관측 이력을 건드리지 않고, 별도 프로젝트에서 **이미지 기반 AI 7축 태깅 → 검증·14축 정규화 → 별도 DERIVED DB 기록 → 내부 대시보드 조회**를 구현. 제출 11/03, 발표 11/05. **오늘은 태깅 계약만** 보강함.

## 검증 수준별 현황

| 항목 | 상태 | 실제 증거와 한계 |
|---|---|---|
| 태깅 표준 사전 | **GitHub 등록·구조 확인** | `taxonomy/tag_schema_v1_1.json`, F01~F14 14축·159개 태그, 원본 v1.0 ID/명칭 유지 |
| P0 규칙 | **등록** | `taxonomy/tag_rules_v1_1.json`, 7축(F01/F03/F05/F06/F08/F09/F10)·84개 규칙 및 모호 용어 10개 |
| 미평가 상태 | **설계/검사 구현** | P1 7축 `not_evaluated`; observed/unknown/not_applicable와 구분 |
| 저장용 결과 계약 | **코드 등록** | `taxonomy/p0_tag_result.schema.json`, `scripts/validate_taxonomy.py` |
| 모델용 응답 계약 | **코드 등록** | `scripts/validate_model_output.py`; 모델 제안 7축 검증 |
| 신뢰된 정보와 결합·정규화 | **순수 Python 코드 등록** | `scripts/normalize_p0_result.py`; AI가 source/model ID 조작하지 못하게 분리, **DB write 없음** |
| 오프라인 전체 계약 smoke | **코드·합성 fixture 등록** | `scripts/smoke_p0_pipeline.py` + `fixtures/sample_trusted_execution_context.json`. 최신 커밋 실제 실행 **미확인** |
| 합성 단위 테스트 | **97개 test 함수 등록 / 최신 CI 미확인** | Python 결과 계약 35·JSON Schema 23·모델 응답 21·정규화 13·smoke 5 |
| 이전 버전 검증 | **과거 로컬 대응 코드 85/85 PASS 기록** | 최신 97개 테스트로 이월 불가 |
| n8n workflow/실 AI 이미지 분석 | **미구현** | 모델 정확도·n8n import·요금·실데이터 전송 미확인 |
| P6 read-only export 실연동 | **미구현/미검증** | 기존 RAW 데이터 운영 변경 금지 |
| DERIVED DB 저장/중복·복구 | **미구현** | 10/23 목표 |
| 내부 운영 대시보드 | **미구현** | 10/24 목표 |
| 실제 네일 이미지 30~50장 검수 | **미실시** | 검수 기준/빈 헤더 CSV만 등록 |
| 고객사 공식 내부 표준 승인 | **미확인** | 제안 태깅표를 오호라 공식 분류표라고 표현 금지 |

## 오늘 추가로 발견·수정한 문제

1. **이미지 근거 없는 판정** 차단: `observed`와 `not_applicable` 모두 `image` 또는 `both` 근거 필수. `not_applicable`은 실제 관찰한 `scope`와 부재 사유 필수.
2. Python 검증기/JSON Schema/모델 출력 검증기 간 이 규칙을 동기화하고 합성 테스트 보강.
3. **모델 7축 JSON → trusted execution context → 저장용 14축 결과 → 두 검증기** 흐름을 단일 오프라인 CLI로 구성.
4. 이전 v1.1의 159개 고정 tag_id/다국어 라벨은 변경하지 않음. 비네일·입력불가·영상 미지원은 job-level.

## 내일 작업 전 오프라인 검사 (GitHub repo root)

```bash
python -m pip install -r requirements-test.txt
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m scripts.validate_model_output --input fixtures/sample_p0_model_output.json
python -m scripts.smoke_p0_pipeline
python -m unittest discover -s tests -v
```

**통과 여부를 실제 GitHub Actions 또는 원본 저장소의 로컬 checkout에서 확인해야 한다.** 이번 세션의 GitHub commit status는 빈 목록이었고, 컨테이너에서 GitHub DNS 연결이 실패하여 최신 HEAD의 원격 실행 성공을 주장할 수 없다.

## 다음 개발 일정

- **10/21(수)**: 최신 CI 97개 재확인 → n8n 환경 및 P6 read-only export 확인 → 합성 1건 Manual Trigger.
- **10/22(목)**: 승인된 이미지 + 캡션 → 7축 VLM 결과 → 검증·정규화.
- **10/23(금)**: 독립 DERIVED 개발 DB 저장·재실행 중복 방지·실패 복구.
- **10/24(토)**: 내부 운영 관리 화면(조회 전용).
- **10/25(일)**: 합성/승인된 실샘플 통합·팀원 조회 계약.
- **11/03(화) 제출 / 11/05(목) 발표**.

## 안전 경계

- P6의 공식 294계정, 3 API 레인, limit=4, 2라운드/원본 재관측 정책을 이 저장소에서 변경하지 않는다.
- Analyzer는 P6 원본에 **읽기 전용**으로 접근하고 파생 데이터를 별도 DB에 기록한다.
- 사용자 승인 없이 Meta 실호출, 기존 RAW/운영 DB 변경, 운영 n8n 자동실행, 유료 모델 호출, 미승인 이미지 외부 전송 금지.
- GitHub 저장소는 공개(public)로 조회된 적 있으므로 토큰·운영 DB·실수집 데이터·권한 없는 이미지 커밋 금지.
- 화면 F5/필터 조회로 모델 재분석 호출이 발생하지 않아야 한다.

## 최신 문서

- [HANDOFF.md](HANDOFF.md): 다음 채팅방 필독
- [태깅 smoke 실행 안내](docs/TAGGING_SMOKE_RUNBOOK_2026-10-20.md): 97개 테스트 수·CI 확인법
- [태깅 규칙 정본](taxonomy/tag_schema_v1_1.json), [P0 상세 규칙](taxonomy/tag_rules_v1_1.json), [저장 계약](taxonomy/p0_tag_result.schema.json)
- [n8n 상세 설계](docs/N8N_WORKFLOW_SPEC.md), [모델 프롬프트 계약](docs/P0_VISION_PROMPT_CONTRACT_v1_1.md)
- [설계도](docs/IMPLEMENTATION_PLAN.md), [DB/입출력 계약](docs/ARCHITECTURE_AND_CONTRACTS.md)

**매 작업 완료 후 `HANDOFF.md`와 `STATUS.md`를 동기화하고 GitHub 재조회.** 프로젝트 번호는 등록부 확인 전 미배정.
