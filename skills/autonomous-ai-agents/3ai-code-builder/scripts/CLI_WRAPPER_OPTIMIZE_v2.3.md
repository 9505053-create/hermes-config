# 3AI CLI Wrapper 優化方案 v2.3（待顧問團審核後實施）

**日期：** 2026-05-07
**狀態：** 待審核，暫不實施
**觸發者：** Scott — 管線執行時 Claude timeout 議題

---

## 問題陳述

現有 `ai_cli_wrapper.py` 用 `subprocess.run()` 一次等到底，存在三大問題：
1. **Timeout 不精準** — 固定 600s，架構規劃/報告浪費時間，複雜程式碼可能不夠
2. **完全黑箱** — 執行中無法判斷 CLI 是還在跑還是卡死
3. **無法回報進度** — Scott 無法知道目前跑到哪

## 已完成的程式碼改動（ai_cli_wrapper.py）

已在 `code_create/ai_cli_wrapper.py` 完成以下改動，但**未套用到管線實際執行流程**：

### 改動點

| 項目 | 舊版 | 新版 |
|------|------|------|
| subprocess | `subprocess.run()` 阻塞 | `subprocess.Popen()` 非阻塞 |
| Timeout | 固定 600s | 自適應 profiles |
| 進度監控 | 無 | 三層監控 |
| Hang detection | 無 | 120s 無活動 → 警告 |
| 回傳欄位 | 無 progress_log | 新增 `progress_log` list |

### 三層監控策略

1. **Non-blocking pipe** — `fcntl.set O_NONBLOCK` + `select.select` 每 2s 檢查 stdout/stderr
2. **工作目錄監控** — 監控 Claude 寫檔（`calculator.py` 等）的 mtime 變化
3. **Hang detection** — 任何活動來源（pipe/檔案）超過 `HANG_THRESHOLD_SECONDS`（120s）無更新

### Timeout Profiles

```python
TIMEOUT_PROFILES = {
    "claude": {
        "phase0": 180,      # 架構規劃
        "phase1": 600,      # 寫完整程式碼
        "phase5": 180,      # 最終報告
        "_default": 300,
    },
    "gemini": {
        "_default": 180,
    },
    "codex": {
        "_default": 300,
    },
}
```

## ⚠️ 待辦：同步套用到 Gemini 和 Codex

目前改動只影響 `call_cli()` 函數，而該函數已經是三個 CLI 的統一入口，所以 Gemini 和 Codex 自動繼承 POPEN + 監控邏輯。

但需確認以下細節：

- [ ] **Gemini** 的 `--approval-mode yolo` 是否有 stdout streaming？
- [ ] **Codex** 的 `exec --sandbox workspace-write` 是否有類似的檔案寫入行為？
- [ ] 三個 CLI 的工作目錄監控路徑是否一致（都寫到 `workdir`？）
- [ ] Hang detection 閾值是否需要因 tool 不同而調整？

## 待顧問團審核項目

1. **架構面：** 非阻塞 POPEN + select 輪詢是否為最佳方案？有沒有更好的模式？
2. **穩定性面：** O_NONBLOCK 在 WSL 環境下是否穩定？
3. **效能面：** 每 2s 輪詢工作目錄（os.listdir + os.stat）是否有 overhead？
4. **UX 面：** progress_callback 該如何接到 Telegram 通知？
5. **Timeout 數值：** 各 phase 的 timeout 是否合理？需要調整嗎？

## 實施順序

1. 3AI 顧問團審核此方案
2. 根據回饋修正
3. 同步修改 `build_runner.py` 和 `contract_check.py`（如需要）
4. 更新 `3ai-code-builder` skill 的 CLI 呼叫說明
5. 在下一次管線執行時實際驗證
