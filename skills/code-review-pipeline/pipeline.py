#!/usr/bin/env python3
"""
3AI Code Review Pipeline — ~!! 觸發（v2）
Hermes 零思考，Gemini(審查) → Claude(修改) → Codex(驗證)
CLI 透過 stdout 輸出，Hermes 用標記提取後存檔

Usage: python3 pipeline.py "code_review\input.py"
"""

import os
import sys
import re
import subprocess
import time
import zipfile
import json
from datetime import datetime

# ═══════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════
WORKSPACE = r"C:\Users\chien\_3AI_WorkSpace"
WSL_WORKSPACE = "/mnt/c/Users/chien/_3AI_WorkSpace"

MAX_OUTPUT_CHARS = 16000      # 程式碼輸出可能很長
CLI_TIMEOUT = 600             # 10 分鐘

GEMINI_CMD = r"C:\Users\chien\AppData\Roaming\npm\gemini.cmd"
CLAUDE_CMD = r"C:\Users\chien\AppData\Roaming\npm\claude.cmd"
CODEX_CMD  = r"C:\Users\chien\AppData\Roaming\npm\codex.cmd"

SOURCE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h',
    '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.cs', '.sh', '.sql',
    '.html', '.css', '.json', '.yaml', '.yml', '.toml', '.xml', '.md',
}


# ═══════════════════════════════════════════
#  PROMPT TEMPLATES
# ═══════════════════════════════════════════

GEMINI_PROMPT = """你是資深程式碼審查員。請審查以下程式碼檔案。

【檔案路徑】
{file_path}

【指令】
1. 請用你的檔案讀取能力打開上述檔案
2. 逐一檢查：bugs、安全漏洞、效能問題、邏輯錯誤、不良實踐
3. 如果是多個檔案，檢查檔案間的依賴和整合問題

【輸出格式（必須遵守）】
- 每個問題一行，格式：[嚴重度: 高/中/低] 檔案名:行號 → 問題描述 → 建議修法
- 嚴重度定義：
  🔴 高 = 會導致 crash、資料遺失、安全漏洞
  🟡 中 = 效能問題、邏輯錯誤、可能的 edge case
  🟢 低 = 風格問題、命名不佳、缺少註解
- 最後給一個整體評分（1-10）和一句總結
- 用繁體中文回答

【重要】
- 只做審查，不要修改程式碼
- 如果程式碼沒有問題，明確說「✅ 審查通過，未發現問題」
- 不確定的地方標註「⚠️ 需人工確認」"""

GEMINI_FALLBACK_PROMPT = """你是資深程式碼審查員。網路搜尋不可用，請完全依賴你的知識審查。

【檔案路徑】
{file_path}

【指令】
1. 請用你的檔案讀取能力打開上述檔案
2. 逐一檢查：bugs、安全漏洞、效能問題、邏輯錯誤、不良實踐
3. 如果是多個檔案，檢查檔案間的依賴和整合問題

【輸出格式（必須遵守）】
- 每個問題一行，格式：[嚴重度: 高/中/低] 檔案名:行號 → 問題描述 → 建議修法
- 嚴重度定義：
  🔴 高 = 會導致 crash、資料遺失、安全漏洞
  🟡 中 = 效能問題、邏輯錯誤、可能的 edge case
  🟢 低 = 風格問題、命名不佳、缺少註解
- 最後給一個整體評分（1-10）和一句總結
- 用繁體中文回答

【重要】
- 禁止使用網路搜尋
- 只做審查，不要修改程式碼
- 如果程式碼沒有問題，明確說「✅ 審查通過，未發現問題」"""

