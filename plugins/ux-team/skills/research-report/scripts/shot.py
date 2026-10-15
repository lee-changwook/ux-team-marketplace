#!/usr/bin/env python3
"""리포트 HTML을 헤드리스 Chrome으로 찍는다. Code 탭(macOS, Chrome 설치) 전용이다.

사용: python3 shot.py <리포트.html> <out.png> [--width 1280] [--height 2400] [--hide "#summary, #answers"] [--print]

- 한글 경로는 임시 폴더에 ASCII 이름으로 복사해서 찍는다
- 헤드리스 Chrome은 스크린샷을 쓰고도 종료하지 않는다. 파일이 생기면 프로세스를 끝낸다
- 스크롤이 안 되니 뒤쪽 섹션은 --hide 로 앞 섹션을 숨겨서 찍는다
- 헤드리스 Chrome의 최소 폭은 500px이다. 그보다 좁으면 그 폭의 iframe에 넣어 찍는다
- --print 는 @media print 를 @media all 로 바꿔 인쇄 레이아웃을 화면에서 본다 (A4 본문 폭은 --width 703)
- 좁은 폭 자르기에 macOS의 sips를 쓴다
"""
import argparse
import os
import pathlib
import shutil
import signal
import subprocess
import tempfile
import time

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
MIN_WIDTH = 500


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=2400)
    ap.add_argument("--hide", default="")
    ap.add_argument("--print", action="store_true", dest="print_mode")
    a = ap.parse_args()
    if not pathlib.Path(CHROME).exists():
        raise SystemExit("Chrome을 찾지 못했습니다. 캡처 검증은 Code 탭에서 Chrome이 있을 때만 쓸 수 있습니다")

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="rr-shot-"))
    page = tmp / "page.html"
    html = pathlib.Path(a.html).read_text(encoding="utf-8")
    if a.print_mode:
        html = html.replace("@media print", "@media all")
    if a.hide:
        html = html.replace("</head>", f"<style>{a.hide} {{ display: none !important; }}</style></head>", 1)
    page.write_text(html, encoding="utf-8")

    target, window = page, a.width
    if a.width < MIN_WIDTH:
        target = tmp / "frame.html"
        target.write_text(
            f'<!doctype html><body style="margin:0;background:#fff;display:flex;justify-content:center">'
            f'<iframe src="page.html" style="width:{a.width}px;height:{a.height}px;border:0"></iframe></body>',
            encoding="utf-8",
        )
        window = MIN_WIDTH

    png = tmp / "shot.png"
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
         f"--user-data-dir={tmp / 'profile'}", "--virtual-time-budget=8000",
         f"--window-size={window},{a.height}", f"--screenshot={png}", target.as_uri()],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
    )
    deadline = time.time() + 40
    last = -1
    while time.time() < deadline:
        time.sleep(0.5)
        if proc.poll() is not None:
            break
        size = png.stat().st_size if png.exists() else -1
        if size > 0 and size == last:
            break
        last = size
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    if not png.exists():
        raise SystemExit("스크린샷이 만들어지지 않았습니다")
    if a.width < MIN_WIDTH:
        subprocess.run(["sips", "--cropToHeightWidth", str(a.height), str(a.width), str(png)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    shutil.copy(png, a.out)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"찍음: {a.out} ({a.width}x{a.height})")


if __name__ == "__main__":
    main()
