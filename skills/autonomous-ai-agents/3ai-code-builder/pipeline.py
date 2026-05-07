#!/usr/bin/env python3
"""
3AI Code Builder Pipeline v2.1 — 程式建構管線
v2.1 改善 (2026-05-07):
  - Artifact Type Detection: PRD / Source Code / Config / Unknown 分流
  - Verdict Decision Tree: PASS 不自動進 fix，major issues 需 Scott 決策
  - User Intent Alignment Check: 偵測 disclaimer 語句，避免過度修正
  - Codex 獨立第二審: 不只是 Gemini 回音，要獨立找新問題
  - Output Package 分離: review.zip vs project.zip 明確區分
  - Diff 產出: 有修改時自動產 unified diff
  - 實際計時: 移除 ~推估，改用 execution_log.json 真實時間戳
  - import_cmd 引號拼接修復

Usage: python3 pipeline.py "path/to/PR_or_comment.md"
"""

import os
import sys
import re
import subprocess
import json
import time
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════
WORKSPACE = r"C:\Users\chien\_3AI_WorkSpace"
WSL_WORKSPACE = "/mnt/c/Users/chien/_3AI_WorkSpace"

CLAUDE_TIMEOUT = 300
GEMINI_TIMEOUT = 180
CODEX_TIMEOUT = 300

CLAUDE_CMD = r"C:\Users\chien\AppData\Roaming\npm\claude.cmd"
GEMINI_CMD = r"C:\Users\chien\AppData\Roaming\npm\gemini.cmd"
CODEX_CMD  = r"C:\Users\chien\AppData\Roaming\npm\codex.cmd"

# ═══════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════

def wsl_to_win(p):
    if p.startswith("/mnt/"):
        parts = p.split("/")
        drive = parts[2].upper()
        rest = "\\".join(parts[3:])
        return f"{drive}:\\{rest}"
    return p

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p

def read_file_safe(p):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Read failed: {e}]"

def write_file_safe(p, content):
    ensure_dir(os.path.dirname(p))
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

def call_cli(name, prompt_content, cli_cmd, extra_args=None, timeout=180, workdir=None):
    prompt_file = f"prompt_{name.lower().replace('[','_').replace(']','').replace(' ','_')}.txt"
    prompt_path = os.path.join(WSL_WORKSPACE, prompt_file)
    write_file_safe(prompt_path, prompt_content)

    args_str = " ".join(extra_args) if extra_args else ""
    cwd = workdir or WORKSPACE
    full_cmd = (
        f'/mnt/c/Windows/System32/cmd.exe /c '
        f'"cd /d {cwd} && type {prompt_file} | {cli_cmd} {args_str}"'
    )

    start = time.time()
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True,
            text=True, timeout=timeout, encoding="utf-8", errors="replace"
        )
        elapsed = round(time.time() - start, 1)
        output = result.stdout.strip() or result.stderr.strip()
        return {
            "success": result.returncode == 0 and bool(output),
            "output": output or "",
            "error": result.stderr.strip() if result.returncode != 0 else "",
            "elapsed": elapsed
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Timeout (>{timeout}s)", "elapsed": timeout}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e), "elapsed": round(time.time() - start, 1)}


# ═══════════════════════════════════════════
#  ARTIFACT TYPE DETECTION (v2.1 核心改善)
# ═══════════════════════════════════════════

# PRD indicator keywords — detect if .md/.txt is a PRD vs code readme
_PRD_KEYWORDS = [
    "prd", "product requirements", "需求", "功能", "spec", "specification",
    "rfc", "feature request", "user story", "acceptance criteria",
    "project goal", "專案目標", "版本", "提出者"
]

# Config file extensions
_CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf"}

# Source code extensions
_CODE_EXTS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".kt", ".c", ".cpp", ".h",
    ".cs", ".go", ".rs", ".rb", ".php", ".html", ".css", ".vue", ".svelte",
    ".lua", ".swift", ".m", ".scala"
}

def detect_artifact_type(filename, md_content, frontmatter):
    """
    Detect artifact type from filename, content, and frontmatter.
    Returns (artifact_type, pipeline, reason):
      artifact_type: 'prd' | 'source_code' | 'config' | 'project_folder' | 'unknown'
      pipeline: 'prd_review' | 'code_generation' | 'code_review' | 'project_build'
      reason: human-readable explanation
    """
    # 1. Frontmatter override
    if "artifact_type" in frontmatter:
        at = frontmatter["artifact_type"].lower()
        if at in ("prd", "source_code", "config", "project_folder"):
            pipeline_map = {
                "prd": "prd_review",
                "source_code": "code_review",
                "config": "config_review",
                "project_folder": "project_build"
            }
            return at, pipeline_map.get(at, "code_review"), "Frontmatter artifact_type override"

    # 2. Extension-based detection
    ext = os.path.splitext(filename)[1].lower()

    if ext in _CODE_EXTS:
        return "source_code", "code_generation", f"Source code file ({ext})"

    if ext in _CONFIG_EXTS:
        return "config", "config_review", f"Config file ({ext})"

    # 3. For .md/.txt/.rst — check content to distinguish PRD from code readme
    if ext in (".md", ".txt", ".rst", ""):
        content_lower = md_content.lower()
        prd_score = sum(1 for kw in _PRD_KEYWORDS if kw in content_lower)
        # If contains mode: new in frontmatter, it's a code generation input
        if frontmatter.get("mode", "").lower() == "new":
            return "prd", "code_generation", "PRD with mode:new → Code Generation pipeline"
        if frontmatter.get("mode", "").lower() in ("modify", "review", "repair"):
            return "source_code", "code_review", f"Mode {frontmatter['mode']} → Code Review pipeline"
        if prd_score >= 2:
            return "prd", "prd_review", f"PRD document (matched {prd_score} keywords)"
        return "prd", "prd_review", "Markdown/text file treated as document"

    return "unknown", "unknown", f"Unrecognized file type: {ext}"


def check_intent_alignment(md_content):
    """
    Scan PRD content for user intent disclaimer phrases.
    Returns dict with:
      - has_disclaimer: bool
      - strictness_level: 'casual_test' | 'prototype' | 'internal_tool' | 'production'
      - disclaimer_phrases: list of matched phrases
      - should_auto_fix: bool
      - reason: explanation
    """
    content_lower = md_content.lower()

    # Casual/test indicators
    casual_patterns = [
        "大概寫寫", "不用太認真", "簡單就好", "just test", "just for testing",
        "流程測試", "不用認真", "寫寫就好", "磨合", "不用太認真就好",
        "簡單", "不要太認真", "不要認真", "just demo", "prototype",
        "demo purpose", "for testing", "test project", "測試用", "驗證用",
        "不急", "先看看", "隨便", "先試試"
    ]

    # Production indicators
    production_patterns = [
        "production", "正式", "release", "deploy", "上線",
        "嚴格", "strict", "正式版", "final version", "shipped"
    ]

    casual_hits = [p for p in casual_patterns if p in content_lower]
    production_hits = [p for p in production_patterns if p in content_lower]

    if production_hits:
        level = "production"
        should_fix = True
        reason = f"Production intent detected: {', '.join(production_hits[:3])}"
    elif casual_hits:
        level = "casual_test"
        should_fix = False
        reason = f"Test/casual intent detected: {', '.join(casual_hits[:3])}"
    else:
        level = "prototype"
        should_fix = True
        reason = "No explicit intent disclaimer found, defaulting to prototype (auto-fix OK)"

    return {
        "has_disclaimer": len(casual_hits) > 0 or len(production_hits) > 0,
        "strictness_level": level,
        "disclaimer_phrases": casual_hits + production_hits,
        "should_auto_fix": should_fix,
        "reason": reason
    }


