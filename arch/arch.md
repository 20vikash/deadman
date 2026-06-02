# Deadman

Deadman is a heartbeat-based reliability service for Frappe Cloud.

It monitors the liveliness of critical platform capabilities by tracking periodic heartbeats emitted by Press.

Deadman does not perform health checks, collect metrics, or inspect infrastructure. Its sole responsibility is detecting the absence of expected heartbeats and triggering alerts.

---

## Design Pattern

Deadman follows the classic dead man's switch pattern.

> Keep proving you're alive. If you stop proving it, something is wrong.

---

## Architecture

```text
                  Capability Sources
                           │
                           ▼

                        Press
                  (Health Evaluation)
                           │
                           ▼

                        Deadman
                 (Heartbeat Tracking)
                           │
                           ▼

                         Alerts
```

Press acts as the control plane and health aggregator.

Deadman acts as the heartbeat tracker and alerting system.

---

## Capability Sources

Press determines capability health using one of the following sources.

```text
                         Press
                           ▲
                           │

        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼

 Internal Checks     Grafana Data      Agent Queries
```

### Internal Checks

Capabilities evaluated directly by Press.

Examples:

* incident_validation
* incident_resolution
* call_humans
* twilio
* telegram

### Grafana

Infrastructure capabilities should use the existing observability stack whenever possible.

```text
Exporter
    │
    ▼
Prometheus
    │
    ▼
Grafana
    │
    ▼
Press
```

Examples:

* monitor_server
* trace_server
* log_server
* node availability
* service metrics
* infrastructure metrics

### Agent Queries

When capability information is not available through Grafana, Press may query Agent directly.

```text
Press
   │
   ▼
 Agent
   │
   ▼
Local Service State
```

Examples:

* Service-specific health checks
* Machine-local diagnostics

Agent never communicates directly with Deadman.

Agent never emits heartbeats.

---

## Data Flow

```text
Capability
     │
     ▼
Health Verification
     │
     ▼
Press
     │
     ▼
Heartbeat
     │
     ▼
Deadman
     │
     ▼
Alert
```

A heartbeat is emitted only when Press determines that a capability is healthy.

Deadman tracks heartbeat activity and generates alerts when expected heartbeats stop arriving.

---

## Capability Model

Each monitored capability consists of:

| Field             | Description                              |
| ----------------- | ---------------------------------------- |
| Capability        | Unique capability identifier             |
| Expected Interval | Expected heartbeat frequency             |
| Grace Multiplier  | Allowed heartbeat misses before alerting |
| Last Seen         | Timestamp of the last heartbeat          |

Example:

```text
Capability        : trace_server
Expected Interval : 5 minutes
Grace Multiplier  : 3
Last Seen         : 2026-06-02 12:00:00
```

---

## Grace Multiplier

Deadman does not immediately alert when a heartbeat is missed.

Each capability defines:

* Expected Interval
* Grace Multiplier

The effective timeout is calculated as:

```text
effective_timeout = expected_interval × grace_multiplier
```

Example:

```text
Capability        : trace_server
Expected Interval : 5 minutes
Grace Multiplier  : 3

Effective Timeout : 15 minutes
```

This allows Deadman to tolerate:

* Temporary network failures
* Short service restarts
* Deployment windows
* Transient infrastructure issues

before generating alerts.

A capability is considered unavailable only when:

```text
current_time - last_seen > effective_timeout
```

---

## Deadman Processing

### Heartbeat Ingestion

```http
POST /heartbeat
```

Example:

```json
{
  "capability": "trace_server",
  "token": "..."
}
```

### Silence Detection

```text
effective_timeout = expected_interval × grace_multiplier
```

```text
current_time - last_seen > effective_timeout
```

When a capability exceeds its effective timeout, Deadman marks it as unavailable and triggers alert fan-out.

---

## Alerting

```text
Capability Failure
        │
        ▼
      Deadman
        │
        ▼
 Notification Fan-out
        │
        ├── Telegram
        ├── Email
        ├── Phone
        └── Raven
```

Deadman should avoid relying solely on the failing dependency to deliver alerts.

Example:

```text
Twilio Balance < 0
```

Twilio should not be the only configured notification channel for Twilio-related failures.

---

## Deployment

Deadman is provisioned through Press similarly to other platform services.

Provisioning responsibilities include:

* VM provisioning
* Application deployment
* Token generation
* Configuration injection

No manual installation or credential distribution should be required.

---

## Non-Goals

Deadman is not:

* A monitoring system
* A metrics collection platform
* A tracing platform
* A log aggregation platform
* A service discovery system
* A replacement for Prometheus
* A replacement for Grafana
* A replacement for Alertmanager

Deadman complements the existing observability stack by detecting the absence of expected signals rather than producing them.
