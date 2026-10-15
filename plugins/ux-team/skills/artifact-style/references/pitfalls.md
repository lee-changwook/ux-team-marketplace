# 함정

UX팀 문서 두 편을 만들며 실제로 겪은 것이다.
페이지를 만들 때 한 번, 게시 전 점검 때 한 번 본다.

## 1. 전역 box-sizing 리셋이 없으면 넘친다
- 증상: `width: 100%`에 `padding`을 준 상자가 부모보다 넓어져 가로 스크롤이 생긴다.
- 원인: 기본값(`content-box`)에서는 width와 padding이 더해진다.
- 고침: `tokens.css` 끝에 들어 있는 리셋을 지우지 않는다.

```css
*, *::before, *::after { box-sizing: border-box; }
```

## 2. 한 열 grid는 minmax(0, 1fr)로 둔다
- 증상: 표나 흐름도처럼 안쪽에 가로 스크롤 영역이 있는 섹션이 있으면, 페이지 전체가 그 폭만큼 넓어진다. 좁은 화면에서 특히 드러난다.
- 원인: `display: grid`의 기본 트랙(`auto`)은 내용의 최소 폭만큼 늘어난다. 안쪽 스크롤 영역의 `min-width`가 그대로 트랙 폭이 된다.
- 고침: 한 열 grid에 트랙을 명시한다. 여러 열 grid도 `1fr` 대신 `minmax(0, 1fr)`를 쓴다. grid 자식에는 `min-width: 0`을 준다.

```css
.page, .head, section.block { display: grid; grid-template-columns: minmax(0, 1fr); }
.cards > * { min-width: 0; }
```

## 3. 작은 요소의 클래스는 접두어로 구분한다
- 증상: 범례의 작은 스와치가 큰 컴포넌트의 테두리 · 여백 · 폭을 물려받아 깨진다.
- 원인: 범례 스와치에 큰 컴포넌트와 같은 클래스(`.step`, `.chip` 등)를 붙였다.
- 고침: 스와치는 `sw-`, 칩 변형은 `chip-`처럼 접두어를 붙여 이름을 나눈다.

```html
<i class="sw sw-dash"></i>   <!-- O -->
<i class="step dash"></i>    <!-- X: .step의 width · padding이 섞인다 -->
```

## 4. 한글 라벨에 mono 서체를 쓰지 않는다
- 증상: 한글 라벨의 글자 사이가 벌어져 보인다.
- 원인: mono 서체는 공백과 글자 폭이 넓다.
- 고침: mono(`var(--font-mono)`)는 코드 · 경로 · 숫자 · ID에만 쓴다. 한글이 들어가는 라벨 · eyebrow · 칩은 본문 서체로 둔다.

## 5. 한글 본문은 word-break: keep-all
- 증상: 한글 단어가 줄 끝에서 중간에 끊긴다.
- 고침: `tokens.css`의 `body`에 들어 있다. 다른 요소에서 `word-break`를 덮어쓰지 않는다. 긴 경로 · URL은 `overflow-wrap: anywhere`로 따로 풀어 준다.

## 6. headless Chrome으로 390px를 볼 때는 iframe 안에서 본다
- 증상: `--window-size=390,…`로 캡처해도 화면이 390px보다 넓게 그려진다.
- 원인: headless Chrome은 창 최소 폭이 있다.
- 고침: 390px 폭 iframe에 페이지를 넣은 감싸개 파일을 캡처한다. 방법은 `preflight.md` 3절에 있다.

## 7. 경고는 색만으로 나타내지 않는다
- 증상: 강조(Magenta `--accent`)와 경고(빨강 `--warn`)가 둘 다 붉은 계열이라 구분되지 않는다. 색을 잘 구분하지 못하는 사람에게는 더 그렇다.
- 고침: 경고에는 점선 테두리와 글자 라벨("끊김", "빠짐", "충돌", "섞임" 등)을 함께 쓴다. 강조는 실선 · 채움으로 둔다.

```html
<div class="warn"><b>끊김</b>티링 신청 값이 행정 화면에 보이지 않습니다.</div>
```
