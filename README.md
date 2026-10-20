> **2026-10-20 태깅 단계 최종 기준:** 14축/159태그 v1.1 유지, 7축/84태그 P0, [오프라인 smoke](docs/TAGGING_SMOKE_RUNBOOK_2026-10-20.md) 명령 및 **97개 합성 테스트 정의**. **원격 CI 통과·실 AI/n8n/DB 연동 미확인**. 다음 작업은 [HANDOFF.md](HANDOFF.md) 우선. n8n은 10/21 시작 예정.

# OHORA Trend Analyzer

> **2026-10-20 KST — 설계 단계 / 실행 기능 미구현**
>
> 이 저장소는 [OHORA Trend Catcher (P6 RAW 수집기)](https://github.com/hibi89/ohora-trend-catcher)와 **별도**로 관리하는 `AI 태깅 + n8n 자동화 + 파생 DB + 내부 관리 대시보드` 프로젝트다. **이 저장소를 만든 것만으로 Meta 실호출·운영 DB 변경·수집 스케줄러 활성화가 승인된 것은 아니다.**

## 새 채팅방/작업자 시작 순서 (필수)

1. [AGENTS.md](AGENTS.md) — 금지 작업·안전 규칙
2. [HANDOFF.md](HANDOFF.md) — 최신 결정, 다음 작업 한 개, 검증 현황
3. [STATUS.md](STATUS.md) — 단계별 완료·미완료·차단 사항
4. [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) — 10/20~10/25 작업 설계도, 단계별 DoD
5. [docs/ARCHITECTURE_AND_CONTRACTS.md](docs/ARCHITECTURE_AND_CONTRACTS.md) — 수집기 연동, 데이터 경계, 분석 결과 계약
6. [docs/TAXONOMY_DECISIONS.md](docs/TAXONOMY_DECISIONS.md) — 14축/159태그, P0 7축, 애매한 용어 판정 규칙
7. [taxonomy/tag_schema_v1_1.json](taxonomy/tag_schema_v1_1.json) — **현 프로젝트 태깅 기준 v1.1** (14축·159태그; 실제 AI 성능 미검증)
8. [taxonomy/tag_rules_v1_1.json](taxonomy/tag_rules_v1_1.json) — P0 7축·84태그 판정 기준 및 혼동 규칙 10개
9. [docs/TAXONOMY_RULEBOOK_v1_1.md](docs/TAXONOMY_RULEBOOK_v1_1.md) — 태깅 운영 기준서
10. [scripts/validate_taxonomy.py](scripts/validate_taxonomy.py) — 사전·태깅 결과 오프라인 JSON 검사기
11. [taxonomy/p0_tag_result.schema.json](taxonomy/p0_tag_result.schema.json) — 검증·DB 저장 전 **정규화 결과 JSON Schema**
12. [docs/TAGGING_INTEGRATION_HANDOFF_v1_1.md](docs/TAGGING_INTEGRATION_HANDOFF_v1_1.md) — n8n·프론트엔드 인계 계약
13. [docs/P0_VISION_PROMPT_CONTRACT_v1_1.md](docs/P0_VISION_PROMPT_CONTRACT_v1_1.md) — AI 모델에 줄 7축 입력·출력 프롬프트(설계)
14. [scripts/validate_model_output.py](scripts/validate_model_output.py) — AI 7축 모델 응답 사전 검사
15. [scripts/normalize_p0_result.py](scripts/normalize_p0_result.py) — 신뢰된 소스 정보와 7축 결과를 14축 DERIVED 형식으로 변환(오프라인)
16. [docs/TAGGING_IMAGE_QA_PROTOCOL_v1_1.md](docs/TAGGING_IMAGE_QA_PROTOCOL_v1_1.md) — 승인된 사진 30~50장 수동 평가 절차

## 지금 하는 일

- 10/20(화): 태깅 기준 v1.1·아키텍처·안전한 연동 계약 문서화. AI 정확도 미검증
- 10/21(수)~10/23(금): **합성/복제 데이터부터** n8n → AI 7축 태깅 → 분석 전용 DB
- 10/24(토): 분석용 내부 대시보드 최소판
- 10/25(일): E2E 회귀 테스트·팀 인터페이스 인계
- 11/03(화): KDT 2차 프로젝트 최종 제출 / 11/05(목): 발표

**단일 성공 기준:** 저장된 네일 미디어 1건을 읽고 → 모델에 전달 → 허용 태그/상태 JSON 검증 → 파생 DB에 저장 → 페이지 새로고침으로 재분석 없이 조회.

## 프로젝트 경계

```text
[기존 P6 RAW collector]  →  [검증된 읽기 전용 export/adapter]
                                 ↓
                 [n8n / AI vision / taxonomy validator]
                                 ↓
                       [별도 DERIVED DB]
                                 ↓
                      [내부 운영 대시보드]
```

**중요:** P6 수집기는 294계정, A/B/C 3 API 레인, 요청당 limit=4, 일일 2라운드/계정당 최대 12개 게시물 최신 관측 등 사용자 동결 요건을 따른다. 이 저장소에서 P6 수집 방식을 재구현·수정하지 않는다.

## 보안

토큰, `.env`, Meta 응답 전문, 사용자 실수집 CSV/SQLite, 개인 정보, 이미지 파일 원본을 커밋하지 않는다. 운영 접근은 별도 명시 승인 뒤 제한적으로 검증한다.

**상태 해석:** 설계 문서 게시 ≠ n8n 구현 ≠ 운영 연동 성공 ≠ 실 Meta API 검증.

## v1.1 사전·출력 규격 확인 (로컬/CI)

```bash
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m scripts.validate_model_output --input fixtures/sample_p0_model_output.json
python -m pip install -r requirements-test.txt
python -m scripts.smoke_p0_pipeline
python -m unittest discover -s tests -v
```

이 명령은 **외부 API·Meta·DB 연결 없이** 159개 ID 보존과 분류 결과 계약을 검사한다. 사용한 테스트 fixture는 가상 데이터이며 실물 이미지 판정 품질을 증명하지 않는다. [GitHub Actions workflow](.github/workflows/taxonomy-check.yml)는 등록했으나 CI 실행 완료 여부는 별도로 확인해야 한다.
