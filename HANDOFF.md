# HANDOFF — OHORA Trend Analyzer

> **최신 인수인계: 2026-10-20 KST / 태깅표 v1.1 설계 완료. 이 문서를 우선한다.**
>
> GitHub `hibi89/ohora-trend-analyzer`, `main` 기준. **태깅 사전 14축·159태그 / P0 7축·84태그 판정 규칙 / 혼동 사례 10개 / 4상태 계약 / 합성 구조 검증기**까지 GitHub 등록 완료. **n8n 실제 workflow, 외부 AI 태깅 실행, DERIVED DB, 내부 관리 대시보드는 미구현.** 10/21부터 n8n 시작, 오늘은 더 이상 n8n 변경하지 않는다. **P6 RAW 수집기/실 Meta 호출/운영 DB에는 변경 없음.**

## 0. 새 채팅방 복원 순서 (반드시)

1. [README](README.md), [AGENTS](AGENTS.md), [STATUS](STATUS.md), 이 `HANDOFF.md`를 최신 `main`에서 읽고 HEAD SHA 기록.
2. [태깅 사전 v1.1](taxonomy/tag_schema_v1_1.json), [P0 84개 판정 규칙](taxonomy/tag_rules_v1_1.json), [기준서](docs/TAXONOMY_RULEBOOK_v1_1.md), [QA 보고](docs/TAXONOMY_QA_2026-10-20.md) 확인.
3. [실행 설계도](docs/IMPLEMENTATION_PLAN.md), [RAW↔DERIVED 데이터 계약](docs/ARCHITECTURE_AND_CONTRACTS.md), [n8n 노드 명세](docs/N8N_WORKFLOW_SPEC.md), [내부 UI 설계](docs/INTERNAL_DASHBOARD_SPEC.md) 확인.
4. 새 버전 명칭 혼동 금지: `taxonomy/tag_schema_v1_0_draft.json`은 **보존한 원본**, `taxonomy/tag_schema_v1_1.json`은 **프로젝트 개발 기준 정본**. 오호라 회사의 공식 비공개 내부 분류표가 아니다.

## 1. 프로젝트 목적/시스템 경계

사용자가 P6 수집기에 시간을 쓴 이유는 인스타그램 게시물/미디어의 **원본·반응 지표·관측 시점별 데이터·변경 이력을 안정적으로 보존**해 분석 알고리즘이나 태깅 기준을 바꾸더라도 재수집 없이 재해석할 수 있도록 하기 위함이다.

```text
P6 Collector (다른 저장소; 원본 API 응답/관측/변경 이력)
                │ read-only export/adapter [실제 방식 미확정]
                ▼
n8n (이 저장소; 내일 시작)
  → 이미지+캡션 AI 태깅 (P0 7축)
  → taxonomy v1.1 whitelist 및 결과 계약 검증
  → 별도 DERIVED DB에 분석 이력 저장
  → 읽기 전용 내부 대시보드 / 팀 프론트엔드
```

