# OHORA Trend Catcher × Trend Analyzer — 저장소 책임 분리 승인 및 첫 수직 E2E 작업

- 결정일: 2026-10-22 KST
- 승인: 사용자가 P6 단일 저장소 통합안 대비 **기존 Analyzer 분리 유지** 권고를 승인함
- 상태: **아키텍처 선택 확정 / 첫 합성 E2E 구현 대기 / 운영 연동 미승인**
- 담당: GPT-6 High 설계·검수; 이후 해당 저장소 개발 작업자에게 구현 인계
- 이 문서는 수집 정책의 동결 원문을 수정하지 않는다.

## 결정과 근거

기존 P6 수집 저장소 하나에 n8n·AI·파생 DB·대시보드까지 쌓는 안은 초기 연결 수가 적지만 수집 코드와 분석 로직의 결합, 원본 변형 위험, 동시 작업 충돌, 회귀 범위를 키운다. **기존 `hibi89/ohora-trend-analyzer`를 분석 전담으로 유지**하면 이미 등록된 태깅 사전·검증기·합성 테스트를 재사용하고 RAW/DERIVED 소유권을 분명히 할 수 있다.

| 선택안 | 구현 속도 | 원본 안정성/협업 | 유지보수 | 결론 |
| --- | --- | --- | --- | --- |
| A. P6 단일 저장소에 전체 기능 추가 | 단기 연결은 다소 단순 | 수집기/분석기 변경 결합·충돌 증가 | 복잡화 | 선택하지 않음 |
| B. P6 수집 / Analyzer 분석 / 기존 프론트엔드 분리 | 읽기 전용 인터페이스 설계가 필요 | 소유권 명료, 원본 보호 | 기존 14축 태깅 재사용 | **사용자 승인, 채택** |

## 책임과 데이터 흐름

```text
hibi89/ohora-trend-catcher (P6)
  Meta API A/B/C → 승인된 RAW/Capture/SQLite → 영수증 검증 → 읽기 전용 export
  (수집 실행·쿼터·커서·P50/P294·수집용 n8n tick은 P6 소유)
                                  │
                                  ▼
hibi89/ohora-trend-analyzer
  P6 read-only media adapter / synthetic fixture
      → n8n 분석 워크플로 (수동 시작, AI 실행은 별도 승인)
      → P0 7축 모델출력 검사 → 신뢰 필드 결합·14축 정규화
      → 분리된 DERIVED 개발 DB (분석 실행/상태/이력)
      → 조회 전용 API / 내부 운영 대시보드
      → 검증된 관측·분석 결과의 Google Sheets 동기화 (후속)
                                  │
                                  ▼
hibi89/ohora-nail-intelligence-v4 (기존 React/Vite 자산)
  고객사 표현 계층: 통합 읽기 전용 API에 연결 (현재는 정적 스냅샷 기반)
```

