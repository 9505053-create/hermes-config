---
name: jobs-to-be-done
description: Discover customer needs and product opportunities by identifying the job users hire a product to do, including functional, emotional, and social dimensions. Use for customer discovery, product-market fit, churn analysis, switching behavior, competitor alternatives, feature prioritization, or product positioning.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [product, discovery, jtbd, customer-research, positioning]
    related_skills: [research-paper-writing, ideation]
---

# Jobs to Be Done

## Overview

Jobs to Be Done (JTBD) frames products as tools customers hire to make progress in a specific circumstance. This skill helps analyze what users are really trying to accomplish, why they switch, what competitors include, and which features matter.

Core principle: **customers do not buy products; they hire solutions to make progress.**

This skill is adapted from public JTBD skill patterns and rewritten for Hermes.

## When to Use

Use when Scott asks about:

- Customer discovery
- Product-market fit
- Why users churn or switch
- What problem a feature solves
- Product positioning or value proposition
- Competitor analysis beyond direct competitors
- Feature prioritization based on real user progress
- Interview questions for users/customers

## JTBD Framework

### 1. Define the Job Statement

Use this form:

```text
When <situation>, I want to <motivation/progress>, so I can <desired outcome>.
```

Good job statements are about progress, not the product's implementation.

Bad: `Users want an AI calendar button.`

Better: `When my week is overloaded, I want commitments reorganized automatically so I can keep promises without manually comparing every schedule conflict.`

### 2. Capture Three Dimensions

Every job has:

- **Functional**: what task must be done?
- **Emotional**: how does the customer want to feel?
- **Social**: how does the customer want to be perceived?

Ignoring emotional/social dimensions leads to technically correct products that people do not adopt.

### 3. Analyze Forces of Progress

Switching is shaped by four forces:

- **Push**: pain with the current situation
- **Pull**: attraction of the new solution
- **Anxiety**: fear or uncertainty about switching
- **Habit**: inertia of current behavior

A product wins when push + pull exceed anxiety + habit.

### 4. Identify Real Competition

Competition includes any alternative the user hires:

- Direct competitor product
- Spreadsheet / notes / manual workaround
- Human assistant / consultant
- Doing nothing
- Existing habit

Ask: what would the customer do if this product did not exist?

### 5. Interview for Causality

Good JTBD interviews focus on actual past behavior, not hypothetical preferences.

Ask:

- What was happening when you started looking?
- What did you try before this?
- What made the old way unacceptable?
- What almost stopped you from switching?
- Who else was involved?
- What did success look like afterwards?

Avoid asking users to design the solution for you.

### 6. Translate Jobs into Product Decisions

For each job, decide:

- Must-have outcomes
- Current obstacles
- Trigger moments
- Switching anxieties to reduce
- Habits to integrate with or replace
- Metrics proving progress
- Features that directly serve the job
- Features that are distractions

## Output Format

```text
Customer segment / situation:
Job statement:
Functional dimension:
Emotional dimension:
Social dimension:
Push forces:
Pull forces:
Anxieties:
Habits:
Real competitors:
Interview questions:
Product implications:
Validation plan:
```

## Common Pitfalls

1. **Starting with demographics**
   - Circumstance predicts jobs better than age/title/persona.

2. **Confusing feature requests with jobs**
   - A requested feature is one possible solution, not the underlying job.

3. **Ignoring non-consumption**
   - Doing nothing is often the strongest competitor.

4. **Asking hypothetical questions**
   - Past behavior is more reliable than future intention.

5. **Skipping switching anxiety**
   - Adoption fails when anxiety and habit are stronger than perceived benefit.

## Verification Checklist

- [ ] Job statement describes progress in a circumstance
- [ ] Functional, emotional, and social dimensions included
- [ ] Push/pull/anxiety/habit forces mapped
- [ ] Non-obvious competitors identified
- [ ] Interview questions focus on past behavior
- [ ] Product implications connect directly to the job
- [ ] Validation plan defines evidence of real demand
