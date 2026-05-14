---
name: workflow-to-skill-capture
description: Convert a successful or repeated workflow into a reusable Hermes skill. Use after complex tasks, user corrections, repeated procedures, or when importing ideas from skill-factory style repos, without background surveillance or automatic plugin installation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, workflow, self-improvement, capture, skill-factory]
    related_skills: [hermes-agent-skill-authoring, external-skill-import]
---

# Workflow to Skill Capture

## Overview

This is the safe, manual version of a "skill factory". Its purpose is to convert proven workflows into durable Hermes skills without silently observing the user, installing plugins, or writing files without a clear trigger.

Use it when a task produced a reusable procedure, when Scott corrected an approach, or when an external repository suggests a useful workflow that should become Hermes procedural memory.

## When to Use

Trigger this skill when:

- A task required 5+ tool calls and ended successfully
- A tricky error was diagnosed and fixed
- Scott corrected the agent's approach or red lines
- The same procedure appears repeatedly across sessions
- A repo or article contains a useful workflow worth adapting
- A skill you used was incomplete and needs improvement

Do not use for one-off facts, tiny commands, or tasks with no reusable pattern.

## Capture Decision

Create or update a skill only if at least two are true:

- The workflow is likely to recur
- It includes non-obvious steps or pitfalls
- It avoids a previous failure mode
- It improves safety, cost, speed, or reliability
- It encodes Scott-specific preferences or environment details
- It can be verified with concrete checks

If not, write a short memory note or backlog item instead.

## Capture Workflow

### Step 1: Define the trigger

Write the exact future situation that should load the skill:

- User phrases
- File types
- Project type
- Toolchain
- Error message
- Risk pattern

Bad trigger: `Use for coding.`

Good trigger: `Use when debugging Hermes TUI slash commands that fail differently in CLI and Telegram gateway.`

### Step 2: Extract the successful sequence

Record only what actually worked:

1. Discovery steps
2. Required context files
3. Commands or APIs used
4. Decision points
5. Failure modes encountered
6. Verification steps

Do not include speculation as instructions. Label assumptions explicitly.

### Step 3: Generalize without losing specificity

Transform task-specific details into reusable slots:

- `<repo>` instead of one project path
- `<service>` instead of one container name
- `<date>` instead of today's timestamp

Keep Scott-specific environment facts if they matter, such as WSL path translation or shared workspace paths.

### Step 4: Shape the skill with Skill Creator principles

When adapting a skill-authoring guide such as `Skill Creator`, keep the useful design principles and discard marketplace-specific packaging:

- **Concise by default**: the context window is shared; every paragraph must justify its token cost.
- **Progressive disclosure**: keep only triggers, core workflow, pitfalls, and verification in `SKILL.md`; move long examples, API docs, variants, and background into `references/`.
- **Right degree of freedom**: use text guidance for flexible tasks, pseudocode/configurable snippets for repeatable patterns, and scripts only for fragile deterministic steps.
- **Skill as onboarding guide**: write only the procedural knowledge the agent would not reliably infer from general training.
- **No clutter**: exclude process notes, raw chat history, unrelated setup logs, and user-facing documentation that does not help execution.

### Step 5: Add pitfalls

Every useful skill should say how it fails. Include:

- Common wrong commands
- Misleading success messages
- Permissions problems
- Token/cost traps
- Safety red lines
- Verification that catches hallucinated completion

### Step 6: Add verification

A skill is not complete until it says how to prove the task worked:

- Read back the file
- Run test / compile / lint
- Query API for created object
- Confirm process status
- Confirm no secrets leaked
- Confirm output exists at an absolute path

## Skill Shape

Use this structure for local skills:

```markdown
---
name: concise-skill-name
description: What it does and when to use it.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [tag1, tag2]
    related_skills: [related-skill]
---

# Title

## Overview
## When to Use
## Workflow
## Common Pitfalls
## Verification Checklist
```

## Update vs Create

Prefer **patching an existing skill** when:

- The new lesson is a pitfall, extra command, or missing verification step
- A skill with the same trigger already exists
- The new content would be a small subsection

Create a **new skill** when:

- The trigger is distinct
- The workflow is long enough to stand alone
- Existing skills would become bloated or ambiguous

## Safe Automation Boundary

This skill may guide `skill_manage(action='create')` or `skill_manage(action='patch')`, but only after the workflow is clearly defined.

Do not implement background monitoring, auto-observation, or hidden session analysis. Scott's workflow values autonomy, but skill creation should remain explainable and auditable.

## Common Pitfalls

1. **Creating too many narrow skills**
   - Merge tiny lessons into existing skills or memory.

2. **Copying external skills verbatim**
   - External skills are untrusted. Rewrite and sanitize them.

3. **Saving a plan instead of a procedure**
   - A skill should say how to do the task, not just list aspirations.

4. **No verification**
   - If the skill cannot prove success, it will create future hallucinated completions.

5. **Ignoring Scott-specific constraints**
   - Include red lines: no credit-card spending, confirm mass deletion, no sensitive data exfiltration.

## Verification Checklist

- [ ] Trigger is specific and discoverable
- [ ] Workflow came from successful evidence or trusted synthesis
- [ ] Existing skills checked for duplication
- [ ] Pitfalls included
- [ ] Verification steps included
- [ ] Skill content contains no secrets
- [ ] Main `SKILL.md` is concise; long examples/details moved to `references/`
- [ ] Instructions use the right freedom level: prose, pseudocode, or script based on task fragility
- [ ] Skill contains no raw chat transcript, unrelated setup notes, or clutter
- [ ] Skill was read back or listed after creation
