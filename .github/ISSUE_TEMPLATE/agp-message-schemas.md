---
name: AGP Protocol Message Schemas
about: Define message formats for the AEGIS Governance Protocol
title: 'AGP Protocol Message Schemas'
labels: ['protocol', 'specification', 'agp']
assignees: ''
---

## Overview

Define the complete message schemas for the AEGIS Governance Protocol (AGP), including action proposals, governance decisions, execution results, and escalations.

## Scope

This issue tracks the specification of:

- [ ] ACTION_PROPOSE message format
- [ ] DECISION_RESPONSE message format
- [ ] EXECUTION_RESULT message format
- [ ] ESCALATION_REQUEST message format
- [ ] Message envelope (headers, metadata, signatures)
- [ ] Error and exception formats
- [ ] Protocol versioning and compatibility

## Related Specifications

- AGP-1: AEGIS Governance Protocol
- RFC-001: Governance Architecture
- RFC-002: Governance Runtime

## Message Types

### ACTION_PROPOSE
Agent proposes an action for governance evaluation.

### DECISION_RESPONSE
Governance engine returns a decision (ALLOW, DENY, ESCALATE, REQUIRE_CONFIRMATION).

### EXECUTION_RESULT
Tool proxy reports execution outcome back to the agent.

### ESCALATION_REQUEST
Request human intervention for high-risk operations.

## Discussion Points

1. Should messages use JSON, Protocol Buffers, or support multiple formats?
2. How should we handle message authentication and integrity?
3. What metadata should be included in all messages? (trace IDs, timestamps, etc.)
4. How should we support protocol versioning and backward compatibility?
5. Should the protocol support streaming/bidirectional communication?

## Deliverables

- [ ] JSON Schema definitions for all message types
- [ ] Protocol message flow diagrams
- [ ] Example message sequences
- [ ] Error handling specification
- [ ] SDK/client library interface design
- [ ] Protocol conformance test suite

## Additional Context

AGP is the wire protocol between AI agents and AEGIS governance infrastructure. It must be:
- Language agnostic
- Easy to implement for agent developers
- Secure (prevent tampering or replay attacks)
- Observable (support tracing and debugging)
