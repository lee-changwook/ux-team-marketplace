#!/usr/bin/env python3
"""기능 사용 설명서 원고(.md) → PDF.  (feature-guide 스킬)

이미지를 HTML에 내장하고 Chrome headless로 인쇄한다. 디자인은 ../templates/의
manual.css(정본) 위에 guide-extra.css를 덧붙이고, 표지 로고는 logo.webp를 쓴다.
macOS 기본 Python 3.9에서도 돈다.

usage: build_guide.py <원고.md> -o <out.pdf> [--assets <캡처 폴더>] [--keep-html]

원고 문법
---------
    ---                                  프론트매터: title · kicker · subtitle · date · footer · footer_left
    (첫 ## 앞 내용)                       표지 쪽 본문(한 장 요약)
    ## 1단계 · 제목                        새 쪽에서 시작하는 단계
    ### 소제목                             단계 안 소제목 (이럴 땐 이렇게의 질문 등)
    ![캡션](파일.png)                      캡처 (가로 전체)
    ![캡션](파일.png){side}                캡처를 왼쪽에 두고 바로 아래 번호 목록을 오른쪽에
    ![캡션](파일.png){w=60%}               캡처 폭 지정 (가운데 정렬)
    1. 설명                                번호 설명 (캡처의 번호 배지와 같은 모양)
    - 설명                                 불릿
    > 짚어둘 것                            콜아웃
    그 밖의 줄                             문단
"""
from __future__ import annotations

import argparse
import base64
import html
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]
RE_IMG = re.compile(r"^!\[(.*?)\]\((.+?)\)(\{(.+?)\})?\s*$")
RE_NUM = re.compile(r"^(\d+)\.\s+(.+)$")
RE_BULLET = re.compile(r"^-\s+(.+)$")


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def resolve_img(base: Path, ref: str, assets: Path | None = None):
    """정확한 파일명 → 없으면 `<선행 숫자>_*` 접두 매칭으로 폴백.

    원고는 `![](3.png)` 처럼 번호만 적어도 되고, 캡처가
    `3_출결관리-보호자HP.png` 로 들어오면 그대로 붙는다.
    """
    dirs = [d for d in (base, assets) if d]
    for d in dirs:
        if (d / ref).exists():
            return d / ref
    m = re.match(r"^(\d+)", Path(ref).stem)
    if not m:
        return None
    for d in dirs:
        hits = sorted(q for q in d.glob(f"{m.group(1)}_*")
                      if q.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"})
        if hits:
            return hits[0]
    return None


def inline(text: str) -> str:
    """**굵게** · `코드` · 나머지는 이스케이프."""
    out, i = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|`(.+?)`", text):
        out.append(html.escape(text[i:m.start()]))
        if m.group(1) is not None:
            out.append(f"<strong>{html.escape(m.group(1))}</strong>")
        else:
            out.append(f"<strong>{html.escape(m.group(2))}</strong>")
        i = m.end()
    out.append(html.escape(text[i:]))
    return "".join(out)


def to_pdf(html_path: Path, out: Path):
    chrome = next((c for c in CHROME_CANDIDATES if c and Path(c).exists()), None)
    if not chrome:
        sys.exit("❌ Chrome을 찾지 못했습니다. Google Chrome을 설치하십시오.")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", f"--print-to-pdf={out}", html_path.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not out.exists():
        sys.exit(f"❌ PDF 생성 실패\n{r.stderr[-1500:]}")


def parse(src: Path):
    lines = src.read_text(encoding="utf-8").split("\n")
    meta, start = {}, 0
    if lines and lines[0].strip() == "---":
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
        for l in lines[1:end]:
            if ":" in l:
                k, v = l.split(":", 1)
                meta[k.strip()] = v.strip()
        start = end + 1
    pages = [{"title": None, "blocks": []}]
    for raw in lines[start:]:
        l = raw.rstrip()
        s = l.strip()
        if not s:
            pages[-1]["blocks"].append(("gap", "", ""))
            continue
        if s.startswith("## "):
            pages.append({"title": s[3:].strip(), "blocks": []})
        elif s.startswith("### "):
            pages[-1]["blocks"].append(("h3", s[4:].strip(), ""))
        elif m := RE_IMG.match(s):
            pages[-1]["blocks"].append(("img", m.group(1).strip(), (m.group(2).strip(), m.group(4) or "")))
        elif m := RE_NUM.match(s):
            pages[-1]["blocks"].append(("num", m.group(2).strip(), m.group(1)))
        elif m := RE_BULLET.match(s):
            pages[-1]["blocks"].append(("li", m.group(1).strip(), ""))
        elif s.startswith("> "):
            pages[-1]["blocks"].append(("note", s[2:].strip(), ""))
        else:
            pages[-1]["blocks"].append(("p", s, ""))
    return meta, pages


def render_blocks(blocks, base: Path, assets: Path | None, missing: list) -> str:
    o = []
    i = 0
    n = len(blocks)

    def figure(cap, ref, opt):
        p = resolve_img(base, ref, assets)
        if p is None:
            missing.append(ref)
            return f'<figure class="missing">캡처 없음: {html.escape(ref)}</figure>'
        style = ""
        if opt.startswith("w="):
            style = f' style="width:{html.escape(opt[2:])}"'
        capt = f"<figcaption>{inline(cap)}</figcaption>" if cap else ""
        return f'<figure{style}><img src="{data_uri(p)}">{capt}</figure>'

    def take_run(kind):
        nonlocal i
        # 같은 종류가 이어지는 동안 한 목록으로 묶는다(사이의 빈 줄 하나는 건너뜀)
        items = []
        while i < n:
            if blocks[i][0] == kind:
                items.append(blocks[i])
                i += 1
            elif blocks[i][0] == "gap" and i + 1 < n and blocks[i + 1][0] == kind:
                i += 1
            else:
                break
        return items

    def num_list(items):
        return '<ol class="steps">' + "".join(
            f'<li><span class="num">{html.escape(k)}</span><span>{inline(t)}</span></li>'
            for _, t, k in items
        ) + "</ol>"

    while i < n:
        kind, a, b = blocks[i]
        if kind == "gap":
            i += 1
        elif kind == "img":
            ref, opt = b
            i += 1
            if opt.startswith("side"):
                # 바로 뒤(빈 줄 건너뜀) 번호 목록을 오른쪽 칸에. {side=55%}로 캡처 폭 지정
                while i < n and blocks[i][0] == "gap":
                    i += 1
                items = take_run("num") if i < n and blocks[i][0] == "num" else []
                width = opt.split("=", 1)[1] if "=" in opt else ""
                style = f' style="width:{html.escape(width)}"' if width else ""
                fig = figure(a, ref, "").replace("<figure", f"<figure{style}", 1)
                o.append(f'<div class="side">{fig}'
                         f'<div class="side-body">{num_list(items)}</div></div>')
            else:
                o.append(figure(a, ref, opt))
        elif kind == "num":
            o.append(num_list(take_run("num")))
        elif kind == "li":
            items = take_run("li")
            o.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for _, t, _ in items) + "</ul>")
        elif kind == "note":
            o.append(f'<div class="note">{inline(a)}</div>')
            i += 1
        elif kind == "h3":
            o.append(f"<h3>{inline(a)}</h3>")
            i += 1
        else:
            o.append(f"<p>{inline(a)}</p>")
            i += 1
    return "\n".join(o)


