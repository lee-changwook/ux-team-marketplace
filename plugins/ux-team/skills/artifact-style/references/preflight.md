# 게시 전 점검

게시하거나 같은 링크에 다시 올리기 전에 본다.
먼저 스크립트를 돌리고, 스크립트가 보지 않는 것은 아래 점검표로 본다.

## 1. 스크립트

페이지를 파일로 저장한 뒤 스킬 폴더에서 돌린다.
명령을 실행할 수 있는 화면(Chat · Cowork의 실행 환경, Code 탭)이면 어디서나 된다.

```
python3 scripts/preflight.py <페이지.html>
```

| 결과 | 뜻 | 할 일 |
|---|---|---|
| 고칠 것 · 토큰 | tokens.css의 토큰이 빠졌거나 값이 다르다 | `references/_shared/tokens.css`를 통째로 다시 붙인다 |
| 고칠 것 · 색값 | 토큰 블록 밖에 색값이 있다 | `var(--…)`로 바꾸거나, 옅은 바탕이면 `color-mix`로 만든다 |
| 고칠 것 · 버전 | 제목 · 본문 · 파일 이름에 버전 표기가 있다 | 뺀다 |
| 확인할 것 · 줄바꿈 | 불릿이 아닌 글 한 줄에 문장이 둘 이상이다 | 문장 사이에 `<br>`을 넣는다. 숫자 목록("1. 항목")처럼 문장이 아니면 그대로 둔다 |
| 확인할 것 · 범례 | 자체 ID가 있다 | 문서 맨 앞에 범례(접두어 · 뜻 · 번호 규칙)가 있는지 본다 |

- 고칠 것이 0건이 될 때까지 고친다. 확인할 것은 하나씩 보고 고칠지 판단한다.
- 스크립트를 돌릴 수 없으면 아래 점검표의 해당 줄을 손으로 본다.

## 2. 점검표

### 글
- [ ] 결론이 맨 위에 있다. 판단할 것 → 확인할 것 → 참고 순서다.
- [ ] 서술 문단은 문장마다 줄을 바꿨다. 불릿은 예외다. (스크립트 "줄바꿈")
  - 손으로 볼 때: 각 `<p>` · 카드 본문에서 "다." · "요." 뒤에 `<br>` 없이 글이 이어지는 곳을 찾는다.
- [ ] 제목과 본문이 다른 줄에 있다.
- [ ] 팀원에게 쓰는 글은 높임말이다.
- [ ] 사람이 확인하지 않은 것을 "확정"이라고 쓰지 않았다. 근거가 없는 칸은 `미결`이다.
- [ ] 버전 라벨(v2, ver, 최종본, 수정본 등)이 제목 · 본문 · 파일 이름 어디에도 없다. (스크립트 "버전")
- [ ] 자체 ID를 쓰면 문서 맨 앞에 범례가 있다. (스크립트 "범례")

### 색과 서체
- [ ] `<style>` 맨 위에 tokens.css가 통째로 있다. (스크립트 "토큰")
- [ ] 토큰 블록 밖에 색값이 없다. SVG의 `fill` · `stroke`도 `var(--…)`나 `currentColor`다. (스크립트 "색값")
- [ ] 스크립트(JS)로 그리는 차트 · 캔버스도 색을 `getComputedStyle(document.documentElement).getPropertyValue('--accent')`처럼 토큰에서 읽는다. 스크립트는 JS 안의 색값을 보지 않는다.
- [ ] 사람 색은 사람을 표시할 때만 썼다. 강조색은 한 화면에 한두 곳이다.
- [ ] 경고는 점선 테두리와 글자 라벨이 함께 있다 (`pitfalls.md` 7번).
- [ ] 한글 라벨에 mono 서체를 쓰지 않았다 (`pitfalls.md` 4번).

### 화면
- [ ] 라이트 · 다크 두 테마에서 글자와 테두리가 모두 보인다.
- [ ] 390px 폭에서 가로로 넘치지 않는다. 표처럼 일부러 가로 스크롤을 둔 곳은 그 안에서만 스크롤된다.
- [ ] 한 열 grid는 `minmax(0, 1fr)`이다 (`pitfalls.md` 2번).
- [ ] 키보드 Tab으로 링크 · 버튼에 초점 테두리가 보인다.

### 게시
- [ ] 고친 것이면 같은 아티팩트를 고쳐 같은 링크에 다시 올린다. 새 링크를 만들지 않는다.
- [ ] 팀원에게 보일 것이면 Share 메뉴로 공유하라고 안내한다. 아티팩트는 처음에 비공개다.

## 3. 테마와 390px 확인

### Chat · Cowork
- 아티팩트 미리보기에서 시스템 테마를 바꿔 라이트 · 다크를 본다. 사용자에게 바꿔 보라고 부탁해도 된다.
- 390px 확인은 사용자에게 창을 좁히거나 휴대폰으로 열어 보라고 부탁한다.

### Code 탭 (Chrome이 있을 때)
로컬 파일을 headless Chrome으로 캡처한다. 사이트를 열지 않으므로 흔적이 남지 않는다.
Chrome이 없으면 위 Chat · Cowork 방법으로 바꾼다.

1. 다크 사본을 만든다. `<html lang="ko">`에 `data-theme="dark"`를 더한 사본이다.
2. 390px 감싸개를 만든다. headless Chrome은 창 최소 폭이 있어서 창 폭으로는 390px를 볼 수 없다 (`pitfalls.md` 6번).
3. 캡처한 그림을 열어 본다.

```
# 임시 폴더에서 한다. 페이지가 page.html일 때
sed 's/<html lang="ko">/<html lang="ko" data-theme="dark">/' page.html > page.dark.html
cat > frame390.html <<'HTML'
<!doctype html><meta charset="utf-8">
<body style="margin:0;display:flex;gap:16px;background:#888">
<iframe src="page.html" style="width:390px;height:2400px;border:0;background:#fff"></iframe>
<iframe src="page.dark.html" style="width:390px;height:2400px;border:0;background:#000"></iframe>
</body>
HTML

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless --disable-gpu --hide-scrollbars --window-size=1280,2400 --screenshot="$PWD/wide.png" "file://$PWD/page.html"
"$CHROME" --headless --disable-gpu --window-size=820,2400 --screenshot="$PWD/narrow.png" "file://$PWD/frame390.html"
```

- `narrow.png`에서 두 iframe 안에 가로 스크롤 막대가 보이거나 글이 잘리면 넘친 것이다.
- 감싸개의 회색 · 흰색 · 검은색은 캡처용 틀이다. 페이지에는 넣지 않는다.
