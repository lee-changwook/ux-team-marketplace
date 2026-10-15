# Figma Recipe (Figma 코드 실행 레시피)

**이 파일의 코드는 전부 대상 파일에서 실행해 통과시킨 것이다.** 임의로 고치지 말고, 고쳐야 하면 먼저 작은 스모크로 돌려보고 결과를 이 파일에 반영한다.

`figma-use` 스킬이 있으면 호출 전에 먼저 불러온다. 없으면 아래 0절 호출 규약을 따른다. 코드 실행 도구가 스킬 이름을 받으면 `screen-to-hifi`를 넘긴다.

---

## 0. 호출 규약

도구는 이름이 아니라 동작으로 찾는다. 이름은 화면과 시기마다 다를 수 있다. 아래 이름은 지금 알려진 예시이고, 보이지 않으면 동작 칸으로 찾는다.

| 동작 | 지금 알려진 이름 (예시) |
| ---- | ----------------------- |
| Figma 코드 실행 (Plugin API, 읽기 · 쓰기) | `use_figma` |
| Figma 화면 캡처 (HTML → 디자인) | `generate_figma_design` |
| Figma 노드 구조 읽기 · 스크린샷 | `get_metadata` · `get_screenshot` |
| 브라우저의 페이지 스크립트 실행 (Code 탭) | Claude in Chrome의 `javascript_tool` |
| 사용자에게 묻기 | `AskUserQuestion` (Code 탭) |

- 코드는 **top-level `await` + `return`**. async IIFE로 감싸지 않는다
- `console.log`는 돌아오지 않는다. 결과는 `return`
- 색은 0~1 범위
- 페이지 전환은 `await figma.setCurrentPageAsync(page)`, **호출당 한 번**
- 한 호출 = 변경목록 3~5건. 그 이상이면 쪼갠다
- 생성·변경한 node id를 **전부** `return`

## 1. 프리앰블 — 폰트 확보

Step 0 preflight와 모든 write 호출의 첫머리에 넣는다.

```js
// 원본 폰트를 우선 시도하고, 안 되면 이 파일이 이미 쓰는 42dot Sans로 내려앉는다.
async function ensureFonts() {
  const want = {
    bold: { family: 'Pretendard', style: 'SemiBold' },
    med:  { family: 'Pretendard', style: 'Medium' },
    reg:  { family: 'Pretendard', style: 'Regular' },
  };
  try {
    for (const k of Object.keys(want)) await figma.loadFontAsync(want[k]);
    return { fonts: want, fallback: false };
  } catch (e) {
    const fb = {
      bold: { family: '42dot Sans', style: 'SemiBold' },
      med:  { family: '42dot Sans', style: 'Medium' },
      reg:  { family: '42dot Sans', style: 'Regular' },
    };
    for (const k of Object.keys(fb)) await figma.loadFontAsync(fb[k]);
    return { fonts: fb, fallback: true, reason: String(e && e.message || e) };
  }
}
```

`fallback: true`가 나오면 **사용자에게 먼저 알리고 선택을 받는다.** 조용히 진행하지 않는다.

## 2. 노드 찾기 — 텍스트가 앵커다

```js
// 화면 텍스트로 TEXT 노드를 잡는다.
function byText(root, matcher) {
  const re = matcher instanceof RegExp ? matcher : null;
  return root.findAll(n => n.type === 'TEXT' && (re ? re.test(n.characters) : n.characters === matcher));
}

// 앵커에서 조상으로 올라가며 조건에 맞는 프레임을 잡는다.
function ancestorWhere(node, pred, stopAt) {
  let p = node.parent;
  while (p && (!stopAt || p.id !== stopAt.id)) { if (pred(p)) return p; p = p.parent; }
  return null;
}

// 흔한 용법: 앵커를 품은 "패널" 크기의 프레임
function panelOf(anchor, root, min = 300, max = 700) {
  return ancestorWhere(anchor, p => p.type === 'FRAME' && p.width >= min && p.width <= max && p.height >= min, root);
}

// 라벨로 기존 버튼(= clone source) 찾기
function buttonByLabel(root, label) {
  return root.findAll(n =>
    n.type === 'FRAME' && n.name === 'Button' &&
    n.findAll(x => 'characters' in x && x.characters === label).length > 0
  )[0];
}
```

