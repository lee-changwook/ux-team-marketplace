#!/bin/sh
# 팀 지침(references/_shared/ux-team-guide.md)을 Code 탭의 사용자 규칙 폴더에 설치한다.
# Code 탭(내 Mac)에서만 실행한다.
#
#   install-guide.sh check [대상]   상태를 한 단어로 출력한다. DIFF면 바뀌는 내용이 이어진다
#       NOT_MAC  macOS가 아니다. Code 탭이 아니므로 설치하지 않는다
#       LINK     대상이 링크다. 덮어쓰면 링크 너머 파일이 바뀌므로 멈춘다
#       NEW      대상이 없다
#       SAME     대상이 원본과 같다
#       DIFF     대상이 원본과 다르다
#   install-guide.sh apply [대상]   대상을 원본으로 통째로 덮어쓰고 INSTALLED를 출력한다. 폴더가 없으면 만든다
#                                   이미 같으면 쓰지 않고 SAME, NOT_MAC · LINK면 쓰지 않고 그 단어를 출력한다
#
# 대상을 주지 않으면 ~/.claude/rules/ux-team-guide.md다. 대상 인자는 시험할 때만 쓴다.
set -eu

src="$(cd "$(dirname "$0")/.." && pwd)/references/_shared/ux-team-guide.md"
dest="${2:-$HOME/.claude/rules/ux-team-guide.md}"

state() {
  if [ "$(uname -s)" != Darwin ]; then echo NOT_MAC
  elif [ -L "$dest" ]; then echo LINK
  elif [ ! -e "$dest" ]; then echo NEW
  elif cmp -s "$src" "$dest"; then echo SAME
  else echo DIFF
  fi
}

case "${1:-}" in
  check)
    s=$(state)
    echo "$s"
    if [ "$s" = DIFF ]; then
      diff -u -L "지금 설치된 지침" -L "새 지침" "$dest" "$src" || true
    fi
    ;;
  apply)
    s=$(state)
    case "$s" in
      NOT_MAC | LINK) echo "$s"; exit 1 ;;
      SAME) echo SAME; exit 0 ;;
    esac
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    cmp -s "$src" "$dest"
    echo INSTALLED
    ;;
  *)
    sed -n '2,14p' "$0"
    exit 2
    ;;
esac
