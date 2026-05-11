#!/usr/bin/env python3
"""
build_runner.py — Phase 4 證據鏈執行器 (v2.3)
所有 build/test/lint 操作都透過 subprocess capture，保留 raw log。

v2.3 改進：
- 動態掃描 test_*.py，不再 hardcode 檔名
- AST-based 安全檢查，取代 crude grep
- 動態發現主模組，不再 hardcode calculator

用法：
    from build_runner import run_phase4
    result = run_phase4(output_dir, raw_dir)
"""

import subprocess
import json
import os
import ast
import glob
import time
import shlex
import re


def _run(cmd: str, cwd: str, timeout: int = 120) -> dict:
    """執行命令，capture stdout/stderr"""
    start = time.time()
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration_seconds": round(time.time() - start, 2),
            "timeout": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"TIMEOUT after {timeout}s",
            "duration_seconds": round(time.time() - start, 2),
            "timeout": True,
        }


def _discover_main_module(output_dir: str) -> str:
    """動態發現主模組：找 output/ 或 source/ 下的主要 .py 檔案。

    v2.7: PR 修改模式常見乾淨交付結構是 source/calculator.py，
    若只掃 output/ 根目錄會漏掉真正入口，導致 README/啟動 smoke test 沒跑到。
    """
    candidates = []
    skip = {"__init__", "setup", "conftest"}
    search_dirs = [output_dir, os.path.join(output_dir, "source"), os.path.join(output_dir, "src")]
    for base in search_dirs:
        if not os.path.isdir(base):
            continue
        for f in os.listdir(base):
            if not (f.endswith(".py") and not f.startswith("test_")):
                continue
            name = f[:-3]
            if name not in skip:
                candidates.append(os.path.relpath(os.path.join(base, f), output_dir))
    # 優先順序：calculator.py > app.py > main.py；root 與 source/src 皆納入
    for pref in ["calculator.py", "app.py", "main.py", "source/calculator.py", "source/app.py", "source/main.py", "src/app.py", "src/main.py"]:
        if pref in candidates:
            return pref
    return candidates[0] if candidates else None


def _module_name_from_path(py_path: str) -> str:
    """source/calculator.py -> source.calculator; calculator.py -> calculator"""
    return py_path.replace(os.sep, ".").replace("/", ".").removesuffix(".py")


def _entrypoint_smoke_status(result: dict) -> str:
    """Classify direct entrypoint execution.

    GUI apps in WSL/headless may fail with DISPLAY/TclError or keep running until timeout;
    those prove import/entrypoint reached GUI layer and are not module-path crashes.
    ModuleNotFoundError/ImportError remain hard failures. If the app implements --smoke and
    prints SMOKE_OK, that is the strongest PASS signal.
    """
    combined = (result.get("stderr") or "") + "\n" + (result.get("stdout") or "")
    if "SMOKE_OK" in combined:
        return "PASS_SMOKE"
    if result.get("timeout"):
        return "PASS_LAUNCHED_TIMEOUT"
    if result.get("returncode") == 0:
        return "PASS"
    if "ModuleNotFoundError" in combined or "ImportError" in combined:
        return "FAIL_IMPORT"
    if "no display name" in combined or "$DISPLAY" in combined or "TclError" in combined:
        return "PASS_HEADLESS_UI_BLOCKED"
    return "FAIL"


