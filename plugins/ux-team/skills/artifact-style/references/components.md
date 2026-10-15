# 페이지 뼈대와 컴포넌트

UX팀 문서 두 편(팀 파이프라인, 하네스 세팅)의 레이아웃과 구조를 가져와 색만 팀 토큰으로 바꿨다.
아래 CSS는 `var(--…)`만 쓴다. 색값을 새로 적지 않는다.

## 목차
1. 페이지 뼈대
2. 머리 (eyebrow · 제목 · 리드 · 요점 카드)
3. 섹션과 카드
4. 칩
5. 표
6. 범례와 스와치
7. 콜아웃과 경고
8. 사람 색
9. 옅은 바탕 만들기
10. 선택: 오른쪽 목차, 체크리스트
11. 쓰지 않는 것

## 1. 페이지 뼈대

`/* tokens.css */` 자리에 `references/_shared/tokens.css`를 **처음부터 끝까지 그대로** 붙인다.
값을 골라 옮기거나 고치지 않는다. 다크 모드 구조, `box-sizing` 리셋, `word-break: keep-all`이 그 안에 들어 있다.

```html
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>문서 이름</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans+KR:wght@400;500;600;700&display=swap">
<style>
/* tokens.css */

/* Layout: 이 페이지가 어떤 순서로 읽히는지 한 줄로 적는다. */
body { margin: 0; font-size: 14.5px; }
.page { max-width: 1120px; margin-inline: auto; padding-inline: 16px; padding-block: 32px 72px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 48px; }
h1, h2, h3, h4 { margin: 0; text-wrap: balance; }
p { margin: 0; }
a { color: inherit; text-underline-offset: 3px; }
a:focus-visible, button:focus-visible, input:focus-visible, .table-wrap:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
code { font-family: var(--font-mono); font-size: .9em; background: var(--bg); border: 1px solid var(--rule); border-radius: 4px; padding: 0 4px; overflow-wrap: anywhere; }
</style>
</head>
<body>
<main class="page">
  <header class="head">…</header>
  <section class="block" id="decide">…</section>
  <footer class="foot">…</footer>
</main>
</body>
</html>
```

- 제목(`<title>`)은 두세 단어 이름으로 둔다. 버전 표기를 넣지 않는다.
- 폭이 좁은 화면에서 좌우 여백은 16px이다.

## 2. 머리

결론이 머리에 온다.
`lede`에는 이 문서가 무엇을 정하는지, `thesis` 카드에는 판단할 것 · 확인할 것을 둔다.

```html
<header class="head">
  <p class="eyebrow">UX팀 · <프로젝트 이름></p>
  <h1><결론 한 줄. 결론이 아직 없으면 무엇을 정하는 문서인지></h1>
  <p class="lede"><이 문서가 무엇인지 한 문장>.<br><언제까지 무엇을 정하는지 한 문장>.</p>
  <div class="thesis">
    <div><span class="k">판단할 것</span><p><정할 것></p></div>
    <div><span class="k">확인할 것</span><p><확인할 것></p></div>
    <div><span class="k">참고</span><p><근거 자료></p></div>
  </div>
</header>
```

```css
.head { display: grid; grid-template-columns: minmax(0, 1fr); gap: 18px; }
.eyebrow { font-size: 12px; letter-spacing: .02em; color: var(--muted); }
.head h1 { font-size: clamp(26px, 4vw, 40px); font-weight: 700; letter-spacing: -0.01em; line-height: 1.25; }
.lede { font-size: 17px; max-width: 50em; text-wrap: pretty; }
.thesis { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.thesis > div { background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius-card); padding: 12px 14px; display: grid; gap: 4px; align-content: start; min-width: 0; }
.thesis .k { font-size: 11px; letter-spacing: .02em; color: var(--muted); }
.thesis ul { margin: 0; padding-left: 18px; display: grid; gap: 2px; }
```

- 예시의 `<…>` 자리는 요청에서 채운다. 예시 문구를 그대로 쓰지 않는다.
- `eyebrow` · `.k` 같은 한글 라벨은 본문 서체로 둔다. mono로 두지 않는다.

## 3. 섹션과 카드

```css
section.block { display: grid; grid-template-columns: minmax(0, 1fr); gap: 14px; scroll-margin-top: 16px; }
section.block > h2 { font-size: 22px; font-weight: 700; letter-spacing: -0.01em; }
.sub { color: var(--muted); max-width: 70ch; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
.card { background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius-card); padding: 12px 14px 14px; display: grid; gap: 8px; align-content: start; min-width: 0; }
.card h3 { font-size: 15px; font-weight: 600; }
.card ul { margin: 0; padding-left: 18px; display: grid; gap: 4px; font-size: 13.5px; }
.card.key { border: 1.5px solid var(--ink); }
.foot { font-size: 12.5px; color: var(--muted); border-top: 1px solid var(--rule); padding-top: 14px; display: grid; gap: 6px; }
```

