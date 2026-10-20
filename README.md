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
7. [taxonomy/tag_schema_v1_0_draft.json](taxonomy/tag_schema_v1_0_draft.json) — **원본 제안 태그 사전 스냅샷**; 확정 v1.1 아님

## 지금 하는 일

- 10/20(화): 태깅 기준·아키텍처·안전한 연동 계약 확정
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
