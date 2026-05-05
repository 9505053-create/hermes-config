#!/usr/bin/env python3
"""
3AI Pipeline — 純搬運管線
Hermes 零思考，Gemini → Claude → Codex 依次淬鍊問題
Usage: python3 pipeline.py "你的問題"
"""

import os
import sys
import re
import subprocess
import time
from datetime import datetime

# ═══════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════
WORKSPACE = r"C:\Users\chien\_3AI_WorkSpace"
RESULT_DIR = os.path.join(WORKSPACE, "pipeline_results")
WSL_WORKSPACE = "/mnt/c/Users/chien/_3AI_WorkSpace"

MAX_OUTPUT_CHARS = 4000       # 每段輸出截斷上限
CLI_TIMEOUT = 180             # 每個 CLI 最長等待秒數（Gemini 搜尋需較久）

GEMINI_CMD = r"C:\Users\chien\AppData\Roaming\npm\gemini.cmd"
CLAUDE_CMD = r"C:\Users\chien\AppData\Roaming\npm\claude.cmd"
CODEX_CMD  = r"C:\Users\chien\AppData\Roaming\npm\codex.cmd"

# ═══════════════════════════════════════════
#  PROMPT TEMPLATES（支援四種任務類型）
# ═══════════════════════════════════════════
# 任務類型分類：
#   A = 資訊分析（事實查核、介紹、比較、研究）
#   B = 創意寫作（文章、故事、詩詞、文案）
#   C = 技術問題（程式、系統架構、debug、工程）
#   D = 其他（翻譯、摘要、建議、一般對話）
# ═══════════════════════════════════════════

GEMINI_PROMPT = """你是任務分類員兼情報搜集員。請先判斷以下問題的類型，再執行對應工作。

【任務類型判斷】在回答的第一行，必須輸出以下其中一個標籤（單獨一行）：
[TASK_TYPE: A] — 資訊分析類（事實查核、公司介紹、歷史事件、比較分析、研究調查）
[TASK_TYPE: B] — 創意寫作類（文章撰寫、故事創作、詩詞、文案、劇本）
[TASK_TYPE: C] — 技術問題類（程式開發、系統架構、debug、演算法、工程實作）
[TASK_TYPE: D] — 其他類（翻譯、摘要、一般建議、日常對話、開放式問題）

【各類型工作內容】
A 類：判斷是否需要網路資料 → 需要就搜尋 → 整理客觀資訊 + 來源，只做情報不做結論
B 類：搜集相關背景素材、風格參考、修辭靈感，整理後交給後續階段產出成品
C 類：搜集技術文件、API 語法、已知問題、最佳實踐，整理後交給後續階段
D 類：搜集相關背景知識，整理後交給後續階段

【規則】
- 第一行必須是 [TASK_TYPE: X]，後面才是內容
- 標註資料來源
- 如果不確定，明確說「此處資訊可能不完整」
- 用繁體中文回答

【問題】
{question}"""

GEMINI_FALLBACK_PROMPT = """你是任務分類員兼情報搜集員。以下問題的網路搜尋目前無法使用，請完全依賴你的訓練資料回答。

【任務類型判斷】在回答的第一行，必須輸出以下其中一個標籤（單獨一行）：
[TASK_TYPE: A] — 資訊分析類
[TASK_TYPE: B] — 創意寫作類
[TASK_TYPE: C] — 技術問題類
[TASK_TYPE: D] — 其他類

【重要】
- 第一行必須是 [TASK_TYPE: X]，後面才是內容
- 禁止使用網路搜尋功能
- 僅根據你已知的知識整理客觀資訊
- 明確標註「以下為本地知識，未經網路查證」
- 如果你的知識不足以回答，誠實說明哪些部分不確定
- 用繁體中文回答

【問題】
{question}"""

# ── Claude：四模式 prompt ──

CLAUDE_PROMPT_A = """你是批判分析員。以下是 Gemini 提供的情報資料，以及原始問題。

【原始問題】
{question}

【Gemini 情報】
{gemini_output}

【你的任務】
1. 理解 Gemini 的資料內容
2. 找出漏洞、缺漏、不合理之處
3. 發表你對內容的分析與理解
4. 補充可能被忽略的面向
5. 用繁體中文回答

不要重複貼 Gemini 的內容，直接分析。"""