def render(meta, pages, base: Path, assets: Path | None) -> str:
    css = (TEMPLATES / "manual.css").read_text(encoding="utf-8")
    css += "\n" + (TEMPLATES / "guide-extra.css").read_text(encoding="utf-8")
    logo = TEMPLATES / "logo.webp"
    brand = (f'<img src="{data_uri(logo)}" alt="티키타">'
             if meta.get("logo", "tikita") == "tikita" and logo.exists()
             else f'<span class="wordmark">{html.escape(meta.get("brand", "티키타"))}</span>')
    missing: list = []
    o = [f'<div class="masthead">{brand}<span class="kicker">{html.escape(meta.get("kicker", "사용 설명서"))}</span></div>',
         '<div class="lede">', f'<h1>{inline(meta.get("title", "사용 설명서"))}</h1>']
    if meta.get("date"):
        o.append(f'<div class="date">{html.escape(meta["date"])}</div>')
    if meta.get("subtitle"):
        o.append(f'<div class="subtitle">{inline(meta["subtitle"])}</div>')
    o.append("</div>")

    cover, *steps = pages
    o.append(f'<section class="cover-body">{render_blocks(cover["blocks"], base, assets, missing)}</section>')
    for pg in steps:
        o.append('<section class="page">')
        o.append(f'<div class="page-head"><h2>{inline(pg["title"])}</h2></div>')
        o.append(render_blocks(pg["blocks"], base, assets, missing))
        o.append("</section>")

    o.append(f'<div class="docfoot"><span>{html.escape(meta.get("footer_left", meta.get("title", "")))}</span>'
             f'<span>{html.escape(meta.get("footer", ""))}</span></div>')
    if missing:
        print("⚠️  이미지를 찾지 못해 자리만 남김:", ", ".join(missing), file=sys.stderr)
    title = html.escape(meta.get("title", "사용 설명서"))
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{title}</title>'
            f"<style>{css}</style></head><body>" + "\n".join(o) + "</body></html>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--assets")
    ap.add_argument("--keep-html", action="store_true")
    a = ap.parse_args()

    src = Path(a.src).expanduser().resolve()
    assets = Path(a.assets).expanduser().resolve() if a.assets else None
    meta, pages = parse(src)
    doc = render(meta, pages, src.parent, assets)
    out = Path(a.out).expanduser().resolve()
    hp = (out.parent / f".{out.stem}.build.html") if a.keep_html else Path(tempfile.mkdtemp()) / "manual.html"
    hp.write_text(doc, encoding="utf-8")
    to_pdf(hp, out)
    n_img = doc.count('<img src="data:image/png')
    print(f"✅ {out}  ({len(pages) - 1}개 단계 쪽 · 이미지 {n_img}장 · {out.stat().st_size // 1024}KB)")
    if a.keep_html:
        print(f"   HTML: {hp}")


if __name__ == "__main__":
    main()