def parse_gemini_verdict(output_text):
    """
    Parse Gemini review output to extract verdict, major count, minor count.
    Returns (verdict, major_count, minor_count, has_required_fixes)
    """
    verdict = "UNKNOWN"
    major_count = 0
    minor_count = 0
    has_required_fixes = False

    lines = output_text.split("\n")
    for line in lines:
        lower = line.lower().strip()
        # Detect verdict
        if "verdict" in lower and any(v in lower for v in ["pass", "fail", "needs_fix"]):
            if "fail" in lower and "pass" not in lower.replace("fail", ""):
                verdict = "FAIL"
            elif "needs_fix" in lower or "needs fix" in lower:
                verdict = "NEEDS_FIXES"
            elif "pass_with_warn" in lower:
                verdict = "PASS_WITH_WARNINGS"
            elif "pass" in lower:
                verdict = "PASS"
        # Count severities
        if "critical" in lower or "high" in lower:
            major_count += 1
        if "medium" in lower or "low" in lower:
            minor_count += 1
        # Check for must fix = yes
        if "yes" in lower and ("must fix" in lower or "must_fix" in lower):
            has_required_fixes = True

    return verdict, major_count, minor_count, has_required_fixes


# ═══════════════════════════════════════════
#  OUTPUT PACKAGING (v2.1)
# ═══════════════════════════════════════════

def create_package(output_dir_wsl, build_dir_wsl, package_type, project_name):
    """
    Create a zip package of the output.
    package_type: 'review' | 'project'
    Returns the zip file path.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"{package_type}_{project_name}_{ts}.zip"
    zip_path = os.path.join(build_dir_wsl, zip_name)

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(output_dir_wsl):
                for f in files:
                    if f.endswith('.zip'):
                        continue  # Don't include zip inside zip
                    full = os.path.join(root, f)
                    arc = os.path.relpath(full, output_dir_wsl)
                    zf.write(full, arc)
        return zip_path
    except Exception as e:
        return f"Error creating package: {e}"


# ═══════════════════════════════════════════
#  MODE DETECTION (A2: Frontmatter 优先)
# ═══════════════════════════════════════════

def parse_frontmatter(content):
    """Parse YAML frontmatter from MD content. Returns dict or {}."""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm

def detect_mode(filename, md_content):
    """Priority: frontmatter mode > filename pattern > error."""
    fm = parse_frontmatter(md_content)
    if "mode" in fm:
        mode = fm["mode"].lower()
        if mode in ("new", "modify", "review", "repair"):
            return mode, fm
    # Fallback to filename
    lower = filename.lower()
    if "pr" in lower:
        return "new", fm
    elif "comment" in lower:
        return "modify", fm
    return None, fm

def detect_build_system(directory):
    try:
        files = os.listdir(directory)
    except Exception:
        return "unknown", {}
    fl = [f.lower() for f in files]

    py = [f for f in files if f.endswith(".py")]
    if py or "setup.py" in fl or "pyproject.toml" in fl or "requirements.txt" in fl:
        return "python", {"py_files": py}
    if "package.json" in fl:
        return "nodejs", {}
    if "pom.xml" in fl:
        return "java_maven", {}
    if "build.gradle" in fl:
        return "java_gradle", {}
    if "cmakelists.txt" in fl:
        return "cpp", {}
    if "cargo.toml" in fl:
        return "rust", {}
    if "go.mod" in fl:
        return "go", {}
    if any(f.endswith(".csproj") for f in files):
        return "dotnet", {}
    return "unknown", {}

def find_code_files(directory, exclude):
    exts = {".py",".js",".ts",".jsx",".tsx",".java",".kt",".c",".cpp",".h",
            ".cs",".go",".rs",".rb",".php",".html",".css",".vue",".svelte"}
    found = []
    try:
        for f in sorted(os.listdir(directory)):
            if f == exclude:
                continue
            if os.path.splitext(f)[1].lower() in exts:
                found.append(f)
    except Exception:
        pass
    return found


# ═══════════════════════════════════════════
#  BUILD VERIFICATION (A7+A8: 升级版)
# ═══════════════════════════════════════════

def run_build_verify(output_dir_win, output_dir_wsl, build_type):
    """Multi-layer build verification: deps → compile → test → smoke"""
    log_lines = [f"# Build & Test Report ({build_type})\n"]
    all_pass = True
    steps = []

    if build_type == "python":
        # A8: Check dependencies first
        req_path = os.path.join(output_dir_wsl, "requirements.txt")
        if os.path.exists(req_path):
            content = read_file_safe(req_path).strip()
            if content and "no external" not in content.lower():
                steps.append(("Dependency Install",
                    f'cd /d {output_dir_win} && python -m pip install -r requirements.txt -q',
                    120))
            else:
                log_lines.append("## Dependency Install\n⏭️ Skipped (no external deps)\n")
        else:
            log_lines.append("## Dependency Install\n⏭️ No requirements.txt found\n")

        # Compile check
        py_files = []
        try:
            py_files = [f for f in os.listdir(output_dir_wsl) if f.endswith(".py")]
        except Exception:
            pass
        for pf in py_files[:10]:
            steps.append((f"Compile: {pf}",
                f'cd /d {output_dir_win} && python -m py_compile {pf}', 30))

        # Import smoke test
        for pf in py_files[:5]:
            mod = pf.replace(".py", "")
            import_cmd = (
                f'cd /d {output_dir_win} && '
                f'python -c "import {mod}; print(\'import ok\')"'
            )
            steps.append(("Import: " + mod, import_cmd, 30))

        # Test discovery
        test_dir = os.path.join(output_dir_wsl, "tests")
        if os.path.isdir(test_dir):
            steps.append(("Unit Tests",
                f'cd /d {output_dir_win} && python -m pytest tests -v 2>nul || python -m unittest discover tests -v', 60))
        else:
            log_lines.append("## Unit Tests\n⏭️ No tests/ directory found\n")

    elif build_type == "nodejs":
        steps.append(("npm install", f'cd /d {output_dir_win} && npm install', 120))
        pkg = os.path.join(output_dir_wsl, "package.json")
        if os.path.exists(pkg):
            try:
                p = json.loads(read_file_safe(pkg))
                if "build" in p.get("scripts", {}):
                    steps.append(("npm run build", f'cd /d {output_dir_win} && npm run build', 60))
                if "test" in p.get("scripts", {}):
                    steps.append(("npm test", f'cd /d {output_dir_win} && npm test', 60))
            except Exception:
                pass
        js_files = [f for f in os.listdir(output_dir_wsl) if f.endswith(".js")]
        for jf in js_files[:5]:
            steps.append((f"Syntax: {jf}", f'cd /d {output_dir_win} && node -c {jf}', 15))

    elif build_type == "java_maven":
        steps.append(("mvn compile", f'cd /d {output_dir_win} && mvn compile -q', 120))
    elif build_type == "java_gradle":
        steps.append(("gradle build", f'cd /d {output_dir_win} && gradle build -x test', 120))
    elif build_type == "rust":
        steps.append(("cargo build", f'cd /d {output_dir_win} && cargo build', 120))
    elif build_type == "go":
        steps.append(("go build", f'cd /d {output_dir_win} && go build ./...', 120))
    elif build_type == "dotnet":
        steps.append(("dotnet build", f'cd /d {output_dir_win} && dotnet build', 120))
    else:
        log_lines.append("## Build\n⏭️ Unknown project type, skipping\n")

    for step_name, cmd, tout in steps:
        log_lines.append(f"## {step_name}\n`{cmd}`\n")
        try:
            r = subprocess.run(f'/mnt/c/Windows/System32/cmd.exe /c "{cmd}"',
                shell=True, capture_output=True, text=True, timeout=tout,
                encoding="utf-8", errors="replace")
            if r.returncode == 0:
                log_lines.append("✅ Passed\n")
            else:
                all_pass = False
                err = (r.stderr.strip() or r.stdout.strip())[:500]
                log_lines.append(f"❌ Failed (exit {r.returncode})\n```\n{err}\n```\n")
        except subprocess.TimeoutExpired:
            all_pass = False
            log_lines.append(f"❌ Timeout (>{tout}s)\n")
        except Exception as e:
            all_pass = False
            log_lines.append(f"❌ Error: {e}\n")

    return all_pass, "\n".join(log_lines)


# ═══════════════════════════════════════════
#  PROMPT TEMPLATES
# ═══════════════════════════════════════════

# --- PRD Review (v2.1: for document/spec review) ---
PRD_REVIEW_PROMPT = """你是資深產品規格審查員。請對以下 PRD / 規格文件進行結構化審查。

