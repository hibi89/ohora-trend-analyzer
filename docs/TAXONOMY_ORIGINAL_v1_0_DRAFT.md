# OHORA Trend Catcher — 최종 네일 디자인 태깅 표준안 v1.0

> **구분:** 프로젝트 제안 표준안 / 오호라 공식 내부 분류표 아님 / 2026-10-20
> **목적:** 3개국 인스타그램 원본을 보존하면서 네일 디자인 AI 태깅을 일관되게 저장하고, 향후 오호라 상품·기획 데이터와 연결할 수 있는 확장 가능한 데이터 사전.

## 0. 핵심 원칙

- 14개 대분류는 **서로 독립**. 한 디자인에 크롬·프렌치·리본·코케트가 동시 부여될 수 있다.
- Meta 원본·수집 관측값은 **불변 보존**하고, AI 결과는 별도 저장한다.
- 분류 결과의 `unknown`(분석했으나 판단 불가), `not_applicable`(해당 없음), `not_observed`(분석 대상 자체 없음)를 구분한다.
- 이미지에서 확인한 것과 캡션에서 주장한 것을 분리하고 근거를 기록한다.
- 게시물 1건에 미디어 여러 개, 디자인 관측 여러 개를 허용한다.
- 태깅 사전 버전·모델·프롬프트·분석 시각을 반드시 기록한다.
- 오호라 공개 상품 필터는 **외부 연동용 대응표**이며 내부 표준이라고 주장하지 않는다.

## 1. 디자인 태깅 대분류 14개 — 전체 사전

| 코드 | 대분류 | 중분류/의미 | 표준 태그 예시 (한글) | 적용 규칙 |
|---|---|---|---|---|
| `F01` | **색상** | 색상군·금속색 | 화이트, 블랙, 그레이, 누드, 베이지, 핑크, 레드, 코랄, 오렌지, 옐로, 그린, 블루, 퍼플, 브라운, 골드, 실버, 로즈골드, 멀티컬러 | 무늬의 금속색과 베이스색 모두 선택 가능. primary/secondary/accent 관계는 S01에서 기록. |
| `F02` | **색상 특성** | 채도·명도·온도·톤 | 파스텔, 뮤트, 비비드, 딥, 다크, 더스티, 네온, 라이트, 웜, 쿨, 중성 톤 | 웜·쿨은 이미지 조명에 민감하므로 판단 불가 시 보류. 밀키는 F03으로만 표준화. |
| `F03` | **발색·투명도** | 불투명도·발색 방식 | 불투명, 반투명, 투명, 시어, 시럽, 젤리, 밀키, 레이어드 발색 | solid는 F03 opaque(발색)와 F06 full_color(디자인)를 구분. |
| `F04` | **표면 마감** | 광택·반사 표현 | 글로시, 세미매트, 매트, 글레이즈드, 미러, 펄광, 오팔광, 홀로그램 | chrome은 F05 효과, mirror는 F04 마감으로 별도 공존 가능. |
| `F05` | **효과·재질감** | 특수 시각 효과 | 캣아이, 벨벳, 크롬, 글리터, 쉬머, 플래시, 자개, 유리알, 슈가, 호일, 오로라, 메탈릭 효과 | 자석/마그넷/캣아이 동의어를 cat_eye로 정규화; 실제 시술 방법은 외형만으로 단정 금지. |
| `F06` | **기본 디자인 기법** | 면·색상 구성 | 풀컬러, 프렌치, 그라데이션, 옴브레, 블러셔, 아우라, 컬러블록, 네거티브 스페이스, 하프문, 아웃라인 | gradient와 ombre는 기준에 따라 병존 가능; 원문도 별도 보존. |
| `F07` | **프렌치 세부형** | 프렌치 세부 형태 | 클래식, 마이크로, 딥, 더블, 사선, 사이드, 리버스, V라인, 웨이브, 스캘럽 | F06 french가 선택된 디자인에서만 적용; 그렇지 않으면 not_applicable. |
| `F08` | **패턴·문양** | 반복·추상 무늬 | 도트, 스트라이프, 체크, 깅엄, 마블, 타이다이, 토터스셸, 레오파드, 지브라, 추상 웨이브, 레이스, 플래드 | 리본·하트 같은 구체적 대상은 F09, 반복되는 추상 무늬는 F08. |
| `F09` | **모티프·오브젝트** | 구체적인 형상 | 플라워, 리본, 하트, 별, 체리, 나비, 구름, 눈꽃, 조개, 캐릭터, 레터링, 과일, 달, 동물 | 리본 형태 F09 ribbon과 실제 입체 장식 F10 three_d_ribbon 공존 가능. |
| `F10` | **입체 장식** | 부착물·볼륨 | 스톤, 진주, 스터드, 체인, 참, 3D 리본, 엠보 꽃, 물방울 젤, 3D 조형, 비즈 | 사진만으로 재료·부착 방식 확정하지 말고 시각적으로 확인된 모양을 우선. |
| `F11` | **디자인 배치** | 위치·밀도·조합 | 전체, 팁, 큐티클, 중앙, 사이드, 포인트 1~2개, 올아트, 믹스매치, 비대칭, 분산 배치, 집중 배치 | 이미지에 보이는 손톱만 기준; 전체 손톱 미노출 시 all_art를 무리하게 확정하지 않음. |
| `F12` | **네일 형태** | 셰이프·길이 (각각 단일 선택) | 라운드, 오벌, 스퀘어, 스퀘어오프, 아몬드, 코핀, 스틸레토, 숏, 미디엄, 롱 | shape와 length 분리 저장; 여러 손톱의 형태가 다르거나 불명확하면 단일 값 강제 금지. |
| `F13` | **스타일·무드** | 미학·감성 표현 | 미니멀, 클린, 러블리, 코케트, 발레코어, Y2K, 키치, 빈티지, 고딕, 럭셔리, 내추럴, 스포티, 엣지 | 감성적·주관적 축. 임계 신뢰도 미달은 unknown 처리. |
| `F14` | **시즌·사용 맥락** | 계절·행사·사용 상황 (추정 별도 표시) | 봄, 여름, 가을, 겨울, 크리스마스, 핼러윈, 발렌타인, 웨딩, 데일리, 휴가, 파티, 페스티벌 | 게시일이 곧 시즌 디자인을 뜻하지 않음. 행사 태그는 모티프/캡션 등 근거 요구. |

