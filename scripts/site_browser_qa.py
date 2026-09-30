#!/usr/bin/env python3
"""Optional browser QA; exits clearly with code 0 when Playwright is unavailable."""
from pathlib import Path
import argparse, json, sys, tempfile
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({"status":"SKIP","reason":"Playwright is not installed; run: pip install playwright && playwright install chromium"}))
    raise SystemExit(0)

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument("--url",default="http://127.0.0.1:8765/")
ap.add_argument("--output",type=Path,default=None,help="QA output directory (default: temporary directory)")
a=ap.parse_args()
out=a.output or Path(tempfile.mkdtemp(prefix="agentic-world-blog-qa-"))
out.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
    try: browser=pw.chromium.launch(headless=True)
    except Exception as e:
        print(json.dumps({"status":"SKIP","reason":f"Playwright browser unavailable: {e}"}))
        raise SystemExit(0)
    for viewport,size in (("desktop",{"width":1440,"height":1000}),("mobile",{"width":390,"height":844})):
        for lang,path in (("zh","index.html"),("en","en.html")):
            page=browser.new_page(viewport=size)
            errors=[]; failed=[]
            page.on("console",lambda m: errors.append(f"console {m.type}: {m.text}") if m.type=="error" else None)
            page.on("pageerror",lambda e: errors.append(str(e)))
            page.on("requestfailed",lambda r: failed.append(f"{r.url}: {r.failure}"))
            page.goto(a.url.rstrip("/")+"/"+path,wait_until="networkidle")
            page.wait_for_selector("#table-5 table")
            assert page.locator(".table-figure table").count()==5
            assert page.locator("model-viewer").count()==4
            for viewer in page.locator("model-viewer").all():
                viewer.scroll_into_view_if_needed()
                page.wait_for_function("(x) => x.loaded === true", arg=viewer.element_handle(), timeout=45_000)
            for img in page.locator("img").all():
                img.scroll_into_view_if_needed()
                loaded=img.evaluate("""(x) => x.complete
                  ? x.naturalWidth > 0
                  : new Promise(resolve => {
                      x.addEventListener("load", () => resolve(x.naturalWidth > 0), {once:true});
                      x.addEventListener("error", () => resolve(false), {once:true});
                    })""")
                assert loaded, f"image failed: {img.get_attribute('src')}"
            overflow=page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow,f"horizontal overflow: {viewport}/{lang}"
            assert not errors,errors; assert not failed,failed
            page.screenshot(path=str(out/f"{viewport}-{lang}.png"),full_page=True)
            results.append({"viewport":viewport,"language":lang,"status":"PASS","tables":5,"models":4,"overflow":overflow})
            page.close()
    browser.close()
(out/"report.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":"PASS","output":str(out),"runs":results},ensure_ascii=False))
