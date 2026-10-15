#!/usr/bin/env python3
"""조립한 리포트 HTML을 헤드리스 브라우저로 A4 PDF로 만든다.

사용: python3 to_pdf.py <리포트.html> [--out <파일.pdf>] [--check]

- 기본 출력은 리포트 옆의 같은 이름 .pdf
- --check 는 만들 수 있는지만 보고 끝낸다
- 브라우저: macOS의 Chrome · Chromium · Edge 앱, PATH의 chromium · google-chrome 등, Playwright가 받아 둔 Chromium
- 리눅스 실행 환경(Chat · Cowork)이면 한글 글꼴이 있는지 본다. 없으면 글자가 깨지므로 만들지 않는다
- 리포트는 render.js로 답변을 그리므로, JavaScript를 돌리는 브라우저가 있어야 템플릿 그대로 나온다
- 한글 경로는 임시 폴더에 ASCII 이름으로 복사해서 돌린다. 헤드리스 Chrome은 PDF를 쓰고도 종료하지 않을 때가 있어 시간 제한을 건다

종료 코드: 0 만듦(또는 --check 통과), 3 이 환경에서는 만들 수 없음(이유를 출력), 1 그 밖의 실패
"""
import argparse
import glob
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import tempfile
import time

CANNOT = 3
MAC_APPS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "microsoft-edge"]
PLAYWRIGHT = [
    "~/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
    "~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
]


def find_browser():
    for path in MAC_APPS:
        if os.path.exists(path):
            return path
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for pattern in PLAYWRIGHT:
        hits = sorted(glob.glob(os.path.expanduser(pattern)))
        if hits:
            return hits[-1]
    return None


def has_korean_font():
    if sys.platform == "darwin":
        return True
    if not shutil.which("fc-list"):
        return False
    out = subprocess.run(["fc-list", ":lang=ko", "family"], capture_output=True, text=True).stdout
    return bool(out.strip())


def cannot(reason):
    print(f"PDF를 만들 수 없습니다: {reason}")
    print("대안: HTML만 받기 / HTML을 브라우저에서 열고 인쇄 › PDF로 저장 / Code 탭에서 다시 요청")
    return CANNOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    browser = find_browser()
    if not browser:
        return cannot("이 실행 환경에 헤드리스 브라우저(Chrome · Chromium · Edge)가 없습니다")
    if not has_korean_font():
        return cannot("이 실행 환경에 한글 글꼴이 없어 글자가 깨집니다")
    if a.check:
        print(f"만들 수 있습니다: {browser}")
        return 0

    src = pathlib.Path(a.html).resolve()
    out = pathlib.Path(a.out) if a.out else src.with_suffix(".pdf")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rr-pdf-"))
    page = tmp / "report.html"
    shutil.copy(src, page)
    pdf = tmp / "report.pdf"

    cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
           f"--user-data-dir={tmp / 'profile'}", "--virtual-time-budget=8000",
           f"--print-to-pdf={pdf}", page.as_uri()]
    if sys.platform.startswith("linux"):
        cmd.insert(1, "--no-sandbox")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    deadline = time.time() + 40
    last = -1
    while time.time() < deadline:
        time.sleep(0.5)
        size = pdf.stat().st_size if pdf.exists() else -1
        if proc.poll() is not None or (size > 0 and size == last):
            break
        last = size
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    if not pdf.exists() or pdf.stat().st_size == 0 or not pdf.read_bytes().startswith(b"%PDF"):
        shutil.rmtree(tmp, ignore_errors=True)
        print("PDF가 만들어지지 않았습니다. 브라우저 실행에 실패했습니다")
        return 1
    data = pdf.read_bytes()
    pages = data.count(b"/Type /Page") - data.count(b"/Type /Pages")
    shutil.copy(pdf, out)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"만듦: {out} ({pages}쪽)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
