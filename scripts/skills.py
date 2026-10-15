#!/usr/bin/env python3
"""UX팀 플러그인 저장소 도구.

    python3 scripts/skills.py sync              shared/ 원본을 MAP.tsv대로 각 스킬의 references/_shared/에 복사한다
    python3 scripts/skills.py check [스킬 ...]   스킬 규칙을 점검한다. 문제가 있으면 종료 코드 1

트랙 세션은 자기 스킬 이름을 주어 check한다. 다른 트랙의 폴더는 작업 중일 수 있다.
sync는 내용이 같은 파일을 다시 쓰지 않는다. 여러 세션이 함께 돌려도 서로 덮지 않게 하기 위해서다.

check가 보는 것
  - frontmatter: 폴더 이름 = name, 필수 · 허용 키(리드 user scope 스킬과 같은 필드), description 200자 이내,
    disable-model-invocation 값, relates가 이 플러그인의 스킬인지, triggers 키워드가 description에 있는지
  - description이 docs/01-트리거 지도.md에 그대로 있는지 (트리거 문구는 지도에서 먼저 고친다)
  - 리드 전용 흔적: 절대경로, 리드 개인 CLI, 다른 스킬 폴더 참조
  - references/_shared/ 사본이 shared/ 원본과 같은지
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "ux-team" / "skills"
SHARED = ROOT / "shared"
MAP_FILE = SHARED / "MAP.tsv"
TRIGGER_MAP = ROOT / "docs" / "01-트리거 지도.md"

# 리드 user scope 스킬이 쓰는 필드를 그대로 쓴다 (docs/00-명세.md DEC-16)
REQUIRED_KEYS = {"name", "version", "description", "author", "relates", "disable-model-invocation"}
ALLOWED_KEYS = REQUIRED_KEYS | {"argument-hint", "triggers", "user-invocable", "allowed-tools",
                                "metadata", "license", "tags", "dependencies", "hooks"}
MANUAL_ONLY = {"hello-ux-team"}
AUTHOR = "lee-changwook"
DESC_MAX = 200
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SHARED_DIR = ("references", "_shared")
SHARED_README = "README.md"
SHARED_README_TEXT = (
    "이 폴더의 파일은 저장소의 shared/에서 복사됩니다.\n"
    "직접 고치지 말고 shared/ 원본을 고친 뒤 `python3 scripts/skills.py sync`를 실행하세요.\n"
)
FORBIDDEN = [
    (re.compile(r"/Users/"), "절대경로"),
    (re.compile(r"woogy"), "리드 계정명"),
    (re.compile(r"~/dada"), "리드 작업공간 경로"),
    (re.compile(r"obsidian/노트|옵시디언"), "리드 vault 경로"),
    (re.compile(r"clickup-cli|\bclkup\b"), "리드 개인 CLI (ClickUp은 커넥터로)"),
    (re.compile(r"agent-slack"), "리드 개인 CLI (Slack은 커넥터로)"),
    (re.compile(r"\bapidog\b"), "리드 개인 CLI"),
    (re.compile(r"\bgh (pr|api|repo|run|issue|release|gist)\b"), "리드 개인 CLI (gh)"),
    (re.compile(r"\.claude/skills/"), "다른 스킬 폴더 참조"),
]
TEXT_EXT = {".md", ".txt", ".py", ".sh", ".js", ".mjs", ".css", ".html", ".json", ".swift", ".yaml", ".yml", ".tsv"}


def read_map():
    rows = []
    for line in MAP_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        src, _, targets = line.partition("\t")
        rows.append((src.strip(), targets.split()))
    return rows


def expected_shared():
    want = {}
    for src, targets in read_map():
        for skill in targets:
            want.setdefault(skill, set()).add(src)
    return want


def write_if_changed(path, data):
    if path.exists() and path.read_bytes() == data:
        return
    path.write_bytes(data)


def sync():
    want = expected_shared()
    for skill, files in sorted(want.items()):
        skill_dir = SKILLS / skill
        if not skill_dir.is_dir():
            print(f"[건너뜀] 스킬 폴더 없음: {skill}")
            continue
        dest = skill_dir.joinpath(*SHARED_DIR)
        dest.mkdir(parents=True, exist_ok=True)
        for old in dest.iterdir():
            if old.name != SHARED_README and old.name not in files:
                old.unlink(missing_ok=True)
        write_if_changed(dest / SHARED_README, SHARED_README_TEXT.encode("utf-8"))
        for name in sorted(files):
            write_if_changed(dest / name, (SHARED / name).read_bytes())
        print(f"[복사] {skill}: {', '.join(sorted(files))}")


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def frontmatter(path):
    """최상위 키마다 (한 줄 값, 아래 들여쓴 줄들)을 돌려준다."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, "frontmatter가 없음"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "frontmatter 닫는 줄(---)이 없음"
    data, current = {}, None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            current = m.group(1)
            data[current] = (unquote(m.group(2)), [])
        elif current and line[:1] in (" ", "\t", "-"):
            data[current][1].append(line)
        else:
            return None, f"frontmatter 줄을 읽을 수 없음: {line!r}"
    return data, None