CLAUDE_PROMPT_B = """你是創意寫作者。以下是 Gemini 提供的背景素材，以及原始問題。

【原始問題】
{question}

【Gemini 背景素材】
{gemini_output}

【你的任務】
1. 以 Gemini 的素材為參考，直接產出完整的成品文章
2. 融入真情實感，避免空洞口號
3. 注意起承轉合、節奏與情感張力
4. 不要回覆分析或評論，直接給成品
5. 用繁體中文撰寫

直接產出成品，不要說「以下是一篇文章」之類的開場白。"""

CLAUDE_PROMPT_C = """你是技術問題解決者。以下是 Gemini 提供的技術參考資料，以及原始問題。

【原始問題】
{question}

【Gemini 技術參考】
{gemini_output}

【你的任務】
1. 理解問題的技術本質
2. 分析 Gemini 資料中的技術觀點是否正確
3. 提供具體的解決方案或回答
4. 如果涉及程式碼，提供可執行的範例
5. 用繁體中文回答

直接給解決方案，不要空泛的分析。"""

CLAUDE_PROMPT_D = """你是全能助理。以下是 Gemini 提供的相關資料，以及原始問題。

【原始問題】
{question}

【Gemini 資料】
{gemini_output}

【你的任務】
1. 理解原始問題的真正需求
2. 參考 Gemini 的資料，直接產出完整、可用的回答
3. 如果是翻譯題，直接給翻譯結果
4. 如果是建議題，給出具體可行的建議
5. 用繁體中文回答

直接產出成品，不要多餘的分析框架。"""

# ── Codex：四模式 prompt ──

CODEX_PROMPT_A = """你是技術審核員。以下是原始問題、Gemini 的情報、以及 Claude 的分析。

【原始問題】
{question}

【Gemini 情報】
{gemini_output}

【Claude 分析】
{claude_output}

【你的任務】
1. 先判斷此問題是否涉及技術/邏輯/系統架構
2. 若是技術題：
   - 驗證 Gemini + Claude 的技術說法是否合理
   - 找出技術錯誤或邏輯矛盾
   - 整合三方資訊，形成最終成熟結論
3. 若非技術題：
   - 直接回覆：「此問題非技術性質，跳過技術審核。建議直接採納 Claude 分析。」
4. 用繁體中文回答"""

CODEX_PROMPT_B = """你是品質優化者。以下是原始問題、Gemini 的素材、以及 Claude 產出的成品。

【原始問題】
{question}

【Gemini 素材】
{gemini_output}

【Claude 成品】
{claude_output}

【你的任務】
1. 潤飾 Claude 產出的文章，改善用詞、節奏與流暢度
2. 修正任何語法錯誤、不通順之處
3. 如果文章已經很好，只需微調，不要大幅改寫
4. 保留原文的風格與情感，不要讓它變成「AI味很重」的改寫
5. 產出最終潤飾版，直接給成品
6. 用繁體中文"""

CODEX_PROMPT_C = """你是技術驗證者。以下是原始問題、Gemini 的技術參考、以及 Claude 的解決方案。

【原始問題】
{question}

【Gemini 技術參考】
{gemini_output}

【Claude 解決方案】
{claude_output}

【你的任務】
1. 驗證 Claude 的技術方案是否正確
2. 檢查程式碼是否有 bug、安全漏洞或效能問題
3. 如果發現問題，提供修正後的版本
4. 如果 Claude 的方案正確且完整，簡短確認即可
5. 用繁體中文回答"""

CODEX_PROMPT_D = """你是品質優化者。以下是原始問題、Gemini 的資料、以及 Claude 的回答。

【原始問題】
{question}

【Gemini 資料】
{gemini_output}

【Claude 回答】
{claude_output}

【你的任務】
1. 潤飾 Claude 的回答，改善表達的清晰度與流暢度
2. 修正任何錯誤或補充遺漏的重點
3. 如果 Claude 的回答已經很好，只需微調
4. 產出最終優化版，直接給成品
5. 用繁體中文"""

