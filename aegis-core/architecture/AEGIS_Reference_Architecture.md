# AEGIS™ Reference Architecture

### Architectural Enforcement & Governance of Intelligent Systems

Version: 0.1\
Status: Draft\
Effective Date: March 5, 2026

---

# Overview

The AEGIS™ reference architecture defines the core components required to enforce governance over AI-generated actions.

The architecture separates **AI reasoning** from **operational execution** by introducing a governance layer that evaluates actions before they interact with external systems.

This design ensures that AI systems cannot directly execute operational actions without governance approval.

---

> **Architectural Layer Enforcement**: AEGIS operates at the architectural layer, enforcing policy at the execution boundary between AI agents and infrastructure. Unlike model-internal approaches (Constitutional AI, RLHF, fine-tuning), AEGIS is model-agnostic, deterministic, and federated. See [System Overview](../overview/AEGIS_System_Overview.md#architectural-positioning) for detailed positioning.

---

# Architectural Model

```
AI Agent
   │
   ▼
AEGIS™ Governance Gateway
   │
   ▼
Decision Engine
 ├ Capability Authorization
 ├ Authority Verification
 ├ Risk Evaluation
 └ Policy Enforcement
   │
   ▼
Tool Proxy Layer
   │
   ▼
External Systems
```

---

# Architectural Principles

The architecture is designed around several core principles.

### Deterministic Governance

Governance decisions must be enforced through system architecture rather than relying on model behavior.

### Capability Isolation

AI systems may only access explicitly defined capabilities.

### Default-Deny Model

Actions are rejected unless explicitly permitted.

### Operational Auditability

All governance decisions must produce immutable records.

### Incremental Deployability

AEGIS™ can be introduced gradually into existing AI systems.

---

# Core Components

## AI Agent

The AI agent is responsible for generating action proposals.

Agents may be implemented using:

* LLM-based agents
* workflow orchestration systems
* enterprise automation platforms
* autonomous software agents

The agent does **not execute actions directly**.

Instead, it submits action proposals through the AEGIS Governance Protocol (AGP).

---

## Governance Gateway

The governance gateway acts as the **entry point** for all AI-generated actions.

Responsibilities include:

* validating action schemas
* authenticating actors
* assigning action identifiers
* forwarding requests to the decision engine

Example API endpoint:

```
POST /aegis/action
```

The gateway ensures that all operational actions pass through the governance runtime.

---

## Decision Engine

The decision engine evaluates governance rules and determines whether actions may execute.

The engine consists of four subsystems.

### Capability Authorization

Verifies that the requested capability exists within the capability registry.

Example capabilities:

```
telemetry.query
identity.disable_account
infrastructure.deploy
communication.send_alert
```

If a capability is undefined, the action is rejected.

---

### Authority Verification

Validates that the actor has permission to request the capability.

Actors may include:

* authenticated users
* service identities
* AI agents operating under delegated authority

Authorization may incorporate:

* role-based access control
* attribute-based authorization
* policy constraints

---

### Risk Evaluation

Evaluates contextual risk associated with the requested action.

Risk evaluation may consider:

* resource classification
* operational impact
* environment (production vs staging)
* historical risk signals

Risk scores may influence governance outcomes.

---

### Policy Enforcement

Evaluates governance policies against the action request.

Policies define conditions under which actions may execute.

Possible outcomes:

```
ALLOW
DENY
ESCALATE
REQUIRE_CONFIRMATION
```

Policies may incorporate:

* capability rules
* actor roles
* environmental constraints
* risk thresholds

---

## Capability Registry

The capability registry defines the actions available within a governed system.

Example entry:

```
capability: telemetry.query
description: Query security telemetry
allowed_roles:
  - soc_analyst
environment:
  - production
risk_level: low
```

Capabilities must be defined before they can be used.

---

## Policy Engine

The policy engine evaluates governance rules defined in structured formats.

Policies determine when capabilities may be exercised.

Example rule:

```
policy: production_deploy_guardrail
when:
 capability: infrastructure.deploy
 environment: production
then:
 decision: ESCALATE
```

---

## Tool Proxy Layer

Tool proxies provide controlled interfaces to external systems.

Examples include:

* cloud API proxies
* security telemetry proxies
* database proxies
* messaging system proxies

Proxies enforce:

* parameter validation
* access restrictions
* audit logging
* rate limits

---

## Audit System

All governance decisions must generate audit records.

Example record:

```
decision_id: d-1001
action_id: a-1001
actor: agent:soc-01
capability: telemetry.query
decision: ALLOW
timestamp: 2026-03-05T18:42:11Z
```

Audit logs provide transparency and accountability.

---

# Data Structures

The architecture uses several core data models.

### Action

Represents a proposed operation from an AI system.

Example:

```
actor
capability
resource
parameters
context
```

---

### Decision

Represents the governance outcome.

Example:

```
decision
risk_score
policy_version
audit_reference
```

---

### Capability

Defines allowed system operations.

---

### Policy

Defines rules governing capability execution.

---

# Deployment Architecture

AEGIS™ supports multiple deployment patterns based on scale, latency requirements, and organizational structure.

## Pattern 1: Embedded Runtime (Single-Node)

The governance runtime operates as an embedded component within an AI platform.

```
┌─────────────────────────────────────┐
│       AI Platform Process           │
│  ┌──────────────┐                   │
│  │  AI Agent    │                   │
│  └──────┬───────┘                   │
│         │                            │
│  ┌──────▼───────┐    ┌────────────┐ │
│  │AEGIS Runtime │───▶│   Audit    │ │
│  └──────┬───────┘    └────────────┘ │
└─────────┼────────────────────────────┘
          │
    ┌─────▼─────┐
    │External   │
    │Systems    │
    └───────────┘
```

**Use Case:** Single AI agent, development/testing, small-scale deployment  
**Latency:** <5ms (in-process)  
**Scalability:** Limited to process resources  
**Complexity:** Low  
**Benefits:** Simple deployment, minimal infrastructure, fast evaluation  
**Limitations:** No shared governance across agents, single point of failure

---

## Pattern 2: Sidecar Deployment (Distributed)

AEGIS operates as a sidecar service alongside each AI agent.

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│   AI Agent A   │       │   AI Agent B   │       │   AI Agent C   │
└────────┬───────┘       └────────┬───────┘       └────────┬───────┘
         │                        │                        │
    ┌────▼────┐              ┌────▼────┐              ┌────▼────┐
    │ AEGIS   │              │ AEGIS   │              │ AEGIS   │
    │ Runtime │              │ Runtime │              │ Runtime │
    └────┬────┘              └────┬────┘              └────┬────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                  ┌───────────────▼──────────────┐
                  │  Centralized Audit & Policy  │
                  └──────────────────────────────┘
```

**Use Case:** Multiple AI agents, Kubernetes environments, independent scaling  
**Latency:** 5-10ms (network call)  
**Scalability:** Scales independently per agent  
**Complexity:** Medium  
**Benefits:** Agent isolation, independent scaling, fault tolerance  
**Limitations:** Duplicated runtime instances, configuration drift risk

---

## Pattern 3: Central Governance Service (High-Availability)

A shared AEGIS runtime cluster governs multiple AI agents.

```
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Agent A │  │ Agent B │  │ Agent C │  │ Agent D │
└────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘
     │            │            │            │
     └────────────┴────────────┴────────────┘
                  │
        ┌─────────▼─────────┐
        │   Load Balancer   │
        └─────────┬─────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│ AEGIS   │  │ AEGIS   │  │ AEGIS   │
│Runtime 1│  │Runtime 2│  │Runtime 3│
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌────▼────┐  ┌────▼────┐
│Capability│  │ Policy  │  │  Audit  │
│Registry  │  │ Store   │  │  Store  │
└──────────┘  └──────────┘  └──────────┘
```

**Use Case:** Enterprise deployment, multiple agents, high availability required  
**Latency:** 10-15ms (network + evaluation)  
**Scalability:** Horizontal scaling of runtime cluster  
**Complexity:** High  
**Benefits:** Centralized policy management, consistent governance, HA/DR, shared intelligence  
**Limitations:** Network latency, potential bottleneck, requires infrastructure expertise

---

## Deployment Comparison Matrix

| Capability | Embedded | Sidecar | Central Service |
|------------|----------|---------|-----------------|
| **Latency** | <5ms | 5-10ms | 10-15ms |
| **Scalability** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Complexity** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **High Availability** | ❌ | Partial | ✅ |
| **Shared Policies** | ❌ | Via sync | ✅ |
| **Resource Overhead** | Low | Medium | Low (shared) |
| **Isolation** | Process | Container | Network |
| **Best For** | Dev/Test | Kubernetes | Enterprise |

---

# Decision Flow Sequence

The following sequence illustrates how AEGIS evaluates an AI-generated action:

```
┌──────────┐          ┌──────────┐          ┌──────────┐          ┌──────────┐          ┌──────────┐
│  AI      │          │Governance│          │ Decision │          │   Tool   │          │ External │
│  Agent   │          │ Gateway  │          │  Engine  │          │  Proxy   │          │ System   │
└────┬─────┘          └────┬─────┘          └────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                     │                     │                     │
     │ 1. ACTION_PROPOSE   │                     │                     │                     │
     │────────────────────▶│                     │                     │                     │
     │                     │                     │                     │                     │
     │                     │ 2. Validate Schema  │                     │                     │
     │                     │ + Authenticate Actor│                     │                     │
     │                     │                     │                     │                     │
     │                     │ 3. Evaluate Action  │                     │                     │
     │                     │────────────────────▶│                     │                     │
     │                     │                     │                     │                     │
     │                     │                     │ 4. Check Capability │                     │
     │                     │                     │   Registry          │                     │
     │                     │                     │                     │                     │
     │                     │                     │ 5. Verify Authority │                     │
     │                     │                     │   & Actor Perms     │                     │
     │                     │                     │                     │                     │
     │                     │                     │ 6. Evaluate Risk    │                     │
     │                     │                     │   Score             │                     │
     │                     │                     │                     │                     │
     │                     │                     │ 7. Evaluate Policy  │                     │
     │                     │                     │   Rules             │                     │
     │                     │                     │                     │                     │
     │                     │ 8. DECISION_RESPONSE│                     │                     │
     │                     │◀────────────────────│                     │                     │
     │                     │   (ALLOW/DENY)      │                     │                     │
     │                     │                     │                     │                     │
     │                     │ 9. Write Audit Log  │                     │                     │
     │                     │────────────────────▶│                     │                     │
     │                     │                     │                     │                     │
     │ 10. DECISION        │                     │                     │                     │
     │◀────────────────────│                     │                     │                     │
     │                     │                     │                     │                     │
     │ 11. If ALLOW: EXECUTE_ACTION               │                     │                     │
     │─────────────────────────────────────────────────────────────────▶│                     │
     │                     │                     │                     │                     │
     │                     │                     │                     │ 12. Execute         │
     │                     │                     │                     │────────────────────▶│
     │                     │                     │                     │                     │
     │                     │                     │                     │ 13. Result          │
     │                     │                     │                     │◀────────────────────│
     │                     │                     │                     │                     │
     │ 14. EXECUTION_RESULT│                     │                     │                     │
     │◀─────────────────────────────────────────────────────────────────│                     │
     │                     │                     │                     │                     │
     │                     │ 15. Log Execution   │                     │                     │
     │                     │────────────────────▶│                     │                     │
```

## Flow Steps Explained

1. **ACTION_PROPOSE** — AI agent submits action request via AGP
2. **Schema Validation** — Gateway validates message schema and authenticates actor
3. **Evaluate Action** — Gateway forwards request to Decision Engine
4. **Check Capability** — Verify capability exists in registry
5. **Verify Authority** — Validate actor has permission to request this capability
6. **Evaluate Risk** — Calculate risk score based on context and recent history
7. **Evaluate Policy** — Run policy rules against action + context
8. **DECISION_RESPONSE** — Decision Engine returns ALLOW/DENY/ESCALATE/REQUIRE_CONFIRMATION
9. **Write Audit Log** — Record governance decision immutably
10. **DECISION** — Gateway returns decision to AI agent
11. **EXECUTE_ACTION** — If ALLOW, agent submits to Tool Proxy
12. **Execute** — Tool Proxy calls external system
13. **Result** — External system returns result
14. **EXECUTION_RESULT** — Tool Proxy returns result to agent
15. **Log Execution** — Record execution outcome in audit log

## Decision Outcomes

| Decision | Meaning | Agent Response |
|----------|---------|----------------|
| **ALLOW** | Action approved | Execute via Tool Proxy |
| **DENY** | Action rejected | Do not execute; inform user |
| **ESCALATE** | Requires human review | Wait for approval; notify escalation target |
| **REQUIRE_CONFIRMATION** | Needs user confirmation | Prompt user; execute if confirmed |

---

# Performance Considerations

AEGIS governance introduces evaluation latency before every action execution.

## Latency Targets

| Evaluation Phase | Target Latency | Optimization Strategy |
|------------------|----------------|----------------------|
| Schema Validation | <1ms | Pre-compiled schemas, fast parsers |
| Actor Authentication | <2ms | Token caching, session management |
| Capability Lookup | <1ms | In-memory registry with LRU cache |
| Authority Check | <2ms | Role cache, pre-computed permissions |
| Risk Evaluation | <3ms | Recent history cache, async scoring |
| Policy Evaluation | <5ms | Compiled policies, indexed rules |
| Audit Write | <1ms | Async log write, buffering |
| **Total (95th percentile)** | **<15ms** | **End-to-end optimization** |

## Performance Optimization Strategies

### Caching

* **Capability Registry Cache** — Cache frequently accessed capabilities in memory
* **Policy Cache** — Pre-compile policies for fast evaluation
* **Actor Permission Cache** — Cache role/permission lookups with TTL
* **Risk Score Cache** — Cache recent risk calculations (5-minute TTL)

### Asynchronous Processing

* **Audit Logging** — Write audit records asynchronously (don't block decision)
* **Federation Signals** — Send governance signals async
* **Telemetry** — Metrics and monitoring via background threads

### Horizontal Scaling

* **Stateless Gateway** — Scale gateway nodes independently
* **Policy Engine Workers** — Distribute policy evaluation across workers
* **Capability Registry Read Replicas** — Scale read-heavy registry lookups

### Connection Pooling

* **Database Connections** — Pool connections to audit store
* **External API Clients** — Reuse HTTP clients for tool proxies

## Throughput Targets

| Deployment Pattern | Target Throughput | Notes |
|-------------------|-------------------|-------|
| Embedded Runtime | 1,000 actions/sec | Single process limits |
| Sidecar Deployment | 5,000 actions/sec | Per sidecar instance |
| Central Service (3-node) | 50,000 actions/sec | Horizontally scalable |

## Performance Monitoring

Key metrics to monitor:

* **Governance Latency** — p50, p95, p99 latency per evaluation phase
* **Decision Throughput** — Actions evaluated per second
* **Cache Hit Rates** — Capability, policy, actor cache effectiveness
* **Error Rates** — Schema validation failures, evaluation errors
* **Queue Depths** — Audit log buffer, async processing queues

---

# Security Architecture

AEGIS governance enforces security through multiple layers.

## Trust Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    UNTRUSTED ZONE                           │
│  ┌────────────┐                                             │
│  │  AI Agent  │ ◀── Treats AI reasoning as untrusted input │
│  └─────┬──────┘                                             │
└────────┼────────────────────────────────────────────────────┘
         │ AGP over mTLS
         │
┌────────▼────────────────────────────────────────────────────┐
│              GOVERNANCE TRUST BOUNDARY                       │
│  ┌────────────────────────────────────────────────┐         │
│  │          AEGIS Governance Runtime              │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │         │
│  │  │ Gateway  │  │ Decision │  │  Policy  │     │         │
│  │  │          │  │  Engine  │  │  Engine  │     │         │
│  │  └──────────┘  └──────────┘  └──────────┘     │         │
│  └────────────────────────────────────────────────┘         │
└────────┬────────────────────────────────────────────────────┘
         │ Controlled proxies
         │
┌────────▼────────────────────────────────────────────────────┐
│                    TRUSTED ZONE                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Database  │  │    APIs    │  │Infrastructure│           │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Security Mechanisms

### 1. Authentication & Authorization

**Actor Authentication:**

* Mutual TLS (mTLS) for AI agent connections
* API keys or JWT tokens for actor identity
* Service account validation for autonomous agents
* Human actor verification via SSO/OIDC

**Authorization:**

* Role-Based Access Control (RBAC) for capabilities
* Attribute-Based Access Control (ABAC) for context-aware decisions
* Least privilege enforcement per actor identity
* Dynamic permission elevation via policy

### 2. Data Protection

**In Transit:**

* TLS 1.3 for all network communication
* mTLS between AI agents and governance gateway
* Encrypted AGP protocol messages

**At Rest:**

* Encrypted audit logs (AES-256)
* Encrypted capability and policy stores
* Encrypted credentials in tool proxies
* Secret management integration (HashiCorp Vault, AWS Secrets Manager)

### 3. Input Validation

**Schema Validation:**

* Strict JSON schema validation for all AGP messages
* Parameter type checking and range validation
* SQL injection/command injection prevention in tool proxies
* Resource identifier validation (no path traversal)

**Capability Validation:**

* Whitelist-only capability registry (no dynamic creation)
* Capability schema enforcement
* Parameter sanitization before proxy execution

### 4. Audit & Forensics

**Immutable Audit Logs:**

* Append-only audit storage
* Cryptographic hashing for tamper detection
* Write-once-read-many (WORM) storage for compliance
* Audit log retention policies (7 years for compliance)

**Audit Data:**

* Actor identity + authentication method
* Action details + capability reference
* Governance decision + policy version
* Execution result + timestamps
* Risk score + evaluation context

### 5. Defense in Depth

**Multiple Enforcement Points:**

* Gateway-level validation (schema, authentication)
* Decision Engine denial (capability, authority, policy)
* Tool Proxy validation (parameter sanitization)
* External system access controls (independent layer)

**Fail-Secure Design:**

* Default-deny for unknown capabilities
* Fail-closed on policy evaluation errors
* Explicit ALLOW required; implicit DENY
* Circuit breakers for degraded decision engine

---

# Integration Patterns

AEGIS integrates with popular AI agent frameworks through adapters.

## Pattern 1: LangChain Integration

```python
from langchain.agents import AgentExecutor
from langchain_aegis import AEGISToolkit

# Initialize AEGIS toolkit with governance gateway endpoint
aegis_toolkit = AEGISToolkit(
    gateway_url="https://aegis.example.com",
    actor_token="agent-token-12345"
)

# Wrap LangChain tools with AEGIS governance
governed_tools = aegis_toolkit.wrap_tools([
    SearchTool(),
    DatabaseQueryTool(),
    SlackNotificationTool()
])

# Create agent executor with governed tools
agent = AgentExecutor(
    agent=llm_agent,
    tools=governed_tools,
    verbose=True
)

# All tool executions now flow through AEGIS governance
result = agent.run("Query production database for user metrics")
# AEGIS evaluates: capability=database.query, env=production
# Decision: REQUIRE_CONFIRMATION (production database)
```

## Pattern 2: CrewAI Integration

```python
from crewai import Agent, Task, Crew
from aegis_crewai import AEGISGovernedAgent

# Create AEGIS-governed agent
soc_analyst = AEGISGovernedAgent(
    role="Security Analyst",
    goal="Investigate security incidents",
    backstory="SOC analyst with incident response experience",
    aegis_config={
        "gateway_url": "https://aegis.example.com",
        "actor_id": "agent:soc-analyst-01",
        "default_policy": "soc_operations"
    },
    tools=[TelemetryQueryTool(), IPBlockTool(), AlertTool()]
)

# Tasks automatically governed by AEGIS
investigate_task = Task(
    description="Investigate suspicious IP 203.0.113.42",
    agent=soc_analyst
)

# All tool calls evaluated by governance runtime
crew = Crew(agents=[soc_analyst], tasks=[investigate_task])
result = crew.kickoff()
```

## Pattern 3: AutoGPT Integration

```python
from autogpt.agent import Agent
from autogpt.config import Config
from aegis_autogpt import AEGISCommandRegistry

# Initialize AEGIS command registry
aegis_registry = AEGISCommandRegistry(
    gateway_url="https://aegis.example.com",
    actor_credentials="autogpt-agent-token"
)

# Register commands with AEGIS governance
aegis_registry.register_governed_commands([
    "execute_shell",
    "write_file",
    "delete_file",
    "git_operations"
])

# Create AutoGPT agent with governed commands
config = Config()
agent = Agent(
    ai_name="DevOps Assistant",
    memory=...,
    command_registry=aegis_registry
)

# AutoGPT commands now require governance approval
agent.run("Deploy the updated application to production")
# AEGIS evaluates: capability=deployment.production_deploy
# Decision: ESCALATE (requires human approval)
```

## Pattern 4: OpenAI Assistants Integration

```python
from openai import OpenAI
from aegis_openai import AEGISFunctionHandler

client = OpenAI(api_key="...")

# Wrap OpenAI functions with AEGIS governance
aegis_handler = AEGISFunctionHandler(
    gateway_url="https://aegis.example.com",
    actor_identity="assistant:financial-advisor"
)

# Define governed functions
governed_functions = aegis_handler.wrap_functions([
    {
        "name": "execute_trade",
        "description": "Execute a stock trade",
        "capability": "trading.execute_order",
        "parameters": {...}
    },
    {
        "name": "query_portfolio",
        "description": "Query portfolio holdings",
        "capability": "trading.query_portfolio",
        "parameters": {...}
    }
])

# Create assistant with governed functions
assistant = client.beta.assistants.create(
    name="Financial Advisor",
    instructions="...",
    tools=governed_functions
)

# Function calls routed through AEGIS before execution
thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Buy 100 shares of MSFT at market price"
)
# AEGIS evaluates execute_trade capability before OpenAI function runs
```

## Integration Benefits

| Framework | AEGIS Integration Pattern | Benefits |
|-----------|---------------------------|----------|
| **LangChain** | Tool wrapper | Transparent governance, no agent code changes |
| **CrewAI** | Governed agent class | Role-based governance, team coordination |
| **AutoGPT** | Command registry | Shell command protection, filesystem governance |
| **OpenAI Assistants** | Function handler | API-level governance, serverless compatible |
| **Custom Frameworks** | AGP client library | Full control, protocol-level integration |

---

# Scaling Considerations

AEGIS runtimes may scale horizontally.

Typical strategies include:

* stateless gateway nodes
* distributed policy evaluation
* centralized audit logging
* capability cache layers

Scaling the governance runtime allows it to support large numbers of AI agents.

---

# Alternative Architectural Approaches

Other governance approaches include:

### Embedded Guardrails

Governance rules embedded directly within AI agents.

Limitation:

* rules can be bypassed by prompt manipulation.

---

### API-Level Access Control

Traditional access control mechanisms at the API layer.

Limitation:

* does not understand AI-generated intent.

---

### AEGIS Runtime Governance

AEGIS separates governance from the AI system itself.

Benefits:

* deterministic enforcement
* independent governance layer
* auditable decisions
* extensible governance model

---

# Federation Integration

AEGIS runtimes may optionally connect to the **AEGIS Governance Federation Network (GFN)**.

This enables nodes to share:

* governance signals
* circumvention reports
* policy updates
* risk intelligence

Federation integration is defined in **RFC-0004**.

---

# Relationship to Other Specifications

This document complements:

* RFC-0001 — AEGIS Architecture
* RFC-0002 — Governance Runtime
* RFC-0003 — Capability Registry
* RFC-0004 — Governance Event Model
* AGP-1 — Governance Protocol

Together these documents define the complete AEGIS™ governance architecture.

---

# Foundational Principle

> Capability without constraint is not intelligence™
