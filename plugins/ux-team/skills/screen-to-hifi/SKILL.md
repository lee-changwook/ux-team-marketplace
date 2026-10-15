---
name: screen-to-hifi
version: 1.0.0
description: "staging 화면을 Figma로 캡처하고, 말로 준 개선 방향을 그 위에 hifi 제안(본편·제안부·설명)으로 얹는다. '이 화면 피그마로 떠 줘', '기존 화면에 시안 얹어 줘', 'hifi 제안 만들어 줘'를 요청할 때 쓴다."
author: lee-changwook
relates:
  - intent-check
  - handoff-check
argument-hint: "[base Figma URL 또는 staging 화면 주소] [방향 텍스트] [선택: 기획 원문 URL·파일] [선택: 타겟 Figma URL]"
triggers:
  keywords:
    - 이 화면 피그마로 떠 줘
    - 기존 화면에 시안 얹어 줘
    - hifi 제안 만들어 줘
disable-model-invocation: false
---

# Screen to Hi-fi

staging에서 **실행 중인 화면을 캡처해 만든 Figma 프레임**(DOM 구조가 그대로 레이어가 된 오토레이아웃)을 원본으로 받아, 사용자가 말로 준 방향을 그 위에 얹는다.
base가 아직 Figma에 없으면 먼저 캡처하고(모드 B), 같은 실행에서 방향 얹기(모드 A)로 이어간다.

## 어디서 되는가

화면 판별은 [references/_shared/surfaces.md](references/_shared/surfaces.md)의 순서를 따른다.

| 단계 | Chat | Cowork | Code 탭 |
| ---- | ---- | ------ | ------- |
| Figma 커넥터 확인 | 됨 | 됨 | 됨 |
| 모드 B 캡처 | 안 됨 → Cowork · Code 탭 안내 | 내장 브라우저 | Claude in Chrome 확장이 있을 때 |
| 모드 A 정찰 · 승인 게이트 · 산출물 A · B | base가 Figma에 있으면 됨 | 됨 | 됨 |
| 산출물 C: 오버레이 · Description 카드 | 기획 원문을 붙여 넣거나 올리면 됨 | 됨 | 됨 |
| 산출물 C: API 주석 | 안 됨 (빼고 알림) | 안 됨 (빼고 알림) | 레포를 열었을 때 |

- 지금 화면에서 안 되는 단계는 조용히 건너뛰지 않는다. 어디서 하면 되는지 알리고, 빼고 진행할 수 있으면 사용자에게 고르게 한다.

## 언제 무엇을 읽는가

| 파일 | 읽는 때 |
| ---- | ------- |
| [references/FIGMA_RULES.md](references/FIGMA_RULES.md) | 항상. 시작할 때 |
| [references/CHECKLIST.md](references/CHECKLIST.md) | 항상. 승인 게이트(Step 5)와 보고(Step 9) 전 |
| [references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) | 첫 Figma 코드 실행 전 |
| [references/MODE_B_CAPTURE.md](references/MODE_B_CAPTURE.md) | base가 Figma에 없을 때 (모드 B) |
| [references/API_CONTRACT.md](references/API_CONTRACT.md) | 레포를 연 Code 탭에서 API 주석을 만들 때 |

## 산출물 3종

| 산출물 | 정의 | 만드는 법 |
| ------ | ---- | --------- |
| **A. 본편** | 실화면과 동일한 프레임 전체 + 방향을 적용한 컴포넌트 추가·수정 | base 프레임 `clone()` → 변경목록대로 패치 |
| **B. 제안부** | 설명할 컴포넌트만 뽑은 시안 + 화살표 + 메모 | base에서 해당 서브트리 `clone()` → 절단 → 시안별 변형 |
| **C. 설명 레이어** | A·B 위에 얹는 설명 — 오버레이 · 주석 · Description 카드 | 코드에서 API 계약 추출 + 기획 원문 verbatim |

**C를 후속 작업으로 미루지 않는다.** 설명 없는 시안은 리뷰에서 같은 질문을 다시 받는다. 설명 소스를 받았으면 한 번의 실행에서 A·B·C를 함께 낸다.

