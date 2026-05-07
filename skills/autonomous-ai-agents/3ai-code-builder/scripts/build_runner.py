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
    """動態發現主模組：找 output/ 根目錄下的主要 .py 檔案"""
    candidates = []
    skip = {"__init__", "setup", "conftest"}
    for f in os.listdir(output_dir):
        if f.endswith(".py") and not f.startswith("test_"):
            name = f[:-3]
            if name not in skip:
                candidates.append(f)
    # 優先順序：calculator.py > app.py > main.py > 其他
    for pref in ["calculator.py", "app.py", "main.py"]:
        if pref in candidates:
            return pref
    return candidates[0] if candidates else None


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
        r = _run(f"python3 -m py_compile {main_module}", output_dir)
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
    # 先收集所有快取路徑，再從深到淺刪除（避免 walk 時目錄消失）
    import shutil
    cache_paths = []
    for cache_dir_name in [".pytest_cache", "__pycache__"]:
        for root, dirs, files in os.walk(output_dir):
            if cache_dir_name in dirs:
                cache_paths.append(os.path.join(root, cache_dir_name))
    # 深度優先：路徑長的先刪
    cache_paths.sort(key=len, reverse=True)
    for cache_path in cache_paths:
        try:
            shutil.rmtree(cache_path)
        except (PermissionError, OSError):
            # Windows Python 建立的快取，WSL 刪不掉 → 嘗試 subprocess
            import subprocess
            subprocess.run(["rm", "-rf", cache_path], capture_output=True)

    # === 4. import smoke test（動態模組名）===
    if main_module:
        module_name = main_module.replace(".py", "")
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
        "security_grep": {
            "status": "CLEAN" if sec_result["clean"] else "FOUND",
            "method": "ast",
            "findings": sec_result["findings"],
            "raw_log": "security_grep_raw.txt",
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