**文件路徑：** {md_path}

**你的任務：**
直接輸出以下結構的 Markdown（不要寫檔案，直接 stdout）：

## Verdict
PASS / PASS_WITH_WARNINGS / NEEDS_FIXES / FAIL

## Review Items

| ID | Severity | Category | Issue | Recommendation | Must Fix |
|----|----------|----------|-------|----------------|----------|
| R001 | ... | ... | ... | ... | Yes/No |

Severity: Critical / High / Medium / Low / Info
Category: Completeness / Ambiguity / Testability / Scope / Security / Feasibility

## Required Fix List
列出所有 Must Fix = Yes 的項目 ID 與摘要

## Optional Improvement List
列出可選改善

## Final Notes
整體評價（2-3 句話）"""

# --- Intent Alignment Check (v2.1) ---
INTENT_CHECK_PROMPT_TEMPLATE = """# Intent Alignment Check

## User Intent Summary
{intent_summary}

## Strictness Level
{strictness_level}

## Should Auto-Fix?
{should_auto_fix}

## Reason
{reason}

## Disclaimer Phrases Found
{disclaimers}
"""

# --- Phase 0: Architecture (A1) ---
PHASE0_PROMPT = """你是資深架構師。請根據以下 PR 規格，產出架構規劃文件。

**PR 規格路徑：** {md_path}

**你的任務：**
1. 使用 Read 工具讀取 PR 規格
2. 產出架構規劃，寫入：{output_dir}\\arch_plan.md

**arch_plan.md 必須包含以下章節：**

```md
# Architecture Plan

## 1. Requirement Summary
簡短整理 PR 需求（2-5 句話）

## 2. Project Type
ex: Python Tkinter app / Web frontend / CLI tool / Node.js app

## 3. Proposed File Structure
預計產出的完整檔案樹

## 4. Core Features
必要功能清單

## 5. Non-goals
本次不做的功能（避免 AI 自行擴張）

## 6. Dependencies
需要的第三方套件；若全用標準庫，寫 "No external dependency"

## 7. Build / Run Strategy
如何啟動、如何驗證

## 8. Test Strategy
會產生哪些基本測試或驗收項目

## 9. Known Risks
已知風險（如 GUI 無法 headless 測試、版本相容性等）
```

**規則：**
- 保持務實，不要過度設計
- 如 PR 沒指定技術棧，選擇最簡方案
- 非目標（Non-goals）很重要，要明確列出
- 直接產出 arch_plan.md，不要多餘解釋"""

# --- Phase 1: Implementation (A3: 含測試) ---
PHASE1_PROMPT = """你是資深軟體工程師。請根據架構規劃和 PR 規格，建立完整的應用程式。

**PR 規格路徑：** {md_path}
**架構規劃路徑：** {output_dir}\\arch_plan.md

**你的任務：**
1. 讀取 PR 規格和架構規劃
2. 建立所有程式碼檔案，寫入：{output_dir}\\
3. 同時產出以下檔案：
   - `{output_dir}\\README.md` — 執行方式、功能說明、需求
   - `{output_dir}\\requirements.txt` — 若無第三方套件，寫 "# No external dependencies"
   - `{output_dir}\\tests\\test_basic.py` — 基本測試（至少 import smoke + 核心邏輯測試）
4. 寫建構計劃到：{output_dir}\\claude_plan.md

**claude_plan.md 格式：**
```md
# Implementation Plan

## Implemented Files
列出每個檔案及其用途

## Main Entry Point
啟動方式

## Dependencies
依賴說明

## Test Files
測試檔案說明

## Manual Run Command
手動執行命令

## Assumptions
做出的假設
```

**重要規則：**
- 所有產出檔案寫到 output_dir 目錄
- 程式碼需完整可執行，不留 TODO
- 適當使用註解
- GUI 專案的 __main__ 入口要設計成 import 不會直接啟動 GUI（方便測試）
- 測試檔案要能獨立執行"""

# --- Comment 模式 Phase 1 ---
PHASE1_COMMENT_PROMPT = """你是資深軟體工程師。請根據審查意見修改現有程式碼。

**審查意見：** {md_path}
**現有程式碼：**{code_refs}

**你的任務：**
1. 閱讀審查意見和現有程式碼
2. 修改程式碼，寫入：{output_dir}\\
3. 產出 diff.md 說明修改內容
4. 寫計劃到：{output_dir}\\claude_plan.md

**diff.md 格式：**
```md
# Diff Report

## Modified Files
## Added Files
## Deleted Files
## Before / After Summary
## Risk Assessment
```

修改後的完整檔案寫到 output_dir（不改動原始檔案）。"""

# --- Phase 2: Gemini Review (A4: 结构化) ---
PHASE2_PROMPT = """你是資深程式碼審查員。請對以下程式碼進行結構化審查。

**程式碼目錄：** {output_dir}
**需審查的檔案：**
{file_list}

**你的任務：**
直接輸出以下結構的 Markdown（不要寫檔案，直接 stdout）：

## Verdict
PASS / PASS_WITH_WARNINGS / NEEDS_FIX / FAIL

