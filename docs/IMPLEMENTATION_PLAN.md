> **2026-10-20 최신 알림:** 태깅 정본 v1.1 등록 완료. [STATUS](../STATUS.md)와 [QA](TAXONOMY_QA_2026-10-20.md)를 우선한다. 아래 단계별 일정은 *미구현 작업의 계획*이다.

# OHORA Trend Analyzer — 2026-10-20~10-25 실행 설계도

작성: 2026-10-20 KST | 상태: **태깅 사전 D0 v1.1 등록 완료 / n8n·파생 DB·실AI 구현 전** | 기준일: 2026-10-20 화요일
최종 기한: KDT 2차 11/03(화) 제출, 11/05(목) 발표

## 0. 한 문장 목표

**안전하게 수집·보존된 기존 P6 게시물/미디어를 읽기만 해서, n8n으로 이미지+캡션을 AI 7축 표준 태그로 분석·검증하고 별도 DERIVED DB에 기록한 뒤, 새로고침 시 AI 재호출 없이 내부 운영 화면에 보여주는 최소 완성 흐름을 만든다.**

새 기능 추가보다 **실제 돌아가는 수직 관통(slice)**을 우선한다. P6의 수집 방식 변경, Meta 운영 실행, 실데이터 이전은 본 계획에서 승인되지 않는다.

## 1. 범위 고정

### 이번 주에 반드시 구현 (MVP/P0)
- 원본 조회 어댑터: 합성 fixture와 P6 형식 차이를 흡수하는 입력 계약. P6 원본은 read-only.
- 미디어 분석 대상 분리: 정지 이미지 우선, 캐러셀의 개별 자식 이미지 지원. 비디오는 URL 메타데이터 저장·`pending_unsupported_video`로 명확히 구분하고 이번 주 영상 프레임 추출 강제 금지.
- 표준 태깅 사전: 14개 축/159개 코드 보존, 이번 모델 호출은 F01·F03·F05·F06·F08·F09·F10 **7축만**.
- 이미지+캡션 AI 요청: schema-enforced JSON, 출처(evidence_source), 판단 불가/미분석/해당 없음 구분; 모델/프롬프트/태깅 사전 버전 기록.
- DERIVED DB: append-only 분석 실행 이력, 결과 참조, 처리/실패/중복 상태, 읽기 전용 조회.
- n8n: 수동 또는 테스트 트리거 → 후보 조회 → 모델 호출 → 검증 → 단일 DB writer/HTTP adapter 저장 → 오류 분기/재시도.
- 내부 대시보드: 마지막 작업 결과, 성공·대기·실패·검수 필요, 사진+태그+게시물 정보 상세 화면, 필터 최소판.
- 최소 회귀: 동일 미디어 2회 → 중복 처리 없음; F5→ 모델 호출 없음; invalid 태그→ 저장 차단; RAW 파일 해시/변경 시각 불변.

### 명시적으로 다음 단계로 보류 (P1/P2)
- 14축 전체 AI 운영 분석, 네일별 정밀 개체 분리, 비디오 프레임/릴스 자체 분석.
- 국가간 확산 모델, 장기 트렌드 점수·판매/검색 데이터 연결, 재학습, 자사 SKU 추천.
- 실 Meta 294계정 무인 운영, P6 history 백필, 공개 API 서비스/배포, n8n 고가용성, 권한형 관리자 UI.
- 오호라 공식 **내부** 분류표 연동(현재 미확보). 공개몰 필터는 대응표일 뿐 내부 표준 주장 금지.

## 2. 단계별 일정·납품·완료 정의 (Definition of Done)

