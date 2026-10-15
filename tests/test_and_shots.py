"""Headless test + screenshots for Pumpkin Carver (Playwright + system Chrome)."""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent.parent
URL = "http://127.0.0.1:4359/index.html"
SHOTS = HERE / "screenshots"; SHOTS.mkdir(exist_ok=True)
OUT = HERE.parent / "out-oct15"
CHROME = "/usr/bin/google-chrome"
fails, errors, external = [], [], []

def check(name, cond, info=""):
    print(("PASS " if cond else "FAIL ") + name + (f"  [{info}]" if info else ""))
    if not cond: fails.append(name)

def hook(page):
    page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("request", lambda r: external.append(r.url) if not r.url.startswith(("http://127.0.0.1:4359", "data:", "blob:")) else None)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True, args=["--no-sandbox"])
    # ---------- desktop ----------
    ctx = b.new_context(viewport={"width": 1280, "height": 860}, accept_downloads=True)
    page = ctx.new_page(); hook(page)
    page.goto(URL); page.wait_for_function("window.__PC__ && window.__PC__.S.W > 0"); page.wait_for_timeout(400)
    ev = page.evaluate
    check("starts empty", ev("__PC__.ops()") == 0 and ev("__PC__.coverage()") == 0)
    # freehand drawing with real mouse events
    x0, y0 = ev("__PC__.toScreen(-0.4, 0.1)"); x1, y1 = ev("__PC__.toScreen(0.4, 0.2)")
    box = page.locator("#cv").bounding_box()
    page.mouse.move(box["x"] + x0, box["y"] + y0); page.mouse.down()
    for i in range(1, 21):
        t = i / 20; page.mouse.move(box["x"] + x0 + (x1 - x0) * t, box["y"] + y0 + (y1 - y0) * t + 20 * (t - t * t))
    page.mouse.up(); page.wait_for_timeout(100)
    c1 = ev("__PC__.coverage()")
    check("mouse drawing carves", ev("__PC__.ops()") == 1 and c1 > 0.003, f"cov={c1:.4f}")
    # pixel under stroke glows (bright warm) vs untouched skin
    page.screenshot(path=str(SHOTS / "t-stroke.png"))
    # stamp via toolbar + click
    page.click('.tool[data-tool="star"]')
    sx, sy = ev("__PC__.toScreen(0, -0.45)")
    page.mouse.click(box["x"] + sx, box["y"] + sy); page.wait_for_timeout(100)
    c2 = ev("__PC__.coverage()")
    check("star stamp adds carving", ev("__PC__.ops()") == 2 and c2 > c1, f"cov={c2:.4f}")
    for k in ["eyes", "nose", "grin", "cat", "bat", "moon"]:
        before = ev("__PC__.coverage()")
        page.click(f'.tool[data-tool="{k}"]')
        ux, uy = {"eyes": (0, -0.3), "nose": (0, 0), "grin": (0, 0.42), "cat": (-0.75, 0.2), "bat": (0.6, -0.6), "moon": (0.8, 0.15)}[k]
        sx, sy = ev(f"__PC__.toScreen({ux}, {uy})"); page.mouse.click(box["x"] + sx, box["y"] + sy); page.wait_for_timeout(60)
        check(f"stamp {k}", ev("__PC__.coverage()") > before)
    n = ev("__PC__.ops()")
    # undo via button
    before = ev("__PC__.coverage()"); page.click("#undoBtn"); page.wait_for_timeout(60)
    check("undo button removes last op", ev("__PC__.ops()") == n - 1 and ev("__PC__.coverage()") < before)
    # undo via keyboard
    page.keyboard.press("Control+z"); page.wait_for_timeout(60)
    check("ctrl+z undo", ev("__PC__.ops()") == n - 2)
    # clear + undo restores
    cov = ev("__PC__.coverage()"); page.click("#clearBtn"); page.wait_for_timeout(60)
    check("clear empties pumpkin", ev("__PC__.coverage()") == 0)
    page.click("#undoBtn"); page.wait_for_timeout(60)
    check("undo after clear restores", abs(ev("__PC__.coverage()") - cov) < 1e-6)
    # lights off: scene darker, carving brighter-ish contrast
    lum = """(() => { const c=document.getElementById('cv'), g=c.getContext('2d'); __PC__.redraw();
      const sample=(x,y)=>{const d=g.getImageData(x,y,1,1).data;return (d[0]*.3+d[1]*.59+d[2]*.11)};
      const s=__PC__.S; return {corner: sample(Math.round(s.W*0.5*s.dpr), Math.round(s.H*0.08*s.dpr)), skin: sample(Math.round((s.cx+0.85*s.R)*s.dpr), Math.round((s.cy-0.3*s.R)*s.dpr))}; })()"""
    on = ev(lum)
    page.click("#lightsBtn"); page.wait_for_timeout(200)
    off = ev(lum)
    check("lights-off darkens scene", ev("!__PC__.S.lights") and off["corner"] < on["corner"] * 0.5 and off["skin"] < on["skin"] * 0.6, f"on={on} off={off}")
    check("body has dark class", ev("document.body.classList.contains('dark')"))
    page.click("#lightsBtn"); page.wait_for_timeout(100)
    check("lights back on", ev("__PC__.S.lights"))
    # shape + color switches keep carving
    cov = ev("__PC__.coverage()")
    page.click('.chip[data-shape="tall"]'); page.click('.swatch[data-color="ghost"]'); page.wait_for_timeout(100)
    check("shape/color switch", ev("__PC__.S.shape") == "tall" and ev("__PC__.S.color") == "ghost" and ev("__PC__.coverage()") > 0)
    page.screenshot(path=str(SHOTS / "02-ghost-tall-lights-on.png"))
    page.click('.chip[data-shape="round"]'); page.click('.swatch[data-color="classic"]')
    # save png -> download
    with page.expect_download() as dl:
        page.click("#saveBtn")
    d = dl.value; path = SHOTS / "t-export.png"; d.save_as(str(path))
    check("save PNG downloads a png", path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" and path.stat().st_size > 20000, f"{d.suggested_filename} {path.stat().st_size}B")
    # surprise
    ev("__PC__.surprise(5)"); check("surprise face", ev("__PC__.coverage()") > 0.01)
    # ---------- best shot: programmatic demo face, lights off ----------
    ev("__PC__.demo(); __PC__.setLights(false); document.getElementById('hint').style.opacity=0; document.getElementById('toast').classList.remove('on')")
    page.mouse.move(5, 5); page.wait_for_timeout(1500)
    page.screenshot(path=str(OUT / "pumpkin-carver-00-best.png"))
    page.screenshot(path=str(SHOTS / "00-best-lights-off.png"))
    ev("__PC__.setLights(true)"); page.wait_for_timeout(300)
    page.screenshot(path=str(SHOTS / "01-demo-lights-on.png"))
    ctx.close()

    # ---------- iPhone-ish touch ----------
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True,
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1")
    page = ctx.new_page(); hook(page)
    page.goto(URL); page.wait_for_function("window.__PC__ && window.__PC__.S.W > 0"); page.wait_for_timeout(300)
    ev = page.evaluate
    no_overflow = ev("document.documentElement.scrollWidth <= innerWidth + 1")
    check("iphone: no horizontal overflow", no_overflow)
    offs = ev("[...document.querySelectorAll('button')].filter(b => { const r = b.getBoundingClientRect(); return r.right > innerWidth + 0.5 || r.left < -0.5 || r.bottom > innerHeight + 0.5; }).map(b => b.title || b.id)")
    check("iphone: every button fully on screen", not offs, str(offs))
    check("iphone: pumpkin fits", ev("(() => { const s=__PC__.S; return s.cx - 1.32*1.04*s.R >= 0 || s.R*1.12*1.04*2 <= s.W; })()"))
    page.tap('.tool[data-tool="grin"]')
    sx, sy = ev("__PC__.toScreen(0, 0.3)"); box = page.locator("#cv").bounding_box()
    page.touchscreen.tap(box["x"] + sx, box["y"] + sy); page.wait_for_timeout(100)
    check("iphone: tap stamps grin", ev("__PC__.ops()") == 1 and ev("__PC__.coverage()") > 0.005)
    # touch drag via CDP touch events
    cdp = ctx.new_cdp_session(page)
    page.tap('.tool[data-tool="knife"]')
    pts = [ev(f"__PC__.toScreen({-0.5 + i * 0.05}, -0.35)") for i in range(21)]
    tp = lambda x, y: [{"x": box["x"] + x, "y": box["y"] + y, "id": 1}]
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": tp(*pts[0])})
    for q in pts[1:]: cdp.send("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": tp(*q)})
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []}); page.wait_for_timeout(150)
    check("iphone: touch drag carves", ev("__PC__.ops()") == 2, f"ops={ev('__PC__.ops()')}")
    page.tap("#lightsBtn"); page.wait_for_timeout(200)
    check("iphone: lights toggle by tap", ev("!__PC__.S.lights"))
    ev("__PC__.demo(); document.getElementById('hint').style.opacity=0"); page.wait_for_timeout(1200)
    page.screenshot(path=str(SHOTS / "03-iphone-lights-off.png"))
    ctx.close()

    # ---------- iPad landscape ----------
    ctx = b.new_context(viewport={"width": 1180, "height": 820}, device_scale_factor=2, is_mobile=True, has_touch=True)
    page = ctx.new_page(); hook(page); page.goto(URL); page.wait_for_function("window.__PC__ && window.__PC__.S.W > 0")
    page.evaluate("__PC__.surprise(3); document.getElementById('hint').style.opacity=0"); page.wait_for_timeout(900)
    page.screenshot(path=str(SHOTS / "04-ipad-surprise.png"))
    ctx.close(); b.close()

check("no console errors", not errors, "; ".join(errors[:5]))
check("no external network requests", not external, "; ".join(external[:5]))
print(json.dumps({"fails": fails}))
sys.exit(1 if fails else 0)
