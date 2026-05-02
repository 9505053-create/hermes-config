---
name: pipeline-dry-run
description: Manually trigger, monitor, and verify a multi-phase cron pipeline end-to-end — diagnose silent failures via session files and fall back to manual execution when needed.
version: 1.0.0
---

# Pipeline Dry-Run & Verification

## 觸發條件
- 使用者說「先 run 一次看看」、「測試一下流程」、「演練」、「dry run」、「模擬執行」
- 剛設定完多階段 cron pipeline 需要驗證
- cron job 沒收到預期結果，需要診斷

## 工作流程

### Step 1: 逐 Phase 觸發

```python
cronjob(action='run', job_id='<phase1_id>')
```

每個 phase 完成後再觸發下一個。Phase N 可能依賴 Phase N-1 的產出（如 patched skill），不可全平行觸發。

### Step 2: 等待並檢查產出

用 `terminal` 檢查預期輸出檔案是否出現：
```bash
sleep 60 && ls -la ~/.hermes/<output_dir>/<expected_file>
```

**等待時間基準**：
- Phase 1（情蒐 + skill patch）：5-8 分鐘（大量 web_search + web_extract + 多次 skill_manage patch）
- Phase 2（唯讀掃描）：2-3 分鐘
- Phase 3（整合報告 + 寄信）：1-2 分鐘

若超過基準時間 50% 仍未出現產出，才判定為 timeout。

### Step 3: 診斷失敗 — 讀取 Session 檔案

```bash
find ~/.hermes/sessions -name "session_cron_<job_id>*" -type f
```

讀取該 session JSON，跳到最後 100 行看它停在哪一步：
```python
read_file(path="<session_path>", offset=-100)
```

常見失敗模式：
- **Timeout/中斷**: session 停在 `web_search` 或 `web_extract` 中間，`finish_reason` 非 `stop`。解決：加 `max_runtime_seconds` 或改 prompt 用 `execute_code`
- **Job 已完成但產出在別處**: job `finish_reason` = `stop` 但本地無檔案 → 可能 deliver 到 Telegram/其他平台而非寫入磁碟
- **權限錯誤**: tool call 回傳 error，session 有記錄
- **被其他 session 覆寫**: 同時有兩個 session 寫同一檔案，後寫者覆蓋前者（注意 cron session 和手動 session 可能重疊）
- **檢測規則自我匹配**: Phase 2 掃描到的「可疑內容」其實是 skill 中的檢測規則本身（false positive），需人工排除

### Step 4: Fallback — 手動完成

若 job timeout，接手執行該 phase 的步驟：
1. 從 session 中的 search results 提取已取得的資料
2. 補做未完成的搜尋/分析
3. 繼續產出該 phase 的結果

### Step 5: 記錄並修正

若 root cause 是 timeout，有兩個修復層級：

#### 層級 A：加安全網（config.yaml）
```yaml
cron:
  max_runtime_seconds: 900   # 15 分鐘，給慢 job 足夠時間
```

#### 層級 B：加速 job 本身（prompt 改寫）
將循序呼叫改為 `execute_code` 平行執行，減少 LLM round-trip：

**改寫前**（多次循序 web_search）：
```
先搜尋 A → 等結果 → 再搜尋 B → 等結果 → 再搜尋 C...
```
LLM round-trip: ~8-10 次，session 大小 ~300KB

**改寫後**（一次 execute_code 平行搜尋）：
```python
# Phase 1 prompt 範例
## 第一步：用 execute_code 一次平行搜尋所有關鍵字
from hermes_tools import web_search
results = {}
results["topic_a"] = web_search("keyword A")
results["topic_b"] = web_search("keyword B")
# ... 所有搜尋一次做完
print(json.dumps(results))
```
LLM round-trip: ~3 次，session 大小減少 25-40%

效果驗證方法：對比新舊 session 的 message 數量與檔案大小。

---

## 注意事項

- `cronjob(action='run')` 回報成功 ≠ job 實際完成。job 在獨立 session 執行，需主動檢查產出。
- Session 檔案是最可靠的診斷來源：`~/.hermes/sessions/session_cron_{job_id}_{timestamp}.json`
- 若 Phase N 依賴 Phase N-1 的 `skill_manage patch`，確保 Phase N-1 確實有 patch 成功再觸發 Phase N

### Step 6: 驗證修復

修復後必須重跑一次 job 確認：
1. `cronjob(action='run', job_id='<id>')` 再次觸發
2. 觀察 session 檔案的新舊對比：
   ```bash
   ls -la ~/.hermes/sessions/session_cron_<job_id>_*
   ```
3. 確認 `finish_reason` = `stop`（非 `tool_calls` 中途掛掉）
4. 確認產出檔案已正確寫入
5. 若用 `execute_code` 優化，對比新舊 session message 數量與檔案大小確認改善幅度
