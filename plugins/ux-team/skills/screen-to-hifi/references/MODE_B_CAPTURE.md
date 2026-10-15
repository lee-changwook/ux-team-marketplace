# 모드 B — 아직 Figma에 없는 화면을 먼저 캡처한다

base가 Figma에 없으면 clone할 원본이 없다. 그때만 이 모드를 쓰고, **한 번 캡처해두면 그 뒤로는 계속 모드 A**로 돈다.

2026-09-20에 등·하원 내역 화면(staging)으로 전 단계를 검증했다.

## 화면별 경로

captureId 발급(B-2)과 폴링(B-5)은 Figma 커넥터로 하므로 모든 화면에서 같다. 달라지는 것은 "로그인된 탭에서 capture 스크립트를 실행하는 방법"(B-3 · B-4)뿐이다.

| 화면 | 브라우저 | 스크립트 주입 · 캡처 실행 | 안 될 때 |
| ---- | -------- | ------------------------- | -------- |
| Code 탭 | Claude in Chrome 확장 | 아래 B-3 · B-4 그대로. 사용자가 로그인해 둔 탭에서 페이지 스크립트를 실행한다 | 확장이 없으면 설치를 안내하거나 Cowork로 옮기라고 알리고 멈춘다. CSP로 막히면 fetch + inline 주입 → Playwright 도구가 있으면 Playwright → 없으면 멈추고 알린다 |
| Cowork | 내장 브라우저 | 사용자가 로그인한 뒤, 페이지 스크립트 실행이 되면 Code 탭과 같은 절차 | 페이지 스크립트를 실행할 수 없으면 Code 탭에서 하라고 알리고 멈춘다 |
| Chat | 없음 | 모드 B 불가 | Cowork나 Code 탭에서 하라고 알린다. base가 이미 Figma에 있으면 모드 A로 간다 |

## 안전 범위

- **staging 주소에서만 캡처한다.** 주소가 staging이 아니어 보이면 멈추고 사용자에게 확인한다. 운영 화면을 캡처하면 실데이터(학원생 이름 등)가 Figma 문서로 남는다.
- 조회 · 탭 전환 · 필터 · 화면 이동만 한다. 저장 · 삭제 · 발송 · 결제 같은 쓰기 동작은 하지 않는다.
- 로그인은 사용자가 직접 한다. 비밀번호 · 토큰을 다루지 않는다.

## B-0. 캡처 전 확인

캡처는 사용자 Figma 파일에 프레임을 만드는 쓰기다. 아래를 보여 주고 확인받은 뒤에 B-2로 간다.

- 캡처할 화면 주소와 화면 상태 (탭 · 필터 · 조회 조건)
- 뷰포트 폭
- 캡처를 넣을 Figma 파일 · 페이지 · 섹션

## B-1. 캡처할 화면 상태를 먼저 만든다

빈 목록을 캡처하면 빈 목록이 문서가 된다. **조회를 실행해 데이터를 띄우고**, 보여주려는 탭·필터·선택 상태를 맞춘 뒤에 캡처한다. 조회는 읽기 동작이라 안전하다.

뷰포트 폭도 확인한다 (`window.innerWidth`). 캡처 크기가 그대로 프레임 크기가 되므로, 기존 캡처와 나란히 둘 거면 폭을 맞춘다.

## B-2. captureId 발급

Figma 커넥터의 화면 캡처를 `fileKey`로 호출하면 capture script와 `captureId`를 준다. **single-use**다.

`nodeId`는 **부모 지정이 아니라 페이지 지정**이다 (실측: 빈 프레임을 줬는데 그 페이지의 최상위에 생성). **`nodeId`를 아예 생략하면 파일 첫 페이지의 `x=28937` 같은 먼 좌표에 떨어져 사용자 눈에 안 띈다.** 목표 페이지에 있는 아무 노드나 `nodeId`로 주고, 캡처 후 Figma 코드 실행으로 의도한 섹션·좌표에 옮긴 뒤 URL을 보고한다.

## B-3. 스크립트 주입 — 외부 URL이어도 Playwright는 대개 불필요

공식 안내는 외부 URL이면 Playwright MCP를 쓰라고 한다. 그 이유는 **CSP 우회**뿐이다. 대상 앱에 CSP가 없으면 Claude in Chrome만으로 된다. 로그인 세션도 그대로 쓰인다.

capture 스크립트 주소는 캡처 도구가 돌려준 것을 쓴다. 아래 주소는 2026-09 기준 예다.

```js
// 브라우저의 페이지 스크립트 실행 — 이미 로그인된 탭에서
await new Promise((res, rej) => {
  const s = document.createElement('script');
  s.src = 'https://mcp.figma.com/mcp/html-to-design/capture.js';
  s.onload = res; s.onerror = () => rej(new Error('script-src blocked'));
  document.head.appendChild(s);
});
typeof window.figma.captureForDesign;   // 'function'이면 통과
```

`onerror`가 나면 CSP가 있는 것이다. 그때 fetch + inline 주입을 시도하고, 그것도 막히면 Playwright로 간다.

## B-4. 캡처 실행 — CDP 45초 타임아웃은 실패가 아니다

```js
await window.figma.captureForDesign({
  captureId: '<captureId>',
  endpoint: 'https://mcp.figma.com/mcp/capture/<captureId>/submit?bindVariables=true',
  selector: 'body',
});
```

DOM 직렬화가 무거워서 **`CDP sendCommand "Runtime.evaluate" timed out after 45000ms`가 거의 항상 뜬다.** 캡처는 뒤에서 계속 돈다. 이걸 실패로 보고 재시도하지 말고 바로 폴링으로 넘어간다.

## B-5. 폴링

Figma 커넥터의 화면 캡처를 `fileKey` + `captureId`로 호출한다. `completed`가 나올 때까지 5초 간격, 최대 10회. **폴링 중에 새 captureId를 만들지 않는다.**

## B-6. 캡처 직후 보정 (필수)

캡처본은 폰트가 없으면 텍스트가 부풀어 오토레이아웃이 넘친다. [FIGMA_RULES.md](FIGMA_RULES.md) 6-5절의 순서대로 보정한다. **이 보정을 건너뛰면 padding이 깨진 채로 문서가 된다.**

점검은 `maxRight > frame.width`(부모 박스 탈출)로 한다. padding만 2~4px 침범하는 건은 손대지 않는다.

## B-7. 모드 A로 이어간다

- 보정이 끝난 캡처 프레임을 base로 삼아 SKILL.md Step 3 정찰로 바로 간다. 새 URL을 다시 묻지 않는다.
- 모드 A의 승인 게이트(Step 5)는 그대로 받는다. 정찰 결과가 있어야 변경목록을 만들 수 있기 때문이다.
- 방향을 주지 않고 캡처만 요청했으면 여기서 캡처 결과 URL(`https://www.figma.com/design/<fileKey>/?node-id=<id>`)과 보정 내역(바꾼 `itemSpacing` 값 등)을 주고 끝낸다. 방향을 지어내지 않는다.
