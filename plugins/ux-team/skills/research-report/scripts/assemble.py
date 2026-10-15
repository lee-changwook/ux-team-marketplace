#!/usr/bin/env python3
"""뼈대에서 채운 리포트 HTML의 /*@css*/ · /*@render*/ 자리에 공통 파일을 넣어 파일 하나로 만든다.

사용: python3 assemble.py <리포트.html> [<리포트.html> ...]
파일을 제자리에서 고친다. 이미 조립한 파일은 조립을 건너뛰고 채우지 않은 자리만 검사한다.
"""
import pathlib
import re
import sys

TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "templates"
SLOTS = {"/*@css*/": "report.css", "/*@render*/": "render.js"}


def assemble(path: pathlib.Path) -> None:
    html = path.read_text(encoding="utf-8")
    if any(mark in html for mark in SLOTS):
        for mark, name in SLOTS.items():
            if html.count(mark) != 1:
                sys.exit(f"{path}: {mark} 자리가 {html.count(mark)}개입니다. 1개여야 합니다")
            html = html.replace(mark, (TEMPLATES / name).read_text(encoding="utf-8"))
        path.write_text(html, encoding="utf-8")
        print(f"조립함: {path}")
    else:
        print(f"이미 조립됨: {path}")
    left = sorted(set(re.findall(r"\{\{[^}]*\}\}", html)))
    if left:
        print("  채우지 않은 자리:", ", ".join(left))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        assemble(pathlib.Path(arg))