정찰 단계에서 이걸로 찾은 **node-id를 변경목록에 박아두고**, write 호출에서는 그 id로 먼저 `getNodeByIdAsync`를 시도한다. `null`이면 텍스트 앵커로 다시 찾는다 (id 재발급, [FIGMA_RULES.md](FIGMA_RULES.md) 6-9절). **패치 대상은 언제나 clone본 안에서 찾는다** — 원본에서 찾으면 원본을 고치게 된다.

## 3. 패치 프리미티브

### 3-1. 텍스트 교체 — 두 경로

```js
// (A) 원본 폰트가 로드되는 경우: 노드를 그대로 두고 characters만 바꾼다.
async function setTextDirect(textNode, str) {
  for (const seg of textNode.getStyledTextSegments(['fontName'])) await figma.loadFontAsync(seg.fontName);
  textNode.characters = str;
  return textNode;
}

// (B) 원본 폰트가 없는 경우: 스타일을 복사한 새 TEXT로 교체한다.
//     fills / fontSize / name / lineHeight 를 옮기면 눈으로는 구분되지 않는다.
function replaceText(textNode, str, font) {
  const parent = textNode.parent;
  const idx = parent.children.indexOf(textNode);
  const fresh = figma.createText();
  fresh.fontName = font;
  fresh.characters = str;
  if (typeof textNode.fontSize === 'number') fresh.fontSize = textNode.fontSize;
  fresh.fills = textNode.fills;
  fresh.name = textNode.name;
  try { if (textNode.lineHeight && textNode.lineHeight.unit) fresh.lineHeight = textNode.lineHeight; } catch (e) {}
  parent.insertChild(idx, fresh);
  textNode.remove();
  return fresh;
}
```

**교체 직후 반드시 컨테이너를 HUG로 전환한다.** 안 하면 고정폭에 잘린다 (실측 54px 안에 88px 텍스트).

```js
function hugIfAutoLayout(frame) {
  if (frame && frame.layoutMode && frame.layoutMode !== 'NONE') frame.layoutSizingHorizontal = 'HUG';
}
```

### 3-2. 요소 추가 — 같은 역할의 기존 요소를 복제한다

```js
// 기존 버튼을 복제해 라벨만 바꿔 같은 줄에 끼운다.
async function addButtonLike(srcButton, holder, label, font, fallback) {
  const btn = srcButton.clone();
  const t = btn.findAll(n => n.type === 'TEXT')[0];
  if (fallback) replaceText(t, label, font.med); else await setTextDirect(t, label);
  holder.appendChild(btn);        // 오토레이아웃이면 위치는 부모가 잡는다
  hugIfAutoLayout(btn);
  return btn;
}
```

행·칩·필드도 같은 방식이다. **추가하려는 것과 같은 역할의 형제를 찾아 복제한다.** 없으면 만들지 말고 미결로 올린다.

### 3-3. 삭제 · 이동

```js
function moveInto(node, newParent, index) {
  if (typeof index === 'number') newParent.insertChild(index, node); else newParent.appendChild(node);
}
// 삭제는 node.remove(). 단 clone본 위에서만. 원본 프레임은 건드리지 않는다.
```

## 4. 산출물 A — 전체 clone + 패치

```js
const base = await figma.getNodeByIdAsync('BASE_NODE_ID');
const page = base.parent.parent;            // FRAME -> SECTION -> PAGE (정찰에서 확인한 실제 체인을 쓴다)
await figma.setCurrentPageAsync(page);
const F = await ensureFonts();

const hifi = base.clone();
hifi.name = base.name + ' — [제안] SLUG';
TARGET_SECTION.appendChild(hifi);
hifi.x = X; hifi.y = Y;                     // 섹션 로컬 좌표

const created = [hifi.id];
const applied = {};

// CHG-01 …
const anchor = byText(hifi, '수업들')[0];
const holder = anchor.parent;
const src = buttonByLabel(hifi, '수업 추가');
const btn = await addButtonLike(src, holder, '등록 일괄 생성 (3)', F.fonts, F.fallback);
created.push(btn.id); applied['CHG-01'] = btn.id;

await hifi.screenshot();
return { createdNodeIds: created, applied, fallback: F.fallback };
```