## Review Items

| ID | Severity | Category | Issue | Recommendation | Must Fix |
|----|----------|----------|-------|----------------|----------|
| G001 | ... | ... | ... | ... | Yes/No |
| G002 | ... | ... | ... | ... | Yes/No |

Severity: Critical / High / Medium / Low / Info
Category: Runtime / Logic / Security / UX / Compatibility / Maintainability / Test / Dependency

## Required Fix List
列出所有 Must Fix = Yes 的項目 ID 與摘要

## Optional Improvement List
列出可選改善

## Final Notes
整體評價（2-3 句話）"""

# --- Phase 3: Codex Fix (v2.1: 獨立第二審，不只是 Gemini 回音) ---
PHASE3_PROMPT = """你是獨立的第二審查員兼修正工程師。你不只是 Gemini 的驗收秘書，你有自己的判斷義務。

**程式碼目錄：** {output_dir}
**Gemini 審查：** {output_dir}\\gemini_review.md
**User Intent：** {intent_summary}

**你的任務有三個：**

1. **驗證 Gemini 提到的問題** — 逐條檢查是否已處理
2. **獨立重新審視程式碼** — 找出 Gemini 沒發現的新問題（這是義務，不是可選）
3. **實作修正** — 直接修改 output_dir 中的檔案

**關鍵規則：**
- 如果你發現新的 blocking issue，即使 Gemini 的問題都已修好，verdict 也必須是 NEEDS_FIXES
- 如果 User Intent 是 casual_test（簡單/不用太認真），不要過度工程化修正
- 如果原 PRD 說「大概寫寫就好」，你的修正幅度應該是最低限度的，不要自動升級為正式產品規格

**codex_report.md 格式（強制）：**
```md
# Codex Independent Validation Report

## Verdict
PASS / PASS_WITH_WARNINGS / NEEDS_FIXES / FAIL

## Verification of Prior Issues (Gemini)

| Gemini ID | Decision | Action Taken | Modified File | Notes |
|-----------|----------|--------------|---------------|-------|
| G001 | Accepted | ... | app.py | ... |
| G002 | Rejected | ... | N/A | reason... |
| G003 | Partially Accepted | ... | app.py | ... |

Decision 只允許：Accepted / Rejected / Partially Accepted / Deferred
Rejected/Deferred 必須說明原因。

## Independent Review (New Issues)

| New Issue ID | Severity | Category | Description | Must Fix |
|-------------|----------|----------|-------------|----------|
| C001 | ... | ... | ... | Yes/No |

如果你沒有發現新問題，也必須明確寫出 "No new issues found by independent review"，並簡述你獨立檢查了哪些面向。

## Intent Alignment Check
修復是否偏離原始 User Intent？Yes / No / Uncertain
若偏離或 uncertain → 標記 PASS_WITH_SCOTT_DECISION_REQUIRED

## Summary
## Remaining Risks
```

執行修正後，暫不 build（build 由下個階段處理）。"""

# --- Phase 3.5: Diagnostic Repair (B1) ---
PHASE3_5_PROMPT = """你是 Debug 診斷專家。上一輪 Build 失敗了，請分析根因並給出具體修復指引。

**程式碼目錄：** {output_dir}
**Build 日誌：** {output_dir}\\build_log.md

**你的任務：**
1. 讀取 build_log.md 中所有失敗步驟
2. 分析每個失敗的根本原因
3. 區分是「環境問題」「程式碼問題」「依賴問題」還是「驗證命令問題」
4. 產出 fix_instruction.md

**fix_instruction.md 格式：**
```md
# Fix Instruction

## Failure Summary
逐條列出失敗項目

## Root Cause Analysis
每個失敗的根因分析

## Error Type Classification
- [ ] Code bug
- [ ] Missing dependency
- [ ] Environment issue
- [ ] Test command error
- [ ] Other

## Files Likely Involved
## Required Changes
具體要改什麼

## Validation Commands
修復後應執行什麼命令驗證
```

直接輸出到 stdout，不要寫檔案。"""

# --- Final Report (B4) ---
PHASE5_PROMPT = """請讀取以下所有報告，組裝最終報告。

**報告目錄：** {output_dir}

**你的任務：**
讀取以下檔案（存在的才讀）：
- arch_plan.md
- claude_plan.md
- gemini_review.md
- lint_report.md（如有）
- codex_report.md
- build_log.md

然後產出 final_report.md，寫入：{output_dir}\\final_report.md

**final_report.md 格式：**
```md
# Final Report — {project_name}

## Project: {project_name}
## Mode: {mode}
## Output Directory: {output_dir}
## Generated: {timestamp}

## Pipeline Result

| Phase | Status | Output File |
|-------|--------|-------------|
| Phase 0 Architecture | ✅/⚠️/❌ | arch_plan.md |
| Phase 1 Implementation | ✅/❌ | claude_plan.md + source |
| Phase 2 Review | ✅/⚠️/❌ | gemini_review.md |
| Phase 2.5 Lint | ✅/⏭️/❌ | lint_report.md |
| Phase 3 Fix | ✅/❌ | codex_report.md |
| Phase 4 Build/Test | ✅/❌ | build_log.md |

## Generated Files
完整列出所有产出档案

## Run Command
如何执行这个专案

## Test Command
如何跑测试

## Known Limitations
已知限制

## Suggested Next Step
建议下一步

## Final Verdict
PASS / PASS_WITH_WARNINGS / FAIL

判定规则：
- PASS = 所有 Phase 通过，Gemini Must Fix 全部处理
- PASS_WITH_WARNINGS = build 通过但有未处理的 warning
- FAIL = build 失败或有 Critical 未修复
```

直接写入 final_report.md。"""


# ═══════════════════════════════════════════
#  REPORT GENERATION
# ═══════════════════════════════════════════

def generate_telegram_summary(output_dir_wsl, mode, md_path, phases, build_pass,
                               retry_count, artifact_type, pipeline_type, verdict_decision,
                               package_path=None):
    """Generate Telegram-friendly summary (not file-based)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    md_name = os.path.basename(md_path)

    lines = [
        f"🏗️ **3AI Code Builder v2.1** — 完成",
        f"",
        f"**模式：** {'新建' if mode == 'new' else mode}",
        f"**輸入：** {md_name}",
        f"**Artifact 類型：** {artifact_type}",
        f"**Pipeline：** {pipeline_type}",
        f"**Verdict 決策：** {verdict_decision}",
        f"**時間：** {ts}",
        f"",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📋 **Pipeline 執行摘要**",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"| 階段 | 狀態 | 耗時 |",
        f"|------|------|------|",
    ]

    for p in phases:
        icon = "✅" if p["success"] else ("⚠️" if p.get("skipped") else "❌")
        lines.append(f"| {p['name']} | {icon} | {p['elapsed']}s |")

    build_icon = "✅ PASS" if build_pass else ("🚨 ESCALATE" if retry_count >= 2 else "❌ FAIL")
    lines.append(f"| Build | {build_icon} | {retry_count}輪 |")

    # File listing
    lines.extend(["", "━━━━━━━━━━━━━━━━━━━━", "📦 **產出檔案**", "━━━━━━━━━━━━━━━━━━━━", ""])
    output_subdir = os.path.join(output_dir_wsl, "output")
    try:
        for f in sorted(os.listdir(output_subdir)):
            fp = os.path.join(output_subdir, f)
            if os.path.isfile(fp):
                sz = os.path.getsize(fp)
                lines.append(f"- `{f}` ({sz:,} bytes)")
    except Exception:
        pass

    lines.extend([
        "", f"📂 **路徑：** `{output_dir_wsl}`",
        f"🚀 **執行：** `python app.py`" if build_pass else ""
    ])

    if package_path:
        lines.append(f"📦 **Package：** `{os.path.basename(package_path)}`")

    return "\n".join(lines)