- 같은 n8n 서버를 사용해도 **수집 트리거와 분석 트리거는 별개의 워크플로**로 운영한다.
- P6 내 기존 `n8n_p6_sheets_manual_pilot.json`(Windows/Linux)과 read-only exporter는 버리지 않는다. **현재 비활성 수동 프로토타입**을 참고자료로 유지하고, 최종 분석/Sheets 활용 워크플로의 소유자는 Analyzer로 정한다. 두 경로를 동시에 가동해 이중 쓰기하지 않는다.
- Google Sheets는 원본도 수집 커서 DB도 아니다. 파일 자동 로테이션은 P6 [Draft PR #17](https://github.com/hibi89/ohora-trend-catcher/pull/17)의 **미병합 후속 제안**으로만 보존한다. 사용자 재승인 및 안전 테스트 없이 구현/활성화하지 않는다.
- 팀 프론트엔드는 수집·AI 실행 없이 DERIVED read-only API를 호출한다. **F5로 Meta API·VLM·n8n 호출 0회**여야 한다.

## 현행 코드와 정확한 미구현 경계 (2026-10-22 GitHub 재조회)

- P6 feature SHA `1417a8ef902201738b8f74aaddcb3ffe6d6b628f`: 오프라인 CI 6종 성공. **P50 실제 운영 수집 재개 및 백업 canonical 결정은 별도로 NOT READY**.
- Analyzer `main` 출발 SHA `8679806bb8644772597d584160e9588a40fec82d`: v1.1 **14축/159태그**, P0 **7축/84태그**, `validate_model_output.py`, `normalize_p0_result.py`, `validate_taxonomy.py`, JSON Schema·합성 테스트가 존재. **실 n8n workflow import, DERIVED writer, 내부 대시보드와 실제 이미지 모델 품질은 미검증/미구현**. 97개 테스트 함수가 있다고 성공한 97개는 아니다.
- `ohora-nail-intelligence-v4`는 현시점 샘플 스냅샷을 제공하는 별도 React/Vite 대시보드 코드이며 Analyzer live API에 연결되었다는 검증 없음.
- **현재 P6 `three_api_sheets_export.py`는 관측행 내보내기 계약이다. 이미지/캐러셀 자식별 분석 입력 및 실제 이미지 바이트를 모두 제공한다고 가정하지 않는다.** Analyzer 입력용 미디어 어댑터는 별도 스키마 매핑/접근성 검증이 필요하다.

## 바로 다음 개발 1단위 — SYNTHETIC 1개 미디어 → DERIVED DB → read-only 조회

**구현 저장소: Analyzer만. P6와 프론트엔드 코드를 이 단위에서 수정하지 않는다.**

1. 기존 합성 fixture, v1.1 정본·검증 코드를 변경 없이 우선 사용한다. 필요 시 최소한의 개발 전용 fixture를 추가한다.
2. `source_kind=synthetic_fixture`인 1개 이미지 미디어를 신뢰된 실행 컨텍스트로 읽는다. 실제 SNS ID·비밀·이미지 URL은 사용하지 않는다.
3. 합성된/Mock P0 7축 모델 응답을 `validate_model_output`로 검사하고 `normalize_p0_result`로 14축으로 정규화한 뒤 `validate_taxonomy` 및 저장용 JSON Schema를 모두 통과시킨다.
4. **분석 전용 개발 SQLite**를 원자 트랜잭션으로 작성한다. 원본 RAW DB를 열거나 변경하지 않는다. 최소 `analysis_jobs`, `analysis_runs`, `facet_results` 및 오류/상태 증거를 포함하고 원문 응답과 정규화 결과를 재조회할 수 있게 한다. 소스/모델/사전/프롬프트와 입력 hash/version 키를 보존한다.
5. 동일 입력 2회 실행 시 중복 성공행 및 불필요한 모델 재호출이 없도록 영속 멱등키를 검증한다. 잘못된 `tag_id`/필수 근거 누락은 DB 성공 저장 0건, 실패는 원인과 작업 상태로 보존한다.
6. 독립 read-only 조회 명령이나 최소 API로 방금 저장한 1건을 조회한다. **조회 3회에서 수집/분석 실행 0회**. 사용자용 화면과 실제 n8n 서버 연결은 다음 단위.
7. 실제 테스트 실행 로그·PASS/FAIL 건수와 git commit SHA를 남긴다. 기존 97개 전체 회귀는 코드 영향 범위에 맞춰 검증하되, CI 실패 시 새 오류인지 기존 문제인지 구별한다.

**완료 기준:** (a) 합성 1건이 영속 DERIVED DB에 저장된 뒤 다른 프로세스에서 조회 가능, (b) 재실행 중복 0, (c) invalid 태그 성공 저장 0, (d) P6 원본/수집 코드 변경 0, (e) 테스트 명령·결과·GitHub SHA 확인.

**별도 단계:** 실제 P6 media read-only adapter → 학원 n8n 수동 import → 사용자 승인된 이미지/VLM 소량 호출 → 팀 프론트 API 연결 → Google Sheets 자동 동기화/회전. 운영 데이터·외부 전송·비용·권한 설정은 별도 승인.

## 운영·보안·복구

- GitHub에는 코드/합성 fixture/비민감 문서만. 운영 RAW, 원본 이미지, 실제 토큰/계정 ID·실사용 URL을 포함하지 않는다.
- 원본을 덮어쓰지 않으며 GitHub 기준 시작 SHA로 롤백 가능. `AGENTS.md`·`HANDOFF.md`·`STATUS.md` 동기화 의무 유지.
- 두 번 실패해도 진전 없으면 중단하고 대안 제시. 실 데이터 수집 성공이나 고객사 분석 완성이라고 주장하지 않는다.
