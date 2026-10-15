#!/usr/bin/env python3
"""UX팀 플러그인 eval 케이스 도구.

    python3 scripts/evals.py build          docs/evals/*.md와 팀 지침 원본으로 evals/의 케이스를 만든다
    python3 scripts/evals.py stage <폴더>    <폴더>/ux-team에 플러그인 사본과 evals/를 합치고 실행 명령을 출력한다

케이스는 플러그인 밖(evals/)에 둔다. claude plugin eval은 케이스를 플러그인 폴더 안에서만 찾고,
마켓플레이스 설치는 플러그인 폴더를 통째로 복사하므로, 안에 두면 팀원에게 케이스가 함께 배포된다.
그래서 실행할 때 stage로 임시 사본을 만들어 돌린다.

build가 만드는 것
  evals/trigger/<케이스>/        docs/evals/<스킬>.md의 "켜져야 할 요청" · "켜지면 안 될 요청" 한 줄당 한 케이스
                                 (같은 요청은 한 번만). 기대 스킬이 켜지고 다른 ux-team 스킬은 켜지지 않아야 통과한다.
                                 맡는 스킬이 켜졌을 때 tikita-policy가 함께 켜지는 것은 통과로 본다
  evals/hello-ux-team/<케이스>/  hello-ux-team 스킬 단위 시험. 실행마다 임시 home을 쓰는지 home-check로 먼저 본다
build는 내용이 같은 파일을 다시 쓰지 않고, 두 폴더 안에서 더는 만들지 않는 케이스를 지운다.
"""
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ux-team"
SKILLS = sorted(p.name for p in (PLUGIN / "skills").iterdir() if p.is_dir())
EVAL_DOCS = ROOT / "docs" / "evals"
EVALS = ROOT / "evals"
GUIDE = ROOT / "shared" / "ux-team-guide.md"
MANUAL_ONLY = {"hello-ux-team"}   # 켜져야 할 요청이 슬래시 호출이라 트리거 eval에서 뺀다 (RSK-01로 확인)
CO_TRIGGER_OK = "tikita-policy"   # 맡는 스킬과 함께 켜져도 통과 (통합 판단 3번)
TRIGGER_FM = {"max_turns": 4, "timeout_seconds": 180, "allowed_tools": ["Skill", "Read", "Glob", "Grep"]}


def skill_pattern(names):
    alt = "|".join(sorted(names))
    return f'"skill"\\s*:\\s*"(?:ux-team:)?(?:{alt})"'


def frontmatter(fields):
    return "---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fields.items()) + "---\n"


def grader(**fields):
    return frontmatter(fields)


