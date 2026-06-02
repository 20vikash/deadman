# Deadman

Deadman is an independent service responsible for monitoring the **liveliness of critical Frappe Cloud capabilities**.

Unlike traditional monitoring systems, Deadman does not perform health checks itself. It only receives periodic heartbeats from components that have already verified their own health.

If a heartbeat stops arriving within the expected interval, Deadman assumes that the capability has failed and raises alerts.

---

## Philosophy

Deadman follows the classic dead man's switch pattern:

> "Keep proving you're alive. If you stop proving it, I'll assume something is wrong."

Deadman does **not** know:

- How Prometheus works
- How Sentry works
- How Twilio works
- How Elasticsearch works

Those systems are responsible for determining their own health.

Deadman only knows:

- Capability Name
- Expected Heartbeat Interval
- Last Seen Timestamp

---

## Architecture

```text
                Deadman
                     ▲
                     │
              Heartbeats
                     │
 ┌───────────────────┼───────────────────┐
 │                   │                   │
 │                   │                   │

Press            Monitor Agent      Trace Agent
                 Log Agent

 │                   │                   │

validate_incidents   Prometheus          Sentry
resolve_incidents    Alertmanager
call_humans          Grafana

Twilio
Telegram
```

---

## Responsibilities

### Press

Press is responsible for heartbeats related to operational workflows and external dependencies.

Examples:

- validate_incidents
- resolve_incidents
- call_humans
- Twilio
- Telegram

Example:

```python
def validate_incidents():
    ...
    send_heartbeat("incident_validation")
```

Example:

```python
if twilio_balance > 0:
    send_heartbeat("twilio")
```

---

### Agent

Agent is responsible for heartbeats related to infrastructure services.

Agent runs on:

- Monitor Servers
- Trace Servers
- Log Servers

A dedicated background process can periodically verify services present on the machine and emit heartbeats.

Example:

```python
while True:
    check_monitor_server()
    check_trace_server()
    check_log_server()

    sleep(60)
```

---

### Monitor Server

Before sending a heartbeat, Agent verifies:

- Prometheus
- Alertmanager
- Grafana

Example:

```python
if prometheus_healthy() and alertmanager_healthy():
    heartbeat("monitor_server")
```

---

### Trace Server

Before sending a heartbeat, Agent verifies:

- Sentry
- Supporting containers/services

Example:

```python
if sentry_healthy():
    heartbeat("trace_server")
```

---

### Log Server

Before sending a heartbeat, Agent verifies:

- Elasticsearch
- Kibana

Example:

```python
if elasticsearch_healthy() and kibana_healthy():
    heartbeat("log_server")
```

---

## Deadman Responsibilities

Deadman is intentionally simple.

It performs only three actions:

### Receive Heartbeats

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

---

### Track Last Seen

```text
trace_server
last_seen = 2026-06-02 12:00:00
```

---

### Detect Silence

If:

```text
current_time - last_seen > expected_interval
```

Deadman creates an alert and begins notification fan-out.

---

## Notification Fan-out

Deadman notifies engineers through every available channel.

Examples:

- Telegram
- Phone Calls
- Email
- Raven
- Future notification providers

Deadman should avoid circular dependencies whenever possible.

Example:

If:

```text
Twilio Balance < 0
```

Deadman should not rely solely on Twilio to notify engineers about the Twilio outage.

Alternative channels such as Telegram and Email should still be used.

---

## Provisioning

Deadman is provisioned through Press similar to:

- Monitor Server
- Trace Server
- Log Server

Provisioning responsibilities include:

- VM creation
- Frappe app installation
- Token generation
- Configuration injection
- Agent configuration

No manual installation or credential copy-pasting should be required.

---

## Core Principle

Deadman is not another monitoring system.

Monitoring systems determine health.

Deadman determines silence.

```text
Component
     │
     ▼
Self Health Check
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