# screen-to-hifi eval

- 켜짐 eval(켜져야 할 요청 · 켜지면 안 될 요청)은 통합 단계에서 11개 스킬을 함께 켠 상태로 돌린다.
- 기능 확인 중 브라우저 캡처 · Figma 쓰기가 드는 항목은 시험용 Figma 파일과 staging 화면이 정해지면 통합 단계에서 돌린다 (10/15 리드 결정).
- 이번 트랙에서는 기능 확인마다 스킬 본문의 어느 지시가 그 결과를 내는지 정적으로 대조했다 (맨 아래 표).

## 켜져야 할 요청
1. 이 화면 피그마로 떠 줘. staging의 등·하원 내역 화면이고, 기간을 이번 달로 조회한 상태로 떠 줘.
2. 기존 화면에 시안 얹어 줘. <Figma 프레임 URL> 수업 관리 화면에서 '수업들' 헤더 오른쪽에 등록 일괄 생성 버튼을 넣고 싶어.
3. 이 피그마 프레임으로 hifi 제안 만들어 줘. 수업 행마다 등록 있음/없음 칩을 붙이는 안이야.
4. 수업 관리 화면을 피그마로 캡처하고, 이 기획 문서 2.4절대로 바꾼 시안이랑 설명 카드까지 같이 올려 줘.
5. 피그마에 있는 기존 화면 프레임 위에 시안 1 · 시안 2를 나란히 비교하는 제안 섹션 만들어 줘.

## 켜지면 안 될 요청
다른 스킬이 맡는 말을 넣는다 (`docs/01-트리거 지도.md`의 "겹치는 말 정리").

| 요청 | 대신 맡는 스킬 |
|---|---|
| staging에 올라간 출결 관리 화면이 기획 의도대로 구현됐는지 봐 줘 | `intent-check` |
| 개발로 넘기기 전에 요구사항 글이랑 피그마 시안이 맞는지 확인해 줘 | `handoff-check` |
| 새 기능 화면을 백지에서 와이어프레임 시안으로 그려 줘 | 없음 (기존 화면이 없는 시안은 해당 없음) |
| 출결 관리에서 지각과 결석은 어떻게 달라? | `tikita-policy` |
| 이번 기능 사용 설명서 PDF로 만들어 줘 | `feature-guide` |
| 시안 리뷰 결과를 공유할 HTML 페이지로 만들어 줘 | `artifact-style` |

## 기능 확인
| 확인 | 화면 | 기대 결과 | 관련 ACC |
|---|---|---|---|
| Figma 커넥터를 끊은 상태에서 "hifi 제안 만들어 줘" + Figma URL | Chat | 다른 단계보다 먼저 Customize › Connectors에서 Figma를 연결하라고 안내하고 멈춘다 | ACC-22 |
| staging 화면 주소 + 방향 + 타겟 Figma 페이지 URL | Code 탭 (Claude in Chrome 확장) | 캡처 전 확인 → 캡처 · 보정 → 새 URL을 묻지 않고 정찰로 이어감 → 승인 게이트 → 산출물 A · B | ACC-23 |
| staging 화면 주소만, 방향 없음 ("이 화면 피그마로 떠 줘") | Code 탭 | 캡처 · 보정 후 결과 URL과 보정 내역을 주고 끝낸다. 방향을 지어내지 않는다 | ACC-23 |
| 레포 폴더 없이 Figma URL + 방향 + 기획 원문 | Cowork | 주석 계획에 `API` 행이 없고, 게이트와 보고의 "확인할 것"에 API 주석을 뺀 이유와 붙이는 방법이 있다. Description 카드는 만든다 | ACC-24 |
| 같은 요청을 티키타 FE 레포를 연 Code 탭에서 | Code 탭 | 주석 계획에 `API` 행이 있고, 출처가 fetcher · schema 원문이다 | ACC-24 |
| Pretendard가 로드되지 않는 파일 | 모두 | 대체 폰트로 바꾸기 전에 알리고 (a) 재시도 · (b) 대체 중 고르게 한다 | ACC-25 |
| 주석을 붙이는 호출에서 대상 노드 하나가 없음 | 모두 | 가드로 `skipped`에 남기고 나머지는 붙인다. 부착 뒤 별도 호출로 붙었는지 확인한다 | ACC-25 |
| 정찰 뒤 사용자가 캡처를 다른 섹션으로 옮김 (id 재발급) | 모두 | 정찰 id가 `null`이면 텍스트 앵커로 다시 찾는다 | ACC-25 |
| 운영 주소를 주고 캡처 요청 | Code 탭 · Cowork | 캡처하지 않고 멈춘 뒤 사용자에게 확인한다 | (CHG-26, `docs/tracks/D-CHG.md`) |
| base Figma URL + 방향 | Chat | 모드 A를 하고, 모드 B와 API 주석은 빼고 알린다 | (CHG-27, `docs/tracks/D-CHG.md`) |
| 산출물 C를 만든 뒤 캔버스 확인 | 모두 | Description 카드 · 주석 · 오버레이 글에 `CHG` · `ANN` · `DSC` · `OVL` 번호가 없다 | (CHG-21, `docs/tracks/D-CHG.md`) |

## 정적 대조 (이번 트랙)
| 관련 ACC | 결과를 내는 지시 | 결과 |
|---|---|---|
| ACC-22 | SKILL.md Step 0-1 (다른 단계보다 먼저), CHECKLIST.md 1-3 첫 항목 | 있음 |
| ACC-23 | SKILL.md Step 1, MODE_B_CAPTURE.md B-0 · B-7 | 있음 |
| ACC-24 | SKILL.md "어디서 되는가" · 입력 3, API_CONTRACT.md "레포를 찾는다", CHECKLIST.md 1-1 "API 주석" 줄 · 2-4 | 있음 |
| ACC-25 폰트 대체 | SKILL.md Step 0-2, FIGMA_RULES.md 6-1절 · 7절, FIGMA_RECIPE.md 1절 · 3-1절, CHECKLIST.md 1-3 · 3절 | 원본 문구 그대로 |
| ACC-25 전체 롤백 | SKILL.md 8-5, FIGMA_RULES.md 6-3절 · 6-9절, FIGMA_RECIPE.md 8-3절, CHECKLIST.md 2-3 | 원본 문구 그대로 (도구 이름만 동작으로) |
| ACC-25 id 재발급 | SKILL.md 8-2 · 8-5, FIGMA_RULES.md 6-9절, FIGMA_RECIPE.md 2절 · 8-3절 | 원본 문구 그대로. FIGMA_RECIPE.md 2절은 CHG-19로 재탐색과 맞춤 |