- 강조할 카드 하나는 `.key`(진한 테두리)로 둔다. 강조색은 한 화면에 한두 곳만 쓴다.
- 꼬리(`.foot`)에는 근거 링크와 관련 문서를 둔다. "고칠 때마다 같은 링크에 다시 올립니다."를 적어 두면 좋다.

## 4. 칩

결정 상태는 채움(합의) · 테두리(논의 중) · 점선(제안) · 옅은 회색 바탕(미결)으로 구분한다. 색이 아니라 모양으로 나눈다.

```html
<p class="row">
  <span class="chip chip-agree">합의</span>
  <span class="chip chip-talk">논의 중</span>
  <span class="chip chip-prop">제안</span>
  <span class="chip chip-open">미결</span>
</p>
```

```css
.row { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.chip { display: inline-block; justify-self: start; font-size: 11px; font-weight: 500; border-radius: var(--radius-chip); padding: 0 7px; line-height: 18px; white-space: nowrap; }
.chip-agree { background: var(--ink); color: var(--bg); border: 1px solid var(--ink); }
.chip-talk { border: 1px solid var(--ink); color: var(--ink); }
.chip-prop { border: 1px dashed var(--muted); color: var(--muted); }
.chip-open { background: var(--hatch); border: 1px solid var(--rule); color: var(--ink); }
.chip-accent { background: var(--accent-soft); color: var(--accent-ink); border: 1px solid var(--accent); }
```

- 칩은 `.row`나 문장 안에 둔다. grid 바로 아래에 두면 한 줄 전체로 늘어나므로 `justify-self: start`를 넣어 두었다.
- 칩 글자가 한글이면 본문 서체, 코드 · 번호(`CRS-03` 같은)면 `font-family: var(--font-mono)`를 더한다.

## 5. 표

표는 가로 스크롤 감싸개 안에 두고 최소 폭을 준다.
감싸개가 grid 안에 있으면 그 grid 트랙이 `minmax(0, 1fr)`인지 본다 (`pitfalls.md` 2번).

```html
<div class="table-wrap" tabindex="0" role="region" aria-label="화면별 위치">
  <table>…</table>
</div>
```

```css
.table-wrap { overflow-x: auto; border: 1px solid var(--rule); border-radius: var(--radius-card); background: var(--surface); }
table { border-collapse: collapse; width: 100%; min-width: 720px; font-size: 13px; } /* 열이 적으면 열당 160px 안팎으로 줄인다 */
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--rule); vertical-align: top; }
thead th { font-weight: 600; font-size: 12px; color: var(--muted); background: var(--bg); }
tr:last-child th, tr:last-child td { border-bottom: 0; }
td.code { font-family: var(--font-mono); font-weight: 600; white-space: nowrap; }
```

## 6. 범례와 스와치

스와치 클래스는 `sw-` 접두어로 시작한다. 큰 컴포넌트 클래스(`.step`, `.chip`)를 그대로 쓰지 않는다 (`pitfalls.md` 3번).

```html
<p class="legend">
  <span><i class="sw sw-solid"></i>합의</span>
  <span><i class="sw sw-dash"></i>제안</span>
  <span><i class="sw sw-warn"></i>끊김</span>
</p>
```

```css
.legend { display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 12.5px; color: var(--muted); align-items: center; }
.legend span { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.sw { display: inline-block; flex: none; width: 22px; height: 14px; border-radius: 4px; background: var(--surface); }
.sw-solid { border: 1.5px solid var(--ink); }
.sw-dash { border: 1.5px dashed var(--ink); }
.sw-warn { border: 1.5px dashed var(--warn); }
.sw-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--c, var(--muted)); }
```

## 7. 콜아웃과 경고

```html
<div class="callout"><strong>먼저 정할 것</strong><p><이것을 정해야 다음 일을 할 수 있다는 한 문장></p></div>
<div class="warn"><b>끊김</b><무엇이 어디서 끊겼는지 한 문장></div>
```

```css
.callout { display: grid; gap: 4px; border: 1.5px dashed var(--ink); border-radius: var(--radius-card); padding: 12px 14px; background: var(--surface); }
.callout p { font-size: 13.5px; color: var(--muted); }
.warn { border: 1.5px dashed var(--warn); color: var(--warn); background: var(--surface); border-radius: 8px; padding: 6px 10px; font-size: 12.5px; }
.warn b { font-weight: 600; margin-right: 6px; }
```

- 경고는 점선 테두리와 글자 라벨을 함께 쓴다. 라벨은 문제를 두 글자로 이름 붙인다 (예: "끊김", "빠짐", "충돌", "섞임", "중복"). 색만으로 경고를 나타내지 않는다 (`pitfalls.md` 7번).

## 8. 사람 색