**주의:** 표에 열거된 태그는 v1.0 추천 사전이다. 새로운 트렌드 용어는 대분류를 새로 만들기 전에 해당 축에 새 코드를 추가한다. 이미 사용한 `tag_id`의 의미는 바꾸지 않는다.

### 1-1. 다중 선택 / 계층적 선택 규칙

- `F01~F11`, `F13~F14`: 다중 태그 허용. 사진으로 확인된 요소만 기록.
- `F07`: `F06.french`가 있는 경우에만 세부형 사용. 프렌치가 없다면 `not_applicable`.
- `F12`: **shape**와 **length**를 서로 다른 필드로 관리하고, 한 손톱/디자인 단위에서 각각 단일 값 또는 `unknown`. 여러 손톱의 모양이 다른 경우 손톱별 기록.
- `F14`의 계절·행사는 캡션과 시각적 근거를 분리. 10월 게시물이라는 이유만으로 핼러윈으로 태깅하지 않는다.
- `F02.milky`는 사용하지 않는다. **밀키는 `F03.milky`** 한 곳에 통일하고 채도·색온도는 `F02`에서 기록한다.
- `F05.cat_eye`의 동의어: 자석 네일, 마그넷 네일, Magnetic, マグネットネイル. `F05.chrome`과 `F04.mirror`는 효과/마감으로 구분.

## 2. 디자인 ID 준비용 구조 정보 4개

| 코드 | 항목 | 권장 필드 | 분석 규칙 |
|---|---|---|---|
| `S01` | 주색·보조색·포인트색 | `color_roles` | 주색/보조색/포인트색 순위는 이미지 근거; HEX는 이미지 추정값으로만 |
| `S02` | 베이스·기법·장식 관계 | `design_elements` | 누드 베이스 위 실버 프렌치와 역관계 구분; 보이지 않는 도포 순서는 추정 금지 |
| `S03` | 네일별 구성 | `nail_layout` | 손가락 번호를 알 수 없으면 임의 할당 금지; 사진에 보이는 손톱만 |
| `S04` | 대표 요소와 부가 요소 | `design_signatures` | 차별화된 주 요소와 작은 부가 요소 분리 |

