---
name: literate-programming
description: Create and maintain literate programming documents that explain a codebase in human-first narrative order while preserving source-code traceability. Use when asked to document a codebase deeply, produce architecture walkthroughs tied to code chunks, or make source understandable before refactoring.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [documentation, codebase, literate-programming, refactoring, architecture]
    related_skills: [codebase-inspection, writing-plans, systematic-debugging]
---

# Literate Programming

## Overview

Literate programming presents software in the order easiest for humans to understand, not necessarily the order required by the compiler. The output is a narrative document with named code chunks, explanations, diagrams, invariants, and links back to source files.

This skill is inspired by public literate-programming skill repositories, but is rewritten for Hermes. It does not require adopting any external scripts. Use it as a documentation and comprehension workflow first; only add tangling/weaving automation after review.

## When to Use

Use when Scott asks to:

- Explain a complex codebase as a readable document
- Turn source code into a maintainable technical walkthrough
- Prepare for refactoring by understanding architecture first
- Document algorithms, pipelines, or agent workflows
- Produce onboarding docs that remain close to the source
- Create `.lit.md` style files with prose plus code chunks

Do not use for shallow README edits or quick API docs.

## Core Concepts

- **Psychological order**: explain concepts in the order humans need, not import order or file order.
- **Code chunk**: a named block of source code referenced by the narrative.
- **Tangle**: generate source files from chunks.
- **Weave**: generate human-readable docs from the literate source.
- **Single source of truth**: optional advanced mode where `.lit.md` becomes canonical and source is generated from it.

For Hermes tasks, start with **documentation mode**: source remains canonical, `.lit.md` explains it. Move to single-source-of-truth mode only with explicit project agreement.

## Workflow

### Step 1: Inspect the codebase

Gather:

- Entry points
- Main modules
- Data flow
- External APIs
- Config files
- Tests
- Build/run commands
- Known pain points

Use `codebase-inspection` or direct file search when useful.

### Step 2: Choose narrative spine

Pick one organizing story:

- Request lifecycle
- Data pipeline
- Agent loop
- CLI command flow
- State machine
- Domain model
- Deployment path

Avoid file-by-file narration unless the project is tiny.

### Step 3: Create chunk map

For each important source region, record:

```text
chunk name: short-descriptive-name
source: path/to/file.py:120-180
purpose: why this code exists
dependencies: chunks or modules it relies on
```

Chunk names should describe intent, not file names.

### Step 4: Draft `.lit.md`

Suggested structure:

```markdown
# System Title

## Reader Map
Who this document is for and what it explains.

## Big Picture
Architecture diagram or bullet flow.

## Core Flow
Narrative explanation with code chunks.

## Edge Cases and Failure Modes
What breaks and how the code handles it.

## Extension Points
Where future changes should hook in.

## Source Index
Chunk-to-file mapping.
```

### Step 5: Verify traceability

For every quoted code chunk:

- Confirm the source path exists
- Confirm line numbers or anchors are current
- Keep code snippets short enough to maintain
- Prefer references over copying huge blocks

### Step 6: Optional tangle/weave automation

Only after documentation mode is stable:

- Consider scripts that generate docs or extract chunks
- Keep generated files clearly labeled
- Run diffs before overwriting source
- Never install or run third-party scripts without review

## Output Modes

### Documentation Mode (default)

- Source code remains canonical
- `.lit.md` explains the code
- Best for audits, onboarding, debugging, and refactoring prep

### Refactor Planning Mode

- `.lit.md` describes desired architecture
- Code chunks show before/after sketches
- Pair with `writing-plans` and `test-driven-development`

### Single Source Mode (advanced)

- `.lit.md` becomes canonical
- Source is generated from named chunks
- Requires explicit project decision and tests

## Common Pitfalls

1. **Explaining files instead of ideas**
   - Readers need the flow, not a directory tour.

2. **Copying too much code into docs**
   - Large pasted blocks drift. Use focused snippets and source references.

3. **No verification loop**
   - A literate doc that cannot be checked against source becomes stale quickly.

4. **Premature tangling**
   - Do not make `.lit.md` the source of truth until the team agrees.

5. **Ignoring tests**
   - If source is generated or changed, run tests before claiming success.

## Verification Checklist

- [ ] Narrative spine chosen
- [ ] Entry points and data flow identified
- [ ] Chunk map created with source paths
- [ ] `.lit.md` uses psychological order
- [ ] Source references verified
- [ ] Generated or modified source diffed before acceptance
- [ ] Tests/build run if any source changed
