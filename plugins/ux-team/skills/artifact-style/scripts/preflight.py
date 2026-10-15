#!/usr/bin/env python3
"""UX팀 아티팩트 게시 전 점검.

    python3 scripts/preflight.py <페이지.html>

표준 라이브러리만 쓴다. Chat · Cowork의 실행 환경과 Code 탭에서 모두 돈다.
경로는 스킬 폴더 기준이다. 토큰 원본은 이 파일 옆의 ../references/_shared/tokens.css를 읽는다.

보는 것
  고칠 것 (종료 코드 1)
    - 토큰: tokens.css의 토큰이 같은 값으로 들어 있는지
    - 색값: 토큰 블록 밖의 색값(#…, rgb( 등, 이름 색)
    - 버전 라벨: 제목 · 본문의 v2 · ver · 최종본 같은 표기
  확인할 것 (사람이 보고 판단)
    - 줄바꿈: 서술 문단 한 줄에 문장이 둘 이상인 곳 (불릿은 제외)
    - 범례: 자체 ID(ABC-01 꼴)가 있는데 범례가 있는지
"""
import html.parser
import pathlib
import re
import sys

TOKENS = pathlib.Path(__file__).resolve().parent.parent / "references" / "_shared" / "tokens.css"

DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+)")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
COLOR_RE = re.compile(
    r"#[0-9a-fA-F]{3,8}\b"
    r"|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\("
    r"|(?<![\w.#-])(?:white|black|red|blue|green|gray|grey|orange|yellow|purple|pink|navy|silver|maroon|teal|olive|lime|aqua|fuchsia)(?![\w-])"
)
STYLE_REGION_RE = re.compile(
    r"<style\b[^>]*>(.*?)</style>"
    r"|\sstyle\s*=\s*\"([^\"]*)\""
    r"|\sstyle\s*=\s*'([^']*)'"
    r"|\s(?:fill|stroke|stop-color|flood-color|lighting-color|color)\s*=\s*\"([^\"]*)\"",
    re.S | re.I,
)
VERSION_RE = re.compile(
    r"(?<![A-Za-z])[vV]\d+(?:\.\d+)*\b"
    r"|\b[vV]er(?:sion)?\.?\s*\d"
    r"|버전\s*\d|\d+\s*차\s*(?:수정|개정)|개정판|최종본|최종\s*수정본|수정본|\bfinal\b|\brev\.?\s*\d",
    re.I,
)
ID_RE = re.compile(r"\b[A-Z]{3}-\d{2,3}\b")
SENTENCE_BREAK_RE = re.compile(r"[.?!](?=\s+\S)")
ENUM_RE = re.compile(r"[A-Za-z0-9]{1,3}(?:-\d+)?")  # "D." "3." "A-1." 같은 절 번호는 문장 끝이 아니다

BLOCK_TAGS = {
    "p", "div", "section", "article", "header", "footer", "main", "aside", "nav", "figure", "figcaption",
    "blockquote", "dd", "dt", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "table",
    "tr", "thead", "tbody", "summary", "details", "label", "form", "body", "html",
    "span",  # 카드 안에서 span을 블록처럼 쌓는 일이 많아 경계로 본다
}
SKIP_TAGS = {"script", "style", "pre", "code", "svg", "noscript", "template"}
VOID_TAGS = {"br", "img", "input", "meta", "link", "hr", "source", "wbr", "area", "col", "embed", "track"}


def norm(value):
    return re.sub(r"\s+", " ", value.strip().lower())


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


