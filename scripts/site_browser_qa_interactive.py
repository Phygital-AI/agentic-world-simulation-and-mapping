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
            def record_failure(request):
                if request.url.endswith("/assets/walkthrough.mp4") and request.failure=="net::ERR_ABORTED":
                    return
                if "/assets/fixed_views/" in request.url and request.failure=="net::ERR_ABORTED":
                    return
                failed.append(f"{request.url}: {request.failure}")
            page.on("requestfailed",record_failure)
            page.goto(a.url.rstrip("/")+"/"+path,wait_until="networkidle",timeout=120_000)
            assert page.locator("h1").inner_text()==("合理，不等于忠实" if lang=="zh" else "Plausible Is Not Faithful")
            for section_id in ("introduction","motivation","method","results","interactive","discussion","limitations","office-cafe"):
                assert page.locator(f"#{section_id}").count()==1
            assert page.locator("#introduction .insight-strip > div").count()==3
            assert page.locator('meta[name="twitter:card"]').get_attribute("content")=="summary_large_image"
            page.wait_for_selector("#table-7 table"); assert page.locator(".table-figure table").count()==7
            table2_headers=page.locator("#table-2 thead th").all_text_contents()
            assert len(table2_headers)==5 and all("配准" not in x and "Alignment" not in x for x in table2_headers)
            table3_headers=page.locator("#table-3 thead th").all_text_contents()
            assert len(table3_headers)==4 and all("SHA256" not in x and "配准" not in x and "Alignment" not in x for x in table3_headers)
            assert page.locator("#table-2").evaluate("(x)=>x.compareDocumentPosition(document.querySelector('#figure-2')) & Node.DOCUMENT_POSITION_FOLLOWING")
            for table_index in range(2,8):
                assert page.locator(f"#table-{table_index} tbody strong").count()>0
            assert page.locator("#figure-1 > img").count()==1
            assert page.locator("#figure-1 > img").get_attribute("src")=="assets/teaser_originals.png"
            assert page.locator("#figure-4").evaluate("(x)=>x.compareDocumentPosition(document.querySelector('#figure-5')) & Node.DOCUMENT_POSITION_FOLLOWING")
            figure3=page.locator("#figure-3"); figure3.scroll_into_view_if_needed()
            page.wait_for_function("document.querySelector('#figure-3').dataset.state === 'ready'",timeout=120_000)
            for method in ("M1","M2","M3","M4","GT"):
                page.select_option("#model-select",method)
                page.wait_for_function("(m)=>{const p=document.querySelector('#figure-3');const d=p.sceneDiagnostics?.();return p.dataset.state==='ready'&&p.dataset.loadedModel===m&&d?.loaded===m&&d.gtLoaded&&d.singleCamera&&d.singleViewport&&(m==='GT'||d.hiddenCutaway>0)}",arg=method,timeout=120_000)
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
            iframe=page.locator("#office-cafe iframe")
            assert iframe.get_attribute("src")=="https://office-cafe-vipe.hiwtishere.chatgpt.site/"
            iframe.scroll_into_view_if_needed()
            office=None
            for _ in range(30):
                page.wait_for_timeout(1000)
                candidate=next((f for f in page.frames if f.url.startswith("https://office-cafe-vipe.hiwtishere.chatgpt.site/")),None)
                if candidate is not None:
                    office=candidate
                    break
            assert office is not None
            office.wait_for_selector("#compare-mode",timeout=120_000)
            if viewport=="desktop" and lang=="zh":
                assert office.locator("#compare-mode option").all_text_contents()==["模型","扫描 ↔ 模型","原视频 ↔ 模型"]
                assert office.locator("#play").get_attribute("aria-label")=="播放原视频相机轨迹"
                assert office.locator("a.shake-link").get_attribute("href")=="./shake.html"
                shake=browser.new_page()
                shake.goto("https://office-cafe-vipe.hiwtishere.chatgpt.site/shake.html",wait_until="domcontentloaded",timeout=120_000)
                assert shake.locator(".run-list button").count()==3
                assert shake.locator(".run-list button").evaluate_all("(xs)=>xs.map(x=>x.dataset.run)") == ["control","gentle","strong"]
                shake.close()
            overflow=page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow,f"horizontal overflow: {viewport}/{lang}"
            assert not errors,errors; assert not failed,failed
            page.screenshot(path=str(out/f"{viewport}-{lang}.png"),full_page=True)
            results.append({"viewport":viewport,"language":lang,"status":"PASS","scene_models":["M1","M2","M3","M4","GT"],"fixed_views":len(loaded_images),"divider_changed":True,"overflow":overflow})
            page.close()
    browser.close()
(out/"report.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":"PASS","output":str(out),"runs":results},ensure_ascii=False))
