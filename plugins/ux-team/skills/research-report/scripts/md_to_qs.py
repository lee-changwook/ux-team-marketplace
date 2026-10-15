#!/usr/bin/env python3
"""markdown 질문 리스트를 리포트의 GROUPS · QS 상수로 옮기고, 판본을 고를 숫자를 낸다.

사용:
  python3 md_to_qs.py <질문 리스트.md>                        단일형. 답 키는 r
  python3 md_to_qs.py <응답1.md> <응답2.md> --keys a,b         두 응답 세트. 같은 문항끼리 짝짓는다

stdout에는 리포트 <script>에 붙일 `const GROUPS` · `const QS`, stderr에는 문항 수와 판본 판정이 나온다.

md 형식:
  ## 구성                       선택. `- **PRE. 사전 확인**: …` 줄이 있으면 묶음 이름을 여기서 가져온다
  ## PRE. 데스크와 출석부 위치    대문자 키 + 점. 구성의 이름과 다르면 제목을 첫 주제로 쓴다
  ### 출석 확인 방식              주제. 묶음 제목은 `<부 이름>: <주제>`
  - 질문                          최상위 목록 = 문항
  - 질문: 답                      쌍점 뒤는 한 줄 답
  	- 답                         들여쓴 목록 = 답 줄
답 줄 끝의 출처 표시 `(녹음)`은 떼고, `(제안)`으로 끝나는 줄은 응답이 아니라서 뺀다. 답이 없는 문항은 싣지 않는다.
"""
import argparse
import json
import re
import sys

STRIP = ["(녹음)"]
SKIP = ["(제안)"]
PART = re.compile(r"^## ([A-Z][A-Z0-9]*)\.\s*(.*)$")
PLAN = re.compile(r"^- \*\*([A-Z][A-Z0-9]*)\.\s*([^*]+)\*\*")


def clean(text: str) -> str:
    for mark in STRIP:
        text = text.replace(f" {mark}", "").replace(mark, "")
    return text.strip()


def parse(path: str):
    lines = open(path, encoding="utf-8").read().splitlines()
    names = {m.group(1): m.group(2).strip() for m in map(PLAN.match, lines) if m}
    groups, qs = {}, []
    part = group = None
    count = {}

    def open_group(label: str) -> str:
        key = f"{part}{count.get(part, 0)}"
        count[part] = count.get(part, 0) + 1
        groups[key] = label
        return key

    for line in lines:
        m = PART.match(line)
        if m:
            part, title = m.group(1), m.group(2).strip()
            name = names.get(part, title)
            group = open_group(f"{name}: {title}" if title and title != name else name)
            continue
        if line.startswith("## "):
            part = None
            continue
        if part is None:
            continue
        if line.startswith("### "):
            label = f"{names.get(part, groups[group].split(':')[0])}: {line[4:].strip()}"
            if not any(q["g"] == group for q in qs) and groups[group] == names.get(part):
                groups[group] = label
            else:
                group = open_group(label)
            continue
        top = re.match(r"^- (.*)$", line)
        if top:
            text = top.group(1).strip()
            if ": " in text:
                q, a = text.split(": ", 1)
            else:
                q, a = text.rstrip(":"), ""
            qs.append({"g": group, "q": clean(q.rstrip(":")), "a": [clean(a)] if clean(a) else []})
            continue
        sub = re.match(r"^(?:\t+|\s{2,})- (.*)$", line)
        if sub and qs:
            a = sub.group(1).strip()
            if a and not any(a.endswith(mark) for mark in SKIP):
                qs[-1]["a"].append(clean(a))
    used = {q["g"] for q in qs}
    return {k: v for k, v in groups.items() if k in used}, qs


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def emit(groups, qs) -> None:
    print("const GROUPS = " + json.dumps(groups, ensure_ascii=False) + ";")
    print("const QS = [")
    for q in qs:
        print("  " + json.dumps(q, ensure_ascii=False) + ",")
    print("];")


def verdict(ratio: float) -> str:
    if ratio >= 0.7:
        return "비교형"
    if ratio <= 0.3:
        return "단일형"
    return "애매함. 사용자에게 추천안과 함께 묻는다"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--keys", default="p1,p2", help="두 응답 세트 모드의 답 키 (기본 p1,p2)")
    args = ap.parse_args()

    if len(args.files) == 1:
        groups, raw = parse(args.files[0])
        answered = [q for q in raw if q["a"]]
        qs = [{"n": i, "g": q["g"], "q": q["q"], "r": {"a": "\n".join(q["a"])}} for i, q in enumerate(answered, 1)]
        emit(groups, qs)
        print(f"문항 {len(raw)}개 중 답 있음 {len(answered)}개, 묶음 {len(groups)}개", file=sys.stderr)
        print("판정: 단일형 (자료가 파일 하나). 대결 카드는 같은 질문에 답이 갈린 곳을 직접 골라 만든다", file=sys.stderr)
        return 0

    if len(args.files) != 2:
        ap.error("파일은 하나(단일형) 또는 둘(두 응답 세트)이어야 합니다. 셋 이상이면 한 문서로 만들지 않는다 (SKILL.md 0절)")
    keys = args.keys.split(",")
    if len(keys) != 2:
        ap.error("--keys는 쉼표로 이은 두 개여야 합니다")
    groups, by_label, merged = {}, {}, {}
    for key, path in zip(keys, args.files):
        src_groups, source = parse(path)
        for q in source:
            label = src_groups[q["g"]]
            if label not in by_label:
                by_label[label] = f"G{len(by_label)}"
                groups[by_label[label]] = label
            item = merged.setdefault(norm(q["q"]), {"g": by_label[label], "q": q["q"]})
            if q["a"]:
                item[key] = {"a": "\n".join(q["a"])}
    order = list(groups)
    rows = sorted((m for m in merged.values() if keys[0] in m or keys[1] in m), key=lambda m: order.index(m["g"]))
    both = sum(1 for m in rows if keys[0] in m and keys[1] in m)
    qs = [{"n": i, **m} for i, m in enumerate(rows, 1)]
    used = {q["g"] for q in qs}
    emit({k: v for k, v in groups.items() if k in used}, qs)
    ratio = both / len(rows) if rows else 0
    print(f"문항 {len(rows)}개 중 양쪽 모두 답함 {both}개 ({ratio:.0%})", file=sys.stderr)
    print(f"판정: {verdict(ratio)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