**디자인 ID 정책:** 원본 게시물 ID ≠ 미디어 ID ≠ 디자인 관측 ID. 동일 디자인을 국가·게시물 간 묶는 **클러스터/정규 디자인 ID**는 유사도·사람 검증 단계 이후에 별도로 부여한다. 해시나 태그 문자열만으로 동일 디자인을 확정하지 않는다.

## 3. OHORA 공식몰 공개 상품 필터 대응표 (내부 기준 아님)

공식몰 공개 분류에서는 색상, Style(Chrome, Color Mix, Design, French, Gem, Glitter, Jelly, Magnet, Marble, Ombre, Solid), LINE UP(MANI/PEDI/SET), PRODUCT TYPE(GEL STRIPS/GEL PRESS ONS 등), Nail Shape·Nail Length 등을 확인할 수 있다.

| 오호라 공개 필터 | 권장 내부 태그/필드 | 적용 조건 | 주의 |
|---|---|---|---|
| Color / 색상군 | `F01` | 실제 색상값에 근거하여 다중 태깅 | 색상칩·패턴 내 부위별 색상 다를 수 있음 |
| Style: Chrome | `F05.chrome` | 외형상 크롬 효과일 때 | F04.mirror와 중복 가능 |
| Style: Magnet | `F05.cat_eye` | 자석 효과가 시각적으로 확인될 때 | 시술 재료는 단정하지 않음 |
| Style: French | `F06.french` | 프렌치 구조 확인 | F07 세부형 병행 |
| Style: Glitter | `F05.glitter` | 입자형 반짝임 확인 | 쉬머와 구별 |
| Style: Jelly | `F03.jelly` | 젤리 발색 확인 | 시럽·시어와 중복 가능 |
| Style: Marble | `F08.marble` | 마블 문양 확인 | 태깅시 F06 기법과 독립 |
| Style: Ombre | `F06.ombre` | 옴브레 색상 전환 확인 | 그라데이션과 경계 검토 |
| Style: Solid | `F06.full_color + F03.opaque` | 불투명 단색 풀코트일 때만 | 상황에 따라 한쪽만 적용 |
| Style: Gem | `F10.rhinestone` | 실제 스톤형 장식이 보일 때 | 모든 Gem=스톤으로 강제하지 않음 |
| Style: Color Mix | `F01 다중 색상 / F11.mix_match` | 색상 혼합이나 손톱별 믹스 확인 | 공식몰 분류와 1:1 동치 아님 |
| Style: Design | `매핑 없음` | 광범위한 상위 분류 | F06~F11의 개별 구체 태그 사용 |
| Line up: MANI / PEDI / SET | `P01.lineup` | 상품 분류/명시적 메타 정보에서만 | 손 사진만으로 오호라 상품 여부 추정 금지 |
| Product type: GEL STRIPS / GEL PRESS ONS | `P02.product_type` | 상품 카탈로그/메타 연계 시 | SNS 이미지에서 제품 종류를 임의 확정 금지 |
| Nail shape: Almond / Oval | `F12.shape` | 손톱 형태 시각적으로 확인 시 | 공식몰 제공 상품 속성과 별도 저장 |
| Nail length: Short / Medium | `F12.length` | 보이는 사진에 한해 | 비율/원근에 따라 unknown 가능 |

상품 Line Up / Product Type는 인스타그램 사진만으로 오호라 상품 여부를 판단하지 말고, **상품 카탈로그 ID·SKU가 확인된 경우에만 연결**한다. 공개 필터와 분석용 태그는 동일 구조가 아니다.

## 4. 한국·미국·일본 공통 표준화 원칙

분석 데이터에는 표시명을 직접 비교하지 않고 **불변 `tag_id`**를 저장한다. 표시명(`label_ko`, `label_en`, `label_ja`)과 동의어(`aliases`)는 별도 태그 사전 테이블에서 관리한다.

