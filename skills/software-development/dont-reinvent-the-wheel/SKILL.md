---
name: dont-reinvent-the-wheel
description: 開發前先查開源 — 不要每個功能都從零開始，先去 GitHub 找現成方案再決定
---

# 開發前先查開源原則

## 核心規則

> **不要每個功能都自己重新開發。**
> 開始寫任何新功能前，先去 GitHub 搜尋是否有開源方案可以學習、套用、或 fork。

---

## 工作流程

### Step 1: 需求分析
收到開發需求時，先拆解：
- 這個功能的核心是什麼？
- 有哪些子功能？
- 哪些是「通用型」功能（別人一定做過）？

### Step 2: 搜尋開源
```bash
# 用 GitHub CLI 搜尋
gh search repos "關鍵字" --language=python --sort=stars --limit 5

# 或用 web_search
web_search("github open source 關鍵字 python stars:>100")
```

**搜尋優先級**:
1. GitHub 搜尋（stars > 100 的優先）
2. PyPI / npm 套件搜尋
3. 技術部落格 / Stack Overflow 推薦

### Step 3: 評估可用性
| 評估項目 | 標準 |
|----------|------|
| Stars 數 | > 100 基本可信，> 1000 高度可信 |
| 最近更新 | 6 個月內有更新 |
| License | MIT / Apache 2.0 最友善 |
| 文件完整度 | 有 README + 使用範例 |
| 依賴數量 | 依賴越少越好 |
| 中文支援 | 若需要中文，確認支援度 |

### Step 4: 決策

```
找到了適合的開源方案？
├── ✅ 完美匹配 → 直接套用 / fork / pip install
├── ⚠️ 部分匹配 → 參考實作邏輯，自己改寫
├── ❌ 沒找到 → 自己開發，但記錄下來未來可開源
└── 🔄 多個選擇 → 比較後選最佳方案
```

### Step 5: 記錄決策
在專案 `README.md` 或 `devlog.md` 中記錄：
```markdown
## 技術選型
- 功能 X: 使用 [lib-name](github-url) v1.2.3
- 功能 Y: 自行開發（未找到合適方案）
```

---

## 常見可套用的通用功能

以下功能**幾乎一定有開源方案**，不要自己寫：

| 功能類型 | 推薦搜尋關鍵字 |
|----------|---------------|
| PDF 生成/處理 | `python pdf library` |
| OCR 文字辨識 | `ocr python github` |
| 圖片處理/裁切 | `image processing python` |
| 瀏覽器自動化 | `browser automation python` |
| CLI 框架 | `python cli framework` |
| 配置管理 | `python config management` |
| 日誌系統 | `python logging library` |
| API 客戶端 | `api client python` |
| 資料視覺化 | `data visualization python` |
| 日期時間處理 | `python datetime library` |

---

## 注意事項

- ❌ 不要盲目套用 → 先看文件、看 code、看 issues
- ❌ 不要套用 abandoned 專案（> 1 年沒更新）
- ✅ 套用後記錄版本號，避免未來 breaking change
- ✅ 如果找到好方案但不完美，可以 fork 後改良
- ✅ 自己開發的功能也可以考慮開源回饋社群

---

## 記憶指令

每次收到開發需求時，自動執行：
1. 拆解功能需求
2. 搜尋 GitHub / PyPI
3. 評估方案
4. 決策並記錄
5. 開始開發（或套用）