| 단계 | 날짜 | 산출물 | 통과 조건 | 차단/의존 |
|---|---|---|---|---|
| D0: 설계/태깅 | 10/20(화) | README, AGENTS, HANDOFF/STATUS, v1.1 스키마·84 P0 태그 규칙·QA | **정적 구조 검사 12/12 통과, 파일 GitHub 등록 완료** | Python CI·실이미지 분류 품질·오호라 내부 검수 미확인 |
| D1: 데이터 입출력 계약 | 10/21(수) | synthetic/raw adapter, n8n input/output sample, DB schema 초안 | 합성 1건 읽고 media/post 연결·NULL 구분, RAW 변동 0 | P6 실데이터 export 위치/형식 미확인 |
| D2: n8n 기본 작동 | 10/21~22 | export→image+caption→LLM→validation→writer workflow | 가상 미디어 1건이 정해진 7축 JSON으로 통과 | n8n 호스팅·네트워크·이미지 접근 확인 필요 |
| D3: 안정화/저장 | 10/23(금) | DERIVED tables, idempotency, retry/errors, 재분석 규칙 | 재실행 중복 없음, 잘못된 태그 저장 금지, 실패 후 재개 | DB 종류 최종 선택·접근 승인 |
| D4: 내부 대시보드 | 10/24(토) | 최소 조회 화면(Streamlit 등) | 새로고침해도 모델/API 호출 0, 카드/이미지/태그/출처/실행 내역 조회 | 조회용 view 스키마 확정 필요 |
| D5: 통합/인수인계 | 10/25(일) | E2E 테스트, 운영 가이드, 버전·샘플 결과, 팀 핸드오프 | 합성+승인된 실샘플 E2E, RAW 변화 없음, 오류 시 복구 가이드 | 실샘플 테스트는 별도 승인/환경 필요 |

날짜는 **예정**이며 완료 표시가 아니다. 진행 현황은 루트 `STATUS.md`가 정본이다.

## 3. 상세 개발 순서 (작업을 끊는 최소 단위)

### D0 — 10/20
1. 과거 설계 태그 스냅샷을 `taxonomy/tag_schema_v1_0_draft.json`에 **그대로** 보관(완료/정합성 확인).
2. **완료:** `taxonomy/tag_schema_v1_1.json`, `taxonomy/tag_rules_v1_1.json`, `docs/TAXONOMY_DECISIONS.md` 및 QA 보고 등록. 실제 이미지 분류 정확도는 미검증.
3. `docs/ARCHITECTURE_AND_CONTRACTS.md`에서 P6 export 입력·DERIVED 출력·보안 계약 확정.
4. P6 운영 준비와 Analyzer 개발을 분리; 실제 Meta 수집은 P6 승인·점검 항목으로 분류.

### D1 — 10/21
1. Git 추적 가능한 **synthetic fixture** 1~3건 생성(실게시물/실 URL 금지).
2. export adapter가 정확히 한 post, 여러 media, engagement NULL, 국가·관측시각을 표현하는지 확인.
3. source identity·media id·permalink·caption·media_type·가능한 URL·이미지 사용 가능 여부 정의.
4. read-only 연결 방식 선택. 로컬 P6 SQLite 복제→사전 export JSON을 기본 경로로 권장. 학교 원격 n8n이 로컬 PC DB를 볼 수 있다고 가정 금지.

### D2 — 10/21~22
1. 수동 트리거→fixture 또는 조회 어댑터→각 image media 반복(`Split Out`/`Loop Over Items` 등 실제 n8n 버전에 맞춰).
2. 사진+캡션을 VLM에 전달(이미지 URL 만료·접근 실패 시 retryable error로 기록).
3. JSON parse, code whitelist, 각 facet의 `status`와 `tag_ids` 일치 검증. invalid는 DB 저장 대신 격리.
4. `F01,F03,F05,F06,F08,F09,F10`만 `evaluated`. 나머지 F02,F04,F07,F11,F12,F13,F14는 `not_evaluated`. unknown/NA는 판정 규칙 따름.
5. 성공 출력은 source post/media, taxonomy/model/prompt/input fingerprint 포함.

### D3 — 10/23
1. 별도 DB 스키마 migration부터 준비, 개발 DB만 생성.
2. 작업 claim(중복 작업 방지)→AI 실행→검증→원자적 기록→성공 상태 전이. 실패 시 오류·재시도 메타정보 기록.
3. 3회 재실행·실패 후 중단·부분 캐러셀·빈 태그·언어 동의어·존재하지 않는 코드 테스트.
4. raw write/writeback 0건 검증.

