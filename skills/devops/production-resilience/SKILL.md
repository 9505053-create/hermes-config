---
name: production-resilience
description: Design and review production systems for resilience using timeouts, retries, circuit breakers, bulkheads, health checks, capacity planning, observability, and safe deployments. Use for outages, cascading failures, deployment risk, service reliability, retry/backoff, health checks, or Release It style production hardening.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [production, resilience, reliability, outages, devops, sre]
    related_skills: [system-design, n8n-automation, weekly-security-audit]
---

# Production Resilience

## Overview

Production is hostile: dependencies fail, traffic spikes, queues back up, networks partition, disks fill, and humans deploy bad changes. This skill helps design and review systems that degrade gracefully instead of collapsing.

It adapts public Release It style resilience patterns into Hermes procedures.

## When to Use

Use when the user mentions:

- Production outage, instability, cascading failure
- Circuit breaker, timeout, retry, backoff, bulkhead
- Health checks, readiness/liveness, observability
- Deployment safety, rollback, zero downtime
- Capacity planning, load shedding, chaos testing
- Hardening a service before release

## Resilience Review Framework

### 1. Integration Points

Most outages cross boundaries. For every dependency, record:

- Timeout
- Retry policy
- Circuit breaker policy
- Fallback behavior
- Idempotency guarantee
- Rate limits
- Monitoring

If there is no timeout, the system has an implicit infinite wait bug.

### 2. Stability Anti-Patterns

Look for:

- Cascading synchronous calls
- Unbounded queues
- Retry storms
- Shared resource pools across critical/non-critical work
- No backpressure
- Slow external dependency on request path
- Hidden single points of failure
- Logging/metrics that can block main flow

### 3. Stability Patterns

Apply where appropriate:

- **Timeouts**: fail fast enough for caller budgets
- **Retries with exponential backoff and jitter**: only for transient/idempotent operations
- **Circuit breakers**: stop hammering unhealthy dependencies
- **Bulkheads**: isolate resource pools by dependency or priority
- **Rate limiting/load shedding**: preserve core service under overload
- **Fallbacks**: provide degraded but useful behavior
- **Idempotency keys**: make retries safe

### 4. Health Checks

Separate:

- Liveness: process should be restarted if false
- Readiness: instance should receive traffic if true
- Deep dependency checks: useful for diagnostics, dangerous as liveness gates

Health checks should be cheap, bounded, and not create dependency storms.

### 5. Deployment Safety

Before release:

- Feature flags for risky behavior
- Backward-compatible schema changes
- Canary or phased rollout
- Rollback command/path documented
- Metrics watched during rollout
- Error budget / stop conditions defined

### 6. Observability

Minimum signals:

- Request rate
- Error rate
- Latency percentiles, not just average
- Saturation: CPU, memory, disk, queue depth, connection pools
- Dependency health
- Business-level success metric

## Incident Triage Flow

1. Stabilize: stop bleeding, roll back or disable feature if needed.
2. Scope: what users/systems are affected?
3. Timeline: when did it start and what changed?
4. Bottleneck: latency, errors, saturation, or dependency?
5. Mitigate: reduce load, scale, circuit-break, or rollback.
6. Verify: metrics return to normal.
7. Learn: write concrete prevention actions.

## Common Pitfalls

1. **Retrying non-idempotent operations**
   - Can duplicate payments, messages, or writes.

2. **No timeout hierarchy**
   - Child calls must time out before parent request deadline.

3. **Health check depends on every downstream service**
   - This turns dependency failures into restart storms.

4. **Queue without limit**
   - Infinite queues become memory outages.

5. **Rollback not tested**
   - A rollback plan that was never practiced is a hope, not a plan.

## Output Format

```text
System/service:
Critical dependencies:
Failure modes:
Current resilience gaps:
Recommended controls:
Deployment/rollback plan:
Observability gaps:
Verification:
```

## Verification Checklist

- [ ] Timeouts defined for all external calls
- [ ] Retries are bounded, jittered, and idempotent
- [ ] Circuit breakers or load shedding considered for fragile dependencies
- [ ] Bulkheads isolate critical resources
- [ ] Health checks are cheap and correctly scoped
- [ ] Rollback path documented
- [ ] Metrics/alerts cover rate, errors, latency, saturation
