---
name: system-design
description: Design scalable and reliable systems by clarifying requirements, estimating capacity, choosing architecture building blocks, and documenting tradeoffs. Use for system design, scalability, high availability, distributed architecture, capacity planning, rate limiters, queues, caches, databases, or microservice vs monolith decisions.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [architecture, scalability, distributed-systems, capacity-planning, design]
    related_skills: [production-resilience, codebase-inspection, writing-plans]
---

# System Design

## Overview

Use this skill to design or review software systems from requirements to architecture tradeoffs. It is adapted from public system-design skill patterns and rewritten for Hermes.

Core principle: **start with requirements and constraints, not technology choices.**

## When to Use

Use when Scott asks to:

- Design a new service, workflow, or platform
- Scale an existing app
- Choose between monolith, modular monolith, microservices, serverless, or queue-based design
- Estimate load, storage, throughput, latency, or cost
- Design rate limiters, notification systems, search, feeds, file upload, URL shorteners, or data pipelines
- Review architecture for high availability and operational risk

## Four-Step Design Process

### 1. Clarify Requirements

Separate:

- Functional requirements: what the system must do
- Non-functional requirements: scale, latency, availability, privacy, compliance, cost
- Out-of-scope items: what not to solve yet
- Users and actors
- Read/write patterns
- Data retention and deletion needs

Do not design until scope is explicit.

### 2. Estimate Capacity

Back-of-the-envelope estimates:

- Daily/monthly active users
- Requests per second: average and peak
- Read/write ratio
- Storage per item and total storage growth
- Bandwidth
- Cache size
- Queue throughput
- Failure budget / availability target

Label assumptions clearly.

### 3. High-Level Architecture

Choose building blocks deliberately:

- API gateway / load balancer
- App service(s)
- Database(s)
- Cache
- Queue / stream
- Object storage
- Search index
- CDN
- Background workers
- Observability stack

Draw or describe data flow before deep-diving.

### 4. Deep Dive and Tradeoffs

Address the riskiest parts:

- Database schema and indexes
- Consistency requirements
- Partitioning/sharding strategy
- Cache invalidation
- Idempotency and retries
- Rate limiting
- Authentication/authorization boundaries
- Deployment and rollback
- Monitoring and alerting

Every architecture decision should name the tradeoff it accepts.

## Review Rubric

Score 0-10:

- Requirements are explicit
- Capacity estimates are plausible
- Data model fits access patterns
- Scaling strategy matches actual bottlenecks
- Failure modes are handled
- Security and privacy are considered
- Operations/observability are included
- Tradeoffs are documented

## Common Design Patterns

- **Cache-aside** for read-heavy data with tolerable staleness
- **Write-through / write-behind cache** only with clear consistency needs
- **Queue + workers** for async tasks and traffic smoothing
- **Outbox pattern** for reliable event publication
- **CQRS** only when read/write models genuinely diverge
- **Rate limiter** using token bucket or leaky bucket depending on burst tolerance
- **Bulkheads** to isolate resource pools

## Common Pitfalls

1. **Jumping to microservices too early**
   - Start with modular boundaries; split only when operational need is clear.

2. **No numbers**
   - Architecture without estimates is guesswork.

3. **Ignoring data ownership**
   - Most system failures become data consistency failures.

4. **Treating cache as magic**
   - Always define invalidation and staleness tolerance.

5. **No failure story**
   - Explain what happens when dependencies slow down or fail.

## Output Format

```text
Requirements:
Assumptions / estimates:
High-level architecture:
Data model:
Critical flows:
Failure modes:
Security/privacy:
Tradeoffs:
Open questions:
Verification plan:
```

## Verification Checklist

- [ ] Functional and non-functional requirements separated
- [ ] Capacity estimates included
- [ ] Data flow documented
- [ ] Consistency and failure modes addressed
- [ ] Security boundaries identified
- [ ] Operational metrics/alerts proposed
- [ ] Tradeoffs and open questions listed
