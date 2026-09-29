#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8765/');p.add_argument('--output',default='local');a=p.parse_args()
out=ROOT/'qa'/a.output;out.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/google-chrome',headless=True,args=['--no-sandbox'])
    for name,size in [('desktop',{'width':1440,'height':1000}),('mobile',{'width':390,'height':844})]:
        for lang,path in [('zh','index.html'),('en','en.html')]:
            page=browser.new_page(viewport=size,device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('response',lambda r:errors.append(f'HTTP {r.status} {r.url}') if r.status>=400 else None)
            page.goto(a.url.rstrip('/')+'/'+path,wait_until='networkidle')
            page.wait_for_selector('.bar-fill')
            assert page.locator('#trajectory-svg polyline').count()==4
            initial=page.locator('#trajectory-svg polyline').first.get_attribute('points')
            page.select_option('#projection','0,2')
            assert page.locator('#trajectory-svg polyline').first.get_attribute('points')!=initial
            assert '21.62%' in page.locator('#depth-bars').inner_text()
            page.locator('[data-split="modeling_180"]').click()
            assert '19.06%' in page.locator('#depth-bars').inner_text()
            page.select_option('#depth-metric','missing_penalty_mae_m')
            assert '1.3850' in page.locator('#depth-bars').inner_text()
            page.locator('[data-split="eval_500"]').click()
            page.select_option('#depth-metric','absrel')
            page.select_option('#projection','0,1')
            for img in page.locator('img').all():
                img.scroll_into_view_if_needed()
                img.evaluate('(img) => img.decode()')
                assert img.evaluate('(img)=>img.complete && img.naturalWidth>0')
            overflow=page.evaluate('document.documentElement.scrollWidth>window.innerWidth')
            assert not overflow, f'Horizontal page overflow: {name}/{lang}'
            assert not errors,errors
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(out/f'{name}-{lang}.png'),full_page=True)
            results.append({'viewport':name,'language':lang,'status':'PASS','page_errors':errors,'horizontal_overflow':overflow,'tables':page.locator('table').count(),'figures':page.locator('img').count()})
            page.close()
    browser.close()
(out/'report.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