# ═══════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════

def truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    """截斷過長輸出"""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n_(已截斷，原始輸出 {len(text)} 字元)_"


def write_prompt(filename: str, content: str):
    """寫 prompt 檔到 WSL 可存取的共享空間"""
    path = os.path.join(WSL_WORKSPACE, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def call_cli(cmd_name: str, pipe_file: str, cli_cmd: str, extra_args: list[str] = None) -> dict:
    """
    呼叫 CLI，回傳 {success, output, error, elapsed}
    """
    args = " ".join(extra_args) if extra_args else ""
    full_cmd = (
        f'/mnt/c/Windows/System32/cmd.exe /c '
        f'"cd /d {WORKSPACE} && type {pipe_file} | {cli_cmd} {args}"'
    )

    start = time.time()
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
            encoding="utf-8",
            errors="replace"
        )
        elapsed = time.time() - start

        output = result.stdout.strip()
        if not output and result.stderr.strip():
            output = result.stderr.strip()

        return {
            "success": result.returncode == 0 and bool(output),
            "output": output or "",
            "error": result.stderr.strip() if result.returncode != 0 else "",
            "elapsed": round(elapsed, 1)
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"超時（>{CLI_TIMEOUT}s）",
            "elapsed": CLI_TIMEOUT
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "elapsed": round(time.time() - start, 1)
        }


def format_section(label: str, icon: str, result: dict) -> str:
    """格式化單段輸出為 Telegram Markdown"""
    status = ""
    if not result["success"]:
        if "超時" in result.get("error", ""):
            status = f" ⏱️ 超時 ({result['elapsed']}s)"
        elif result["error"]:
            status = f" ❌ 失敗：{result['error'][:100]}"
        else:
            status = " ⚠️ 無回應"
    else:
        status = f" ✅ ({result['elapsed']}s)"

    content = result["output"] if result["success"] else (
        result["output"] or result["error"] or "無輸出"
    )

    return f"{icon} **{label}**{status}\n{truncate(content)}"