**패치 대상은 반드시 `hifi`(clone본) 안에서 찾는다.** `base`에서 찾으면 원본을 고치게 된다.

## 5. 산출물 B — 제안 섹션

### 5-1. 섹션과 라벨 스트립

```js
const sec = figma.createSection();
sec.name = '[<작성자> 제안] <MMDD> <주제>';
page.appendChild(sec);
sec.x = X; sec.y = Y;
sec.resizeWithoutConstraints(1500, 1100);   // resize()가 아니라 이것

// 시안 제목은 h=9 얇은 섹션을 라벨로 쓴다 (팀 기획안 파일 관용구)
function labelStrip(parent, name, x, y, w) {
  const s = figma.createSection();
  s.name = name;
  parent.appendChild(s);
  s.x = x; s.y = y;
  s.resizeWithoutConstraints(w, 9);
  return s;
}
```

### 5-2. 절단 시안

```js
// 설명에 필요한 최소 패널만 잘라낸다. 화면 전체를 다시 넣지 않는다.
const anchor = byText(base, '수업들')[0];
const panel = panelOf(anchor, base);        // 실측 381x453
const sian1 = panel.clone();
sian1.name = '시안 1. <구분 기준>';
sec.appendChild(sian1); sian1.x = 40; sian1.y = 60;

const sian2 = panel.clone();
sian2.name = '시안 2. <구분 기준>';
sec.appendChild(sian2); sian2.x = 40; sian2.y = 620;
// sian2에 변경 적용 (3-1 ~ 3-3)
```

### 5-3. 화살표 (CONNECTOR 아님)

```js
// pts: 섹션 로컬 기준 꺾임점 배열. 마지막 점에만 화살촉이 붙는다.
async function arrow(parent, pts, name, x, y) {
  const v = figma.createVector();
  v.name = name;                                     // '<출발> --> <도착>'
  v.strokes = [{ type: 'SOLID', color: { r: 1, g: 0, b: 0 } }];
  v.strokeWeight = 2;
  parent.appendChild(v);
  await v.setVectorNetworkAsync({
    vertices: pts.map((p, i) => (i === pts.length - 1
      ? { x: p.x, y: p.y, strokeCap: 'ARROW_LINES' }
      : { x: p.x, y: p.y, strokeCap: 'ROUND' })),
    segments: pts.slice(1).map((_, i) => ({ start: i, end: i + 1 })),
    regions: [],
  });
  v.x = x; v.y = y;                                  // setVectorNetworkAsync 이후에 배치
  return v;
}

// ㄱ자 2번 꺾임 예시 (실측 320x240)
await arrow(sec, [{x:0,y:0},{x:160,y:0},{x:160,y:240},{x:320,y:240}],
            'Button 등록 일괄 생성 --> [Modal] 등록 생성하기', 760, 90);
```

### 5-4. 메모 박스

```js
async function memo(parent, title, bullets, x, y, w, F) {
  const box = figma.createAutoLayout('VERTICAL', { name: '메모', itemSpacing: 8 });
  box.fills = [{ type: 'SOLID', color: { r: 1, g: 0.984, b: 0.902 } }];
  box.strokes = [{ type: 'SOLID', color: { r: 0.949, g: 0.855, b: 0.553 } }];
  box.cornerRadius = 8;
  box.paddingTop = box.paddingBottom = box.paddingLeft = box.paddingRight = 16;
  parent.appendChild(box);
  box.x = x; box.y = y;
  box.layoutSizingHorizontal = 'FIXED';
  box.resize(w, box.height);

  const h = figma.createText(); h.fontName = F.fonts.bold; h.characters = title; h.fontSize = 14;
  box.appendChild(h);
  for (const b of bullets) {
    const t = figma.createText(); t.fontName = F.fonts.reg; t.characters = '• ' + b; t.fontSize = 12;
    box.appendChild(t);
    t.layoutSizingHorizontal = 'FILL';
    t.textAutoResize = 'HEIGHT';          // 둘 다 해야 한글이 흐른다
  }
  return box;
}
```