CLAUDE_PROMPT = """你是程式碼修復工程師。以下是一位審查員對程式碼的審查意見，請根據意見修改程式碼。

【原始程式碼檔案路徑】
{file_path}

【Gemini 審查意見】
{gemini_output}

【你的任務】
1. 讀取原始程式碼檔案
2. 根據 Gemini 的審查意見進行修改
3. 如果 Gemini 說「審查通過，未發現問題」，不做修改，直接確認
4. 修改時保留原有邏輯，只修復指出的問題

【輸出格式（絕對必須遵守）】
- 先用 2-3 行簡要說明你做了哪些修改
- 然後輸出修改後的完整程式碼，用以下標記包裹：

<<<FIXED_CODE_START>>>
（修改後的完整程式碼，原封不動）
<<<FIXED_CODE_END>>>

【重要】
- <<<FIXED_CODE_START>>> 和 <<<FIXED_CODE_END>>> 是提取程式碼的唯一標記，絕對不能省略
- 程式碼必須完整，不能有遺漏或截斷
- 如果不需要修改，在 <<<FIXED_CODE_START>>> 和 <<<FIXED_CODE_END>>> 之間放原始程式碼即可
- 不要加任何 markdown code fence（不要用 ```）"""

CODEX_PROMPT = """你是最終品質驗證者。以下是原始程式碼、審查意見、以及修改後的程式碼。

【原始程式碼檔案路徑】
{file_path}

【修改後程式碼】
{fixed_code}

【Gemini 審查意見】
{gemini_output}

【你的任務】
1. 驗證修改是否正確解決了審查意見中的問題
2. 檢查修改是否引入了新的問題（regression）
3. 如果修改完全正確，簡短確認即可
4. 如果需要進一步修正，輸出修正後的完整程式碼

【輸出格式】
- 先簡要說明你的驗證結論
- 如果需要修正，輸出修正後的完整程式碼，用以下標記包裹：

<<<FINAL_CODE_START>>>
（修正後的完整程式碼）
<<<FINAL_CODE_END>>>

- 如果不需要修正，直接說「✅ 最終驗證通過」，不要加標記
- 用繁體中文回答"""


# ═══════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════

def truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n_(已截斷，原始輸出 {len(text)} 字元)_"


def win_path(p: str) -> str:
    if os.path.isabs(p):
        return p.replace('/', '\\')
    return os.path.join(WORKSPACE, p.replace('/', '\\'))


def wsl_path(p: str) -> str:
    if os.path.isabs(p) and p.startswith('/'):
        return p
    wp = win_path(p)
    return '/mnt/c/' + wp[3:].replace('\\', '/')


def write_prompt(filename: str, content: str):
    path = os.path.join(WSL_WORKSPACE, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def extract_between_markers(text: str, start_marker: str, end_marker: str) -> str | None:
    """從 stdout 中提取標記之間的程式碼"""
    pattern = re.escape(start_marker) + r'(.*?)' + re.escape(end_marker)
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def call_cli(cmd_name: str, pipe_file: str, cli_cmd: str, extra_args: list[str] = None) -> dict:
    args = " ".join(extra_args) if extra_args else ""
    full_cmd = (
        f'/mnt/c/Windows/System32/cmd.exe /c '
        f'"cd /d {WORKSPACE} && type {pipe_file} | {cli_cmd} {args}"'
    )

    start = time.time()
    try:
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True,
            timeout=CLI_TIMEOUT, encoding="utf-8", errors="replace"
        )
        elapsed = time.time() - start
        output = result.stdout.strip()
        if not output and result.stderr.strip():
            output = result.stderr.strip()
        return {
            "success": result.returncode == 0 and bool(output),
            "output": output or "",
            "error": result.stderr.strip() if result.returncode != 0 else "",
            "elapsed": round(elapsed, 1),
            "cmd": full_cmd,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False, "output": "",
            "error": f"超時（>{CLI_TIMEOUT}s）", "elapsed": CLI_TIMEOUT,
            "cmd": full_cmd, "returncode": -1
        }
    except Exception as e:
        return {
            "success": False, "output": "",
            "error": str(e), "elapsed": round(time.time() - start, 1),
            "cmd": full_cmd, "returncode": -1
        }