class TextScan(html.parser.HTMLParser):
    """블록 단위로 글을 모은다. <br>과 블록 · span 경계에서 끊는다. li 안의 글은 불릿으로 보고 줄바꿈 점검에서 뺀다."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.skip = 0
        self.segments = []  # (줄, 글, 불릿 여부)
        self.buf, self.buf_line = [], None
        self.title = []
        self.in_title = False

    def in_li(self):
        return "li" in self.stack

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text:
            self.segments.append((self.buf_line, text, self.in_li()))
        self.buf, self.buf_line = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        if tag in SKIP_TAGS:
            self.skip += 1
            if tag == "code":
                self.buf.append(" CODE ")
            return
        if tag == "br" or tag in BLOCK_TAGS:
            self.flush()
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if tag in BLOCK_TAGS:
            self.flush()
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
            return
        if self.skip:
            return
        if self.buf_line is None and data.strip():
            self.buf_line = self.getpos()[0]
        self.buf.append(data)


def check(path):
    page = path.read_text(encoding="utf-8")
    fix, look = [], []

    # 토큰: tokens.css의 선언(라이트 · 다크)이 같은 값으로 있는지
    token_text = TOKENS.read_text(encoding="utf-8")
    token_pairs = {(n, norm(v)) for n, v in DECL_RE.findall(token_text)}
    regions = []
    for m in STYLE_REGION_RE.finditer(page):
        for g in range(1, 5):
            if m.group(g) is not None:
                regions.append((m.start(g), m.end(g)))
    page_pairs = set()
    allowed = []
    for start, end in regions:
        for comment in COMMENT_RE.finditer(page, start, end):
            allowed.append((comment.start(), comment.end()))
        for d in DECL_RE.finditer(page, start, end):
            pair = (d.group(1), norm(d.group(2)))
            page_pairs.add(pair)
            if pair in token_pairs:
                allowed.append((d.start(), d.end()))
    missing = sorted({n for n, v in token_pairs if (n, v) not in page_pairs})
    if missing:
        fix.append(f"[토큰] tokens.css와 다르거나 빠진 토큰 {len(missing)}개: {', '.join(missing[:8])}"
                   f"{' …' if len(missing) > 8 else ''} → tokens.css를 통째로 다시 붙입니다")

    # 색값: 토큰 선언 밖의 색
    for start, end in regions:
        for c in COLOR_RE.finditer(page, start, end):
            if any(a <= c.start() < b for a, b in allowed):
                continue
            fix.append(f"[색값] {line_of(page, c.start())}행 `{c.group(0)}` → var(--…)나 color-mix로 바꿉니다")

    scan = TextScan()
    scan.feed(page)
    scan.flush()

    # 버전 라벨
    title = " ".join(scan.title).strip()
    for m in VERSION_RE.finditer(title):
        fix.append(f"[버전] 제목 `{m.group(0)}` → 버전 표기를 뺍니다")
    for line, text, _ in scan.segments:
        for m in VERSION_RE.finditer(text):
            fix.append(f"[버전] {line}행 `{m.group(0)}` → 버전 표기를 뺍니다")
    for m in VERSION_RE.finditer(path.name):
        fix.append(f"[버전] 파일 이름 `{m.group(0)}` → 파일 이름에서 뺍니다")

    # 줄바꿈: 불릿이 아닌 글에서 한 줄에 문장이 둘 이상
    for line, text, bullet in scan.segments:
        if bullet:
            continue
        if any(not ENUM_RE.fullmatch(re.search(r"[^\s\"'“‘(\[]*$", text[:m.start()]).group())
               for m in SENTENCE_BREAK_RE.finditer(text)):
            short = text if len(text) <= 60 else text[:57] + "…"
            look.append(f"[줄바꿈] {line}행 한 줄에 문장이 둘 이상: {short}")

    # 범례
    ids = sorted({m.group(0) for _, t, _ in scan.segments for m in ID_RE.finditer(t)})
    if ids:
        look.append(f"[범례] 자체 ID {len(ids)}종({', '.join(ids[:4])}{' …' if len(ids) > 4 else ''}) → 문서 맨 앞에 범례가 있는지 봅니다")

    return fix, look


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = pathlib.Path(sys.argv[1])
    if not path.is_file():
        print(f"파일이 없음: {path}")
        return 2
    fix, look = check(path)
    print(f"점검: {path.name}")
    print(f"\n고칠 것 {len(fix)}건")
    for item in fix:
        print(f"  - {item}")
    print(f"\n확인할 것 {len(look)}건 (예외일 수 있으니 보고 판단합니다)")
    for item in look:
        print(f"  - {item}")
    print("\n스크립트가 보지 않는 것은 references/preflight.md의 점검표로 봅니다.")
    return 1 if fix else 0


if __name__ == "__main__":
    sys.exit(main())
