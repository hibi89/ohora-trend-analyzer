# 태깅 기준 결정 기록 및 P0 판정 규칙 — v1.1 프로젝트 기준

작성 2026-10-20 KST | 상태: **v1.1 프로젝트 기준 파일 등록·정적 구조 검증 / AI 정확도·오호라 내부 검수 미완료**.

> **최신 기준:** [tag_schema_v1_1.json](../taxonomy/tag_schema_v1_1.json) + [tag_rules_v1_1.json](../taxonomy/tag_rules_v1_1.json) + [TAXONOMY_RULEBOOK_v1_1.md](TAXONOMY_RULEBOOK_v1_1.md). 기존 v1.0-draft는 변경하지 않고 보존한다. 실제 AI 성능이나 n8n 연결이 검증된 것은 아니다.
원본 14축·159태그는 [JSON 스냅샷](../taxonomy/tag_schema_v1_0_draft.json) 및 [v1.0 설명서](TAXONOMY_ORIGINAL_v1_0_DRAFT.md)를 기준으로 한다. 오호라 공식 **내부** 분류표가 아니라 팀 제안 표준이다.

## 1. 목적

- 한국/미국/일본 네일 게시물의 스타일을 통일된 불변 `tag_id`로 비교한다.
- 라벨이 한국어/영어/일본어로 달라도 동일한 디자인 요소를 같은 코드로 집계한다.
- 게시물 상세 화면에서 **사진+태그+판정 근거+게시물 수치**를 조회할 수 있도록 한다.
- 분류 체계가 변경되어도 RAW 재수집 없이 기존 미디어의 새 모델 재분석이 가능하도록 한다.
- 훗날 오호라 상품기획과 연결할 수 있지만, 외부 SNS에서 실제 자사 상품/사용 재료·SKU를 추정하지 않는다.

## 2. 14축과 이번 주 범위

| 코드 | 분류 | 현재 AI 처리 |
|---|---|---|
| F01 | 색상 | **P0 분석** |
| F02 | 색상 특성/톤 | P1, not_evaluated |
| F03 | 발색·투명도 | **P0 분석** |
| F04 | 표면 마감 | P1, not_evaluated |
| F05 | 효과·재질감 | **P0 분석** |
| F06 | 기본 디자인 기법 | **P0 분석** |
| F07 | 프렌치 세부형 | P1, not_evaluated |
| F08 | 패턴·문양 | **P0 분석** |
| F09 | 모티프·오브젝트 | **P0 분석** |
| F10 | 입체 장식 | **P0 분석** |
| F11 | 디자인 배치 | P1, not_evaluated |
| F12 | 네일 형태 | P1, not_evaluated |
| F13 | 스타일·무드 | P1, not_evaluated |
| F14 | 시즌·사용 맥락 | P1, not_evaluated |

- `S01` 주색/보조색/포인트색, `S04` 대표/부가 요소: P0에서는 **가능하면 기본 결과**. 못하면 이번 주 미평가를 명시.
- `S02` 베이스·기법·장식 관계, `S03` 네일별 구성: P1 상세 분석 확장.
- 실제 태깅은 **이미지 단위**; 게시물 1건에 캐러셀 여러 장/서로 다른 네일 디자인 가능.
- 디자인 클러스터 ID는 아직 부여하지 않는다. `post_id`·`media_id`와 동일시 금지.

## 3. 모호 용어 판정 규칙 — Astra 검토 반영

| 구별 | 판정 기준 | 처리 |
|---|---|---|
| F03 sheer(시어) | 바탕색이 약하게 비치는 높은 투명감이라는 **시각적 성질** | 확인 가능하면 태깅; 시럽과 공존 가능 |
| F03 syrup(시럽) | 시럽처럼 맑고 맺히는 듯한 컬러/여러 겹 쌓인 듯한 발색 **시각 표현** | 단순 반투명만으로 무조건 syrup 아님 |
| F03 jelly(젤리) | 맑고 말랑한 젤리 같은 볼륨감/투명한 색층의 외관 | syrup·sheer와 공존 가능; 확실치 않으면 unknown |
| F06 gradient(그라데이션) | 한 색의 밝기/채도 또는 색상들이 점진적으로 전환하는 **상위 표현** | 옴브레가 확실할 때도 동시 선택 가능 |
| F06 ombre(옴브레) | 구별되는 둘 이상의 색/톤이 부드럽게 섞여 연속 전환 | 뚜렷한 전환 근거 없으면 gradient만 또는 unknown |
| F05 chrome(크롬) | 금속성·고반사 특수 효과로 보이는 외관 | 실제 크롬 파우더 시술이라고 단정하지 않는다 |
| F04 mirror(미러) | 거울 같은 표면 마감/반사 (이번 주 **미평가 축**) | chrome과 경쟁 태그가 아니며 나중에 공존 가능 |
| F05 cat_eye(캣아이) | 자석 파티클로 보이는 빛띠·방향성·집중 반사 효과 | 약한 단순 쉬머면 cat_eye 강제 금지; 사용한 자석 실제 시술은 추정 |
| F08 반복 패턴 vs F09 모티프 | 추상 반복 무늬는 F08, 리본/꽃/별 등 구체 형상은 F09 | 같은 이미지에 동시 태깅 가능 |
| F09 ribbon vs F10 three_d_ribbon | 리본 모양 자체 F09, 솟아오른 입체 장식이 보일 때 F10 추가 | 평면 리본 이미지에 F10 부여 금지 |
| F02 tone, F13 mood, F14 season | 조명·스타일 감성·게시 시점에 의존, 추측 다수 | P0 실행하지 않음. P1에서도 뚜렷한 근거 없으면 unknown |

