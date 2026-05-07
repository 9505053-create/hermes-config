#!/usr/bin/env python3
"""
contract_check.py — Phase 1→2 契約驗證
比對 arch_plan.md 預期檔案 vs 實際產出檔案。

用法：
    from contract_check import run_contract_check
    result = run_contract_check(arch_plan_path, output_dir, report_path, intent="casual")
"""

import re
import os
import json
from pathlib import Path


def extract_expected_files(arch_plan_path: str) -> list[str]:
    """
    從 arch_plan.md 提取預期檔案清單。
    偵測方式：
    1. 搜尋 "File structure" 或 "檔案結構" 段落
    2. 搜尋程式碼區塊內的檔名（.py, .js, .ts, .json, .txt, .md）
    3. 搜尋表格中的檔名
    """
    with open(arch_plan_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected = set()

    # 搜尋所有 .py/.js/.ts/.json/.txt/.md 檔名
    # 排除 .md 參考文檔本身
    file_pattern = re.compile(
        r'[\`\s"\'](?!README)([a-zA-Z_][a-zA-Z0-9_/]*\.(?:py|js|ts|json|txt))(?:[\`\s"\':]|$)',
        re.IGNORECASE
    )
    for match in file_pattern.finditer(content):
        fname = match.group(1)
        # 排除路徑中的目錄前導，只取檔名
        expected.add(fname)

    # 也搜尋 tests/ 下的檔案
    test_pattern = re.compile(
        r'(?:test[_s]?/|tests/)([a-zA-Z_][a-zA-Z0-9_]*\.py)',
        re.IGNORECASE
    )
    for match in test_pattern.finditer(content):
        expected.add(f"tests/{match.group(1)}")

    return sorted(expected)


def scan_actual_files(output_dir: str) -> list[str]:
    """掃描 output 目錄，取得實際產出檔案清單（不含 hidden/cache）"""
    actual = []
    skip_dirs = {".pytest_cache", "__pycache__", ".git"}
    for root, dirs, files in os.walk(output_dir):
        # 跳過 cache 目錄
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith((".pyc", ".pyo")):
                continue
            rel = os.path.relpath(os.path.join(root, f), output_dir)
            actual.append(rel)
    return sorted(actual)


def run_contract_check(
    arch_plan_path: str,
    output_dir: str,
    report_path: str,
    intent: str = "casual",
) -> dict:
    """
    執行契約檢查。

    Returns:
        dict with: expected_files, actual_files, drift_detected, verdict, report
    """
    expected = extract_expected_files(arch_plan_path)
    actual = scan_actual_files(output_dir)

    # 去除 README.md（幾乎每個專案都有，不算契約）
    expected_set = set(expected) - {"README.md"}
    actual_set = set(actual) - {"README.md"}

    # === Fail-closed gate: 沒有可解析的 expected files → FAIL ===
    if len(expected_set) == 0:
        verdict = "FAIL"
        severity = "Critical"
        report_lines = [
            "# Contract Check Report",
            "",
            "## ❌ FAIL — No parseable expected file list",
            "",
            "Phase 0 arch_plan.md did not contain a parseable file list.",
            "Contract cannot be verified.",
            "",
            "**Possible causes:**",
            "- arch_plan.md is a summary, not a full architecture plan",
            "- Phase 0 stdout was captured instead of actual file content",
            '- arch_plan.md lacks a "File List", "Expected Deliverables", or code block section',
            "",
            "## Verdict: FAIL",
            "## Severity: Critical",
            "## Intent: " + intent,
            "",
            "## Decision: REJECTED — Phase 0 must produce a parseable file list before Phase 1.5 can pass",
        ]
        report = "\n".join(report_lines)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        return {
            "expected_files": [],
            "actual_files": actual,
            "missing": [],
            "extra": sorted(actual_set),
            "drift_detected": False,
            "verdict": "FAIL",
            "severity": "Critical",
            "report_path": report_path,
            "fail_reason": "expected_count=0: arch_plan.md produced no parseable file list",
        }

    # 找差異
    missing = sorted(expected_set - actual_set)
    extra = sorted(actual_set - expected_set)
    drift = bool(missing)

    # 判斷 verdict
    if not drift:
        verdict = "PASS"
        severity = "N/A"
    elif intent == "casual":
        verdict = "DRIFT_ACCEPTED"
        severity = "Medium"
    elif intent == "production":
        verdict = "DRIFT_REJECTED"
        severity = "High"
    else:
        verdict = "DRIFT_DETECTED"
        severity = "Medium"

    # 產報告
    report_lines = [
        "# Contract Check Report",
        "",
        "## Expected (from arch_plan.md)",
        "",
    ]
    if expected:
        for f in sorted(expected_set):
            report_lines.append(f"- {f}")
    else:
        report_lines.append("_No specific files extracted from arch_plan.md_")

    report_lines += [
        "",
        "## Actual",
        "",
    ]
    for f in actual:
        report_lines.append(f"- {f}")

    report_lines += [
        "",
        "## Comparison",
        "",
        f"- **Expected files:** {len(expected_set)}",
        f"- **Actual files:** {len(actual_set)}",
        f"- **Missing:** {len(missing)}",
        f"- **Extra:** {len(extra)}",
        "",
    ]

    if missing:
        report_lines.append("### Missing Files (Expected but not found)")
        for f in missing:
            report_lines.append(f"- ⚠️ {f}")
        report_lines.append("")

    if extra:
        report_lines.append("### Extra Files (Found but not in arch_plan)")
        for f in extra:
            report_lines.append(f"- ℹ️ {f}")
        report_lines.append("")

    report_lines += [
        f"## Verdict: {verdict}",
        f"## Severity: {severity}",
        f"## Intent: {intent}",
        "",
    ]

    if drift and intent == "casual":
        report_lines.append("## Decision: ACCEPTED (casual intent — drift noted but not blocking)")
    elif drift and intent == "production":
        report_lines.append("## Decision: REJECTED (production intent — must align with arch_plan)")
    elif not drift:
        report_lines.append("## Decision: All expected files present ✅")

    report = "\n".join(report_lines)

    # 寫報告
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    return {
        "expected_files": sorted(expected_set),
        "actual_files": actual,
        "missing": missing,
        "extra": extra,
        "drift_detected": drift,
        "verdict": verdict,
        "severity": severity,
        "report_path": report_path,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python contract_check.py <arch_plan.md> <output_dir> <report_path> [intent]")
        sys.exit(1)
    intent = sys.argv[4] if len(sys.argv) > 4 else "casual"
    result = run_contract_check(sys.argv[1], sys.argv[2], sys.argv[3], intent)
    print(json.dumps(result, indent=2, ensure_ascii=False))