def section(text, title):
    m = re.search(rf"^## {title}[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def strip_note(prompt):
    return re.sub(r"\s*\([^()]*\)$", "", prompt.strip())


def read_requests():
    """(요청, 기대 스킬 또는 None, 출처) 목록을 돌려준다."""
    rows = []
    for doc in sorted(EVAL_DOCS.glob("*.md")):
        skill = doc.stem
        if skill not in SKILLS:
            continue
        text = doc.read_text(encoding="utf-8")
        if skill not in MANUAL_ONLY:
            for n, m in enumerate(re.finditer(r"^\d+\.\s+(.+)$", section(text, "켜져야 할 요청"), re.M), 1):
                rows.append((m.group(1).strip(), skill, f"{skill}-on-{n}", f"docs/evals/{doc.name} 켜져야 할 요청 {n}"))
        n = 0
        for line in section(text, "켜지면 안 될 요청").splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not line.startswith("|") or len(cells) < 2 or cells[0] == "요청" or set(cells[0]) <= set("-: "):
                continue
            n += 1
            named = [s for s in re.findall(r"`([a-z0-9-]+)`", cells[1]) if s in SKILLS]
            expect = None if cells[1].startswith("없음") or not named else named[0]
            rows.append((strip_note(cells[0]), expect, f"{skill}-off-{n}", f"docs/evals/{doc.name} 켜지면 안 될 요청 {n}"))
    return rows


def trigger_cases():
    cases, by_prompt = {}, {}
    for prompt, expect, name, source in read_requests():
        if prompt in by_prompt:
            case = cases[by_prompt[prompt]]
            if case["expect"] != expect:
                sys.exit(f"같은 요청의 기대 스킬이 다름: {prompt!r} ({case['expect']} · {expect})")
            case["sources"].append(source)
            continue
        by_prompt[prompt] = name
        cases[name] = {"prompt": prompt, "expect": expect, "sources": [source]}
    files = {}
    for name, case in cases.items():
        expect = case["expect"]
        if expect:
            outcome = f"{expect}가 켜지고 다른 ux-team 스킬은 켜지지 않는다"
            if expect != CO_TRIGGER_OK:
                outcome += f" ({CO_TRIGGER_OK}는 함께 켜져도 된다)"
            silent = set(SKILLS) - {expect, CO_TRIGGER_OK}
        else:
            outcome = "ux-team 스킬이 하나도 켜지지 않는다"
            silent = set(SKILLS)
        fm = {"description": " · ".join(case["sources"]), "expected_outcome": outcome,
              "tags": ["trigger", f"expect-{expect or 'none'}"], **TRIGGER_FM}
        files[f"{name}/prompt.md"] = frontmatter(fm) + "\n" + case["prompt"] + "\n"
        if expect:
            files[f"{name}/graders/expected-fired.md"] = grader(type="tool_used", tool="Skill", input_match=skill_pattern([expect]))
        files[f"{name}/graders/others-silent.md"] = grader(type="tool_used", tool="Skill", input_match=skill_pattern(silent), min=0, max=0)
    return files


def hello_cases():
    """hello-ux-team 스킬 단위 시험. home-check가 임시 home을 보여 줄 때만 나머지를 돌린다."""
    guide = GUIDE.read_text(encoding="utf-8")
    changed = guide.replace("- 회의 결정이 문서 코멘트보다 우선한다.", "- 회의 결정이 우선한다. (내가 고침)")
    assert changed != guide and "EOF_GUIDE" not in guide

    def scaffold(content):
        return ("#!/bin/bash\nset -eu\nmkdir -p \"$HOME/.claude/rules\"\n"
                "cat > \"$HOME/.claude/rules/ux-team-guide.md\" <<'EOF_GUIDE'\n" + content + "EOF_GUIDE\n")

    base = {"max_turns": 12, "timeout_seconds": 300, "allowed_tools": ["Skill", "Read", "Glob", "Grep"]}
    check = grader(type="tool_used", tool="Bash", input_match=r"sh /[^\" ]+/scripts/install-guide\.sh check")
    no_literal = grader(type="regex", target="trace", pattern=r"\$\{CLAUDE_SKILL_DIR\}/scripts", match="not_contains")
    apply_ran = grader(type="tool_used", tool="Bash", input_match=r"install-guide\.sh apply")
    apply_none = grader(type="tool_used", tool="Bash", input_match=r"install-guide\.sh apply", min=0, max=0)
    files = {
        "home-check/prompt.md": frontmatter({"description": "안전장치: 실행 home이 임시 폴더인지 본다. 아니면 다른 케이스를 돌리지 않는다",
                                             "tags": ["hello", "gate"], "max_turns": 3, "timeout_seconds": 120})
        + "\nBash로 `echo $HOME`을 한 번만 실행하고, 출력된 경로만 그대로 답해 줘.\n",
        "home-check/graders/echo-ran.md": grader(type="tool_used", tool="Bash", input_match=r"echo \$HOME"),
        "first-run/prompt.md": frontmatter({"description": "설치된 파일이 없을 때. check → 묻지 않고 apply (트랙 A 승인 1번). "
                                                           "eval 샌드박스는 home 쓰기를 막으므로 apply가 실패하고, 설치 실패 흐름(통합 체크포인트 2 판단 1번)을 본다",
                                            "tags": ["hello"], **base}) + "\n/ux-team:hello-ux-team\n",
        "first-run/graders/check-with-path.md": check,
        "first-run/graders/no-literal-variable.md": no_literal,
        "first-run/graders/apply-ran.md": apply_ran,
        "first-run/graders/failure-on-top.md": grader(type="regex", pattern=r"^[\s*#>_`-]*팀 지침 설치 못 함"),
        "first-run/graders/connectors-continued.md": grader(type="regex", pattern="Customize › Connectors"),
        "first-run/graders/guide-continued.md": grader(type="regex", pattern="A39pdxytvgJuhiac7Vw3ba"),
        "same-run/case.yaml": 'schema_version: "1.1"\nname: same-run\ncontext:\n  scaffold_script: scaffold.sh\n',
        "same-run/scaffold.sh": scaffold(guide),
        "same-run/prompt.md": frontmatter({"description": "원본과 같은 파일이 이미 있을 때. check → SAME, 쓰지 않음 (ACC-01)",
                                           "tags": ["hello"], **base}) + "\n/ux-team:hello-ux-team\n",
        "same-run/graders/check-with-path.md": check,
        "same-run/graders/apply-not-run.md": apply_none,
        "same-run/graders/says-latest.md": grader(type="regex", pattern="최신"),
        "diff-run/case.yaml": 'schema_version: "1.1"\nname: diff-run\ncontext:\n  scaffold_script: scaffold.sh\n',
        "diff-run/scaffold.sh": scaffold(changed),
        "diff-run/prompt.md": frontmatter({"description": "한 줄 다른 파일이 있을 때. 바뀌는 내용을 보여 주고 묻기만 한다 (트랙 A 승인 1번)",
                                           "tags": ["hello"], **base}) + "\n/ux-team:hello-ux-team\n",
        "diff-run/graders/check-with-path.md": check,
        "diff-run/graders/apply-not-run.md": apply_none,
        "diff-run/graders/asks.md": grader(type="regex", pattern="덮어쓸까요"),
    }
    return files


def write_tree(base, files):
    base.mkdir(parents=True, exist_ok=True)
    keep = set()
    for rel, text in files.items():
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        data = text.encode("utf-8")
        if not (path.exists() and path.read_bytes() == data):
            path.write_bytes(data)
        if path.suffix == ".sh":
            path.chmod(0o755)
        keep.add(rel.split("/")[0])
    for old in base.iterdir():
        if old.is_dir() and old.name not in keep:
            shutil.rmtree(old)
    return len(keep)


def build():
    n_trigger = write_tree(EVALS / "trigger", trigger_cases())
    n_hello = write_tree(EVALS / "hello-ux-team", hello_cases())
    print(f"evals/trigger: 케이스 {n_trigger}개 · evals/hello-ux-team: 케이스 {n_hello}개")


def stage(target):
    dest = pathlib.Path(target).resolve() / "ux-team"
    if dest.exists():
        sys.exit(f"이미 있음: {dest} (새 폴더를 주거나 지운 뒤 다시 실행)")
    ignore = shutil.ignore_patterns(".DS_Store", "__pycache__", "results")
    shutil.copytree(PLUGIN, dest, ignore=ignore)
    shutil.copytree(EVALS, dest / "evals", ignore=ignore)
    print(f"준비됨: {dest}")
    print("트리거 eval (리포트를 claude.ai에 올리지 않음):")
    print(f"  claude plugin eval {dest} --tag trigger --ablation none --no-publish --model sonnet --runs 1 --trust-plugin")
    print("hello-ux-team 단위 시험 (home-check 결과가 임시 home일 때만 나머지를 돌린다):")
    print(f"  claude plugin eval {dest} --case home-check --ablation none --no-publish --model sonnet --runs 1 --trust-plugin --allow-tools 'Bash(echo *)'")


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "build":
        build()
    elif command == "stage" and len(sys.argv) == 3:
        stage(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
