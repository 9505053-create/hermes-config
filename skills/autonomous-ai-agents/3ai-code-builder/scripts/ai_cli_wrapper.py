#!/usr/bin/env python3
"""
ai_cli_wrapper.py — 統一 3AI CLI 啟動介面
解決 WSL→Windows cmd.exe 路徑/登入/stderr 噪音問題。

用法：
    from ai_cli_wrapper import call_cli
    result = call_cli("claude", r"C:\path\to\prompt.txt", "phase0")

回傳：
    {
        "tool": "claude",
        "phase": "phase0",
        "status": "PASS" | "FAIL",
        "returncode": 0,
        "stdout": "...",
        "stderr": "...",
        "stdout_path": "raw/phase0_claude_stdout.txt",
        "stderr_path": "raw/phase0_claude_stderr.txt",
        "duration_seconds": 45.2
    }
"""

import subprocess
import time
import os
import re
import json
from pathlib import Path

# === 常數 ===
CMD_EXE = "/mnt/c/Windows/System32/cmd.exe"
CLAUDE_CMD = "claude.cmd"
GEMINI_CMD = "gemini.cmd"
CODEX_CMD = "codex.cmd"

# stderr 噪音過濾 patterns（AttachConsole、conpty 等）
NOISE_PATTERNS = [
    re.compile(r"AttachConsole failed"),
    re.compile(r"conpty_console_list_agent"),
    re.compile(r"CMD\.EXE was started with the above path"),
    re.compile(r"UNC paths are not supported"),
    re.compile(r"Defaulting to Windows directory"),
    re.compile(r"Warning: 256-color support not detected"),
    re.compile(r"YOLO mode is enabled"),
    re.compile(r"Ripgrep is not available"),
    re.compile(r"node-pty"),
    re.compile(r"var consoleProcessList"),
]

# CLI 指令模板
CLI_COMMANDS = {
    "claude": f'cd /d {{workdir}} && type {{prompt}} | {CLAUDE_CMD} --print --allowedTools "Bash Write Edit"',
    "gemini": f'cd /d {{workdir}} && type {{prompt}} | {GEMINI_CMD} --skip-trust --approval-mode yolo',
    "codex":  f'cd /d {{workdir}} && type {{prompt}} | {CODEX_CMD} exec --skip-git-repo-check --sandbox workspace-write',
}


def _filter_stderr(stderr: str) -> str:
    """過濾 stderr 中的已知噪音"""
    lines = stderr.splitlines()
    filtered = []
    for line in lines:
        if any(p.search(line) for p in NOISE_PATTERNS):
            continue
        filtered.append(line)
    return "\n".join(filtered).strip()


def _win_path(linux_path: str) -> str:
    """將 WSL Linux 路徑轉換為 Windows 路徑"""
    p = linux_path.replace("/mnt/c/", "C:\\").replace("/mnt/d/", "D:\\")
    return p.replace("/", "\\")


# === Phase-specific timeout profiles (v2.4 — Codex=heavy, Claude=light) ===
TIMEOUT_PROFILES = {
    # tool -> phase_keyword -> timeout_seconds
    "codex": {
        "phase0": 180,      # 架構規劃，通常 60-120s
        "phase1": 600,      # 寫完整程式碼，可能需要 3-5 分鐘
        "_default": 300,
    },
    "gemini": {
        "_default": 180,    # Gemini 通常較快（Phase 2 review）
    },
    "claude": {
        "phase3": 300,      # 修正階段（Phase 3）
        "_default": 180,
    },
}

# Hang detection: 如果 stdout 檔案超過此秒數沒增長，視為可能卡死
HANG_THRESHOLD_SECONDS = 120


def _get_timeout(tool: str, phase: str) -> int:
    """根據 tool + phase 選擇合適的 timeout"""
    profiles = TIMEOUT_PROFILES.get(tool, {})
    for key, val in profiles.items():
        if key != "_default" and key in phase:
            return val
    return profiles.get("_default", 300)


