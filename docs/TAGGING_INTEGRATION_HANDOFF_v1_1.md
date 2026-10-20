> **2026-10-20 추가 설계·코드:** 모델의 최소 7축 JSON → [7축 입력 검증기](../scripts/validate_model_output.py) → [신뢰된 메타데이터 결합 및 14축 정규화기](../scripts/normalize_p0_result.py) → [정규화 JSON Schema](../taxonomy/p0_tag_result.schema.json) → DERIVED DB **(저장 단계 미구현)**. [모델 프롬프트 계약](P0_VISION_PROMPT_CONTRACT_v1_1.md) 참조. 현재 로컬 동등 코드 합성 회귀 **85/85 PASS**, GitHub Actions 원격 CI 미확인.

# 태깅 v1.1 개발자·프론트엔드 인계 계약

기준: 2026-10-20 KST. 상태: **데이터 사전/정규화 출력 계약 검증 완료, 실 AI 이미지 태깅 및 n8n/DB 연동은 미구현**.

## 1. 정본 파일
- [14개 축/159개 태그 사전](../taxonomy/tag_schema_v1_1.json): 사람이 변경할 수 있는 표시명과 불변 tag_id. 기존 v1.0-draft 보존.
- [P0 7축/84태그 판정 규칙](../taxonomy/tag_rules_v1_1.json): 각 태그의 한국어 시각 판정 기준과 모호 용어 10개 경계.
- [P0 normalized-result JSON Schema](../taxonomy/p0_tag_result.schema.json): **LLM 원출력용이 아니라 검증·DB 저장 전의 정규화 결과** 계약.
- [샘플 합성 결과](../fixtures/sample_valid_tag_result.json): 진짜 AI 판정/실계정 데이터가 아닌 형태 검사용 JSON.
- [검증기](../scripts/validate_taxonomy.py): 태그 ID whitelist, 범주 일치, 필수 근거, 버전, 해시, timezone 체크.

## 2. 실제 n8n 입출력 분리

1. P6 RAW 저장소에서 **승인된 read-only export**만 받는다. 신규 Meta 요청이나 P6 DB 쓰기는 Analyzer가 수행하지 않는다.
2. 소스 미디어 1건 + 이미지를 볼 수 있는 권한 + 캡션(보조자료)을 AI 모델에 전달한다. 영상의 프레임 분석은 MVP 제외.
3. 모델의 자유 형식 JSON은 신뢰하지 않는다. 내부 정규화/태그 동의어 매핑/화이트리스트 확인 후 **14개 facet_result**로 채운다.
4. P0 일곱 축 `F01, F03, F05, F06, F08, F09, F10`만 실제 검사. 나머지 F02/F04/F07/F11/F12/F13/F14는 `not_evaluated`. **전체 14축을 분석했다고 표시하지 않는다.**
5. 결과 JSON은 필수 `post_id`/`media_id`/`taxonomy_version=1.1.0`/`model_id`/`prompt_version`/`analyzed_at`/`analysis_input_hash`/`source_provenance`를 포함한다. 출처·모델 버전은 모델 생성값보다 **실행 시스템에서 채우는 값**을 우선한다.
6. `observed`는 근거+사전 tag_id 1개 이상, `unknown`은 판단 불가 사유, `not_applicable`는 실제 검사한 가시 범위 안에서 요소 부재 사유, `not_evaluated`는 검사하지 않음을 뜻하며 비어 있어야 한다.
7. `input_unavailable`/`non_nail`/`unsupported_video`는 facet이 아닌 **분석 작업 상태**다. 실패했다고 태그를 만들어 저장하지 않는다.
8. 검증기를 통과한 후 DERIVED 전용 DB에 분석 실행 이력으로 저장한다. `source_post_id`/원본 미디어 참조와 버전 보존; UI에서 **F5 조회는 저장된 데이터만** 조회한다.

## 3. UI 표시 규칙

- 사진/캐러셀 자식 미디어와 해당 media 단위 태깅 결과를 나란히 표시.
- 좋아요·댓글·팔로워 수는 RAW **관측 시각**을 동반한 값; `0`은 실측 0, `null`은 누락/미요청.
- P0 7축만 완성된 분류로 표시. P1은 `미평가`. 판정 모호하면 `판단불가`로 표시하고 '장식 없음'이라고 단정하지 않는다.
- 영상/릴스는 기존 P6 원본 permalink/media URL 및 분석 미지원 상태 표시. 실제 영상 분석 성공으로 오인시키지 않는다.
- 오호라 공개몰 태그 대응은 제안에 불과하며, 회사 공식 **내부** 상품 분류라고 표시하지 않는다.

## 4. 검증 명령 (Python 3.11 기준)

```bash
python -m pip install -r requirements-test.txt
python scripts/validate_taxonomy.py
python scripts/validate_taxonomy.py --result fixtures/sample_valid_tag_result.json
python -m unittest discover -s tests -v
```

- 오늘 로컬 대응 코드 + 사전으로 합성 테스트 **36건 통과**. GitHub Actions **실행 결과는 아직 별도 확인 필요**. 이미지 AI 성능의 검증 증거가 아니다.
- `taxonomy/p0_tag_result.schema.json`은 JSON Schema Draft 2020-12를 쓰므로 **n8n의 기본 JSON Schema/Structured Output 노드가 해당 모든 keyword를 지원하는지 실제 환경에서 확인**해야 한다. 미지원 시 Python 검증기나 별도 API에서 post-validation.
- 원본 P6 운영 DB 접근, Meta 토큰/실호출, 유료 AI 및 실사진 외부 전송은 각각 사용자 승인·권한·예산 조건 확인 이후 실시.

## 5. 인계 점검

- [ ] v1.1/84규칙/정규화 JSON Schema 최신 일치
- [ ] 36건 합성 테스트/실제 환경 재검증
- [ ] 학교 n8n 호스팅/DB/파일 네트워크 연결 확인
- [ ] P6 read-only export 실제 필드·관측 시간·미디어 ID 매핑 확인
- [ ] 비용/토큰·개인정보·권한 승인
- [ ] MVP 미디어 1건 E2E 통과
- [ ] 실패/재시도/idempotency 및 무AI F5 검증

**오늘의 범위는 태깅표 최종화다. n8n은 10/21부터 시작.**