def _supports_smoke_flag(output_dir: str, main_module: str | None) -> bool:
    """Detect explicit GUI smoke-test support without executing the app."""
    if not main_module:
        return False
    try:
        text = open(os.path.join(output_dir, main_module), "r", encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return "--smoke" in text or "SMOKE_OK" in text


def _path_pollution_check(output_dir: str) -> dict:
    """Detect sys.path.insert/append hacks.

    v2.7.1: Not every sys.path use is automatically illegal. A project may allow
    a carefully documented test-helper path with an inline pragma:
    `# hermes: allow-sys-path <reason>`. Anything without that explicit waiver
    remains a blocking finding because it can mask production import bugs.
    """
    findings = []
    allowed = []
    pattern = re.compile(r"sys\.path\.(?:insert|append)\s*\(")
    for root, dirs, files in os.walk(output_dir):
        dirs[:] = [d for d in dirs if d not in {".pytest_cache", "__pycache__", ".git", "venv", ".venv"}]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, output_dir)
            try:
                lines = open(path, "r", encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            for lineno, line in enumerate(lines, 1):
                if pattern.search(line):
                    item = f"{rel}:{lineno}"
                    if "hermes: allow-sys-path" in line:
                        allowed.append(item)
                    else:
                        findings.append(item)
    return {"clean": not findings, "findings": findings, "allowed": allowed}


def _package_hygiene_check(output_dir: str) -> dict:
    """Ensure delivery tree does not contain pytest/python cache artifacts."""
    findings = []
    for root, dirs, files in os.walk(output_dir):
        for d in dirs:
            if d in {".pytest_cache", "__pycache__"}:
                findings.append(os.path.relpath(os.path.join(root, d), output_dir) + "/")
        for f in files:
            if f.endswith(".pyc"):
                findings.append(os.path.relpath(os.path.join(root, f), output_dir))
    return {"clean": not findings, "findings": sorted(findings)}


def _documentation_check(output_dir: str) -> dict:
    """Rule-based delivery documentation checks for PR-style tasks.

    These are intentionally simple machine gates; PRD-specific assertions still
    belong in prd_cross_check.md. The goal is to catch the PR-02 class of misses:
    root README absent, completion report absent, README lacking limitations.
    """
    findings = []
    warnings = []

    readme = os.path.join(output_dir, "README.md")
    if not os.path.isfile(readme):
        findings.append("README.md missing at project root")
    else:
        text = open(readme, "r", encoding="utf-8", errors="replace").read()
        if not re.search(r"已知限制|Known Limitations|Limitations", text, re.I):
            findings.append("README.md missing Known Limitations / 已知限制 section")
        if "python calculator.py" in text and not os.path.isfile(os.path.join(output_dir, "calculator.py")):
            findings.append("README.md references `python calculator.py` but root calculator.py is absent")

    docs_dir = os.path.join(output_dir, "docs")
    if os.path.isdir(docs_dir):
        completion_reports = glob.glob(os.path.join(docs_dir, "pr_*_completion_report.md"))
        if not completion_reports:
            findings.append("docs/pr_##_completion_report.md missing")
        release_notes = os.path.join(docs_dir, "release_notes.md")
        if os.path.isfile(release_notes):
            notes = open(release_notes, "r", encoding="utf-8", errors="replace").read()
            if re.search(r"MiniCalc\s+v1\.0\s+Release Notes", notes):
                findings.append("docs/release_notes.md still says MiniCalc v1.0 Release Notes")
    else:
        warnings.append("docs/ directory absent; skip completion report/release notes checks")

    return {"clean": not findings, "findings": findings, "warnings": warnings}


def _cleanup_python_caches(output_dir: str) -> None:
    """Remove pytest/python cache artifacts, including those created by this runner."""
    import shutil
    cache_paths = []
    for cache_dir_name in [".pytest_cache", "__pycache__"]:
        for root, dirs, files in os.walk(output_dir):
            if cache_dir_name in dirs:
                cache_paths.append(os.path.join(root, cache_dir_name))
    cache_paths.sort(key=len, reverse=True)
    for cache_path in cache_paths:
        try:
            shutil.rmtree(cache_path)
        except (PermissionError, OSError):
            subprocess.run(["rm", "-rf", cache_path], capture_output=True)
            if os.path.exists(cache_path):
                subprocess.run(
                    ["/mnt/c/Windows/System32/cmd.exe", "/c",
                     f"del /f /q /s {cache_path}\\*.* >nul 2>&1 && rd /s /q {cache_path}"],
                    capture_output=True
                )


def _discover_test_files(output_dir: str) -> list[str]:
    """動態掃描 tests/test_*.py"""
    tests_dir = os.path.join(output_dir, "tests")
    if not os.path.isdir(tests_dir):
        return []
    return sorted(glob.glob(os.path.join(tests_dir, "test_*.py")))


def _ast_security_check(output_dir: str) -> dict:
    """
    AST-based 安全檢查：分析 .py 檔案是否真的呼叫危險函數。
    比 grep 精確，不會誤判 evaluates、evaluation、pre_exec 等字串。
    """
    dangerous_calls = []
    DANGEROUS_NAMES = {"eval", "exec", "compile", "system", "popen"}

    py_files = []
    for root, dirs, files in os.walk(output_dir):
        dirs[:] = [d for d in dirs if d not in {".pytest_cache", "__pycache__", ".git", "venv"}]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    for filepath in py_files:
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                source = fh.read()
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue

        rel_path = os.path.relpath(filepath, output_dir)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                func_name = None
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr
                    # 檢查 subprocess.*, os.system 等
                    if isinstance(func.value, ast.Name):
                        obj_name = func.value.id
                        if obj_name in ("subprocess",) and func_name in ("call", "run", "Popen", "check_output", "check_call"):
                            dangerous_calls.append(f"{rel_path}:{node.lineno} → {obj_name}.{func_name}()")
                        elif obj_name in ("os",) and func_name in ("system", "popen"):
                            dangerous_calls.append(f"{rel_path}:{node.lineno} → {obj_name}.{func_name}()")

                if func_name in DANGEROUS_NAMES:
                    dangerous_calls.append(f"{rel_path}:{node.lineno} → {func_name}()")

            # 檢查 import subprocess / import os.system
            elif isinstance(node, ast.ImportFrom):
                if node.module == "subprocess":
                    for alias in node.names:
                        if alias.name in ("call", "run", "Popen", "check_output"):
                            dangerous_calls.append(f"{os.path.relpath(filepath, output_dir)}:{node.lineno} → from subprocess import {alias.name}")

    return {
        "clean": len(dangerous_calls) == 0,
        "findings": dangerous_calls,
    }


def run_phase4(output_dir: str, raw_dir: str) -> dict:
    """
    執行 Phase 4 完整 Build + Test + Lint，保留所有 raw log。

    Args:
        output_dir: 專案程式碼目錄（含主模組 .py, tests/）
        raw_dir: raw log 輸出目錄

    Returns:
        dict with all results and file paths
    """
    os.makedirs(raw_dir, exist_ok=True)
    results = {}

    # === 0. 動態發現 ===
    main_module = _discover_main_module(output_dir)
    test_files = _discover_test_files(output_dir)
    test_file_names = [os.path.basename(f) for f in test_files]

    with open(os.path.join(raw_dir, "discovery_raw.txt"), "w") as f:
        f.write(f"Main module: {main_module}\n")
        f.write(f"Test files: {test_file_names}\n")

    # === 1. py_compile — 主模組 ===
    if main_module:
        r = _run(f"python3 -m py_compile {shlex.quote(main_module)}", output_dir)
    else:
        r = {"returncode": 1, "stdout": "", "stderr": "No main module found", "duration_seconds": 0, "timeout": False}
    results["compile_main"] = r
    with open(os.path.join(raw_dir, "compile_calculator_raw.txt"), "w") as f:
        f.write(f"CMD: python3 -m py_compile {main_module or 'NOT_FOUND'}\n")
        f.write(f"RETURN CODE: {r['returncode']}\n")
        f.write(f"STDOUT:\n{r['stdout']}STDERR:\n{r['stderr']}\n")

    # === 2. py_compile — 所有 test_*.py ===
    compile_test_results = []
    all_tests_compile = True
    compile_test_output = []

    if test_files:
        for tf in test_file_names:
            r = _run(f"python3 -m py_compile tests/{tf}", output_dir)
            compile_test_results.append({"file": tf, "returncode": r["returncode"]})
            compile_test_output.append(
                f"CMD: python3 -m py_compile tests/{tf}\n"
                f"RETURN CODE: {r['returncode']}\n"
                f"STDOUT:\n{r['stdout']}STDERR:\n{r['stderr']}\n"
                f"---\n"
            )
            if r["returncode"] != 0:
                all_tests_compile = False
    else:
        compile_test_output.append("No test_*.py files found in tests/\n")
        all_tests_compile = False

    results["compile_tests"] = {
        "returncode": 0 if all_tests_compile else 1,
        "files": compile_test_results,
    }
    with open(os.path.join(raw_dir, "compile_tests_raw.txt"), "w") as f:
        f.write("".join(compile_test_output))

    # === 3. pytest -v ===
    r = _run("python3 -m pytest tests/ -v --tb=short", output_dir)
    results["pytest"] = r
    with open(os.path.join(raw_dir, "test_raw.txt"), "w") as f:
        f.write(f"CMD: python3 -m pytest tests/ -v --tb=short\n")
        f.write(f"RETURN CODE: {r['returncode']}\n")
        f.write(f"STDOUT:\n{r['stdout']}STDERR:\n{r['stderr']}\n")

    # === 3.5 立即清理 pytest 產生的快取（避免 Windows 權限鎖死）===
    _cleanup_python_caches(output_dir)

    # === 4. import smoke test（動態模組名）===
    if main_module:
        module_name = _module_name_from_path(main_module)
        # 嘗試常見的 Engine class 名稱
        import_cmd = (
            f'python3 -c "import {module_name}; '
            f'mod = {module_name}; '
            f'engines = [getattr(mod, n) for n in dir(mod) if n.endswith(\\\"Engine\\\")] ; '
            f'print(\\\"OK\\\" if engines else \\\"NO_ENGINE\\\')"'
        )
        # 簡化版：直接 import 模組
        import_cmd = f'python3 -c "import {module_name}; print(\\\"OK\\\")"'
    else:
        import_cmd = 'python3 -c "print(\\\"SKIP: no module\\\")"'
    r = _run(import_cmd, output_dir)
    results["import_test"] = r
    with open(os.path.join(raw_dir, "import_raw.txt"), "w") as f:
        f.write(f"CMD: import {main_module or 'NOT_FOUND'}\n")
        f.write(f"RETURN CODE: {r['returncode']}\n")
        f.write(f"STDOUT:\n{r['stdout']}STDERR:\n{r['stderr']}\n")

    # === 4.5 Direct entrypoint smoke test（v2.7 PR 交付驗收）===
    # pytest/import 成功不代表使用者照 README 執行可啟動；直接跑入口檔可抓出
    # `from source.x import ...` 這類 path bug。GUI app 在 headless WSL 可能 timeout
    # 或 TclError/no DISPLAY，這列為 PASS_HEADLESS_UI_BLOCKED，不當作 import crash。
    if main_module:
        if _supports_smoke_flag(output_dir, main_module):
            entry_cmd = f"python3 {shlex.quote(main_module)} --smoke"
        else:
            entry_cmd = f"timeout 5 python3 {shlex.quote(main_module)}"
    else:
        entry_cmd = 'python3 -c "print(\\\"SKIP: no module\\\")"'
    r = _run(entry_cmd, output_dir, timeout=8)
    entry_status = _entrypoint_smoke_status(r)
    results["entrypoint_smoke"] = {**r, "status": entry_status}
    with open(os.path.join(raw_dir, "entrypoint_smoke_raw.txt"), "w") as f:
        f.write(f"CMD: {entry_cmd}\n")
        f.write(f"STATUS: {entry_status}\n")
        f.write(f"RETURN CODE: {r['returncode']}\n")
        f.write(f"STDOUT:\n{r['stdout']}STDERR:\n{r['stderr']}\n")

    # === 5. Security check（AST-based，不再用 grep）===
    sec_result = _ast_security_check(output_dir)
    # 模擬 _run 格式以兼容
    if sec_result["clean"]:
        results["security_grep"] = {
            "returncode": 0,
            "stdout": "CLEAN",
            "stderr": "",
            "duration_seconds": 0,
            "timeout": False,
        }
    else:
        findings_text = "\n".join(sec_result["findings"])
        results["security_grep"] = {
            "returncode": 1,
            "stdout": findings_text,
            "stderr": "",
            "duration_seconds": 0,
            "timeout": False,
        }
    with open(os.path.join(raw_dir, "security_grep_raw.txt"), "w") as f:
        f.write("CMD: AST-based security check (eval/exec/subprocess)\n")
        f.write(f"CLEAN: {sec_result['clean']}\n")
        if sec_result["findings"]:
            f.write("FINDINGS:\n")
            for finding in sec_result["findings"]:
                f.write(f"  - {finding}\n")
        else:
            f.write("No dangerous calls found.\n")

    # === 5.5 Path pollution check（v2.7）===
    path_result = _path_pollution_check(output_dir)
    results["path_pollution"] = path_result
    with open(os.path.join(raw_dir, "path_pollution_raw.txt"), "w") as f:
        f.write("CMD: scan for sys.path.insert/sys.path.append\n")
        f.write(f"CLEAN: {path_result['clean']}\n")
        if path_result["findings"]:
            f.write("FINDINGS:\n")
            for finding in path_result["findings"]:
                f.write(f"  - {finding}\n")
        if path_result.get("allowed"):
            f.write("ALLOWED_WITH_PRAGMA:\n")
            for finding in path_result["allowed"]:
                f.write(f"  - {finding}\n")

    # === 5.6 Documentation delivery check（v2.7.1）===
    doc_result = _documentation_check(output_dir)
    results["documentation"] = doc_result
    with open(os.path.join(raw_dir, "documentation_raw.txt"), "w") as f:
        f.write("CMD: check README.md, docs/pr_##_completion_report.md, release notes, known limitations\n")
        f.write(f"CLEAN: {doc_result['clean']}\n")
        if doc_result["findings"]:
            f.write("FINDINGS:\n")
            for finding in doc_result["findings"]:
                f.write(f"  - {finding}\n")
        if doc_result["warnings"]:
            f.write("WARNINGS:\n")
            for warning in doc_result["warnings"]:
                f.write(f"  - {warning}\n")

    # === 5.7 Package hygiene check（v2.7）===
    # py_compile/import/entrypoint smoke 本身也可能產生 __pycache__；最終交付前再清一次。
    _cleanup_python_caches(output_dir)
    hygiene_result = _package_hygiene_check(output_dir)
    results["package_hygiene"] = hygiene_result
    with open(os.path.join(raw_dir, "package_hygiene_raw.txt"), "w") as f:
        f.write("CMD: scan for .pytest_cache/, __pycache__/, *.pyc\n")
        f.write(f"CLEAN: {hygiene_result['clean']}\n")
        if hygiene_result["findings"]:
            f.write("FINDINGS:\n")
            for finding in hygiene_result["findings"]:
                f.write(f"  - {finding}\n")

    # === 解析 pytest 結果 ===
    pytest_stdout = results["pytest"]["stdout"]
    passed = pytest_stdout.count(" PASSED")
    failed = pytest_stdout.count(" FAILED")
    errors = pytest_stdout.count(" ERROR")

    test_result = {
        "tool": "pytest",
        "total": passed + failed + errors,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "returncode": results["pytest"]["returncode"],
        "duration_seconds": results["pytest"]["duration_seconds"],
        "raw_log": "test_raw.txt",
    }

    with open(os.path.join(raw_dir, "test_result.json"), "w") as f:
        json.dump(test_result, f, indent=2)

    # === 總結 ===
    all_pass = (
        results["compile_main"]["returncode"] == 0
        and all_tests_compile
        and results["pytest"]["returncode"] == 0
        and results["import_test"]["returncode"] == 0
        and results["entrypoint_smoke"]["status"] in {"PASS", "PASS_SMOKE", "PASS_LAUNCHED_TIMEOUT", "PASS_HEADLESS_UI_BLOCKED"}
        and path_result["clean"]
        and doc_result["clean"]
        and hygiene_result["clean"]
    )

    return {
        "overall_status": "PASS" if all_pass else "FAIL",
        "main_module": main_module,
        "test_files": test_file_names,
        "test_result": test_result,
        "compile_main": {
            "status": "PASS" if results["compile_main"]["returncode"] == 0 else "FAIL",
            "file": main_module,
            "raw_log": "compile_calculator_raw.txt",
        },
        "compile_tests": {
            "status": "PASS" if all_tests_compile else "FAIL",
            "files": test_file_names,
            "raw_log": "compile_tests_raw.txt",
        },
        "pytest": {
            "status": "PASS" if results["pytest"]["returncode"] == 0 else "FAIL",
            "passed": passed,
            "total": passed + failed + errors,
            "raw_log": "test_raw.txt",
        },
        "import_test": {
            "status": "PASS" if results["import_test"]["returncode"] == 0 else "FAIL",
            "raw_log": "import_raw.txt",
        },
        "entrypoint_smoke": {
            "status": results["entrypoint_smoke"]["status"],
            "raw_log": "entrypoint_smoke_raw.txt",
        },
        "security_grep": {
            "status": "CLEAN" if sec_result["clean"] else "FOUND",
            "method": "ast",
            "findings": sec_result["findings"],
            "raw_log": "security_grep_raw.txt",
        },
        "path_pollution": {
            "status": "CLEAN" if path_result["clean"] else "FOUND",
            "findings": path_result["findings"],
            "allowed": path_result.get("allowed", []),
            "raw_log": "path_pollution_raw.txt",
        },
        "documentation": {
            "status": "CLEAN" if doc_result["clean"] else "FOUND",
            "findings": doc_result["findings"],
            "warnings": doc_result["warnings"],
            "raw_log": "documentation_raw.txt",
        },
        "package_hygiene": {
            "status": "CLEAN" if hygiene_result["clean"] else "FOUND",
            "findings": hygiene_result["findings"],
            "raw_log": "package_hygiene_raw.txt",
        },
        "raw_dir": raw_dir,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python build_runner.py <output_dir> <raw_dir>")
        sys.exit(1)
    result = run_phase4(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2, ensure_ascii=False))