def save_to_workspace(question: str, sections: list[tuple[str, str, dict]]):
    """儲存完整結果到共享空間備查"""
    try:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path_wsl = os.path.join(WSL_WORKSPACE, "pipeline_results", f"run_{ts}.md")
        os.makedirs(os.path.dirname(result_path_wsl), exist_ok=True)

        lines = [f"# 3AI Pipeline Run — {ts}\n", f"**Question**: {question}\n"]
        for label, icon, result in sections:
            lines.append(f"\n## {label}\n")
            lines.append(result.get("output", result.get("error", "N/A")))

        with open(result_path_wsl, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except Exception:
        pass  # 備存失敗不中斷流程


def parse_task_type(gemini_output: str) -> tuple[str, str]:
    """
    從 Gemini 輸出解析任務類型標籤。
    回傳 (task_type, cleaned_output)。
    task_type 為 'A'/'B'/'C'/'D'，預設 'A'。
    """
    match = re.search(r'\[TASK_TYPE:\s*([ABCD])\]', gemini_output)
    if match:
        task_type = match.group(1)
        # 移除標籤行（含前後空白行）
        cleaned = re.sub(r'\[TASK_TYPE:\s*[ABCD]\]\s*\n?', '', gemini_output, count=1).strip()
        return task_type, cleaned
    return 'A', gemini_output  # 預設 A（向後相容）


# 任務類型對應的 prompt 字典
CLAUDE_PROMPTS = {
    'A': CLAUDE_PROMPT_A,
    'B': CLAUDE_PROMPT_B,
    'C': CLAUDE_PROMPT_C,
    'D': CLAUDE_PROMPT_D,
}
CODEX_PROMPTS = {
    'A': CODEX_PROMPT_A,
    'B': CODEX_PROMPT_B,
    'C': CODEX_PROMPT_C,
    'D': CODEX_PROMPT_D,
}

# 任務類型對應的顯示標籤
TASK_LABELS = {
    'A': {
        'gemini': ("Gemini（情報搜集）", "📡"),
        'claude': ("Claude（批判分析）", "🔬"),
        'codex': ("Codex（技術審核）", "⚙️"),
    },
    'B': {
        'gemini': ("Gemini（素材搜集）", "📡"),
        'claude': ("Claude（創意產出）", "✍️"),
        'codex': ("Codex（品質潤飾）", "✨"),
    },
    'C': {
        'gemini': ("Gemini（技術參考）", "📡"),
        'claude': ("Claude（問題解決）", "🔧"),
        'codex': ("Codex（技術驗證）", "⚙️"),
    },
    'D': {
        'gemini': ("Gemini（背景資料）", "📡"),
        'claude': ("Claude（直接回答）", "💬"),
        'codex': ("Codex（品質優化）", "✨"),
    },
}


# ═══════════════════════════════════════════
#  MAIN PIPELINE
# ═══════════════════════════════════════════

def run_pipeline(question: str) -> str:
    """執行三階段管線，回傳最終 Telegram 訊息"""

    sections = []

    # ── Stage 1: Gemini（含超時 fallback）──
    gemini_prompt = GEMINI_PROMPT.format(question=question)
    write_prompt("prompt_gemini.txt", gemini_prompt)

    gemini_result = call_cli("Gemini", "prompt_gemini.txt", GEMINI_CMD, ["--skip-trust"])

    # 如果 Gemini 超時 → 用 fallback prompt 重試（不觸發網路搜尋）
    if not gemini_result["success"] and "超時" in gemini_result.get("error", ""):
        fallback_prompt = GEMINI_FALLBACK_PROMPT.format(question=question)
        write_prompt("prompt_gemini_fallback.txt", fallback_prompt)
        fallback_result = call_cli("Gemini[Fallback]", "prompt_gemini_fallback.txt", GEMINI_CMD, ["--skip-trust"])

        if fallback_result["success"]:
            fallback_result["output"] = (
                "⚠️ 網路搜尋超時（>180s），以下為本地知識回覆：\n\n"
                + fallback_result["output"]
            )
        else:
            fallback_result["output"] = "⚠️ 網路搜尋超時，本地知識回覆亦失敗。"
            fallback_result["success"] = False

        gemini_result = fallback_result

    # 解析任務類型標籤
    task_type, gemini_clean = parse_task_type(gemini_result["output"])
    labels = TASK_LABELS.get(task_type, TASK_LABELS['A'])

    # 用清理後的輸出（移除標籤行）更新結果
    if gemini_clean:
        gemini_result["output"] = gemini_clean

    sections.append((*labels["gemini"], gemini_result))

    # ── Stage 2: Claude（根據任務類型選 prompt）──
    claude_prompt_tpl = CLAUDE_PROMPTS.get(task_type, CLAUDE_PROMPT_A)
    claude_prompt = claude_prompt_tpl.format(
        question=question,
        gemini_output=gemini_result["output"] or "(Gemini 無輸出)"
    )
    write_prompt("prompt_claude.txt", claude_prompt)

    claude_result = call_cli("Claude", "prompt_claude.txt", CLAUDE_CMD, ["--print"])
    sections.append((*labels["claude"], claude_result))

    # ── Stage 3: Codex（根據任務類型選 prompt）──
    codex_prompt_tpl = CODEX_PROMPTS.get(task_type, CODEX_PROMPT_A)
    codex_prompt = codex_prompt_tpl.format(
        question=question,
        gemini_output=gemini_result["output"] or "(Gemini 無輸出)",
        claude_output=claude_result["output"] or "(Claude 無輸出)"
    )
    write_prompt("prompt_codex.txt", codex_prompt)

    codex_result = call_cli("Codex", "prompt_codex.txt", CODEX_CMD, ["exec", "--skip-git-repo-check"])
    sections.append((*labels["codex"], codex_result))

    # ── 組裝最終輸出 ──
    header = "🔍 **3AI 管線結果**\n"
    separator = "\n━━━━━━━━━━━━━━━━━━━━\n"

    parts = [header]
    for label, icon, result in sections:
        parts.append(separator)
        parts.append(format_section(label, icon, result))

    # ── 備存完整結果 ──
    save_to_workspace(question, sections)

    return "\n".join(parts)


# ═══════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pipeline.py \"你的問題\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = run_pipeline(question)
    print(result)