| 불변 코드 | 한국어 대표명 | 영문·일문·동의어 예시 |
|---|---|---|
| `F05.cat_eye` | 캣아이 | 마그넷, 자석 네일, magnet, magnetic, cat eye, cat-eye, マグネットネイル |
| `F05.chrome` | 크롬 | 크롬 네일, chrome nails, クロムネイル |
| `F03.syrup` | 시럽 | 시럽 네일, syrup nails, シロップネイル |
| `F03.jelly` | 젤리 | 젤리 네일, jelly nails, ジェリーネイル |
| `F06.french` | 프렌치 | 프렌치 네일, French tip, フレンチネイル |
| `F06.blush` | 블러셔 | 치크 네일, blush nails, チークネイル |
| `F08.marble` | 마블 | 대리석 네일, marble nails, マーブルネイル |
| `F09.ribbon` | 리본 | 리본 네일, bow, リボンネイル |
| `F05.glitter` | 글리터 | 글리터 네일, ラメ |
| `F10.rhinestone` | 스톤 | 크리스털 파츠, gem, ストーン |
| `F13.coquette` | 코케트 | 코케트 네일, コケット |
| `F04.glazed` | 글레이즈드 | 글레이즈드 도넛, glazed donut |

**언어 데이터 품질:** JSON 사전에 모든 태그의 영문 코드·한국어 대표명을 제공한다. 일본어 대표명은 확인한 주요 용어만 기재하고 나머지는 `null`로 남겼다. `null`을 임의 번역으로 채우지 않는다. 인스타그램 캡션의 원문, 원어, 해시태그도 수정 없이 보존한다.

## 5. 데이터베이스 저장 계약 (기존 RAW 수집기 침범 금지)

| 논리 데이터 집합 | 핵심 데이터 | 보존 정책 |
|---|---|---|
| `raw_posts`, `raw_media`, `raw_observations` *(기존 이름에 맞춰 적용)* | 계정·게시물·미디어 원본, Meta 수신 필드, 수집 시각, 참여 지표 | 기존 수집 파이프라인/원본 보존 방식 유지 |
| `tag_dictionary` | `tag_id`, 대분류, 표준명, 동의어, 언어, 활성 상태, taxonomy_version | 코드 재사용·의미 변경 금지, 추가 시 버전 갱신 |
| `media_tag_runs` | post_id, media_id, 모델·프롬프트·사전 버전, 실행 시각, 입력 해시, 모델 원출력 | 재실행 시 기존 결과 덮어쓰기 금지 |
| `facet_results` | tag_run_id, facet_id, 상태, tag_ids, 신뢰도, 시각/캡션 근거, 근거 설명 | `unknown`과 `not_applicable`, 미관측을 구분 |
| `design_structure` | S01~S04 구조 정보, 미디어별 디자인 구성 | 전체 손가락이 보이지 않으면 부분 정보 허용 |
| `tag_reviews` | 담당자 승인/수정, 변경 전후, 검수 일시 | AI 원출력 보존, 사람 수정 덮어쓰기 금지 |
| `public_catalog_mappings` | 오호라 공식몰 필터·SKU와 태그의 매핑 및 출처 | 공식 공개 항목과 분석용 가설 구분 |

### 5-1. AI 분석 결과 최소 필수 필드

`post_id`, `media_id`, `taxonomy_version`, `model_id`, `prompt_version`, `analyzed_at`, `analysis_input_hash`, `is_nail_design`, `review_status`, `facet_results`, `design_elements`, `source_provenance`.

태그별 `facet_results`에는 `facet_id`, `status`(`observed`/`unknown`/`not_applicable`/`not_observed`), `tag_ids`, `confidence`, `evidence_source`(`image`/`caption`/`both`/`human`), `evidence_note`를 저장한다. **LLM의 confidence는 보정된 정확도 확률이 아니다.**

### 5-2. 예시 (가상 분석 결과)