def _linux_to_win_path(linux_path: str) -> str:
    """WSL Linux 路徑 → Windows 絕對路徑（用於 subprocess 的 cwd）"""
    return linux_path.replace("/mnt/c/", "C:\\").replace("/mnt/d/", "D:\\").replace("/", "\\")


def build_background_cmd(
    tool: str,
    prompt_path: str,
    phase: str = "",
    workdir: str = r"C:\Users\chien\_3AI_WorkSpace",
) -> str:
    """
    組裝 CLI 命令字串，供 Hermes terminal(background=true) 使用。

    用途：Phase 1 等長時間任務，不能用 execute_code（300s 硬上限）。
    取得命令字串後，用 Hermes terminal(command=cmd, background=true, notify_on_complete=true) 執行。

    Args:
        tool: "claude" | "gemini" | "codex"
        prompt_path: prompt 檔案路徑（Windows 格式）
        phase: 階段名稱（用於 logging）
        workdir: Windows 工作目錄

    Returns:
        完整 shell 命令字串
    """
    if tool not in CLI_COMMANDS:
        raise ValueError(f"Unknown tool: {tool}. Must be one of {list(CLI_COMMANDS.keys())}")

    # 確保 prompt_path 是 Windows 格式
    if prompt_path.startswith("/mnt/"):
        win_prompt = _win_path(prompt_path)
    else:
        win_prompt = prompt_path

    cmd_str = CLI_COMMANDS[tool].format(workdir=workdir, prompt=win_prompt)
    # 返回完整命令（Hermes terminal 工具會用 background=true 執行）
    return f'{CMD_EXE} /c "{cmd_str}"'


