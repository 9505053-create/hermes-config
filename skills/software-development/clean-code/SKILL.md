---
name: clean-code
description: Review, write, and improve code for readability, maintainability, naming, small functions, error handling, and test clarity. Use when the user asks for code review, clean up, readability, code smells, naming, single responsibility, or unit test quality.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [code-quality, review, readability, maintainability, tests]
    related_skills: [refactoring-patterns, requesting-code-review, test-driven-development]
---

# Clean Code

## Overview

Use clean-code principles to make code easier to read, change, test, and debug. This skill is adapted from public clean-code skill patterns but rewritten for Hermes. The goal is not rule-following theater; the goal is reducing future cognitive load.

Core principle: **code is read more often than it is written, so optimize for the next reader.**

## When to Use

Use when:

- Reviewing a PR or patch for maintainability
- Writing a new function/module where clarity matters
- Cleaning up long functions, vague names, duplicated logic, or confusing tests
- The user says code smell, clean code, readability, naming, SRP, or unit test quality

Pair with `refactoring-patterns` when structural changes are needed.

## Review Framework

Score the code from 0-10 and give specific steps to reach 10.

### 1. Meaningful Names

Check:

- Names reveal intent, domain meaning, and units
- Avoid vague names: `data`, `info`, `tmp`, `manager`, `processor`
- Boolean names read as predicates: `is_ready`, `has_token`
- Functions use verb phrases; classes/modules use nouns or domain concepts

Ask: can a reader understand the code without mentally executing it?

### 2. Small Focused Functions

Check:

- One function does one thing at one level of abstraction
- Function names match everything inside the function
- Parameters are minimal and cohesive
- Branching and loops are not deeply nested
- Side effects are obvious from name or placement

Preferred move: extract intention-revealing helper functions.

### 3. Comments and Formatting

Good comments explain why, constraints, gotchas, and non-obvious domain rules.

Bad comments restate what the code already says, preserve dead history, or excuse bad naming.

Formatting should reveal structure: consistent grouping, blank lines between ideas, and no visual noise.

### 4. Error Handling

Check:

- Errors are explicit and actionable
- Exceptions are not swallowed silently
- Recovery paths are separated from main happy path where possible
- Logs include context but not secrets
- User-facing messages do not expose credentials or internals

### 5. Tests as Documentation

Clean tests:

- Express behavior, not implementation trivia
- Use clear arrange/act/assert structure
- Have readable test names
- Minimize mocks unless isolating expensive or external dependencies
- Cover edge cases and failure paths

## Quick Diagnostic

Use this checklist during review:

- [ ] Can I summarize each function in one sentence?
- [ ] Are names domain-specific and intention-revealing?
- [ ] Is duplication hiding a missing abstraction?
- [ ] Are conditionals easy to read?
- [ ] Are errors handled consistently?
- [ ] Would a new teammate know where to make a change?
- [ ] Do tests explain expected behavior?

## Output Format

When reviewing code, report:

1. **Score:** N/10
2. **Top issues:** 3-5 bullets, highest leverage first
3. **Concrete fixes:** exact functions/files to change
4. **Risk:** what could break
5. **Verification:** tests/commands to run

## Common Pitfalls

1. **Renaming everything without improving design**
   - Names help, but bad boundaries still hurt.

2. **Over-extracting tiny helpers**
   - Extract when it names an idea or removes duplication, not just to reduce line count.

3. **Confusing cleverness with clarity**
   - Prefer obvious code unless performance evidence requires otherwise.

4. **Deleting comments that encode domain constraints**
   - Preserve why-comments and invariants.

5. **Ignoring tests**
   - Clean code without clean tests still decays.

## Verification Checklist

- [ ] Code compiles/lints after changes
- [ ] Existing tests pass
- [ ] New behavior has tests if behavior changed
- [ ] No secrets added to logs/errors
- [ ] Review output includes a score and specific improvement list
