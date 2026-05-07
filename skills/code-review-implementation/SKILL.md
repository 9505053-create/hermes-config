---
name: code-review-implementation
description: Process external code review feedback (from AI models, human reviewers, or tools) and implement suggested fixes systematically. Use when user provides review documents, feedback lists, or reviewer comments and asks to implement the changes.
category: software-development
---

# Code Review Implementation

## When to Use
- User provides review feedback from ChatGPT, Gemini, Claude, or human reviewers
- User shares code review documents and asks to implement suggested fixes
- User wants to process feedback from multiple sources and prioritize changes
- User asks to "fix based on review" or "implement reviewer suggestions"

## Workflow

### Step 1: Parse Review Feedback
- Read and understand all review documents
- Extract specific issues, bugs, and suggestions
- Identify which issues are critical vs. nice-to-have
- Note any conflicting feedback between reviewers

### Step 2: Prioritize Fixes
Priority order:
1. **Security issues** — vulnerabilities, credential exposure
2. **Functional bugs** — broken features, logic errors
3. **Performance issues** — efficiency problems, resource usage
4. **Code quality** — maintainability, readability
5. **Style/cosmetic** — formatting, naming conventions

### Step 3: Create Fix Plan
- List each issue with its source (ChatGPT, Gemini, etc.)
- Map issues to specific files and line numbers
- Group related fixes together
- Estimate complexity and dependencies

### Step 4: Implement Fixes
- Clone/access the repository
- Make changes systematically
- Test each fix when possible
- Commit with descriptive messages linking to review feedback

### Step 5: Record Lessons Learned
After all fixes are implemented and pushed:
- Scan for any errors or detours encountered during implementation
- Write a `lessons/dev/YYYY-MM-DD_問題簡述.md` to the workspace `lessons/dev/` directory
- Each lesson must include: 錯誤描述, 情境, 根本原因, 正確做法, 防止重犯措施
- System-level mistakes (CLI errors, tool misconfig) go to `lessons/system/`
- This prevents the same mistakes from recurring in future sessions

### Step 6: Verify and Report
- Verify all critical issues are addressed
- Push changes to version control
- Provide summary of what was fixed and why
- Note any issues that weren't addressed (with reasoning)

## Best Practices

### For Multiple Reviewers
- When reviewers disagree, note the conflict and make a reasoned choice
- Summarize common themes across reviewers
- Prioritize issues mentioned by multiple reviewers
- Document your reasoning when choosing one approach over another

### For Large Feedback Sets
- Group related issues (e.g., all CSS issues, all logic bugs)
- Fix in dependency order (fix foundations before features)
- Make incremental commits for traceability
- Test after each logical group of fixes

### Commit Message Format
```
Fix: [issue category] - [brief description]

Addresses feedback from [reviewer source]:
- [specific issue 1]
- [specific issue 2]

Closes #[issue-number] (if applicable)
```

## Handling Multi-Model Reviews in a Single Document

When the user sends a single file containing reviews from multiple AI models (e.g., ChatGPT + Claude + Gemini in one `.md`):

1. Parse each reviewer's section separately
2. Build a **consolidated issue table** mapping: Issue → Sources → Severity
3. Issues mentioned by **multiple reviewers** get highest priority (likely real bugs)
4. Issues mentioned by only one reviewer need manual verification before fixing
5. Apply the "don't force-find problems" rule: if the user says "沒有明顯大問題可以不用為了評論硬找理由", skip cosmetic/style suggestions — only fix real bugs

## Refactor as Part of Fix Implementation

When review feedback identifies dead code, deprecated features, or architecture issues:
- Fix bugs first, then refactor in the same commit batch
- Removing deprecated features: move to `legacy/` rather than hard-delete (preserves git history)
- Clean up dependencies (`requirements.txt`) when removing features
- Update README to match the new code scope
- Bump version number for major refactors

## Example Usage

**User provides**: "Here's GPT/Claude/Gemini's review of my OCR tool. Fix the issues."

**Agent workflow**:
1. Read all review documents
2. Extract and consolidate issues across reviewers
3. Verify each issue against actual code (reviews may misread code)
4. Prioritize: real bugs > performance > code quality > style
5. Fix bugs in the source code
6. Refactor if needed (remove dead code, clean deps)
7. Update README to match new scope
8. Commit with detailed message listing all fixes
9. Push and report summary

## Tools Required
- Git access (local or via GitHub API)
- Code editor capabilities (via file operations)
- Repository access (clone, commit, push)

## Shared Workspace Integration

When 3AI reviews are stored in `_3AI_WorkSpace/completed/`:
1. Review results are `*_result.md` files in the project directory
2. Clone code goes in `*_code/` subdirectory
3. After fixing, update the project `README.md` with fix status and remaining TODOs
4. Push to GitHub, then record lessons to `lessons/dev/`

## Special Case: Pipeline/Workflow Self-Optimization

When the reviews are about the **pipeline or workflow itself** (not a user application), the task is self-optimization — the code being fixed is the system that does the work.

**Differences from normal code review implementation:**
1. The "application" is the pipeline (e.g., `pipeline.py`, `SKILL.md`, agent config)
2. Changes affect **future** runs, not a deployed product
3. Verification = syntax check + dry-run mental simulation (no user to break)
4. Output must also update the corresponding SKILL.md documentation

**Workflow adjustment:**
1. Synthesize reviews into a prioritized table: Issue → Sources → Severity → Code Location
2. Present a **modification plan** to Scott before implementing (this is his workflow preference)
3. After Scott confirms, implement changes systematically
4. Run `py_compile` on every modified Python file before declaring done
5. Sync to any mirror directories (e.g., `projects/hermes-config/`)
6. Update SKILL.md with changelog and flow diagram
7. Report completion with summary of all changes

**Example**: Scott provides Gemini + ChatGPT + Claude reviews of the 3AI Code Builder pipeline. Agent synthesizes 9 issues, presents plan, implements changes to pipeline.py, updates SKILL.md, verifies syntax.

## Notes
- Always preserve reviewer attribution
- Don't implement suggestions that conflict with user's stated preferences
- When in doubt about a suggestion, ask the user before implementing
- Document any suggestions you chose not to implement and why