### 설명은 4층이고 보이는 곳이 다르다

| 층 | 무엇 | 어디서 보이나 | 누가 만드나 |
| -- | ---- | ------------- | ----------- |
| 오버레이 Frame | 영역 표시 + 커넥터·주석의 **앵커** | Design · Dev 양쪽 | 스킬 |
| Annotation | 카테고리(`API`·`안내`) + 본문. 노드의 **속성** | **Dev Mode 전용** | 스킬 |
| Description 카드 | 기획 원문. 읽는 본문 | Design · Dev 양쪽 | 스킬 |
| 커넥터 | 시각적 연결선 | Design · Dev 양쪽 | **사용자 수기** |

**Annotation만으로 끝내지 않는다.** 개발자가 아닌 사람은 대개 Design 모드로 열기 때문에 Dev Mode 전용 주석은 그들 눈에 보이지 않는다. 그래서 Description 카드가 따로 필요하다.

**커넥터와 주석은 직접 연결되지 않는다.** 커넥터는 양 끝이 `endpointNodeId`로 노드에 붙고, Annotation은 노드의 속성이라 가리킬 대상이 없다. 둘을 잇는 고리는 **노드 하나** — 오버레이에 주석을 달고 그 같은 오버레이를 커넥터 끝점으로 쓴다.

**B는 A에서 잘라낸 것이지 새로 그린 것이 아니다.** 실제 색·폰트·변수 바인딩이 그대로 따라오므로 A와 이질감이 없다. 팀 기획안 파일의 `수업들 panel 시안` > `시안 1. …` / `시안 2. …`가 이 형식의 선례다.

## 쓰는 때 · 쓰지 않는 때

- "이 화면 피그마로 떠 줘" → 모드 B. 방향이 없으면 캡처 · 보정까지 하고 끝낸다
- "기존 화면에 시안 얹어 줘", "hifi 제안 만들어 줘" → 모드 A. base가 Figma에 없으면 모드 B부터
- 기존 화면을 바탕으로 할 때만 쓴다. 아래는 맡지 않는다:
  - 원본 화면 없이 백지에서 새로 그리는 시안
  - 와이어프레임 충실도면 충분한 일
  - Figma를 읽어서 계획서만 쓰는 일

## 입력

1. **base** (필수) — 둘 중 하나
   - Figma 프레임 URL (`?node-id=` 포함). 실화면을 캡처해 만든 프레임
   - Figma에 아직 없으면 staging 화면 주소 + 캡처를 넣을 Figma 파일·페이지 URL (모드 B)
2. **방향** — 자유 텍스트. 모드 A에 필수다. Step 4에서 변경목록으로 정규화한다.
3. **설명 소스** (선택 — 주면 산출물 C를 만든다)
   - **기획 원문** — gist·구글독스·노션 URL이나 파일. Description 카드에 **verbatim**으로 옮긴다. 읽는 방법은 "도구 사용 규칙"
   - **코드** — 레포를 연 Code 탭이면 따로 주지 않아도 페이지 라우트를 따라가 fetcher·schema에서 API 계약을 직접 뽑는다 ([references/API_CONTRACT.md](references/API_CONTRACT.md)). 다른 화면이면 API 주석을 빼고 알린다
   - 둘 다 없으면 C를 건너뛰고 A·B만 만든다. **설명을 지어내지 않는다**
4. **타겟** (선택) — 없으면 base와 같은 파일의 새 섹션. URL을 주면 그 파일/섹션. 제약은 아래 참조.

**fileKey · nodeId는 사용자가 준 URL에서만 뽑는다.** 참고 문서에 나오는 node id는 실측 예일 뿐이니 쓰지 않는다.

### 타겟이 다른 파일일 때의 제약 (중요)

`clone()`은 **같은 파일 안에서만** 동작한다. Plugin API에 파일 간 복사가 없다.

