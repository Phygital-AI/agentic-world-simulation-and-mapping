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
ap.add_argument("--output",type=Path,default=None)
ap.add_argument("--executable-path",type=Path,default=None); a=ap.parse_args()
out=a.output or Path(tempfile.mkdtemp(prefix="agentic-world-blog-qa-")); out.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
demo_metadata=json.loads((root/"data/embodied_demo.json").read_text(encoding="utf-8"))
demo_media=demo_metadata["media"]
office_origin="https://office-cafe-vipe.hiwtishere.chatgpt.site"
results=[]
with sync_playwright() as pw:
    try: browser=pw.chromium.launch(channel="chromium",headless=True,executable_path=a.executable_path)
    except Exception as e:
        print(json.dumps({"status":"SKIP","reason":f"Playwright browser unavailable: {e}"})); raise SystemExit(0)
    for viewport,size in (("desktop",{"width":1440,"height":1000}),("mobile",{"width":390,"height":844})):
        for lang,path in (("zh","zh.html"),("en","index.html")):
            page=browser.new_page(viewport=size); errors=[]; failed=[]
            page.route(office_origin+"/**",lambda route: route.fulfill(
                status=200,
                content_type="text/html",
                body="<!doctype html><title>External not tested</title><p>external-not-tested</p>",
            ))
            page.on("console",lambda m: errors.append(f"console {m.type}: {m.text}") if m.type=="error" else None)
            page.on("pageerror",lambda e: errors.append(str(e)))
            def record_failure(request):
                if request.url.startswith(office_origin):
                    return
                if request.url.endswith("/assets/walkthrough.mp4") and request.failure=="net::ERR_ABORTED":
                    return
                if "/assets/fixed_views/" in request.url and request.failure=="net::ERR_ABORTED":
                    return
                failed.append(f"{request.url}: {request.failure}")
            page.on("requestfailed",record_failure)
            page.goto(a.url.rstrip("/")+"/"+path,wait_until="networkidle",timeout=120_000)
            assert page.locator("h1").inner_text()==("智能体世界仿真与建图" if lang=="zh" else "Agentic World Simulation and Mapping")
            assert page.locator('nav a[aria-current="page"]').get_attribute("href")==path
            assert page.locator('nav').get_by_role("link",name="中文",exact=True).get_attribute("href")=="zh.html"
            assert page.locator('nav').get_by_role("link",name="EN",exact=True).get_attribute("href")=="index.html"
            for section_id in ("results","motivation","workflow","more-results","related-work","limitations","citation","references"):
                assert page.locator(f"#{section_id}").count()==1
            assert page.locator("#results .insight-strip > div").count()==3
            assert page.locator("#results .tldr").count()==1
            assert page.locator("#motivation .contributions > li").count()==3
            assert page.locator("#workflow .workflow-strip > div").count()==5
            assert page.locator("#related-work > .inline-sources > a").count()==4
            assert page.locator("#citation .citation-block").count()==1
            assert page.locator("#references .references-list > li").count()>=7
            assert page.locator('meta[name="twitter:card"]').get_attribute("content")=="summary_large_image"
            demo=page.locator("#embodied-demo")
            assert demo.count()==1
            video=demo.locator("video")
            assert video.count()==1
            assert video.get_attribute("controls") is not None
            assert video.get_attribute("autoplay") is None
            assert video.get_attribute("poster")==demo_media["poster"]
            assert video.locator("source").count()==1
            assert video.locator("source").get_attribute("src")==demo_media["video"]
            assert video.locator("source").get_attribute("type")=="video/mp4"
            details=demo.locator("details.demo-protocol")
            assert details.count()==1 and not details.get_attribute("open")
            details.locator("summary").click()
            assert details.get_attribute("open") is not None
            h264_support=video.evaluate("v=>v.canPlayType('video/mp4; codecs=\"avc1.42E01E\"')")
            if h264_support:
                video.evaluate("v=>v.load()")
                page.wait_for_function("v=>v.readyState>=1||v.error",arg=video.element_handle(),timeout=30_000)
                video_state=video.evaluate("v=>({status:'PASS',error:v.error&&`${v.error.code}: ${v.error.message}`,duration:v.duration,width:v.videoWidth,height:v.videoHeight,readyState:v.readyState})")
                assert not video_state["error"],f"demo video metadata/H.264 load failed: {video_state['error']}"
                assert video_state["readyState"]>=1,"demo video metadata did not load"
                assert abs(video_state["duration"]-demo_media["duration_s"])<0.25,video_state
                assert video_state["width"]==demo_media["width"] and video_state["height"]==demo_media["height"],video_state
                video.evaluate("async v=>{v.muted=true;await v.play()}")
                page.wait_for_function("v=>v.currentTime>0.1",arg=video.element_handle(),timeout=10_000)
                video.evaluate("v=>v.pause()")
                video_state["video_playback"]="PASS"
            else:
                video_state={"status":"UNSUPPORTED","reason":"browser reports no H.264/AVC MP4 support; metadata not tested"}
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
            assert page.locator("#model-select").input_value()=="M4"
            assert page.locator("#figure-3").get_attribute("data-loaded-model")=="M4"
            for method in ("M1","M2","M3","M4","GT"):
                page.select_option("#model-select",method)
                page.wait_for_function("(m)=>{const p=document.querySelector('#figure-3');const d=p.sceneDiagnostics?.();return p.dataset.state==='ready'&&p.dataset.loadedModel===m&&d?.loaded===m&&d.gtLoaded&&d.singleCamera&&d.singleViewport&&(m==='GT'||d.hiddenCutaway>0)}",arg=method,timeout=120_000)
                if method=="M4":
                    bounds=page.evaluate("document.querySelector('#figure-3').sceneDiagnostics().bounds")
                    assert bounds["min"][0]<18<bounds["max"][0]
                    assert bounds["min"][1]<1.2<bounds["max"][1]
                    assert bounds["min"][2]<-21<bounds["max"][2]
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
            assert iframe.get_attribute("src")==office_origin+"/"
            overflow=page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            assert not overflow,f"horizontal overflow: {viewport}/{lang}"
            assert not errors,errors; assert not failed,failed
            page.screenshot(path=str(out/f"{viewport}-{lang}.png"),full_page=True)
            run_status="PASS" if video_state["status"]=="PASS" else "PARTIAL"
            results.append({"viewport":viewport,"language":lang,"status":run_status,"scene_models":["M1","M2","M3","M4","GT"],"fixed_views":len(loaded_images),"tables":7,"divider_changed":True,"video_metadata":video_state,"external_not_tested":True,"overflow":overflow})
            page.close()
    browser.close()
(out/"report.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
overall_status="PASS" if all(run["status"]=="PASS" for run in results) else "PARTIAL"
print(json.dumps({"status":overall_status,"output":str(out),"runs":results},ensure_ascii=False))