```json
{
  "post_id": "POST_EXAMPLE",
  "media_id": "MEDIA_EXAMPLE",
  "taxonomy_version": "1.0.0-draft",
  "model_id": "MODEL_NAME",
  "prompt_version": "prompt-1",
  "analyzed_at": "2026-10-20T13:00:00+09:00",
  "is_nail_design": true,
  "review_status": "unreviewed",
  "facet_results": [
    {
      "facet_id": "F01",
      "status": "observed",
      "tag_ids": [
        "F01.pink",
        "F01.silver"
      ],
      "confidence": 0.92,
      "evidence_source": "image",
      "evidence_note": "분홍색 베이스와 실버 팁"
    },
    {
      "facet_id": "F05",
      "status": "observed",
      "tag_ids": [
        "F05.chrome"
      ],
      "confidence": 0.74,
      "evidence_source": "image",
      "evidence_note": "거울광처럼 보이는 금속성 팁"
    },
    {
      "facet_id": "F06",
      "status": "observed",
      "tag_ids": [
        "F06.french"
      ],
      "confidence": 0.94,
      "evidence_source": "image",
      "evidence_note": "손톱 끝단 컬러 분리"
    },
    {
      "facet_id": "F07",
      "status": "observed",
      "tag_ids": [
        "F07.classic"
      ],
      "confidence": 0.83,
      "evidence_source": "image",
      "evidence_note": "일반 곡선형 팁"
    },
    {
      "facet_id": "F14",
      "status": "unknown",
      "tag_ids": [],
      "confidence": null,
      "evidence_source": "image",
      "evidence_note": "계절과 행사 확인 불가"
    }
  ],
  "design_elements": {
    "S01": {
      "primary": "F01.pink",
      "accent": "F01.silver"
    },
    "S04": {
      "primary_tag_ids": [
        "F06.french",
        "F05.chrome"
      ],
      "secondary_tag_ids": []
    }
  },
  "source_provenance": {
    "image_analyzed": true,
    "caption_analyzed": false
  }
}
```

## 6. 이번 KDT 프로젝트 제출 범위와 확장 계획

| 이번에 반드시 구현(P0) | 향후 고도화(P1+) |
|---|---|
| 14개 축 전체 정의 + 불변 태그 코드·동의어 사전 | 14개 전축 고정밀 판별·모델 평가 |
| 핵심 7개 축 `F01/F03/F05/F06/F08/F09/F10` 태깅 | 나머지 축 정밀 분석, `F12` 네일별 형태 |
| `S01` 주색·보조색·포인트, `S04` 핵심·부가 요소 | `S02` 레이어 관계, `S03` 손톱별 상세 구성 |
| 원본 ID와 미디어 ID 연결, 모델·사전 버전·시각·근거 저장 | 사람 검수 UI, 재분석 이력, 국가별 모델 품질 평가 |
| 이미지 클릭 → 요약 태그 + 게시물 지표 상세 조회 | 상품 카탈로그 연결, 유사 디자인 클러스터링, 트렌드 예측 |

**합격 기준:** (1) 수집 원본 변경 없음, (2) 동일 사진 재조회에서 불필요한 AI 재실행 없음, (3) 태깅 실패해도 게시물 원본 보존, (4) 후속 모델이 taxonomy_version 별 결과를 재생성/비교할 수 있음, (5) UI가 원본 미디어+태그+게시물 데이터를 같은 ID로 조회할 수 있음.

## 7. 화면 데이터 계약 — 이미지 클릭 상세보기

- 왼쪽/상단: 대표 이미지 + 캐러셀 확대, 링크 및 출처
- 오른쪽/하단: 대표 디자인 3~7개 태그, 주요 색상 역할, 세부 14축 펼치기
- 하단: 작성일/국가(계정 리스트 기준)/좋아요/댓글/팔로워(있으면)/관측 시각/원문 캡션
- 운영 보조: AI 판정 근거와 신뢰도, unknown 표시, 분석 시각·버전, 담당자 수정 이력
- **혼동 주의:** 인스타그램 실제 인기 지표와 AI가 추정한 디자인 특징을 명확히 구분한다.

## 8. 출처 및 범위

- OHORA US 공식몰 Pink 컬렉션의 Colors, Nail Length, LINE UP, PRODUCT TYPE, Style 공개 필터: https://ohora.com/collections/by-color_pink
- OHORA US 공식몰 Sale 컬렉션의 Nail Shape/Length/Style 공개 필터: https://ohora.com/collections/sale
- JNA 국제 네일리스트 기능검정시험 소개(기술·교육 기준 참고, 본 14축 승인 근거가 아님): https://www.nail.or.jp/kentei/international_kentei/korea.html

**범위 제한:** 14개 축의 구성·동의어 사전·디자인 구조 4개 및 OHORA 대응 규칙은 프로젝트용 제안이다. 오호라 내부 분류표나 전 세계 공통 공식 네일 디자인 표준이라고 주장하지 않는다. 분석 모델의 실제 정확도는 현장 라벨링·평가 전까지 미검증이다.