- 타겟 파일에 base 캡처가 **이미 있으면** → 그 노드를 base로 잡고 정상 진행
- **없으면** → 절단 시안을 만들 수 없다. 두 경로 중 사용자가 고른다:
  - (a) 원본 파일에 만들고, 사용자가 Figma UI에서 타겟 파일로 복사
  - (b) 사용자가 base 프레임을 타겟 파일에 먼저 붙여넣고 그 node-id를 준다
- 추측으로 재현(색·폰트 하드코딩)해서 채우지 않는다. [references/FIGMA_RULES.md](references/FIGMA_RULES.md) 1절 위반이다.

## 워크플로우

### Step 0. Preflight — Figma 커넥터 · 폰트 · 주석 카테고리

**0-1. Figma 커넥터를 먼저 확인한다.** 다른 단계보다 먼저 한다.

- Figma 커넥터 도구가 보이는지, base URL(모드 B면 타겟 파일)의 노드 구조를 읽을 수 있는지 가볍게 읽어 본다
- 연결이 없으면 멈추고 안내한다. Chat · Cowork는 Customize › Connectors에서 Figma를 연결하라고, Code 탭은 같은 계정의 Figma 커넥터를 연결하라고 알린다
- 파일을 읽을 수 없으면 파일 접근 권한을 확인하라고 알리고 멈춘다
- 쓰기 호출이 권한 오류로 실패하면 파일 편집 권한과 주석에 필요한 Dev · Full 시트([references/FIGMA_RULES.md](references/FIGMA_RULES.md) 6-8절)를 확인하라고 알린다

**0-2. 폰트.** Figma 코드 실행 한 줄로 base가 쓰는 폰트가 **로드 가능한지** 확인한다. 이 확인을 건너뛰면 Step 6에서 전량 실패한다.

원본 파일은 `Pretendard`를 쓰는데 Figma가 인식하지 못하는 경우가 실제로 있다(내 컴퓨터에 설치돼 있어도). 결과에 따라:

