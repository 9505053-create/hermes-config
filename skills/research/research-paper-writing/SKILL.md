---
name: research-paper-writing
title: Research Paper Writing Pipeline
description: "Write ML papers for NeurIPS/ICML/ICLR: design→submit."
version: 1.1.0
author: Orchestra Research
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research, Paper Writing, Experiments, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations, Statistical Analysis]
    category: research
    related_skills: [arxiv, ml-paper-writing, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]

---


# Research Paper Writing Pipeline

## Overview

Use this skill for end-to-end research paper work: project setup, literature review, experiment design, experiment execution, result analysis, paper drafting, self-review, submission preparation, and post-acceptance deliverables.

The previous full playbook was longer than Hermes' `SKILL.md` loader limit. The full original pipeline has been preserved as a supporting reference file:

- `references/full-pipeline.md`

Load that reference when you need the complete detailed procedure, templates, and examples.

## When To Use This Skill

- Writing or revising academic / ML / systems research papers.
- Turning experiment results into a submission-ready paper.
- Planning reproducible experiments and artifact packaging.
- Preparing conference submission checklists, rebuttal support, or post-acceptance deliverables.

## Quick Workflow

1. **Set up project structure**: paper source, experiments, results, figures, bibliography, logs.
2. **Literature review**: gather related work, build citation map, check novelty and positioning.
3. **Experiment design**: define hypotheses, baselines, metrics, ablations, compute budget, and reproducibility requirements.
4. **Experiment execution**: run in resumable batches, log failures, commit completed batches.
5. **Result analysis**: aggregate metrics, generate figures/tables, document failed experiments honestly.
6. **Draft paper**: abstract, intro, method, experiments, related work, limitations, ethics/reproducibility.
7. **Self-review**: check claims vs evidence, citation completeness, figure/table clarity, and reviewer objections.
8. **Submission preparation**: venue template, page limits, anonymous artifacts, clean LaTeX build, final checklist.
9. **Post-acceptance**: camera-ready, artifact release, README, citation, announcement assets.

## Required Full Reference

Before executing a detailed paper-writing task, read:

```text
references/full-pipeline.md
```

The reference contains the original long-form procedures, code snippets, checklists, templates, and reviewer criteria.

## Verification Checklist

- [ ] Full reference exists at `references/full-pipeline.md`.
- [ ] Claims are backed by experiment results or citations.
- [ ] Bibliography entries exist for every citation.
- [ ] Figures/tables are reproducible from saved scripts or notebooks.
- [ ] LaTeX / manuscript build succeeds cleanly.
- [ ] Venue-specific constraints are checked before submission.
