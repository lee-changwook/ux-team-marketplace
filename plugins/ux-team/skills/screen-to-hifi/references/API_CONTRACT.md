# API 계약 수집 (산출물 C의 API 주석을 만들 때)

**레포를 연 Code 탭에서만 읽는다.** 다른 화면이거나 레포가 없으면 API 주석을 빼고 그 사실을 알린다 (SKILL.md "어디서 되는가").

## 레포를 찾는다

| 상황 | 동작 |
| ---- | ---- |
| Code 탭 + 현재 폴더에서 페이지 라우트 → 훅 → fetcher · schema를 찾음 | 아래 수집 절차대로 |
| Code 탭인데 현재 폴더에서 못 찾음 | 레포 폴더가 따로 있는지 한 번 묻는다. 없다고 하면 API 주석 없이 진행 |
| Cowork · Chat | API 주석 없이 진행 |

API 주석을 뺄 때
- 주석 계획 표에서 `API` 카테고리 행만 뺀다. 오버레이와 Description 카드(기획 원문)는 그대로 만든다.
- 승인 게이트와 최종 보고의 "확인할 것"에 적는다: "API 주석을 붙이지 않았습니다. 이유: <레포 없음 · 화면>. 붙이려면 레포를 연 Code 탭에서 다시 실행해 주세요."
- 화면 라벨이나 추측으로 API 내용을 채우지 않는다.

## 수집 절차

페이지 라우트에서 fetcher까지 따라가 엔드포인트와 필드명을 뽑는다. 화면 라벨이 아니라 **스키마가 정답**이다.

아래 경로는 티키타 FE 레포 구조 예다. 구조가 다르면 같은 순서(라우트 → 훅 → fetcher · schema)로 따라간다.

1. `src/app/**/<page>/**/page.tsx` → 페이지 컴포넌트 → 호출하는 훅
2. `src/apis/aca/tanstacks/<page>/hooks/*.ts` → fetcher 이름
3. `src/apis/aca/fetchers/<prefix>/<resource>/{fetcher,schema}.ts` → URL · 요청 · 응답

뽑을 것: HTTP method와 **prefix 상수를 전개한 전체 경로**, 요청 필드(필수·선택·형식), 응답 필드(중첩·nullable), 검증 정규식과 그 위반 시 문구.

**필드가 없다는 사실도 수집 대상이다.** 실측 예 — 고유번호는 POST 요청 본문에 없고(서버가 채번) GET 목록 응답에도 없다. 이런 부재는 기획 판단을 바꾸므로 반드시 적는다.

같은 개념의 필드명이 API마다 다르면 그것도 적는다 (실측: 등·하원은 `haknyeon`, 전체 처리는 `hangnyeon`).

결과는 **스키마 원문**이어야 한다. 코드 읽기 · 검색으로 직접 확인한다.

## 주석 본문 양식

본문은 요청·응답을 나눠 bullet로 쓴다. 필드명은 백틱, 필수·선택과 형식을 함께.

```
`GET /v2/A/aka-t/deunghawon`  · fetcher `getAtDeunghawons`

**요청 — query parameter**
- `jojikNanoId` · 필수
- `startAt` / `endAt` · 필수 · `YYYY-MM-DD` (date-only)
...
**응답**
- `sessions[]`
  - `jaewonsaeng` : `nanoId` · `name` · `goyuBunho`(nullable) · …
```

부착 방법(재탐색 · 가드 · 별도 호출 확인)은 [FIGMA_RECIPE.md](FIGMA_RECIPE.md) 8-3절을 따른다.
