---
name: 3ai-consult
category: software-development
description: 3AI 廉價諮詢管道 — 使用 Gemini API 直接呼叫，0 OpenRouter tokens
version: 1.0
---

# 3AI Consultation Skill

## 觸發條件
使用者輸入 `~!` 開頭的訊息時觸發。

## 流程
1. 解析 `~!` 後面的問題/議題
2. 呼叫 Gemini 2.5 Flash API（Google 搜尋 grounding 自動啟用）
3. 回傳結果到對話視窗

## 實作

```python
import json, urllib.request, os

def gemini_consult(question):
    """Call Gemini API - 0 OpenRouter tokens"""
    with open(os.path.expanduser("~/.hermes/.env")) as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                GK = line.strip().split("=", 1)[1]
                break
    
    body = json.dumps({
        "contents": [{"parts": [{"text": 
            "你是專業 AI 分析師，使用繁體回答。請針對以下議題進行深度分析，如果需要網路搜尋補充最新資訊，請善用搜尋能力。條理分明，附上資料來源。\n\n議題：" + question
        }]}]
    }).encode()
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + GK
    req = urllib.request.Request(url, data=body, 
                                headers={"Content-Type": "application/json"},
                                method="POST")
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read().decode())
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return "❌ Gemini 回覆失敗: " + str(e)[:200]
```

## 成本
- OpenRouter tokens: **0**
- Google Gemini API: **免費額度內**

## 擴充計畫
- Phase 2: 加入 Claude Code（需 Anthropic API Key）
- Phase 3: 加入 Codex CLI（需安裝）
- 最終: n8n 管道 Gemini → Claude → Codex → 結果
