#!/usr/bin/env python3
"""Exercise both interactive figures on desktop/mobile and zh/en."""
from pathlib import Path
import argparse, json, tempfile
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({"status":"SKIP","reason":"Playwright is not installed; run: pip install playwright && playwright install chromium"}))
    raise SystemExit(0)

ap=argparse.ArgumentParser(); ap.add_argument("--url",default="http://127.0.0.1:8765/")
ap.add_argument("--output",type=Path,default=None); a=ap.parse_args()
out=a.output or Path(tempfile.mkdtemp(prefix="agentic-world-blog-qa-")); out.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
    try: browser=pw.chromium.launch(headless=True)
    except Exception as e:
        print(json.dumps({"status":"SKIP","reason":f"Playwright browser unavailable: {e}"})); raise SystemExit(0)
    for viewport,size in (("desktop",{"width":1440,"height":1000}),("mobile",{"width":390,"height":844})):
        for lang,path in (("zh","index.html"),("en","en.html")):
            page=browser.new_page(viewport=size); errors=[]; failed=[]
            page.on("console",lambda m: errors.append(f"console {m.type}: {m.text}") if m.type=="error" else None)
            page.on("pageerror",lambda e: errors.append(str(e)))
            page.on("requestfailed",lambda r: failed.append(f"{r.url}: {r.failure}"))
            page.goto(a.url.rstrip("/")+"/"+path,wait_until="networkidle",timeout=120_000)
            page.wait_for_selector("#table-5 table"); assert page.locator(".table-figure table").count()==5
            table3_headers=page.locator("#table-3 thead th").all_text_contents()
            assert len(table3_headers)==3 and all("SHA256" not in x and "配准" not in x and "Alignment" not in x for x in table3_headers)
            assert page.locator("#figure-1 .hero-pair-grid img").count()==2
            assert page.locator("#figure-4").evaluate("(x)=>x.compareDocumentPosition(document.querySelector('#figure-5')) & Node.DOCUMENT_POSITION_FOLLOWING")
            figure3=page.locator("#figure-3"); figure3.scroll_into_view_if_needed()
            page.wait_for_function("document.querySelector('#figure-3').dataset.state === 'ready'",timeout=120_000)
            for method in ("M1","M2","M3","M4","GT"):
                page.select_option("#model-select",method)
                page.wait_for_function("(m)=>{const p=document.querySelector('#figure-3');const d=p.sceneDiagnostics?.();return p.dataset.state==='ready'&&p.dataset.loadedModel===m&&d?.loaded===m&&d.gtLoaded&&d.singleCamera&&d.singleViewport}",arg=method,timeout=120_000)
            page.select_option("#model-select","M2"); page.select_option("#scene-mode","compare")
            before=page.evaluate("document.querySelector('#figure-3').sceneDiagnostics()")
            page.locator(".scene-divider").focus(); page.keyboard.press("ArrowRight")
            after=page.evaluate("document.querySelector('#figure-3').sceneDiagnostics()")
            assert after["split"]>before["split"] and after["singleCamera"] and after["singleViewport"]
            page.select_option("#scene-mode","single"); assert page.locator("#scene-split").is_disabled()
            page.click("#scene-reset")
            loaded_images=[]
            for method in ("M1","M2","M3","M4"):
                page.select_option("#compare-method",method)
                for frame in ("0","36","72","108","144"):
                    page.select_option("#compare-frame",frame)
                    page.wait_for_function("([m,f])=>{const x=document.querySelector('#figure-4'),a=document.querySelector('#compare-pred'),b=document.querySelector('#compare-gt'),id=String(f).padStart(3,'0');return x.dataset.method===m&&x.dataset.frame===f&&a.currentSrc.endsWith(`/assets/fixed_views/${m}/${id}.png`)&&b.currentSrc.endsWith(`/assets/fixed_views/GT/${id}.png`)&&a.complete&&a.naturalWidth>0&&b.complete&&b.naturalWidth>0}",arg=[method,frame],timeout=30_000)
                    loaded_images.append(f"{method}/{int(frame):03d}")
            overflow=page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow,f"horizontal overflow: {viewport}/{lang}"
            assert not errors,errors; assert not failed,failed
            page.screenshot(path=str(out/f"{viewport}-{lang}.png"),full_page=True)
            results.append({"viewport":viewport,"language":lang,"status":"PASS","scene_models":["M1","M2","M3","M4","GT"],"fixed_views":len(loaded_images),"divider_changed":True,"overflow":overflow})
            page.close()
    browser.close()
(out/"report.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":"PASS","output":str(out),"runs":results},ensure_ascii=False))
