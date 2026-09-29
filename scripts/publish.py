#!/usr/bin/env python3
"""Publish only the clean committed agentic-world-blog repository; no token files."""
from pathlib import Path
import json
import os
import subprocess
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
OWNER='wentingw'
REPO='agentic-world-blog'
REMOTE=f'https://github.com/{OWNER}/{REPO}.git'
HELPER=Path.home()/'.local/lib/sceneweft/git-credential-keyring.py'

def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],check=True,capture_output=True,text=True).stdout.strip()

def main():
    subprocess.run(['python',str(ROOT/'scripts/validate.py')],check=True)
    if git('status','--porcelain'):
        raise SystemExit('Commit the reviewed revision before publishing.')
    if git('remote','get-url','origin')!=REMOTE:
        raise SystemExit('Unexpected repository remote.')
    credentials=subprocess.run([str(HELPER),'get'],input=f'protocol=https\nhost=github.com\nusername={OWNER}\n\n',capture_output=True,text=True,timeout=15)
    if credentials.returncode:raise SystemExit('Desktop GitHub keyring unavailable; unlock it before retrying.')
    token=dict(line.split('=',1) for line in credentials.stdout.splitlines() if '=' in line).get('password')
    if not token:raise SystemExit('No saved GitHub credential. Authenticate without writing a token to this repository.')
    def api(path,method='GET',body=None):
        req=urllib.request.Request('https://api.github.com'+path,method=method,data=json.dumps(body).encode() if body is not None else None,
            headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json','User-Agent':'agentic-world-blog-publisher','X-GitHub-Api-Version':'2022-11-28'})
        try:
            with urllib.request.urlopen(req,timeout=30) as response:
                payload=response.read()
                return response.status,json.loads(payload) if payload else {}
        except urllib.error.HTTPError as error:
            payload=json.loads(error.read())
            return error.code,{'message':payload.get('message'),'errors':payload.get('errors')}
    status,user=api('/user')
    if status!=200 or user.get('login')!=OWNER:raise SystemExit('Credential does not authenticate the expected account.')
    path=f'/repos/{OWNER}/{REPO}'
    status,repo=api(path)
    if status==404:
        status,repo=api('/user/repos','POST',{'name':REPO,'description':'Agentic World: measured camera trajectories, DA3 depth and the path to editable scene programs.','private':False,'auto_init':False,'homepage':f'https://{OWNER}.github.io/{REPO}/'})
        if status!=201:raise SystemExit(f'Repository creation failed: {status} {repo}')
    elif status!=200:raise SystemExit(f'Repository lookup failed: {status}')
    if repo.get('full_name')!=f'{OWNER}/{REPO}' or repo.get('private') or not repo.get('permissions',{}).get('push'):
        raise SystemExit('Repository identity, visibility or push permission does not match the intended publication.')
    # The helper sends the secret over Git's credential pipe, not arguments or URLs.
    result=subprocess.run(['git','-C',str(ROOT),'-c',f'credential.helper={HELPER}','push','-u','origin','main'],capture_output=True,text=True,env={**os.environ,'GIT_TERMINAL_PROMPT':'0'})
    if result.returncode:raise SystemExit('Non-force push failed. Inspect branch state or Git authentication; remote content was not overwritten.')
    status,pages=api(path+'/pages')
    if status==404:
        status,pages=api(path+'/pages','POST',{'build_type':'legacy','source':{'branch':'main','path':'/'}})
        if status!=201:raise SystemExit(f'Pages creation failed: {status} {pages}')
    elif status==200:
        if pages.get('source')!={'branch':'main','path':'/'}:
            status,pages=api(path+'/pages','PUT',{'build_type':'legacy','source':{'branch':'main','path':'/'}})
            if status not in [200,204]:raise SystemExit(f'Pages configuration failed: {status} {pages}')
    else:raise SystemExit(f'Pages lookup failed: {status}')
    build_status,build=api(path+'/pages/builds','POST',{})
    record={'repository':REMOTE.removesuffix('.git'),'commit':git('rev-parse','HEAD'),'url':f'https://{OWNER}.github.io/{REPO}/','pages_build_request_status':build_status,'pages_build_url':build.get('url')}
    (ROOT/'.publication.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__':main()