def call_cli(
    tool: str,
    prompt_path: str,
    phase: str,
    workdir: str = r"C:\Users\chien\_3AI_WorkSpace",
    raw_dir: str = None,
    timeout: int = None,
    progress_callback=None,
) -> dict:
    """
    統一呼叫 3AI CLI（v2.2 — 帶進度監控 + 自適應 timeout）。

    Args:
        tool: "claude" | "gemini" | "codex"
        prompt_path: prompt 檔案路徑（Linux 或 Windows 格式皆可）
        phase: 階段名稱（如 "phase0", "phase1"）
        workdir: Windows 工作目錄
        raw_dir: raw log 輸出目錄（Linux 路徑），None 則不存檔
        timeout: 秒數（None = 根據 tool+phase 自動選擇）
        progress_callback: 可選回調 fn(elapsed, status_msg) 用於進度通知

    Returns:
        dict with keys: tool, phase, status, returncode, stdout, stderr,
                        stdout_path, stderr_path, duration_seconds, progress_log
    """
    if tool not in CLI_COMMANDS:
        raise ValueError(f"Unknown tool: {tool}. Must be one of {list(CLI_COMMANDS.keys())}")

    # 自適應 timeout
    if timeout is None:
        timeout = _get_timeout(tool, phase)

    # 路徑轉換
    if prompt_path.startswith("/mnt/"):
        win_prompt = _win_path(prompt_path)
    else:
        win_prompt = prompt_path

    # 組裝命令
    cmd_str = CLI_COMMANDS[tool].format(workdir=workdir, prompt=win_prompt)
    full_cmd = [CMD_EXE, "/c", cmd_str]

    # 預備 raw log 路徑
    stdout_path = None
    stderr_path = None
    if raw_dir:
        os.makedirs(raw_dir, exist_ok=True)
        stdout_path = os.path.join(raw_dir, f"{phase}_{tool}_stdout.txt")
        stderr_path = os.path.join(raw_dir, f"{phase}_{tool}_stderr.txt")

    # === v2.2: 非阻塞執行 + 進度監控 ===
    # 監控策略：
    #   1. stdout pipe 非阻塞讀取（每 2s 檢查一次）
    #   2. 工作目錄檔案監控（Claude 用 Write 工具會直接建檔）
    #   3. Hang detection：超過 N 秒無任何活動 → 警告
    start = time.time()
    progress_log = []
    last_activity_time = start
    # 記錄工作目錄初始狀態（Windows 路徑 → Linux 路徑 for monitoring）
    linux_workdir = workdir.replace("C:\\", "/mnt/c/").replace("D:\\", "/mnt/d/").replace("\\", "/")

    def _log(msg):
        nonlocal last_activity_time
        elapsed = round(time.time() - start, 1)
        entry = f"[{elapsed}s] {msg}"
        progress_log.append(entry)
        last_activity_time = time.time()
        if progress_callback:
            progress_callback(elapsed, msg)

    def _check_workdir_activity():
        """檢查工作目錄是否有新檔案/變更（Claude 寫檔進度）"""
        nonlocal last_activity_time
        if not os.path.exists(linux_workdir):
            return
        try:
            for item in os.listdir(linux_workdir):
                item_path = os.path.join(linux_workdir, item)
                if os.path.isfile(item_path):
                    mtime = os.path.getmtime(item_path)
                    if mtime > last_activity_time:
                        size = os.path.getsize(item_path)
                        _log(f"File activity: {item} ({size} bytes)")
        except (PermissionError, OSError):
            pass

    _log(f"Starting {tool} (timeout={timeout}s, phase={phase})")

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # line-buffered
        )

        # 設定 non-blocking reads（Unix/WSL 支援）
        import select
        import fcntl
        for fd in [proc.stdout.fileno(), proc.stderr.fileno()]:
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        # 輪詢等待
        while proc.poll() is None:
            elapsed = time.time() - start

            # 超時檢查
            if elapsed > timeout:
                proc.kill()
                proc.wait(timeout=5)
                _log(f"TIMEOUT after {timeout}s")
                stdout_raw = ""
                stderr_raw = f"TIMEOUT after {timeout}s"
                returncode = -1
                break

            # 非阻塞讀取 stdout/stderr
            try:
                ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.1)
                for stream in ready:
                    chunk = stream.read(4096)
                    if chunk:
                        _log(f"Output ({len(chunk)} chars) from {'stdout' if stream == proc.stdout else 'stderr'}")
            except (IOError, OSError):
                pass

            # 監控工作目錄（Claude 寫檔進度）
            _check_workdir_activity()

            # Hang detection
            silence_duration = time.time() - last_activity_time
            if silence_duration > HANG_THRESHOLD_SECONDS:
                _log(f"⚠️ WARNING: No activity for {int(silence_duration)}s (may be stuck)")

            time.sleep(2)  # 輪詢間隔
        else:
            # 正常結束 — 讀取剩餘輸出
            stdout_raw = proc.stdout.read() if proc.stdout else ""
            stderr_raw = proc.stderr.read() if proc.stderr else ""
            returncode = proc.returncode
            _log(f"✅ Completed (exit={returncode}, {time.time()-start:.1f}s)")

    except Exception as e:
        stdout_raw = ""
        stderr_raw = f"EXCEPTION: {e}"
        returncode = -2
        _log(f"❌ Exception: {e}")

    duration = time.time() - start
    stdout = stdout_raw
    stderr = _filter_stderr(stderr_raw)

    # 判斷 status
    status = "PASS" if returncode == 0 and stdout.strip() else "FAIL"

    # 存 raw log
    if raw_dir:
        if stdout_path:
            with open(stdout_path, "w", encoding="utf-8") as f:
                f.write(stdout)
        if stderr_path:
            with open(stderr_path, "w", encoding="utf-8") as f:
                f.write(stderr)

    return {
        "tool": tool,
        "phase": phase,
        "status": status,
        "returncode": returncode,
        "stdout": stdout,
        "stderr": stderr,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "duration_seconds": round(duration, 1),
        "progress_log": progress_log,
    }


# === CLI 時間戳 ===
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python ai_cli_wrapper.py <tool> <prompt_path> <phase> [raw_dir]")
        print("  tool: claude | gemini | codex")
        sys.exit(1)

    tool = sys.argv[1]
    prompt_path = sys.argv[2]
    phase = sys.argv[3]
    raw_dir = sys.argv[4] if len(sys.argv) > 4 else None

    result = call_cli(tool, prompt_path, phase, raw_dir=raw_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))
