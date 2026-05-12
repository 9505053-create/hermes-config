---
name: refactoring-patterns
description: Apply safe, named refactoring transformations to improve code structure without changing observable behavior. Use for refactor requests, code smells, technical debt, extract method, replace conditional, move method, decompose conditional, or legacy-code cleanup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [refactoring, code-smells, legacy-code, tests, technical-debt]
    related_skills: [clean-code, test-driven-development, systematic-debugging]
---

# Refactoring Patterns

## Overview

Refactoring means improving internal structure without changing observable behavior. This skill gives a disciplined, test-backed workflow for transforming messy code safely.

Core principle: **never mix behavioral change and structural change in the same step.**

## When to Use

Use when:

- The user says refactor, technical debt, code smell, cleanup, simplify, or legacy code
- Preparing code for a feature by improving structure first
- Replacing conditionals, extracting methods/classes, moving behavior, or reducing duplication
- Reviewing a patch that claims to be refactoring

Use `clean-code` first if the issue is mostly naming/readability. Use this skill when structural transformations are needed.

## Safe Refactoring Loop

1. **Characterize current behavior**
   - Find existing tests.
   - If tests are weak, add characterization tests before changing structure.

2. **Identify the smell**
   - Long function
   - Duplicated code
   - Large class / god object
   - Primitive obsession
   - Feature envy
   - Data clumps
   - Switch/conditional explosion
   - Shotgun surgery

3. **Pick one named transformation**
   - Extract Function / Method
   - Inline Variable / Function
   - Move Method / Move Field
   - Extract Class
   - Introduce Parameter Object
   - Replace Conditional with Polymorphism
   - Decompose Conditional
   - Replace Temp with Query
   - Encapsulate Collection

4. **Apply one tiny change**
   - Keep commits or patches small.
   - Do not change behavior and structure together.

5. **Verify immediately**
   - Run targeted tests after each meaningful step.
   - If a step fails, revert that step rather than piling on fixes.

## Smell-to-Refactoring Map

- Long function -> Extract Function, Replace Temp with Query, Introduce Explaining Variable
- Duplicated code -> Extract Function, Pull Up Method, Form Template Method
- Large class -> Extract Class, Extract Subclass, Move Method
- Primitive obsession -> Replace Primitive with Value Object, Introduce Parameter Object
- Switch statements -> Replace Conditional with Polymorphism, Replace Type Code with Subclasses
- Feature envy -> Move Method closer to the data it uses
- Data clumps -> Extract Class / Parameter Object
- Shotgun surgery -> Move Method, Inline Class, reorganize ownership

## Planning a Refactor

For non-trivial refactors, produce:

- Current smell inventory
- Behavioral safety net status
- Ordered sequence of small transformations
- Expected file/function changes
- Tests after each phase
- Rollback point

## Output Format

```text
Refactoring goal:
Current behavior safety:
Smells found:
Recommended sequence:
  1. <small transformation> -> verify with <test>
  2. <small transformation> -> verify with <test>
Risks:
Stop conditions:
```

## Common Pitfalls

1. **Big-bang rewrites**
   - They are not refactoring. Break into small reversible steps.

2. **No tests before refactor**
   - Add characterization tests or at least reproducible checks first.

3. **Changing public behavior accidentally**
   - Preserve API contracts unless the user explicitly asked for behavior change.

4. **Refactoring for aesthetics only**
   - Tie changes to maintainability, extension, or bug-risk reduction.

5. **Stopping before verification**
   - Run tests/lint before claiming completion.

## Verification Checklist

- [ ] Behavior before refactor is understood
- [ ] Tests or checks exist before structural changes
- [ ] Each step is small and reversible
- [ ] Behavior-changing work is separated from refactoring
- [ ] Targeted tests pass after each phase
- [ ] Final diff is explainable as structure-preserving
