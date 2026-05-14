---
name: agent-resilience-action-items
description: "Plan and stage agent resilience work items: size gates, token ledger, reference blocks, structured log parsing, and boundary pressure tests."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [agent-resilience, token-management, size-gate, log-parser, pressure-test]
    related_skills: [safe-system-update, openclaw-windows-native, window-compress]
---

# Agent Resilience Action Items

Use this when Scott asks to implement or arrange improvements around token/context safety, CLI output size control, reference blocks, structured log/test parsing, or agent hallucination pressure tests.

## Default Work Package Location

Create staged work packages under:

```text
C:\Users\chien\_3AI_WorkSpace\active\YYYYMMDD-agent-resilience-action-items\
```

WSL equivalent:

```text
/mnt/c/Users/chien/_3AI_WorkSpace/active/YYYYMMDD-agent-resilience-action-items/
```

## Five Standard Tracks

1. **Size Gate**
   - Add line/byte hard limits to shell/read_file/log-output style tools.
   - Risk: medium to high if touching Hermes/OpenClaw core.
   - Must use `safe-system-update` before core changes: scope, 3AI Council, backup, rollback, static checks, smoke tests.

2. **Token Ledger**
   - Define budget class, soft/hard token/round waterlines, compression trigger, fallback.
   - Low risk; can be implemented as documentation first.

3. **Reference Block**
   - Stable anchors only: Scott decisions, task state, important paths, modified files, backup/rollback, verification, pending work, non-negotiable rules.
   - Avoid full transcripts.

4. **Structured Log/Test Output Parser**
   - Extract only error message, paths, stack top, first failure line, and test names.
   - Start as standalone parser before integrating into CLI/core.

5. **Boundary Pressure Test**
   - Verify agents do not hallucinate when context is filtered/truncated.
   - High risk. Only run in isolated folders after Scott go/no-go.

## Safe Sequence

1. Convert screenshot/request into a work package.
2. Classify each item as: doc-only, standalone prototype, core patch, or pressure test.
3. Create specs/templates/prototype under shared workspace.
4. For anything touching Hermes/OpenClaw core, run 3AI Council before implementation.
5. Apply only doc-only / standalone prototype changes first.
6. Verify prototype with `py_compile` and regression/smoke tests.
7. Notify 小蝦 via shared file + compact OpenClaw CLI prompt.
8. For core changes, follow safe-system-update with exact target files, backup, rollback, kill switch, and tests.
9. For pressure tests, require explicit Scott confirmation and synthetic-only scope limits.

## Lessons Learned from 2026-05-14 Drill

- **Staging before core**: Scott saying「安排實做」does not mean reckless core patching. First create a work package, run council, and land standalone prototypes.
- **Council value is boundary-setting**: use Claude/CODEX/Gemini to converge on what must *not* be touched yet. In this drill, all three converged on wrapper-only Size Gate first.
- **Size Gate is not just truncation**: it must externalize full output, return head/tail preview, structured parser summary, exit/stream metadata, and a warning not to assume omitted content.
- **Parser must avoid both false positives and false negatives**: paths alone do not imply failure; `no_signal` does not imply success.
- **Reference Blocks need freshness controls**: include `stale_after`, `last_verified_at`, `source_of_truth`, `confidence`, and `unknowns` so future agents do not blindly trust old handoffs.
- **Pressure tests must be synthetic-only**: never use live shared/inbox/outbox as test fixtures; pressure prompts can otherwise escape into real workflows.
- **Long instructions to 小蝦 should be file-backed**: write long rules to `shared/from-hermes` or the work package, then send a short OpenClaw CLI prompt with the path.
- **Even low-risk prototypes need rollback**: create timestamped backups and `ROLLBACK.txt` before mutating work package specs or scripts.

## Known 2026-05-14 Package

Path:

```text
C:\Users\chien\_3AI_WorkSpace\active\20260514-agent-resilience-action-items\
```

Artifacts created/updated:

- `README.md`
- `TOKEN_LEDGER_STANDARD.md` v0.2 (55/70/85 waterlines, PRE-STOP_STATE before hard stop)
- `REFERENCE_BLOCK_TEMPLATE.md` v0.2 (`stale_after`, `last_verified_at`, `source_of_truth`, `confidence`, `unknowns`, artifact mtime/hash)
- `SIZE_GATE_SPEC.md` v0.2 (wrapper-only boundary, kill switch requirement)
- `LOG_TEST_OUTPUT_PARSER_SPEC.md` v0.2
- `BOUNDARY_PRESSURE_TEST_PLAN.md` v0.2 (synthetic fixtures only; no live shared/inbox/outbox)
- `IMPLEMENTATION_SEQUENCE.md`
- `COUNCIL_ACTION_SUMMARY.md`
- `VERIFICATION_LOG.md`
- `tools/extract_failure_signal.py` v0.2 (paths alone do not imply failure; strict test failure regex; metadata/warnings)
- `tools/size_gate_wrapper.py` standalone prototype (`DISABLE_SIZE_GATE=1` kill switch)
- `tests/test_resilience_tools.py`
- `prompts/openclaw_notify.md`
- `prompts/3ai_council_review.md`

Verification:

- 3AI Council completed: `claude=0 codex=0 gemini=0`.
- `python3 -m py_compile tools/extract_failure_signal.py tools/size_gate_wrapper.py tests/test_resilience_tools.py` passed.
- `python3 -m pytest tests/test_resilience_tools.py -q -o 'addopts='` passed: 8 tests.
- 小蝦 acknowledged Phase 1 v0.2 in session `hermes-agent-resilience-impl-v02-20260514` and confirmed core is not patched and pressure tests need Scott go/no-go.
