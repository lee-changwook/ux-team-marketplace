# 주소 목록

이 파일은 리드가 채웁니다.
스킬은 이 목록을 대조만 하고 고치지 않습니다.

## 규칙

- 허용 목록의 호스트와 그대로 같거나, 허용 목록의 모양에 맞을 때만 실행합니다. 하위 도메인이나 비슷한 이름은 허용으로 보지 않습니다.
- 대조는 호스트 전체가 같은지로 합니다. 차단 목록의 `dash.v3.teachita.com`과 허용 목록의 `staging.dash.v3.teachita.com`은 서로 다른 호스트입니다.
- 허용 목록이 비어 있으면 실행하지 않고 멈춥니다.
- 차단 목록에 있는 호스트는 사용자가 요청해도 열지 않습니다.
- 어느 목록에도 없는 호스트는 운영인지 몰라도 열지 않습니다.
- 이동 중 목록 밖으로 나가면 멈춥니다.

## 허용 (staging)

| 호스트 | 용도 |
|---|---|
| `staging.dash.v3.teachita.com` | staging |

## 허용 (프로젝트 staging)

프로젝트마다 따로 띄운 staging입니다. 호스트 하나씩이 아니라 모양으로 허용합니다.
예시의 번호는 가상입니다.

| 모양 | 맞는 예 | 맞지 않는 예 |
|---|---|---|
| `prj-<숫자 3자리>.dash.v3.teachita.com` | `prj-123.dash.v3.teachita.com` | `prj-123.api.v3.teachita.com` (API 서버) |
| `prj-<숫자 3자리>-<영문 소문자 · 숫자 · 하이픈>.dash.v3.teachita.com` | `prj-123-sample.dash.v3.teachita.com` | `prj-12.dash.v3.teachita.com` (숫자 2자리) |

## 차단 (운영)

| 호스트 | 용도 |
|---|---|
| `dash.v3.teachita.com` | 운영 |

## 접속 조건

- staging(`staging.dash.v3.teachita.com`)은 IP 제한이 없지만 VPN(WireGuard)이 필요합니다.
- 브라우저가 도는 PC에서 WireGuard가 켜져 있어야 열립니다.
- 화면이 안 열리면 WireGuard가 켜져 있는지 먼저 확인해 달라고 알립니다.