- **로드 가능** → 기존 텍스트 노드의 `characters`를 직접 교체 (정확)
- **로드 불가** → 사용자에게 먼저 알리고 선택을 받는다:
  - (a) Figma 재시작 / Font Helper 설치 후 재시도 — 권장
  - (b) 대체 폰트로 진행 — 새 텍스트는 `42dot Sans`(이 파일이 이미 쓰는 폰트), 기존 텍스트는 노드 교체 방식. [references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 3절

폰트 문제를 사용자에게 숨기고 대체 폰트로 조용히 진행하지 않는다.

**0-3. 설명 소스를 받았다면 주석 카테고리도 같이 읽는다.** `figma.annotations.getAnnotationCategoriesAsync()`로 그 파일이 실제로 쓰는 카테고리를 확인한다. 카테고리 이름을 지어내지 않는다.

- **같은 이름이 둘 이상이면 사용자에게 확인한다.** 실측 파일에는 `API`가 2개(노랑 `6:4` · 파랑 `1:10`) 있었다. 기존 주석이 실제로 쓴 쪽을 따른다
- 기존 주석이 달린 노드를 몇 개 읽어 **그 파일의 작성 관행**(어떤 카테고리에 어떤 내용을 넣는지)을 파악한다

### Step 1. 입력 파악 · 화면 판별

fileKey·nodeId 추출, 타겟 모드 결정. 타겟이 다른 파일이면 위 제약을 먼저 고지한다.
화면을 판별해 모드 B와 API 주석이 되는지 정하고, 안 되는 것은 이 자리에서 알린다.

**base가 Figma에 없으면 먼저 모드 B로 캡처한다** ([references/MODE_B_CAPTURE.md](references/MODE_B_CAPTURE.md)). 캡처 · 보정이 끝나면 그 프레임을 base로 삼아 Step 3으로 바로 이어간다. 방향이 없으면 캡처 결과 URL을 주고 끝낸다.

### Step 2. 규칙 읽기

FIGMA_RULES.md, CHECKLIST.md. 첫 Figma 코드 실행 전에 FIGMA_RECIPE.md.

### Step 3. 정찰 (읽기 전용 Figma 코드 실행)

**레이어 이름으로는 아무것도 찾을 수 없다.** 캡처 산출물이라 이름이 전부 `Container` / `Text` / `Button` / `Link`다. 반드시 **텍스트 내용을 앵커로** 잡고 조상으로 올라간다 ([references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 2절).

확인할 것:

- base의 부모 체인 (page · section) 과 섹션 로컬 좌표
- 변경 대상마다 앵커 텍스트 → 노드 id · 크기 · 부모 레이아웃(`layoutMode`·`itemSpacing`·`layoutSizing*`)
- 복제할 원본(clone source): 추가하려는 것과 **같은 역할의 기존 요소**. 새 버튼이면 기존 버튼, 새 행이면 기존 행
- 빈 영역 좌표 (섹션 children의 bbox 스캔)
- 폰트·변수 바인딩 상태

정찰 결과를 변경목록의 `대상` 칸에 node-id로 박는다. 추측 금지.

**API 계약 수집** (산출물 C를 만들고, 레포를 연 Code 탭일 때만) → [references/API_CONTRACT.md](references/API_CONTRACT.md)

### Step 4. 방향 → 변경목록(CHG-NN) 정규화

자유 텍스트를 표로 옮긴다. **한 줄 = 한 변경 = 하나의 검증 가능한 결과.**

| ID | 대상 (앵커 → node-id) | 동작 | 내용 | 산출물 | 근거 |
| --- | --- | --- | --- | --- | --- |
| CHG-01 | `수업들` 헤더 Container → `6240:65xxx` | 추가 | 우측에 `[등록 일괄 생성 (n)]` 버튼. 기존 `[수업 추가]` 버튼 clone | A·B | 사용자 방향 |
| CHG-02 | 수업 행 Container → `…` | 수정 | 행 우측에 `등록 있음/없음` 칩 추가 | A·B | 사용자 방향 |

- **동작**은 `추가` / `수정` / `삭제` / `이동` / `교체` 중 하나.
- **산출물**은 `A` / `B` / `A·B`. B에만 들어가는 설명용 변형도 ID를 받는다.
- 방향 텍스트에 없는 것을 채워 넣지 않는다. 필요한데 안 정해진 건 `미결`로 분리해 Step 5에서 묻는다.
- 시안이 여러 개면 `CHG-01-시안1` / `CHG-01-시안2`로 쪼갠다.

**설명 소스를 받았으면 주석 계획도 함께 만든다.**

| ID | 앵커 (노드) | 층 | 카테고리 | 내용 출처 |
| --- | --- | --- | --- | --- |
| ANN-01 | 캡처 루트 → `6287:2` | Annotation | `API` | fetcher `getAtDeunghawons` |
| ANN-02 | 고유 번호 필드 → `6300:259` | Annotation | `API` | fetcher `updateAjJaewonsaeng` 외 3건 |
| DSC-01 | 섹션 오른쪽 (2143, 112) | Description 카드 | — | `<기획 원문>` 2.4 / 2.5절 |
| OVL-01 | 고유 번호 필드 위 | 오버레이 | — | 커넥터 앵커용 |

- `CHG` · `ANN` · `DSC` · `OVL` ID는 승인 게이트와 보고에만 쓴다. **Figma 캔버스(Description 카드 · 주석 · 오버레이 글)에는 넣지 않는다.** 받는 사람에게는 뜻이 없는 내부 번호다.

**기획 원문과 코드가 어긋나면 고치지 말고 짚는다.** 문서가 낡았을 수도, 코드가 틀렸을 수도 있다. 원문은 verbatim으로 옮기고 충돌 사실을 Step 5에서 사용자에게 보고한다 (실측: 원문의 "학원 내부 이름 다음 배치"가 뒤이은 PM 합의로 뒤집혀 있었다).

### Step 5. 승인 게이트 (필수)

사용자에게 묻는다 (질문 도구가 있으면 그것으로). [references/CHECKLIST.md](references/CHECKLIST.md) 1절의 양식을 쓴다.

- 변경목록 CHG-NN이 방향과 맞는가
- 배치 위치(섹션 이름·좌표)가 맞는가
- 미결 답
- write 실행 OK

**승인 없이 Step 6~8 진행 금지.** Step 6·7·8은 전부 write다. 원본 작성자가 자기든 동료든, Figma write는 작업 파일에 대한 mutation이다.

### Step 6. 산출물 A — 전체 clone + 패치

Figma 코드 실행 호출 단위는 **변경목록 3~5건**. 한 번에 다 하지 않는다.

1. base `clone()` → 이름 `<원본명> — [제안] <슬러그>` → 타겟 섹션에 배치
2. CHG-NN 순서대로 패치. 각 패치는 clone-and-modify가 기본 ([references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 3절)
3. 텍스트를 바꿨으면 **컨테이너를 `HUG`로 전환** — 안 하면 고정폭에 라벨이 잘린다
4. `await node.screenshot()`으로 그 자리에서 눈으로 확인
5. 생성·변경된 node id 전부 `return`

### Step 7. 산출물 B — 제안 섹션

구조는 팀 기획안 파일의 관용구를 따른다:

```
[SECTION] 제안 N. <한 줄 제목>
 ├ [SECTION] 시안 1. <설명>        ← h=9 라벨 스트립
 ├ FRAME    시안 1                 ← base에서 절단한 clone
 ├ [SECTION] 시안 2. <설명>
 ├ FRAME    시안 2                 ← 변경 적용본
 ├ VECTOR   <출발> --> <도착>       ← 빨강 2px, 끝점만 ARROW_LINES
 └ FRAME    메모                    ← 노란 박스 + 불릿
```

- 절단 단위는 **설명에 필요한 최소 패널**. 화면 전체를 다시 넣지 않는다
- 화살표 이름은 `<출발 요소> --> <도착 프레임명>` 형식을 지킨다 (팀 기획안 파일 컨벤션)
- 메모는 `왜 이렇게 바꾸는가` · `무엇이 달라지는가` · `남는 것` 세 갈래로 쓴다. 구현 티켓·일정은 적지 않는다

### Step 8. 산출물 C — 설명 레이어

승인된 주석 계획대로 오버레이 → 주석 → Description 카드 순으로 만든다. 레시피는 [references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 8 · 9절.

**8-1. 오버레이** (커넥터를 이을 자리에만) — 설명할 영역을 감싸는 **Frame**. 번호 뱃지를 넣을 수 있고 커넥터 magnet과 주석을 동시에 받기 때문에 Rectangle이 아니라 Frame이다.

- fill 없음 · stroke 빨강 2px · radius 4 · 대상 박스에 상하좌우 4px 여유
- **`layoutPositioning = 'ABSOLUTE'` 필수.** 캡처 내부는 전부 오토레이아웃이라 그냥 넣으면 레이아웃이 밀려 화면이 깨진다
- 부모의 `clipsContent`를 확인한다. false면 테두리가 살짝 넘쳐도 잘리지 않는다

**8-2. 주석** — 앵커 노드에 `node.annotations = [{ categoryId, labelMarkdown }]`를 건다.

- **write 직전에 노드를 다시 찾는다.** 정찰 때 잡은 id가 그사이 바뀌어 있을 수 있다 (8-5 참조)
- 본문은 요청·응답을 나눠 bullet로. 필드명은 백틱, 필수·선택과 형식을 함께 적는다
- 값 필드가 없는 노드(설정 체크리스트 등)는 API 주석 대상이 아니다. 걸러내고 걸렀다고 보고한다

**8-3. Description 카드** — 기획 원문을 Design 모드에서도 읽히게 옮긴다. **그 파일에 이미 Description 프레임이 있으면 스타일을 실측해 복제한다** — 추측으로 만들지 않는다. 실측 관행 값은 [references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 9-1절.

- 테두리 색은 직접 지정하지 말고 **기존 카드가 쓰는 변수에 바인딩**한다
- Description 프레임은 대개 **Inter**라 Pretendard 문제와 무관하다. 텍스트가 정확히 렌더된다
- 마크다운 표는 Figma에서 표현이 어려우므로 평문으로 편다. **구조만 바꾸고 내용은 원문 그대로**, 그리고 폈다는 사실을 보고한다
- 출처를 제목 아래 12px 회색 한 줄로 남긴다

**8-4. 커넥터는 수기** — Plugin API가 design mode에서 `CONNECTOR` 생성을 막는다. 스킬은 앵커까지 만들고 연결은 사용자가 한다.

- 보고에 **"커넥터만 수기"**를 명시하고, 이을 대상 쌍을 알려준다
- 그 파일의 기존 커넥터를 복사해 양 끝을 드래그하는 방법이 가장 확실하다 (실측 스펙: `CURVED` · 회색 4px · 끝점만 `ARROW_LINES` · 이름 `<출발> --> <도착>`)

**8-5. 노드 id는 write 시점에 다시 찾는다** — 사용자가 캡처를 옮기거나 이름을 바꾸면 **id가 새로 발급된다.** 정찰 때 박아둔 id로 바로 쓰면 `cannot set property of null`이 나고, Figma 코드 실행은 에러 시 **그 호출 전체를 롤백**하므로 같은 호출에서 이미 성공한 주석까지 사라진다.

- 앵커는 **텍스트 내용으로 다시 찾고** 조상으로 올라간다
- 대상마다 `if (!node) { skipped.push(...); continue; }` 가드를 둔다. 하나가 없다고 전체를 잃지 않는다

### Step 9. 검증 + 보고

[references/CHECKLIST.md](references/CHECKLIST.md) 2절을 돌린다. 보고는 높임말로, 아래 순서로 쓴다. 맨 앞에 쓰는 ID의 범례를 둔다.

- **판단할 것**: 남은 미결, 기획 원문과 코드의 충돌
- **확인할 것**
  - 커넥터로 이을 쌍 목록 (수기 작업으로 남긴 것)
  - **주석은 Dev Mode(`Shift+D`)에서만 보인다**는 안내 — 처음 받는 사람은 반드시 막힌다
  - 폰트 대체를 썼다면 그 사실과 영향 범위
  - API 주석을 뺐다면 그 이유와 붙이는 방법
  - 원문에서 구조를 편 부분
  - 실패 · 중단이 있었으면 잔재 노드 id
- **참고**: 생성된 노드 URL (`https://www.figma.com/design/<fileKey>/?node-id=<id>`), 변경목록 CHG-NN별 반영 여부 (미반영이면 사유)

## 도구 사용 규칙

- 도구는 이름이 아니라 동작으로 찾는다. 동작과 지금 알려진 이름의 대응은 [references/FIGMA_RECIPE.md](references/FIGMA_RECIPE.md) 0절
- Figma 읽기: 노드 구조 읽기 · 스크린샷 · 읽기 전용 코드 실행
- Figma 쓰기: 코드 실행 (Step 5 승인 후에만). `figma-use` 스킬이 있으면 먼저 불러온다. 없으면 FIGMA_RECIPE.md 0절 호출 규약을 따른다. 코드 실행 도구가 스킬 이름을 받으면 `screen-to-hifi`를 넘긴다
- 코드 읽기 (API 계약 수집): 코드 읽기 · 검색. 결과는 **스키마 원문**이어야 한다
- 기획 원문 읽기 — 받은 원문을 verbatim으로 옮긴다
  - gist: raw 주소를 웹 가져오기로 읽는다
  - 구글 문서 · 노션: 해당 커넥터가 연결돼 있으면 커넥터로, 없으면 웹 가져오기를 시도한다
  - 못 읽으면 원문을 붙여 넣거나 파일로 올려 달라고 한다. 요약본을 받지 않는다
- subagent 금지. 정찰·패치 모두 직접 한다
- 실패 시 즉시 보고. 부분 생성분의 node id를 제시하고 정리 여부를 묻는다 (자동 삭제 금지)