def list_items(lines):
    return [unquote(re.sub(r"^\s*-\s*", "", l)) for l in lines if re.match(r"^\s*-\s+", l)]


def check(names):
    problems = []
    trigger_text = TRIGGER_MAP.read_text(encoding="utf-8") if TRIGGER_MAP.exists() else ""
    want = expected_shared()
    skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir())
    if names:
        unknown = sorted(set(names) - {p.name for p in skill_dirs})
        if unknown:
            print(f"없는 스킬: {', '.join(unknown)}")
            return 2
        skill_dirs = [p for p in skill_dirs if p.name in names]
    for skill_dir in skill_dirs:
        name = skill_dir.name
        found = []
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            found.append("SKILL.md가 없음")
        else:
            data, err = frontmatter(skill_md)
            if err:
                found.append(err)
            else:
                value = lambda key: data.get(key, ("", []))[0]
                missing = REQUIRED_KEYS - set(data)
                if missing:
                    found.append(f"필수 frontmatter 키 없음: {', '.join(sorted(missing))}")
                extra = set(data) - ALLOWED_KEYS
                if extra:
                    found.append(f"허용하지 않는 frontmatter 키: {', '.join(sorted(extra))}")
                if value("name") != name:
                    found.append(f"name({value('name')!r})이 폴더 이름과 다름")
                if not NAME_RE.match(name) or "claude" in name or "anthropic" in name:
                    found.append("폴더 이름 규칙 위반 (소문자 · 숫자 · 하이픈, claude · anthropic 금지)")
                desc = value("description")
                if "description" in data and data["description"][1]:
                    found.append("description은 한 줄로 쓴다")
                if not desc:
                    found.append("description이 비어 있음")
                elif len(desc) > DESC_MAX:
                    found.append(f"description이 {len(desc)}자 (최대 {DESC_MAX}자)")
                if desc and desc not in trigger_text:
                    found.append("description이 docs/01-트리거 지도.md와 다름")
                if "author" in data and value("author") != AUTHOR:
                    found.append(f"author는 {AUTHOR}여야 함")
                want_flag = "true" if name in MANUAL_ONLY else "false"
                if "disable-model-invocation" in data and value("disable-model-invocation") != want_flag:
                    found.append(f"disable-model-invocation은 {want_flag}여야 함")
                if "relates" in data:
                    for rel in list_items(data["relates"][1]):
                        if not (SKILLS / rel).is_dir():
                            found.append(f"relates에 이 플러그인에 없는 스킬: {rel}")
                if "triggers" in data:
                    for kw in list_items(data["triggers"][1]):
                        if kw not in desc:
                            found.append(f"triggers 키워드가 description에 없음: {kw}")
        for path in skill_dir.rglob("*"):
            if not path.is_file() or path.suffix not in TEXT_EXT:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern, label in FORBIDDEN:
                for m in pattern.finditer(text):
                    line_no = text.count("\n", 0, m.start()) + 1
                    found.append(f"{label}: {path.relative_to(skill_dir)}:{line_no} `{m.group(0)}`")
        shared_dir = skill_dir.joinpath(*SHARED_DIR)
        for src in sorted(want.get(name, set())):
            copy = shared_dir / src
            if not copy.exists():
                found.append(f"공유 사본 없음: {src} (sync 필요)")
            elif copy.read_bytes() != (SHARED / src).read_bytes():
                found.append(f"공유 사본이 원본과 다름: {src} (sync 필요)")
        if shared_dir.is_dir():
            for extra in shared_dir.iterdir():
                if extra.name != SHARED_README and extra.name not in want.get(name, set()):
                    found.append(f"MAP에 없는 공유 사본: {extra.name}")
        status = "통과" if not found else f"문제 {len(found)}건"
        print(f"[{status}] {name}")
        for item in found:
            print(f"    - {item}")
        problems.extend(found)
    print(f"\n스킬 {len(skill_dirs)}개 · 문제 {len(problems)}건")
    return 1 if problems else 0


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "sync":
        sync()
    elif command == "check":
        sys.exit(check(sys.argv[2:]))
    else:
        print(__doc__)
        sys.exit(2)