사람 색은 창욱 · 유진 · 주은을 표시할 때만 쓴다. 꾸밈이나 분류 색으로 쓰지 않는다.
아래 `.person-card`는 카드 제목이 사람 이름일 때 쓴다. 안건 카드에 담당자를 붙일 때는 이름 글자(`.owner`)에만 사람 색을 쓴다.
클래스 하나가 `--c`(선 · 테두리)와 `--c-ink`(글자)를 바꾸고, 컴포넌트는 `--c`만 본다.

```css
.cw { --c: var(--line-cw); --c-ink: var(--line-cw-ink); }
.yu { --c: var(--line-yu); --c-ink: var(--line-yu-ink); }
.ju { --c: var(--line-ju); --c-ink: var(--line-ju-ink); }
.person-card { background: var(--surface); border: 1px solid var(--rule); border-top: 4px solid var(--c); border-radius: 10px; padding: 12px 14px; display: grid; gap: 8px; min-width: 0; }
.person-card h3 { font-size: 15px; color: var(--c-ink); }
.owner { font-weight: 600; color: var(--c-ink); }
```

## 9. 옅은 바탕 만들기

토큰에 옅은 바탕은 `--accent-soft` 하나뿐이다.
다른 옅은 바탕이 필요하면 토큰을 섞어 만든다. 두 테마 모두 따라온다.

```css
.soft-cw { background: color-mix(in srgb, var(--line-cw) 12%, var(--surface)); }
.soft-warn { background: color-mix(in srgb, var(--warn) 10%, var(--surface)); }
```

- 새 색값(`#…`, `rgb(…)`)은 쓰지 않는다. 꼭 필요한 색이 토큰에 없으면 쓰지 말고, 리드에게 `shared/tokens.css`에 더하자고 제안한다.

## 10. 선택

### 오른쪽 목차 (섹션이 다섯 개 넘는 긴 문서)
오른쪽에 대시만 세로로 두고, 보고 있는 섹션의 대시를 강조색으로 길게 바꾼다.
마우스를 올리면 섹션 이름이 펼쳐진다.
폭이 좁은 화면(640px 이하)에서는 내용과 겹치므로 숨긴다.

```css
.rail { position: fixed; z-index: 30; top: 50%; right: 14px; transform: translateY(-50%); padding: 8px 6px; border: 1px solid transparent; border-radius: 12px; }
.rail ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.rail a { display: flex; align-items: center; justify-content: flex-end; height: 24px; padding-left: 10px; color: var(--muted); text-decoration: none; }
.rail-label { max-width: 0; overflow: hidden; opacity: 0; font-size: 12.5px; white-space: nowrap; transition: max-width .2s, opacity .15s, margin-right .2s; }
.rail-dash { width: 14px; height: 2px; border-radius: 2px; background: var(--muted); opacity: .45; }
.rail a.is-active .rail-dash { width: 30px; height: 3px; background: var(--accent); opacity: 1; }
.rail:hover { background: var(--surface); border-color: var(--rule); box-shadow: var(--shadow); }
.rail:hover .rail-label { max-width: 160px; opacity: 1; margin-right: 10px; }
@media (max-width: 1259px) { .page { padding-right: 62px; } }
@media (max-width: 640px) { .page { padding-right: 16px; } .rail { display: none; } }
@media (prefers-reduced-motion: reduce) { .rail * { transition: none !important; } }
```

```js
// 스크롤 위치에서 지금 섹션을 찾아 is-active를 붙인다
(function () {
  var links = [].slice.call(document.querySelectorAll('.rail a[href^="#"]'));
  var targets = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function update() {
    var line = innerHeight * 0.4, active = -1;
    targets.forEach(function (t, i) { if (t && t.getBoundingClientRect().top <= line) active = i; });
    links.forEach(function (a, i) { a.classList.toggle('is-active', i === active); });
  }
  addEventListener('scroll', update, { passive: true });
  update();
})();
```

### 체크리스트
체크 상태는 그 사람의 브라우저에만 남는다. 편의용으로만 쓰고, 팀이 함께 봐야 하는 상태는 담지 않는다.
저장 · 읽기는 `try { … } catch (e) {}`로 감싼다. 저장이 막힌 브라우저에서도 페이지가 그대로 보여야 한다.

```css
.checklist { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.checklist li { display: grid; grid-template-columns: 22px minmax(0, 1fr); gap: 10px; align-items: start; background: var(--surface); border: 1px solid var(--rule); border-radius: 10px; padding: 10px 12px; }
.checklist label { display: grid; gap: 2px; min-width: 0; cursor: pointer; }
.checklist label span { font-size: 12.5px; color: var(--muted); }
.checklist input { width: 18px; height: 18px; margin: 3px 0 0; accent-color: var(--accent); }
.checklist input:checked + label b { color: var(--muted); text-decoration: line-through; }
```

## 11. 쓰지 않는 것

- 포스터 판: 두 테마에서 같은 어두운 판을 쓰려면 토큰 밖 색값이 필요하다.
- 노선도 · 흐름 지도처럼 원래 문서 하나에만 맞춘 컴포넌트: 필요하면 위 카드 · 칩 · 범례로 새로 짠다.