`FILL`은 **appendChild 다음에** 설정한다. `textAutoResize = 'HEIGHT'`를 빼면 한 줄로 늘어나 폭을 뚫는다.

## 6. 빈 영역 찾기

```js
let maxX = 0;
for (const c of page.children) { const r = (c.x ?? 0) + (c.width ?? 0); if (r > maxX) maxX = r; }
const X = Math.round(maxX + 800);   // 기존 작업물과 겹치지 않게 넉넉히
```

섹션 안에 넣을 때는 그 섹션의 children으로 같은 계산을 한다. 좌표는 **승인 게이트에서 사용자에게 보여주고** 확인받는다.

## 7. 검증 · 정리

```js
await node.screenshot();                    // 호출 안에서 바로 눈으로 확인
await node.screenshot({ scale: 3 });        // 라벨 잘림 같은 미세 확인
```

실패한 호출 뒤 잔재 정리:

```js
const prefix = '[제안 작업중]';
const hits = figma.currentPage.findAll(n => typeof n.name === 'string' && n.name.indexOf(prefix) >= 0);
const removed = hits.map(n => ({ id: n.id, name: n.name }));
for (const n of hits) n.remove();
return { removed, pageChildCount: figma.currentPage.children.length };
```

**자동 삭제는 자기가 만든 prefix 노드에만 한다.** 원본 작성자의 노드는 어떤 경우에도 지우지 않는다.

---

## 8. 설명 레이어 — 주석

### 8-1. 카테고리 조회 (지어내지 않는다)

```js
const cats = await figma.annotations.getAnnotationCategoriesAsync();
return cats.map(c => ({ id: c.id, label: c.label, color: c.color, isPreset: c.isPreset }));
```

실측 파일은 14개를 갖고 있었고 그중 `API`가 **둘**이었다 (`6:4` 노랑 · `1:10` 파랑). 기존 주석이 실제로 쓴 쪽을 따른다 — 파일에서 이미 달린 주석을 몇 개 읽어 확인한다.

```js
// 그 파일의 작성 관행 파악: 이미 주석이 달린 노드 훑기
const annotated = page.findAll(n => { try { return Array.isArray(n.annotations) && n.annotations.length; } catch (e) { return false; } });
return annotated.slice(0, 15).map(n => ({
  name: n.name, type: n.type,
  ann: n.annotations.map(a => ({ categoryId: a.categoryId, label: (a.labelMarkdown || '').slice(0, 80) })),
}));
```

### 8-2. 오버레이 — Frame + ABSOLUTE

```js
function overlay(parent, box, name) {
  const f = figma.createFrame();
  f.name = name;                                  // 'Overlay — 고유 번호'
  f.fills = [];                                    // 비워야 아래 내용이 비친다
  f.strokes = [{ type: 'SOLID', color: { r: 1, g: 0, b: 0 } }];
  f.strokeWeight = 2;
  f.cornerRadius = 4;
  parent.appendChild(f);
  f.layoutPositioning = 'ABSOLUTE';                // 없으면 오토레이아웃이 밀려 화면이 깨진다
  f.x = box.x - 4; f.y = box.y - 4;
  f.resize(box.w + 8, box.h + 8);
  return f;
}
```

`box`는 **부모 기준 상대 좌표**다. 캡처 루트 기준으로 쟀다면 이렇게 환산한다.

```js
const rel = (node, root) => ({
  x: Math.round(node.absoluteTransform[0][2] - root.absoluteTransform[0][2]),
  y: Math.round(node.absoluteTransform[1][2] - root.absoluteTransform[1][2]),
  w: Math.round(node.width), h: Math.round(node.height),
});
```