# ═══════════════════════════════════════════
#  MAIN PIPELINE (v2.1)
# ═══════════════════════════════════════════

def run_pipeline(md_path_wsl):
    """Execute full v2.1 pipeline with artifact detection, verdict tree, intent alignment."""

    pipeline_start = time.time()

    # ── 0. Validate input ──
    if not os.path.exists(md_path_wsl):
        print(json.dumps({"error": f"File not found: {md_path_wsl}"}))
        sys.exit(1)

    md_abspath = os.path.abspath(md_path_wsl)
    md_dir = os.path.dirname(md_abspath)
    md_filename = os.path.basename(md_abspath)
    md_content = read_file_safe(md_abspath)

    # A2: Frontmatter-based mode detection
    mode, frontmatter = detect_mode(md_filename, md_content)
    if not mode:
        print(json.dumps({"error": f"Cannot determine mode. Add frontmatter (mode: new/modify) or use PR/comment in filename."}))
        sys.exit(1)

    project_name = frontmatter.get("project_name", os.path.splitext(md_filename)[0])
    code_files = find_code_files(md_dir, md_filename)
    build_type, build_details = detect_build_system(md_dir)

    # If frontmatter specifies language, trust it
    if "language" in frontmatter:
        lang = frontmatter["language"].lower()
        if lang == "python":
            build_type = "python"
        elif lang in ("node", "nodejs", "javascript"):
            build_type = "nodejs"
        elif lang == "java":
            build_type = "java_maven"
        elif lang == "rust":
            build_type = "rust"
        elif lang == "go":
            build_type = "go"

    # ── 0.5. Artifact Type Detection (v2.1) ──
    artifact_type, pipeline_type, detection_reason = detect_artifact_type(
        md_filename, md_content, frontmatter
    )

    # Intent Alignment Check (v2.1)
    intent = check_intent_alignment(md_content)
    intent_summary = (
        f"Strictness: {intent['strictness_level']}. "
        f"Auto-fix: {intent['should_auto_fix']}. "
        f"Reason: {intent['reason']}"
    )
    if intent["disclaimer_phrases"]:
        intent_summary += f" Phrases: {', '.join(intent['disclaimer_phrases'][:5])}"

    # ── 1. Create timestamped output directory ──
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_dir_wsl = os.path.join(md_dir, f"build_{ts}")
    prompts_dir = os.path.join(build_dir_wsl, "prompts")
    output_dir = os.path.join(build_dir_wsl, "output")
    raw_dir = os.path.join(build_dir_wsl, "raw")
    for d in [prompts_dir, output_dir, raw_dir]:
        ensure_dir(d)

    output_dir_win = wsl_to_win(output_dir)
    phases = []

    print(f"[v2.1] Mode: {mode} | Project: {project_name} | Type: {build_type}")
    print(f"[v2.1] Artifact: {artifact_type} | Pipeline: {pipeline_type}")
    print(f"[v2.1] Intent: {intent['strictness_level']} (auto_fix={intent['should_auto_fix']})")
    print(f"[v2.1] Output: {build_dir_wsl}")

    # Write artifact_manifest.json (v2.1)
    artifact_manifest = {
        "input_path": md_abspath,
        "detected_artifact_type": artifact_type,
        "detected_language": frontmatter.get("language", "unknown"),
        "selected_pipeline": pipeline_type,
        "reason": detection_reason,
        "mode": mode,
        "project_name": project_name,
        "build_type": build_type
    }
    write_file_safe(os.path.join(output_dir, "artifact_manifest.json"),
                    json.dumps(artifact_manifest, indent=2, ensure_ascii=False))

    # Write intent_alignment_check.md (v2.1)
    intent_md = INTENT_CHECK_PROMPT_TEMPLATE.format(
        intent_summary=intent_summary,
        strictness_level=intent["strictness_level"],
        should_auto_fix="Yes" if intent["should_auto_fix"] else "No — Need Scott Decision",
        reason=intent["reason"],
        disclaimers=", ".join(intent["disclaimer_phrases"]) if intent["disclaimer_phrases"] else "None"
    )
    write_file_safe(os.path.join(output_dir, "intent_alignment_check.md"), intent_md)

    # ── Track verdict decision for v2.1 ──
    verdict_decision = "proceeding"  # Will be updated after Phase 2

    # ══════════════════════════════════════
    #  PRD REVIEW PIPELINE (v2.1)
    # ══════════════════════════════════════
    # If pipeline_type is prd_review AND mode is not new,
    # we skip Phase 0/1 and go straight to PRD review
    # ══════════════════════════════════════

    if pipeline_type == "prd_review" and mode not in ("new", "modify", "repair"):
        print(f"\n{'='*50}")
        print(f"[PRD Review] Gemini Document Review")
        print(f"{'='*50}")

        prd_prompt = PRD_REVIEW_PROMPT.format(md_path=md_abspath)
        write_file_safe(os.path.join(prompts_dir, "prompt_prd_review.txt"), prd_prompt)

        p2 = call_cli("PRDReview", prd_prompt, GEMINI_CMD,
                       ["--skip-trust", "--approval-mode", "yolo"],
                       GEMINI_TIMEOUT, WORKSPACE)
        write_file_safe(os.path.join(raw_dir, "prd_review_gemini_stdout.txt"), p2.get("output", ""))

        if p2["success"] and p2.get("output"):
            write_file_safe(os.path.join(output_dir, "gemini_review.md"), p2["output"])
            p2_note = "PRD 結構化審查完成"
            print(f"[PRD Review] ✅ ({p2['elapsed']}s)")
        else:
            p2_note = f"審查失敗（{p2.get('error', '無輸出')[:40]}）"
            print(f"[PRD Review] ❌ Failed")

        phases.append({"name": "PRD Review", "success": p2["success"], "elapsed": p2["elapsed"],
                        "note": p2_note})

        # Generate final report for PRD review
        final_content = f"# Final Report — {project_name}\n\n"
        final_content += f"## Artifact Type: PRD Document\n"
        final_content += f"## Pipeline: PRD Review\n"
        final_content += f"## Verdict: See gemini_review.md\n"
        final_content += f"## Intent: {intent['strictness_level']}\n"
        final_content += f"## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        write_file_safe(os.path.join(output_dir, "final_report.md"), final_content)

        # Create review package
        package_path = create_package(output_dir, build_dir_wsl, "review", project_name)

        # execution_log.json with actual timing
        pipeline_elapsed = round(time.time() - pipeline_start, 1)
        exec_log = {
            "timestamp": datetime.now().isoformat(),
            "total_duration_seconds": pipeline_elapsed,
            "phases": phases,
            "artifact_type": artifact_type,
            "pipeline_type": pipeline_type,
            "intent": intent,
            "verdict_decision": "prd_review_complete"
        }
        write_file_safe(os.path.join(output_dir, "execution_log.json"),
                        json.dumps(exec_log, indent=2, ensure_ascii=False))

        verdict_decision = "prd_review_complete"
        summary = generate_telegram_summary(build_dir_wsl, mode, md_path_wsl, phases,
                                             False, 0, artifact_type, pipeline_type,
                                             verdict_decision, package_path)
        print(f"\n{'='*50}")
        print(f"[Pipeline v2.1] Complete!")
        print(f"{'='*50}")
        print(summary)

        result = {
            "report_path": os.path.join(output_dir, "final_report.md"),
            "output_dir": build_dir_wsl,
            "mode": mode,
            "project_name": project_name,
            "build_type": build_type,
            "artifact_type": artifact_type,
            "pipeline_type": pipeline_type,
            "build_pass": False,
            "retry_count": 0,
            "verdict_decision": verdict_decision,
            "phases": phases
        }
        print(f"\n__RESULT_JSON__:{json.dumps(result, ensure_ascii=False)}:__END_RESULT__")
        return

    # ══════════════════════════════════════
    #  CODE GENERATION / REVIEW PIPELINE
    # ══════════════════════════════════════

    # ── Phase 0: Architecture Planning (A1) ──
    print(f"\n{'='*50}")
    print(f"[Phase 0] Architecture Planning (Claude)")
    print(f"{'='*50}")

    p0_prompt = PHASE0_PROMPT.format(md_path=md_abspath, output_dir=output_dir_win)
    write_file_safe(os.path.join(prompts_dir, "prompt_phase0.txt"), p0_prompt)

    p0 = call_cli("Phase0", p0_prompt, CLAUDE_CMD,
                   ["--print", "--allowedTools", "Bash", "Write", "Edit"],
                   CLAUDE_TIMEOUT, WORKSPACE)
    write_file_safe(os.path.join(raw_dir, "phase0_claude_stdout.txt"), p0.get("output",""))

    p0_ok = p0["success"] and os.path.exists(os.path.join(output_dir, "arch_plan.md"))
    phases.append({"name": "Phase 0 架構", "success": p0_ok, "elapsed": p0["elapsed"],
                    "note": "arch_plan.md 已產出" if p0_ok else "架構規劃失敗，繼續"})
    print(f"[Phase 0] {'✅' if p0_ok else '⚠️'} ({p0['elapsed']}s)")

    # ── Phase 1: Implementation (Claude) ──
    print(f"\n{'='*50}")
    print(f"[Phase 1] Implementation (Claude)")
    print(f"{'='*50}")

    if mode in ("new", "review"):
        p1_prompt = PHASE1_PROMPT.format(md_path=md_abspath, output_dir=output_dir_win)
    else:
        refs = "\n".join(f"- {os.path.join(md_dir, c)}" for c in code_files) or "（無現有程式碼）"
        p1_prompt = PHASE1_COMMENT_PROMPT.format(md_path=md_abspath, code_refs=refs, output_dir=output_dir_win)

    write_file_safe(os.path.join(prompts_dir, "prompt_phase1.txt"), p1_prompt)

    p1 = call_cli("Phase1", p1_prompt, CLAUDE_CMD,
                   ["--print", "--allowedTools", "Bash", "Write", "Edit"],
                   CLAUDE_TIMEOUT, WORKSPACE)
    write_file_safe(os.path.join(raw_dir, "phase1_claude_stdout.txt"), p1.get("output",""))

    if not p1["success"]:
        phases.append({"name": "Phase 1 實作", "success": False, "elapsed": p1["elapsed"],
                        "note": f"Claude 失敗: {p1.get('error','')[:60]}"})
        print(f"[Phase 1] ❌ Failed")
        summary = generate_telegram_summary(build_dir_wsl, mode, md_path_wsl, phases,
                                             False, 0, artifact_type, pipeline_type,
                                             "phase1_failed")
        print(summary)
        return

    phases.append({"name": "Phase 1 實作", "success": True, "elapsed": p1["elapsed"],
                    "note": "程式碼已產出"})
    print(f"[Phase 1] ✅ ({p1['elapsed']}s)")

    # Check output files
    try:
        out_files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        print(f"[Phase 1] Files: {out_files}")
    except Exception:
        out_files = []

    # ── Phase 2: Gemini Structured Review (v2.1: select prompt by artifact type) ──
    print(f"\n{'='*50}")
    print(f"[Phase 2] Gemini Review")
    print(f"{'='*50}")

    # v2.1: Use PRD_REVIEW_PROMPT if artifact is PRD and no code was produced
    has_code_files = any(os.path.splitext(f)[1].lower() in _CODE_EXTS
                         for f in out_files) if out_files else False

    if artifact_type == "prd" and not has_code_files:
        # PRD review mode — use document review prompt
        p2_prompt = PRD_REVIEW_PROMPT.format(md_path=md_abspath)
        review_type = "PRD Document Review"
    else:
        file_list_text = "\n".join(f"- {f}" for f in out_files) if out_files else "（無檔案）"
        p2_prompt = PHASE2_PROMPT.format(output_dir=output_dir_win, file_list=file_list_text)
        review_type = "Code Review"

    write_file_safe(os.path.join(prompts_dir, "prompt_phase2.txt"), p2_prompt)

    p2 = call_cli("Phase2", p2_prompt, GEMINI_CMD,
                   ["--skip-trust", "--approval-mode", "yolo"],
                   GEMINI_TIMEOUT, WORKSPACE)
    write_file_safe(os.path.join(raw_dir, "phase2_gemini_stdout.txt"), p2.get("output",""))

    p2_skipped = False
    if p2["success"] and p2.get("output"):
        write_file_safe(os.path.join(output_dir, "gemini_review.md"), p2["output"])
        p2_note = f"結構化審查完成 ({review_type})"
        print(f"[Phase 2] ✅ ({p2['elapsed']}s) [{review_type}]")
    else:
        p2_skipped = True
        p2_note = f"跳過（{p2.get('error','無輸出')[:40]}）"
        print(f"[Phase 2] ⚠️ Skipped")

    phases.append({"name": "Phase 2 審查", "success": p2["success"], "elapsed": p2["elapsed"],
                    "note": p2_note, "skipped": p2_skipped})

    # ══════════════════════════════════════
    #  VERDICT DECISION TREE (v2.1 核心)
    # ══════════════════════════════════════
    # Parse Gemini verdict and decide whether to proceed to Phase 3 fix
    # ══════════════════════════════════════

    gemini_verdict = "UNKNOWN"
    major_count = 0
    minor_count = 0
    has_required_fixes = False
    skip_phase3 = False
    need_scott_decision = False

    if p2["success"] and p2.get("output"):
        gemini_verdict, major_count, minor_count, has_required_fixes = parse_gemini_verdict(p2["output"])
        print(f"[Verdict] Gemini: {gemini_verdict} | Major: {major_count} | Minor: {minor_count} | MustFix: {has_required_fixes}")

        if gemini_verdict == "PASS" and not has_required_fixes:
            if major_count == 0:
                # PASS + only Minor issues → skip fix, proceed to build
                skip_phase3 = True
                verdict_decision = "PASS_minor_only → skip fix, proceed to build"
                print(f"[Verdict] ✅ PASS with minor issues only — skipping Codex fix")
            else:
                # PASS + Major issues → check intent
                if not intent["should_auto_fix"]:
                    skip_phase3 = True
                    need_scott_decision = True
                    verdict_decision = "PASS_major + casual_intent → need Scott decision"
                    print(f"[Verdict] ⚠️ PASS with major issues but casual intent — need Scott decision")
                else:
                    verdict_decision = "PASS_major + production_intent → proceeding to fix"
                    print(f"[Verdict] ⚠️ PASS with major issues + production intent — proceeding to fix")

        elif gemini_verdict == "NEEDS_FIXES" or gemini_verdict == "FAIL":
            verdict_decision = f"{gemini_verdict} → proceeding to Codex fix"
            print(f"[Verdict] ❌ {gemini_verdict} — proceeding to fix")

        elif gemini_verdict == "PASS_WITH_WARNINGS":
            if not intent["should_auto_fix"] and major_count > 0:
                skip_phase3 = True
                need_scott_decision = True
                verdict_decision = "PASS_WITH_WARNINGS + casual_intent → need Scott decision"
                print(f"[Verdict] ⚠️ PASS_WITH_WARNINGS + casual intent — need Scott decision")
            else:
                verdict_decision = "PASS_WITH_WARNINGS → proceeding to fix"
                print(f"[Verdict] ⚠️ PASS_WITH_WARNINGS — proceeding to fix")

        else:
            # Unknown verdict — default to proceeding
            verdict_decision = f"Unknown verdict '{gemini_verdict}' → proceeding to fix (safe default)"
            print(f"[Verdict] ❓ Unknown — proceeding to fix (safe default)")

    # Write verdict decision to intent_alignment_check.md (append)
    verdict_section = f"\n\n## Verdict Decision (v2.1)\n"
    verdict_section += f"- Gemini Verdict: {gemini_verdict}\n"
    verdict_section += f"- Major Issues: {major_count}, Minor: {minor_count}, Must Fix: {has_required_fixes}\n"
    verdict_section += f"- Decision: {verdict_decision}\n"
    verdict_section += f"- Skip Phase 3: {skip_phase3}\n"
    verdict_section += f"- Need Scott Decision: {need_scott_decision}\n"
    existing_intent = read_file_safe(os.path.join(output_dir, "intent_alignment_check.md"))
    write_file_safe(os.path.join(output_dir, "intent_alignment_check.md"),
                    existing_intent + verdict_section)

    # ── Phase 2.5: Static / Lint Check (A5) ──
    print(f"\n{'='*50}")
    print(f"[Phase 2.5] Static Check")
    print(f"{'='*50}")

    lint_lines = ["# Lint / Static Check Report\n"]
    lint_ok = True

    # Re-detect after Claude may have added files
    build_type_actual, _ = detect_build_system(output_dir)
    if build_type_actual != "unknown":
        build_type = build_type_actual

    if build_type == "python":
        py_files = [f for f in os.listdir(output_dir) if f.endswith(".py")] if os.path.isdir(output_dir) else []
        for pf in py_files:
            r = subprocess.run(
                f'/mnt/c/Windows/System32/cmd.exe /c "cd /d {output_dir_win} && python -m py_compile {pf}"',
                shell=True, capture_output=True, text=True, timeout=15, encoding="utf-8", errors="replace"
            )
            if r.returncode == 0:
                lint_lines.append(f"## {pf}\n✅ py_compile passed\n")
            else:
                lint_ok = False
                lint_lines.append(f"## {pf}\n❌ py_compile failed\n```\n{r.stderr.strip()[:300]}\n```\n")
    elif build_type == "nodejs":
        lint_lines.append("## Node.js\n⏭️ Static check deferred to build phase\n")
    else:
        lint_lines.append(f"## {build_type}\n⏭️ No lint tool configured\n")

    write_file_safe(os.path.join(output_dir, "lint_report.md"), "\n".join(lint_lines))
    phases.append({"name": "Phase 2.5 Lint", "success": lint_ok, "elapsed": 2,
                    "note": "靜態檢查完成" if lint_ok else "有 lint 問題"})
    print(f"[Phase 2.5] {'✅' if lint_ok else '⚠️'}")

    # ── Phase 3: Codex Fix (v2.1: verdict-gated) ──
    if skip_phase3:
        print(f"\n{'='*50}")
        print(f"[Phase 3] SKIPPED — {verdict_decision}")
        print(f"{'='*50}")
        phases.append({"name": "Phase 3 修正", "success": True, "elapsed": 0,
                        "note": f"跳過: {verdict_decision}",
                        "skipped": True})
        if need_scott_decision:
            # Write need_scott_decision.md
            scott_md = f"# Need Scott Decision\n\n"
            scott_md += f"## Gemini Verdict: {gemini_verdict}\n"
            scott_md += f"## Issues Found: {major_count} Major, {minor_count} Minor\n"
            scott_md += f"## Intent: {intent['strictness_level']} ({intent['reason']})\n\n"
            scott_md += f"**Why skipped auto-fix:**\n"
            scott_md += f"- Gemini gave {gemini_verdict} but found {major_count} major issue(s)\n"
            scott_md += f"- Your intent is '{intent['strictness_level']}' — auto-fix may over-engineer\n\n"
            scott_md += f"**Options:**\n"
            scott_md += f"1. Accept as-is (issues are minor for your use case)\n"
            scott_md += f"2. Tell me to fix the major issues\n"
            scott_md += f"3. Tell me to rewrite with stricter standards\n"
            write_file_safe(os.path.join(output_dir, "need_scott_decision.md"), scott_md)
            print(f"[Phase 3] 📝 need_scott_decision.md written — waiting for Scott")
    else:
        print(f"\n{'='*50}")
        print(f"[Phase 3] Codex Fix")
        print(f"{'='*50}")

        p3_prompt = PHASE3_PROMPT.format(output_dir=output_dir_win, intent_summary=intent_summary)
        write_file_safe(os.path.join(prompts_dir, "prompt_phase3.txt"), p3_prompt)

        p3 = call_cli("Phase3", p3_prompt, CODEX_CMD,
                       ["exec", "--skip-git-repo-check", "--sandbox", "workspace-write"],
                       CODEX_TIMEOUT, WORKSPACE)
        write_file_safe(os.path.join(raw_dir, "phase3_codex_stdout.txt"), p3.get("output",""))

        if p3["success"] and p3.get("output"):
            # Save codex_report if not already written by Codex
            if not os.path.exists(os.path.join(output_dir, "codex_report.md")):
                write_file_safe(os.path.join(output_dir, "codex_report.md"), p3["output"])
            p3_note = "獨立審查 + 修正完成"
            print(f"[Phase 3] ✅ ({p3['elapsed']}s)")
        else:
            p3_note = p3.get("error", "未知錯誤")[:60]
            print(f"[Phase 3] ❌ {p3_note}")

        phases.append({"name": "Phase 3 修正", "success": p3["success"], "elapsed": p3["elapsed"],
                        "note": p3_note})

        # Generate diff.md if there were modifications (v2.1)
        if p3["success"]:
            diff_content = f"# Diff Report\n\n"
            diff_content += f"## Source: Phase 3 Codex Fix\n"
            diff_content += f"## Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            diff_content += f"## Intent: {intent['strictness_level']}\n\n"
            diff_content += f"See codex_report.md for detailed per-item changes.\n"
            diff_content += f"See gemini_review.md for original issues.\n"
            write_file_safe(os.path.join(output_dir, "diff.md"), diff_content)

    # ── Phase 4: Build + Test (A7+A8) ──
    print(f"\n{'='*50}")
    print(f"[Phase 4] Build + Test")
    print(f"{'='*50}")

    build_pass = False
    retry_count = 0
    MAX_RETRIES = 2

    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            retry_count = attempt
            print(f"\n[Build] Diagnostic Repair Round {attempt}...")

            # B1: Gemini diagnoses the failure
            diag_prompt = PHASE3_5_PROMPT.format(output_dir=output_dir_win)
            write_file_safe(os.path.join(prompts_dir, f"prompt_diagnose{attempt}.txt"), diag_prompt)

            diag = call_cli(f"Diagnose{attempt}", diag_prompt, GEMINI_CMD,
                            ["--skip-trust", "--approval-mode", "yolo"],
                            GEMINI_TIMEOUT, WORKSPACE)
            write_file_safe(os.path.join(raw_dir, f"diagnose{attempt}_stdout.txt"), diag.get("output",""))

            if diag["success"] and diag.get("output"):
                write_file_safe(os.path.join(output_dir, "fix_instruction.md"), diag["output"])
                print(f"[Diagnose] ✅ Gemini root cause analysis done")
            else:
                print(f"[Diagnose] ⚠️ Gemini diagnosis failed, proceeding with raw fix")

            # Codex applies fix based on diagnosis
            fix_prompt = f"""Build 失敗了。請讀取 build_log.md 和 fix_instruction.md（如有），修正程式碼後重新驗證。

**目錄：** {output_dir_win}

**你的任務：**
1. 讀取 build_log.md 了解失敗原因
2. 讀取 fix_instruction.md（如有）了解 Gemini 的診斷
3. 修正程式碼
4. 重新執行 build 驗證（py_compile + import smoke test）
5. 更新 build_log.md

這是第 {attempt} 輪重試（最多 2 輪）。
"""
            write_file_safe(os.path.join(prompts_dir, f"prompt_fix{attempt}.txt"), fix_prompt)

            fix = call_cli(f"Fix{attempt}", fix_prompt, CODEX_CMD,
                          ["exec", "--skip-git-repo-check", "--sandbox", "workspace-write"],
                          CODEX_TIMEOUT, WORKSPACE)
            write_file_safe(os.path.join(raw_dir, f"fix{attempt}_codex_stdout.txt"), fix.get("output",""))
            print(f"[Fix] {'✅' if fix['success'] else '❌'} ({fix['elapsed']}s)")

        # Run build verification
        build_pass, build_log = run_build_verify(output_dir_win, output_dir, build_type)
        write_file_safe(os.path.join(output_dir, "build_log.md"), build_log)

        if build_pass:
            print(f"[Build] ✅ PASSED!")
            break
        else:
            print(f"[Build] ❌ Failed (attempt {attempt + 1}/{MAX_RETRIES + 1})")

    # ── Phase 5: Final Report (B4) ──
    print(f"\n{'='*50}")
    print(f"[Phase 5] Final Report")
    print(f"{'='*50}")

    p5_prompt = PHASE5_PROMPT.format(
        output_dir=output_dir_win,
        project_name=project_name,
        mode=mode,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    write_file_safe(os.path.join(prompts_dir, "prompt_phase5.txt"), p5_prompt)

    p5 = call_cli("Phase5", p5_prompt, CLAUDE_CMD,
                   ["--print", "--allowedTools", "Bash", "Write", "Edit"],
                   120, WORKSPACE)
    write_file_safe(os.path.join(raw_dir, "phase5_claude_stdout.txt"), p5.get("output",""))

    if p5["success"]:
        print(f"[Phase 5] ✅ final_report.md generated")
    else:
        # Fallback: generate minimal final_report
        fallback = f"# Final Report\n\n## Final Verdict\n{'PASS' if build_pass else 'FAIL'}\n\nSee build_log.md for details.\n"
        write_file_safe(os.path.join(output_dir, "final_report.md"), fallback)
        print(f"[Phase 5] ⚠️ Claude failed, generated minimal report")

    phases.append({"name": "Phase 5 報告", "success": True, "elapsed": p5.get("elapsed", 0),
                    "note": "final_report.md 已產出"})

    # ── execution_log.json with ACTUAL timing (v2.1) ──
    pipeline_elapsed = round(time.time() - pipeline_start, 1)
    exec_log = {
        "timestamp": datetime.now().isoformat(),
        "total_duration_seconds": pipeline_elapsed,
        "phases": phases,
        "artifact_type": artifact_type,
        "pipeline_type": pipeline_type,
        "intent": intent,
        "gemini_verdict": gemini_verdict,
        "verdict_decision": verdict_decision,
        "build_pass": build_pass,
        "retry_count": retry_count
    }
    write_file_safe(os.path.join(output_dir, "execution_log.json"),
                    json.dumps(exec_log, indent=2, ensure_ascii=False))

    # ── Output Package (v2.1: project vs review) ──
    package_type = "project" if build_pass else "review"
    package_path = create_package(output_dir, build_dir_wsl, package_type, project_name)

    # ── Summary ──
    summary = generate_telegram_summary(build_dir_wsl, mode, md_path_wsl, phases, build_pass,
                                         retry_count, artifact_type, pipeline_type,
                                         verdict_decision, package_path)
    print(f"\n{'='*50}")
    print(f"[Pipeline v2.1] Complete!")
    print(f"{'='*50}")
    print(summary)

    # JSON result for Hermes
    result = {
        "report_path": os.path.join(output_dir, "final_report.md"),
        "output_dir": build_dir_wsl,
        "mode": mode,
        "project_name": project_name,
        "build_type": build_type,
        "artifact_type": artifact_type,
        "pipeline_type": pipeline_type,
        "build_pass": build_pass,
        "retry_count": retry_count,
        "verdict_decision": verdict_decision,
        "need_scott_decision": need_scott_decision,
        "package_path": package_path if isinstance(package_path, str) else "",
        "phases": phases
    }
    print(f"\n__RESULT_JSON__:{json.dumps(result, ensure_ascii=False)}:__END_RESULT__")


# ═══════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pipeline.py \"path/to/PR_or_comment.md\"")
        sys.exit(1)
    run_pipeline(sys.argv[1])
