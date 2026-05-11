#!/usr/bin/env python3
"""Restore Hermes openai-codex credential pool entry from local Windows Codex auth.json.
Does not contain tokens; reads them from C:\Users\chien\.codex\auth.json at runtime.
"""
import json, pathlib, time
HOME=pathlib.Path.home(); HERMES_AUTH=HOME/'.hermes/auth.json'; WINDOWS_CODEX=pathlib.Path('/mnt/c/Users/chien/.codex/auth.json')
if not WINDOWS_CODEX.exists(): raise SystemExit('Windows Codex auth not found: /mnt/c/Users/chien/.codex/auth.json — login to Codex on Windows first.')
if not HERMES_AUTH.exists():
    HERMES_AUTH.parent.mkdir(parents=True, exist_ok=True)
    HERMES_AUTH.write_text(json.dumps({'version':1,'providers':{},'credential_pool':{},'updated_at':None}, indent=2))
codex_link=HOME/'.codex'
if not codex_link.exists(): codex_link.symlink_to('/mnt/c/Users/chien/.codex')
ca=json.loads(WINDOWS_CODEX.read_text()); t=ca.get('tokens', {})
if not t.get('access_token') or not t.get('refresh_token'): raise SystemExit('Codex tokens missing in Windows auth.json — re-login Codex first.')
ha=json.loads(HERMES_AUTH.read_text())
ha.setdefault('credential_pool', {})['openai-codex']=[{'id':'codex01','label':'CODEX_OAUTH','auth_type':'oauth','priority':0,'source':'file:~/.codex/auth.json','access_token':t['access_token'],'refresh_token':t['refresh_token'],'account_id':t.get('account_id',''),'last_status':None,'last_status_at':None,'last_error_code':None,'last_error_reason':None,'last_error_message':None,'last_error_reset_at':None,'base_url':'https://chatgpt.com/backend-api/codex','request_count':0}]
ha['updated_at']=time.strftime('%Y-%m-%dT%H:%M:%S%z')
HERMES_AUTH.write_text(json.dumps(ha, indent=2, ensure_ascii=False))
print('OK: restored openai-codex credential entry in ~/.hermes/auth.json')
