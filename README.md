# Pumpkin Carver 🎃

A Halloween toy for Char and Vic. It's one self-contained `index.html` (canvas + vanilla JS) that makes no network requests and uses no web fonts, libraries, or images.

**Play:** http://127.0.0.1:4359/ (box) · or open `index.html` / `../out-oct15/pumpkin-carver.html` directly, works offline, AirDrop-able to iPhone/iPad.

## What it does
- **Big glossy pumpkin** with ribbed lobes, sheen, stem, leaf and vine, sitting in a moonlit yard (haunted house, spooky tree, fallen leaves, bats that fly by).
- **Carve freehand** with mouse, finger, or Apple Pencil (the Carve tool). The cut shows the pumpkin's flesh wall, the holes glow with flickering candle light, and pumpkin chips fly out. Carve low and center to see the candle itself.
- **Stamps:** classic triangle eyes, nose, toothy grin, cat, bat, star, and moon. Tap or click to place (on desktop you see a preview first). The **Size** slider sets knife or stamp size.
- **Undo** (button or Ctrl/Cmd+Z) and **Clear**. Clear can also be undone.
- **Lights off** (button or `L`) darkens the night so the carving glows, lighting a warm pool on the ground.
- **Surprise** carves a random face.
- **3 shapes** (Round, Tall, Squat) × **4 colors** (Classic, Cinderella, Ghost, Goblin). Switching keeps your carving.
- **Save** downloads a PNG with a "Happy Halloween!" caption. On iPhone/iPad it opens the Share sheet, so "Save Image" puts it in Photos. If sharing isn't available it falls back to a download.

## Files
- `index.html`: the whole toy
- `tests/test_and_shots.py`: headless Playwright (system Chrome) test + screenshots. Run it with `.venv/bin/python tests/test_and_shots.py` while the server is up.
- `screenshots/`: desktop lights on/off, ghost/tall, iPhone (390×844 @3x, touch), iPad (1180×820)
- `../out-oct15/pumpkin-carver.html` (copy) and `../out-oct15/pumpkin-carver-00-best.png` (best shot)

## Serve
```
cd /workspace/tokenmax/pumpkin-carver && nohup python3 -m http.server 4359 --bind 127.0.0.1 >server.log 2>&1 &
```


---
## Repo notes
- **Built:** Oct 2026 (TokenMax build week; see SHORTLIST/ledger), by TokenMax (Boyd's Grok Bot) on the Grok Bot box.
- **Run:** Open `index.html` in a browser.
- Imported from `/workspace/tokenmax/pumpkin-carver` on Oct 23, 2026. node_modules, virtualenvs, logs and files over 20 MB were left out.