def get_source_files(directory: str) -> list:
    files = []
    for root, dirs, filenames in os.walk(directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__' and d != 'node_modules']
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in SOURCE_EXTENSIONS:
                rel = os.path.relpath(os.path.join(root, f), directory)
                files.append(rel)
    return sorted(files)


def concatenate_files(directory: str, file_list: list, output_path: str):
    with open(output_path, "w", encoding="utf-8") as out:
        for i, rel_path in enumerate(file_list):
            if i > 0:
                out.write("\n\n")
            out.write(f"{'=' * 60}\n")
            out.write(f"# FILE: {rel_path}\n")
            out.write(f"{'=' * 60}\n\n")
            full_path = os.path.join(directory, rel_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"# [讀取失敗: {e}]\n")


# ═══════════════════════════════════════════
#  LOG SYSTEM
# ═══════════════════════════════════════════

class PipelineLogger:
    """記錄每階段執行細節到 JSON log"""

    def __init__(self, log_path: str):
        self.log_path = log_path
        self.entries = []
        self.start_time = datetime.now().isoformat()

    def log_stage(self, stage_name: str, cli_name: str, result: dict,
                  prompt_path: str = "", actions: list = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage_name,
            "cli": cli_name,
            "prompt_file": prompt_path,
            "command": result.get("cmd", ""),
            "success": result["success"],
            "elapsed_seconds": result["elapsed"],
            "returncode": result.get("returncode", -1),
            "output_length": len(result.get("output", "")),
            "error": result.get("error", ""),
            "actions": actions or [],
            "output_preview": result.get("output", "")[:500]  # 前 500 字元預覽
        }
        self.entries.append(entry)

    def flush(self):
        log = {
            "pipeline_start": self.start_time,
            "pipeline_end": datetime.now().isoformat(),
            "total_stages": len(self.entries),
            "stages": self.entries
        }
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════
#  MAIN PIPELINE
# ═══════════════════════════════════════════

def run_pipeline(file_arg: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    wsl_ws = WSL_WORKSPACE

    # ── 解析路徑 ──
    if os.path.isabs(file_arg) or ':' in file_arg:
        input_win = file_arg.replace('/', '\\')
        input_wsl = '/mnt/c/' + input_win[3:].replace('\\', '/') if input_win[1] == ':' else wsl_path(file_arg)
    else:
        input_win = win_path(file_arg)
        input_wsl = wsl_path(file_arg)

    # ── 檢查是否存在 ──
    if not os.path.exists(input_wsl):
        return f"❌ 找不到檔案：\nWindows: {input_win}\nWSL: {input_wsl}\n\n請確認路徑是否正確。"

    is_zip = input_wsl.lower().endswith('.zip')
    review_dir_wsl = os.path.join(wsl_ws, "code_reviews", f"review_{ts}")
    os.makedirs(review_dir_wsl, exist_ok=True)

    # ── 初始化 log ──
    log_path = os.path.join(review_dir_wsl, f"execution_log_{ts}.json")
    logger = PipelineLogger(log_path)

    # ── 處理 ZIP 或單一檔案 ──
    if is_zip:
        try:
            with zipfile.ZipFile(input_wsl, 'r') as zf:
                zf.extractall(review_dir_wsl)
        except Exception as e:
            return f"❌ ZIP 解壓失敗：{e}"

        source_files = get_source_files(review_dir_wsl)
        if not source_files:
            return f"❌ ZIP 中未找到原始碼檔案\n解壓路徑：{review_dir_wsl}"

        concat_path = os.path.join(review_dir_wsl, f"_all_files_{ts}.txt")
        concatenate_files(review_dir_wsl, source_files, concat_path)

        cli_input_win = f"{WORKSPACE}\\code_reviews\\review_{ts}\\_all_files_{ts}.txt"
        review_label = f"ZIP: {os.path.basename(file_arg)} ({len(source_files)} files)"
        file_list_str = "\n".join(f"  - {f}" for f in source_files)
    else:
        source_files = [os.path.basename(input_wsl)]
        cli_input_win = input_win
        review_label = os.path.basename(input_wsl)
        file_list_str = f"  - {os.path.basename(input_wsl)}"

    # 輸出路徑
    out_dir_win = f"{WORKSPACE}\\code_reviews\\review_{ts}\\output"
    out_dir_wsl = os.path.join(review_dir_wsl, "output")
    os.makedirs(out_dir_wsl, exist_ok=True)

    # 決定副檔名
    if is_zip:
        ext = ".txt"
    else:
        ext = os.path.splitext(source_files[0])[1] if source_files else ".txt"

    fixed_filename = f"fixed_{ts}{ext}"
    final_filename = f"final_{ts}{ext}"
    fixed_path_win = f"{out_dir_win}\\{fixed_filename}"
    final_path_win = f"{out_dir_win}\\{final_filename}"
    fixed_path_wsl = os.path.join(out_dir_wsl, fixed_filename)
    final_path_wsl = os.path.join(out_dir_wsl, final_filename)

    results = []

    # ══════════════════════════════════════
    #  Stage 1: Gemini（審查員）
    # ══════════════════════════════════════
    gemini_prompt = GEMINI_PROMPT.format(file_path=cli_input_win)
    write_prompt("prompt_code_gemini.txt", gemini_prompt)

    gemini_result = call_cli("Gemini", "prompt_code_gemini.txt", GEMINI_CMD, ["--skip-trust"])

    # Fallback
    if not gemini_result["success"] and "超時" in gemini_result.get("error", ""):
        fallback_prompt = GEMINI_FALLBACK_PROMPT.format(file_path=cli_input_win)
        write_prompt("prompt_code_gemini_fb.txt", fallback_prompt)
        fb_result = call_cli("Gemini[FB]", "prompt_code_gemini_fb.txt", GEMINI_CMD, ["--skip-trust"])
        if fb_result["success"]:
            fb_result["output"] = "⚠️ 網路搜尋超時，以下為本地知識回覆：\n\n" + fb_result["output"]
        else:
            fb_result["output"] = "⚠️ 網路搜尋超時，本地知識回覆亦失敗。"
            fb_result["success"] = False
        logger.log_stage("Gemini Fallback", "Gemini", fb_result, "prompt_code_gemini_fb.txt")
        gemini_result = fb_result

    g_icon = "✅" if gemini_result["success"] else ("⏱️" if "超時" in gemini_result.get("error", "") else "❌")
    results.append(("📡 Gemini（審查）", g_icon, gemini_result))
    logger.log_stage("Gemini Review", "Gemini", gemini_result, "prompt_code_gemini.txt")

    # ══════════════════════════════════════
    #  Stage 2: Claude（修復工程師）
    # ══════════════════════════════════════
    claude_prompt = CLAUDE_PROMPT.format(
        file_path=cli_input_win,
        gemini_output=gemini_result["output"] or "(Gemini 無輸出)"
    )
    write_prompt("prompt_code_claude.txt", claude_prompt)

    claude_result = call_cli("Claude", "prompt_code_claude.txt", CLAUDE_CMD, ["--print"])

    # 提取程式碼
    claude_actions = []
    if claude_result["success"] and claude_result["output"]:
        fixed_code = extract_between_markers(
            claude_result["output"],
            "<<<FIXED_CODE_START>>>",
            "<<<FIXED_CODE_END>>>"
        )

        if fixed_code:
            # 有標記，精確提取
            with open(fixed_path_wsl, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            claude_actions.append(f"✅ 從 stdout 標記提取程式碼，存入 {fixed_filename}")
            claude_result["output"] += f"\n\n📁 已存檔：{fixed_path_win}"
        elif len(claude_result["output"]) > 50:
            # 沒有標記但有輸出，整段存檔
            with open(fixed_path_wsl, "w", encoding="utf-8") as f:
                f.write(claude_result["output"])
            claude_actions.append(f"⚠️ 未找到 <<<FIXED_CODE_*>>> 標記，整段 stdout 備存為 {fixed_filename}")
            claude_result["output"] += f"\n\n⚠️ Claude 未使用標記格式，已整段 stdout 備存至：{fixed_path_win}"
        else:
            claude_actions.append("⚠️ Claude 輸出過短且無標記，無有效程式碼")
            claude_result["output"] += "\n\n⚠️ 無有效程式碼輸出"

    c_icon = "✅" if claude_result["success"] else ("⏱️" if "超時" in claude_result.get("error", "") else "❌")
    results.append(("🔧 Claude（修改）", c_icon, claude_result))
    logger.log_stage("Claude Fix", "Claude", claude_result, "prompt_code_claude.txt", claude_actions)

    # ══════════════════════════════════════
    #  Stage 3: Codex（最終驗證）
    # ══════════════════════════════════════
    # 讀取 Claude 產出的 fixed code 傳給 Codex
    fixed_code_content = ""
    if os.path.exists(fixed_path_wsl):
        with open(fixed_path_wsl, "r", encoding="utf-8", errors="replace") as f:
            fixed_code_content = f.read()
    else:
        fixed_code_content = "(Claude 未產出修改後程式碼)"

    codex_prompt = CODEX_PROMPT.format(
        file_path=cli_input_win,
        fixed_code=fixed_code_content[:15000],  # 防止 prompt 過大
        gemini_output=gemini_result["output"] or "(Gemini 無輸出)"
    )
    write_prompt("prompt_code_codex.txt", codex_prompt)

    codex_result = call_cli("Codex", "prompt_code_codex.txt", CODEX_CMD, ["exec", "--skip-git-repo-check"])

    # 提取 Codex 修正版（如果有）
    codex_actions = []
    if codex_result["success"] and codex_result["output"]:
        final_code = extract_between_markers(
            codex_result["output"],
            "<<<FINAL_CODE_START>>>",
            "<<<FINAL_CODE_END>>>"
        )

        if final_code:
            with open(final_path_wsl, "w", encoding="utf-8") as f:
                f.write(final_code)
            codex_actions.append(f"✅ Codex 修正版已提取並存入 {final_filename}")
            codex_result["output"] += f"\n\n📁 已存檔：{final_path_win}"
        else:
            codex_actions.append("Codex 無修正版，最終版本為 Claude 產出")

    x_icon = "✅" if codex_result["success"] else ("⏱️" if "超時" in codex_result.get("error", "") else "❌")
    results.append(("⚙️ Codex（驗證）", x_icon, codex_result))
    logger.log_stage("Codex Verify", "Codex", codex_result, "prompt_code_codex.txt", codex_actions)

    # ── 儲存完整結果到備查檔 ──
    try:
        report_path = os.path.join(out_dir_wsl, f"review_report_{ts}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Code Review Report — {ts}\n\n")
            f.write(f"**檔案**: {review_label}\n")
            f.write(f"**檔案列表**:\n{file_list_str}\n\n")
            for label, icon, result in results:
                f.write(f"## {label} {icon}\n\n")
                f.write(result.get("output", result.get("error", "N/A")))
                f.write(f"\n\n_耗時: {result['elapsed']}s_\n\n")
    except Exception:
        pass

    # ── 儲存 execution log ──
    logger.flush()

    # ── 組裝最終輸出 ──
    parts = [f"🔍 **3AI 程式碼審查結果**\n📂 `{review_label}`\n"]

    if is_zip:
        parts.append(f"\n📋 檔案列表（{len(source_files)} 個）：\n```\n{file_list_str}\n```\n")

    sep = "\n━━━━━━━━━━━━━━━━━━━━\n"
    for label, icon, result in results:
        parts.append(sep)
        status = f" ({result['elapsed']}s)" if result["success"] else ""
        content = result["output"] if result["success"] else (result["output"] or result["error"] or "無輸出")
        parts.append(f"{icon} **{label}**{status}\n{truncate(content)}")

    # 最終路徑
    parts.append(sep)
    parts.append("📁 **最終檔案位置**\n")

    if os.path.exists(final_path_wsl):
        parts.append(f"`{final_path_win}`")
    elif os.path.exists(fixed_path_wsl):
        parts.append(f"`{fixed_path_win}`")
    else:
        parts.append("⚠️ 無最終檔案（審查可能無需修改或 CLI 未成功產出）")

    parts.append(f"\n\n📋 完整報告：`{out_dir_win}\\review_report_{ts}.md`")
    parts.append(f"\n📝 執行日誌：`{out_dir_win}\\..\\execution_log_{ts}.json`")

    return "\n".join(parts)


# ═══════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pipeline.py \"path\\to\\file.py\" 或 \"path\\to\\project.zip\"")
        sys.exit(1)

    file_arg = " ".join(sys.argv[1:])
    result = run_pipeline(file_arg)
    print(result)