**수집 스케줄링·API 호출을 n8n으로 재구현하지 않는다.** P6 사용자 동결 요건: 공식 294계정, A/B/C 3 API 레인, `limit=4`, 2라운드/최신 3페이지×4=계정당 최대 12개, 원본 변경 관측, 이후 누락 복구·영속 백필. [P6 동결 설계](https://github.com/hibi89/ohora-trend-catcher/blob/main/docs/P6_FINAL_COLLECTION_DESIGN_2026-10-20.md).

## 2. 오늘 태깅 작업 완료 사항

- [x] 기존 F01~F14 14개 축 및 159개 ID·slug·한영일 표시명·동의어 보존. 동일 축 내 중복/alias 충돌 없음.
- [x] **P0 7축 F01(18) F03(8) F05(12) F06(10) F08(12) F09(14) F10(10) = 84개** 세부 판정 기준 JSON.
- [x] 나머지 P1 F02 F04 F07 F11 F12 F13 F14 = 75태그 사전 유지. 초기 AI는 분석하지 않으며 `not_evaluated` 표시.
- [x] Astra 지적 반영: 시어/시럽/젤리, 옴브레/그라데이션, 크롬/미러, 캣아이/쉬머, 2D/3D 리본 등 혼동 규칙 10개.
- [x] `observed` / `unknown` / `not_applicable` / `not_evaluated` 출력 상태 명시. 입력 불가·영상 분석 미지원은 job-level. v1.0의 `not_observed` 자동 치환 금지.
- [x] `scripts/validate_taxonomy.py` 업로드: 원본 태그 보존, tag whitelist, 결과 P0/P1 구분, 필수 근거·상태·해시·timezone 검증.
- [x] `tests/test_tagging_contract.py` (합성 16개) + `fixtures/sample_valid_tag_result.json` + `.github/workflows/taxonomy-check.yml` 등록.
- [x] 정적 JSON 12개 검사 PASS 및 QA 문서에 근거 기록.

**중요 미검증:** 새 Python 16개 테스트 및 GitHub Actions CI의 실제 PASS 로그는 현재 확보 못함. `git clone` 네트워크 DNS 실패. 이미지 실분류·모델 예측 정확도·오호라 실무자 승인 또한 미검증. '실제 태깅 완성'이라고 말하지 않는다.

## 3. 10/21(수) 바로 시작할 최소 단위

**첫 단계: 기존 검증기 실행 확인.**
```bash
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m unittest discover -s tests -v
```

실패하면 원인 수정→최소 커밋→HANDOFF/STATUS 갱신. 2회 같은 방식으로 재시도하지 않는다.

**그 다음: n8n 합성 1건.**
1. 사용자에게 실제 n8n 환경(학원 원격/로컬, 버전/접속경로)과 파생 DB 선택, 모델 API/전송 권한 확인.
2. P6 RAW 운영 DB를 열기 전에 승인된 **read-only export** 경로를 확인. 미확인 상태라면 `fixtures/sample_valid_tag_result.json`과 새 synthetic input fixture만 사용.
3. Manual Trigger → synthetic image input → VLM P0 7축 → `tag_schema_v1_1.json` + `tag_rules_v1_1.json` 규칙 적용 → JSON 결과 validator → DERIVED test DB.
4. 성공한 1건 다음에만 배치/캐러셀·중복 방지·오류 재시도 확장. 프론트엔드 F5는 읽기 전용.

**사용자 승인 필요한 외부 조치:** 실제 Meta 호출·토큰 사용·P6 운영 DB 변경·외부 모델 이미지 전송·과금·실계정 294개 무인 스케줄. 이 저장소 작업 개시만으로 승인 아님.

## 4. 일정

| 날짜 | 단계 / 납품 상태 |
|---|---|
| 10/20(화) | D0 태깅표 v1.1 데이터 사전/설계/정적 검증 **완료** |
| 10/21(수) | D1 fixture/P6 read-only adapter + D2 n8n 시작 **미착수** |
| 10/22(목) | D2 7축 VLM 태깅 JSON + strict validation **미착수** |
| 10/23(금) | D3 DERIVED DB 원자 저장/중복·오류 복구 **미착수** |
| 10/24(토) | D4 내부 관리 대시보드 최소판 **미착수** |
| 10/25(일) | D5 통합 테스트·프론트 계약 공유 **미착수** |
| 11/03(화) | 제출 / 11/05(목) 발표 **예정** |

## 5. 보안·분류 품질 규칙

- **RAW와 DERIVED 물리/권한 분리:** Analyzer는 원본을 읽기만, 분석 결과·검수 이력은 별도 DB. 과거 AI 원출력 덮어쓰기 금지.
- **태깅 미디어 단위:** 하나의 게시물에 여러 이미지/디자인. `post_id` ≠ `media_id` ≠ `design_cluster_id`. 릴스 프레임 분석은 이번 주 미지원(링크/썸네일 메타만).
- **분류 근거:** 이미지를 주근거, 캡션은 별도 속성. 실제 재료·시술 공정·제품 사용·상품 SKU·국가를 사진에서 임의 추측하지 않는다.
- **시점/관측:** `posted_at`과 `observed_at` 구분. 좋아요/댓글 0은 NULL이 아니다. 출처·모델·프롬프트·taxonomy·분석 입력 해시·실행 시각·검수 상태 기록.
- **다국어:** `tag_id`가 정본, ko/en/ja 표시명은 사전. 일본어 빈 값은 null 유지(검증 없이 번역 채우지 않음).
- **DB 갱신:** F5나 UI 카드 클릭은 API/AI 호출 금지, 저장된 DERIVED 조회만.
- **외부 비밀:** .env/토큰/실 DB·CSV/고객사 파일 원본 Git 업로드 금지. **현재 GitHub repo가 public으로 조회됨**. 공개범위 변경은 사용자가 결정할 사항.

## 6. 이번 작업 결과 증거

- 등록 파일: `taxonomy/tag_schema_v1_1.json`, `taxonomy/tag_rules_v1_1.json`, `docs/TAXONOMY_RULEBOOK_v1_1.md`, `docs/TAXONOMY_QA_2026-10-20.md`, `scripts/validate_taxonomy.py`, `tests/test_tagging_contract.py`, `fixtures/sample_valid_tag_result.json`, `.github/workflows/taxonomy-check.yml`.
- GitHub에서 사전·규칙·fixture·검증 코드를 fetch-back 하여 정적 검사 12/12 PASS. 16개 Python 합성 테스트는 **코드만 등록되었으며 실행 미확인**.
- rollback은 v1.1 신규 파일·그 관련 코드와 테스트를 revert하는 것으로 가능. 기존 v1.0-draft 및 P6 RAW는 변경 없음.

## 7. 반드시 남길 인수인계 형식

```text
UTC/KST date, repository, branch, HEAD commit:
변경 파일/기능:
실행한 테스트 (명령, 실제 PASS 증거):
미실행·실운영 미검증:
RAW/토큰/Meta 작업 여부:
롤백/다음 최소 작업:
HANDOFF.md + STATUS.md 최신화 및 GitHub fetch-back:
```

프로젝트 번호: **미배정**. 번호 등록부/BOOK에서 실 매핑 확인 전 임의 번호 할당 금지.