### 8-3. 주석 부착 — 재탐색 + 가드

**정찰 때 잡은 id를 그대로 쓰지 않는다.** 사용자가 캡처를 옮기거나 이름을 바꾸면 id가 새로 발급되고, `null`에 쓰면 그 호출 전체가 롤백되어 **같은 호출에서 이미 성공한 주석까지 사라진다.**

```js
const applied = [], skipped = [];

const cap = page.findAll(n => n.type === 'FRAME' && /전체 처리/.test(n.name) && n.width > 1500)[0];
if (!cap) skipped.push('capture not found');
else {
  for (const l of cap.findAll(n => 'characters' in n && n.characters === '고유 번호')) {
    // 라벨 + 값을 함께 품는 래퍼까지 올라간다
    let f = l.parent;
    while (f && f.id !== cap.id && f.height < 40) f = f.parent;
    if (!f || f.id === cap.id) { skipped.push('wrapper not found for ' + l.id); continue; }

    // 값 필드가 없는 곳(설정 체크리스트 등)은 API 주석 대상이 아니다
    const hasValue = f.findAll(n => 'characters' in n && /^\d{4,10}$/.test(n.characters)).length > 0;
    if (!hasValue) { skipped.push('no value field under ' + f.id); continue; }

    f.annotations = [{ categoryId: API_ID, labelMarkdown: BODY }];
    applied.push({ id: f.id, w: Math.round(f.width), h: Math.round(f.height) });
  }
}
return { applied, skipped };
```

본문 양식(요청·응답을 나눈 bullet, 필드명은 백틱)은 [API_CONTRACT.md](API_CONTRACT.md) "주석 본문 양식"을 따른다. API 주석은 레포를 연 Code 탭에서만 만든다.

부착 뒤에는 **별도 호출로 확인한다.** 앞 호출이 롤백됐는지 알 수 있는 유일한 방법이다.

```js
for (const id of ids) {
  const n = await figma.getNodeByIdAsync(id);
  rows.push({ id, count: (n && n.annotations || []).length, cat: n && n.annotations[0] && n.annotations[0].categoryId });
}
```

## 9. 설명 레이어 — Description 카드

### 9-1. 관행을 실측해 복제한다

그 파일에 Description 프레임이 이미 있으면 **스타일을 읽어 그대로 쓴다.** 추측으로 만들면 카드 배경·테두리·lineHeight가 어긋난다(실제로 한 번 어긋나 재작업했다).

```js
const conv = await figma.getNodeByIdAsync(CONVENTION_ID);
const card = conv.findAll(n => n.name === 'description sample')[0];
return {
  root: { w: conv.width, padding: conv.paddingTop, itemSpacing: conv.itemSpacing, fills: JSON.stringify(conv.fills) },
  card: { fills: JSON.stringify(card.fills), strokes: JSON.stringify(card.strokes), radius: card.cornerRadius, padding: card.paddingTop, strokeAlign: card.strokeAlign },
  title: { size: conv.children[0].fontSize, lineHeight: JSON.stringify(conv.children[0].lineHeight) },
};
```

실측값 (`1471:2213`): 930폭 · padding 40 · itemSpacing 16 · 흰 배경 / 제목 Inter **Bold 31** → 소제목 **Bold 16** → 본문 **Regular 14** / **본문만 lineHeight 150%, 제목·소제목은 AUTO** / 카드 `#F7F7F7` · 테두리 `#C9CCD6` 1px **변수 바인딩** · radius 4 · padding 16 · strokeAlign INSIDE.

### 9-2. 생성