**위 정의는 운영 전 검수할 1차 규칙**이다. 표준 의미가 서로 완전히 배타적이지 않으므로 억지 단일 분류 불가. 예를 들어 `F06.gradient`와 `F06.ombre`의 병존은 설계상 허용하되 시각적 근거를 기록한다.

## 4. 불확실성 및 누락 처리

- `observed`: 실제 검사했고 하나 이상의 사전 태그를 근거와 연결.
- `unknown`: 검사했으나 사진·캡션으로 판단 불가, 빈 tag_ids.
- `not_applicable`: 검사했으나 논리적으로 해당 없음(세부 프렌치 축 등), 빈 tag_ids.
- `not_evaluated`: 아예 검사하지 않은 축, 빈 tag_ids.
- **이미지 자체가 접근 불가**라면 facet 값을 임의 생성하지 않고 **작업 단위 `input_unavailable`/retryable 상태**.
- 기존 draft JSON에는 `not_observed` 하나에 '미분석/미디어 없는 상태'가 혼재. v1.1에서는 위 상태 구분을 확정하고 구버전 결과 변환 시 맥락 없으면 자동 매핑하지 않는다.
- 사진에 없다고 '장식 없음'을 확정하지 않는다. 일부 손톱/캐러셀만 보이면 관측 범위를 명시.
- 원문 캡션의 제품명/디자인명이 시각적 근거와 다른 경우 원문과 AI 판정을 서로 다른 필드에 보존.
- 태그별 `confidence`는 null 허용(모델 미제공)하며 보정된 정확도 확률이 아님.

## 5. 스키마·사전 진화 원칙

1. 마스터 `tag_id`는 불변; 새 별칭·번역·용어는 사전 새 버전으로 관리.
2. 모델 응답은 `tag_id` 화이트리스트 검사. `자석네일`/`magnet`/`マグネットネイル` 표기는 사전 동의어 `F05.cat_eye`에 연결.
3. 영문·일문 필드는 미검증 번역으로 무단 채우지 않는다. 미확정은 null.
4. taxonomy 파일은 모델/프롬프트 입력값과 별도로 hash/version 기록.
5. v1.0 원본을 **덮어쓰지 말고** 검수 후 `tag_schema_v1_1.json`을 신규 생성.
6. 오호라 **공개몰** 필터(Chrome/Magnet/Jelly/Gem/Mani/Pedi/Product Type 등)는 대응표를 통해 연결하되 내부 표준 확인 전 공식 내부 용어라고 주장 금지.
7. 상품 LINEUP/PEDI/MANI/GEL STRIPS/GEL PRESS ONS와 SNS 네일 사진을 직접 동치 취급하지 않는다.

## 6. v1.1 기준 파일 등록 및 후속 검수 체크리스트

- [x] 기존 159개 `tag_id` 중복 및 facet prefix 전수 검사 (오프라인 사전 검사 통과).
- [ ] 위 모호 용어 정의가 prompt+validator의 테스트 케이스로 반영됐는가.
- [x] 새 v1.1에서 `not_observed` 제거 및 자동 변환 금지 문서화 (구버전 실레코드 마이그레이션 테스트는 추후).
- [x] 7축 P0/7축 P1의 필드 기대값 정합성 정적 검사.
- [ ] 비네일 게시물, 릴스/비디오, 이미지 URL 만료 처리 정책 결정.
- [ ] 샘플 이미지 30~50장(권한 확인)으로 오분류/근거 오류 검토 계획 확정.
- [x] 사용자 지시에 따라 v1.1을 원본을 덮지 않는 별도 신규 파일로 발행 (프로젝트 기준, 고객사 공식 승인 아님).

## 7. AI 프롬프트에 들어갈 최소 명령

```text
Only classify facets F01 F03 F05 F06 F08 F09 F10.
Use existing taxonomy tag_id values only.
Never invent tags or infer materials/brand/SKU from appearance.
Use image evidence first; caption is secondary and must be attributed.
Distinguish sheer/syrup/jelly, gradient/ombre, chrome/mirror, cat_eye/shimmer by written rules.
If uncertain use unknown, not empty observed.
All unrequested facets are not_evaluated.
Return strict JSON and tag evidence; do not include prose outside JSON.
```

**정적 규칙 파일 등록 및 JSON 검증기 추가는 완료했으나**, 시각적 분류의 판정 정확도·실 AI 프롬프트 준수·n8n 연결·GitHub CI의 PASS 결과는 별도 확인이 필요하다.
