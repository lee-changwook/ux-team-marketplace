#!/usr/bin/env python3
"""리포트에 남으면 안 되는 평가 · 추정 표현을 찾는다 (POL-05).

사용: python3 check_shared.py <리포트.html>
<script>(응답 원문 데이터)와 <style>은 검사하지 않는다. 응답자 본인의 말은 그대로 두는 게 규칙이라서다.
금지 표현이 있으면 종료 코드 1. 반말 종결은 경고만 낸다.
"""
import html as htmllib
import re
import sys

BANNED = [
    (r"가설", "불신 표현"),
    (r"추정", "응답자에 대한 추정"),
    (r"판단했", "응답자 추정 문구"),
    (r"조정 필요", "'함께 정할 것'으로"),
    (r"레일", "'먼저 살펴볼 것'처럼 쉬운 말로"),
    (r"게이트", "'결정'으로"),
    (r"\d단계", "'기획 문서 / 동작하는 화면 / 실제 서비스'처럼 이름으로"),
    (r"스펙트럼", "사람을 축 위에 놓는 표현은 쓰지 않는다"),
    (r"확인할 것", "작성자 혼자 확인할 것은 리포트에 넣지 않는다"),
    (r"KPI|보는 숫자|성과 지표", "성과 지표는 리포트에 넣지 않는다"),
    (r"결과물로 (확인|검증)", "강점을 검증하겠다는 항목은 뺀다"),
    (r"약점", "강점식으로"),
]
PLAIN_END = re.compile(r"(?<![니요])다[.]?$")


def visible_lines(src: str) -> list[str]:
    src = re.sub(r"<(script|style)\b.*?</\1>", "", src, flags=re.S | re.I)
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    src = re.sub(r"<(br|/p|/li|/div|/h\d|/dd|/dt|/td|/th|/span|/b|/small)\b[^>]*>", "\n", src, flags=re.I)
    src = re.sub(r"<[^>]+>", "", src)
    lines = [htmllib.unescape(line).strip() for line in src.splitlines()]
    return [line for line in lines if line]


def main(path: str) -> int:
    lines = visible_lines(open(path, encoding="utf-8").read())
    hits = [(p, why, line) for line in lines for p, why in BANNED if re.search(p, line)]
    warns = [line for line in lines if PLAIN_END.search(line) and len(line) > 6]
    for p, why, line in hits:
        print(f"금지  [{p}] {why}\n      {line}")
    for line in warns:
        print(f"경고  반말 종결인지 확인 (합니다체)\n      {line}")
    print(f"금지 {len(hits)}건, 경고 {len(warns)}건")
    return 1 if hits else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