```js
const BOLD = { family: 'Inter', style: 'Bold' };
const REG  = { family: 'Inter', style: 'Regular' };
await figma.loadFontAsync(BOLD); await figma.loadFontAsync(REG);
const LH = { unit: 'PERCENT', value: 150 };

const mkText = (parent, chars, font, size, color) => {
  const t = figma.createText();
  t.fontName = font; t.fontSize = size; t.characters = chars;
  if (color) t.fills = [{ type: 'SOLID', color }];
  parent.appendChild(t);
  t.layoutSizingHorizontal = 'FILL';     // appendChild 다음에
  t.textAutoResize = 'HEIGHT';           // 둘 다 해야 한글이 흐른다
  if (size < 16) t.lineHeight = LH;      // 본문만 150%
  return t;
};

const root = figma.createAutoLayout('VERTICAL', { name: 'Description', itemSpacing: 16 });
root.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];
root.paddingTop = root.paddingBottom = root.paddingLeft = root.paddingRight = 40;
host.appendChild(root);
root.x = X; root.y = Y;
root.layoutSizingHorizontal = 'FIXED';
root.resize(930, root.height);

mkText(root, 'Description - <대상>', BOLD, 31);
mkText(root, '출처: <문서> · <절 번호>', REG, 12, { r: 0.45, g: 0.45, b: 0.45 });

const body = figma.createAutoLayout('VERTICAL', { name: 'Description', itemSpacing: 8 });
body.fills = []; body.paddingTop = body.paddingBottom = 10;
root.appendChild(body); body.layoutSizingHorizontal = 'FILL';

// 카드 스타일 — 테두리는 기존 변수에 바인딩
const strokeVar = await figma.variables.getVariableByIdAsync(STROKE_VAR_ID);
const strokePaint = () => {
  let p = { type: 'SOLID', color: { r: 0.788, g: 0.800, b: 0.839 } };
  if (strokeVar) { try { p = figma.variables.setBoundVariableForPaint(p, 'color', strokeVar); } catch (e) {} }
  return p;
};

const group = (title, text) => {
  const g = figma.createAutoLayout('VERTICAL', { name: 'description sample', itemSpacing: 8 });
  g.fills = [{ type: 'SOLID', color: { r: 0.9686, g: 0.9686, b: 0.9686 } }];
  g.strokes = [strokePaint()];
  g.strokeWeight = 1; g.strokeAlign = 'INSIDE'; g.cornerRadius = 4;
  g.paddingTop = g.paddingBottom = g.paddingLeft = g.paddingRight = 16;
  body.appendChild(g); g.layoutSizingHorizontal = 'FILL';
  mkText(g, title, BOLD, 16);
  mkText(g, text, REG, 14);
  return g;
};
```

본문은 markdown 불릿 기호(`- `)를 떼고 **줄바꿈으로** 넣는다. 이 파일의 관행이 그렇다. 표는 평문으로 편다 — 구조만 바꾸고 내용은 원문 그대로 두고, 폈다는 사실을 보고한다.

### 9-3. 고려사항 블록 (있을 때)

관행 파일은 `FE/BE/EVE 고려사항`을 색 카드로 분리한다. 공통: 테두리 `#DFDFDF` 1px · radius 4 · padding 4 · HORIZONTAL · itemSpacing 10, 안쪽은 `라벨(Bold 14, 폭 72~83)` + `본문(Regular 14, 폭 727~728)`.

| 블록 | 배경 |
| ---- | ---- |
| FE 고려사항 | `#FDF6D4` |
| BE 고려사항 | `#E4F7E4` |

## 10. 커넥터 — 만들 수 없다

design mode에서 `CONNECTOR` 생성은 Plugin API가 막는다. 스킬은 앵커(오버레이·프레임)까지 만들고 **연결은 사용자가 수기로** 한다.

사용자에게 알릴 것:

- 이을 **대상 쌍** 목록 (출발 노드 → 도착 노드)
- 그 파일의 기존 커넥터를 **복사해서** 양 끝을 드래그하는 게 가장 확실하다는 것
- 실측 스펙: `CURVED` · 회색 `#757575` 4px · 시작 `NONE` / 끝 `ARROW_LINES` · 이름 `<출발> --> <도착>` · 커넥터 자체에 `text` 라벨을 넣을 수 있다

5-3절의 빨강 VECTOR 화살표는 **커넥터의 대체재**다. 노드에 붙지 않아 옮기면 따라오지 않지만, 스킬이 만들 수 있는 유일한 연결선이다. 팀 기획안 파일도 이 방식을 쓴다.