### D4 — 10/24
1. 내부 대시보드는 **DERIVED read view만** 사용. 버튼 클릭/새로고침에도 분석 실행·P6 수집 호출 불가.
2. 요약(대기/성공/실패/검수필요) → 미디어별 상세 → 국가/기간/태그 필터 → 작업/오류 보기.
3. 영상/릴스는 썸네일·원본 링크·`not_analyzed_video` 상태만 보여도 인정. `조회 불가`와 `분석 실패` 구분.

### D5 — 10/25
1. 최소 3~5개 합성 시나리오: 정상 단일, 캐러셀 2장, NULL count, 모델 invalid, 네트워크 실패, 중복 재시도.
2. 실제 데이터는 **권한과 비식별/외부 모델 전송 범위를 확인한 소량 샘플**로만 검증.
3. README, STATUS, HANDOFF, 실행 명령, 환경변수 예시, n8n import 파일 경로, DB migration/rollback 단계 최신화.
4. 팀 프론트엔드 담당에게 **읽기 전용 API 계약**과 JSON 샘플 전달.

## 4. 우선순위 규칙 / 일정 지연시 포기 순서

1. **절대 포기 불가**: 원본 쓰기 금지, 코드/비밀정보 보호, 실행 이력, 정해진 태그만 저장, 중복 AI 호출 방지.
2. **필수**: 1건 end-to-end, 태그 확인 화면, 오류 상태 확인, 분리 저장.
3. 시간 부족하면 순서대로 제외: 자동 매일 스케줄 → 태그 수정 UI → 정교한 통계/차트 → 다중 사용자 로그인 → 영상 분석 → 14축 전체 분석.
4. 문제 해결은 동일 접근 2회 실패 후 원인 확인·다른 경로 채택.

## 5. 팀 업무 계약

| 담당 | 받는 것 | 주는 것 | 충돌 금지 |
|---|---|---|---|
| P6 수집기 담당 | 공식 294계정 목록(외부 보관), Meta API/권한 | 승인·검증된 read-only export | RAW DB 변경 없음 |
| Analyzer/n8n 담당 | export 계약, schema draft | DERIVED run/report, 조회 계약 | 분석 결과를 RAW 컬럼에 쓰지 않음 |
| 기획/분석 담당 | 국가·기간·기초 참여값, 태그 | 트렌드 지표/사용 시나리오 | 좋아요 0과 NULL 구분, 시점 명기 |
| 프론트엔드 담당 | 승인된 read-only view/API | 이미지 중심 카드/상세 UI | F5 때 AI 재실행 금지 |

## 6. 사용자 확인이 필요한 사항 (실행 단계 전 확인)

- n8n 환경은 학교 호스팅인지 개인 로컬인지, DB·파일 경로에 어떻게 접근 가능한지.
- DERIVED 개발 DB: SQLite 로컬부터 시작할지, Supabase 등 공유 DB를 쓸지. 운영 접근 승인 여부 별도.
- 실제 Meta 수집 시작 전 P6 G0~G6/실응답·API quota·백업·권한 확인 및 사용자 승인.
- 사용 AI 모델·API 키·이미지 전송 정책·예산·API 요청 제한.
- 첫 배포 시 내부 개발자 화면을 누가 접속할지, 공개 접근 금지 여부.

## 7. 성공/완료 표현

- **설계 완료**: 문서·사전 Git에 저장.
- **로컬 구현**: 실제 코드·fixture/DB migration 존재.
- **오프라인 테스트 완료**: 테스트 명령과 PASS 증거.
- **n8n 연결 검증**: workflow import 및 실행 결과 기록.
- **승인된 실샘플 검증**: 접근 승인 후 시험 결과.
- **운영 검증**: 승인된 운영 실행과 로그·보존/복구 증거.

이 단계들을 섞어서 "완성"으로 보고하지 않는다.

## 8. 관련 문서

- [안전 규칙](../AGENTS.md)
- [아키텍처/계약](ARCHITECTURE_AND_CONTRACTS.md)
- [태깅 결정/판정 규칙](TAXONOMY_DECISIONS.md)
- [n8n 플로 명세](N8N_WORKFLOW_SPEC.md)
- [내부 대시보드 설계](INTERNAL_DASHBOARD_SPEC.md)
- [인수인계](../HANDOFF.md)
