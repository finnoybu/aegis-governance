# AEGIS AGP-1 Complete Specification Suite & Index

**Document**: AGP-1/Index (AEGIS_AGP1_INDEX.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Governance Protocol\
**Last Updated**: March 6, 2026

---

## Executive Summary

The **AEGIS Governance Protocol (AGP-1)** is the normative wire protocol for deterministic governance of AI-generated actions within the AEGIS Federation Network. This is a comprehensive, multi-document specification suite that defines:

- **Wire protocol** for request-response communication between AI systems and governance runtimes
- **Complete message schemas** with field specifications, validation rules, and examples
- **Deterministic decision flow** with policy evaluation, risk assessment, and escalation
- **Comprehensive error handling** with retry semantics and recovery procedures
- **Authentication/Authorization** mechanisms (Bearer tokens, mTLS, API keys)
- **Policy language** for defining capability-based access control rules
- **Risk scoring** algorithms integrating trust scores and federation signals
- **Deployment guidance** for single-instance and distributed deployments

**Key Properties**:

- ✅ Deterministic: identical requests + policies = identical decisions[^2]
- ✅ Default-deny: absence of approval yields denial[^2]
- ✅ Fully auditable: every decision is tamper-evident and attributable[^1]
- ✅ Fail-closed: all subsystem failures result in denial or escalation[^2]

---

## Document Structure

This specification suite consists of **9 modular documents** organized by domain:

### Core Protocol (Read in this order)

1. **[AEGIS_AGP1_OVERVIEW.md](./AEGIS_AGP1_OVERVIEW.md)** - Protocol overview, principles, and design rationale
   - Purpose and scope
   - Core principles (determinism, default-deny, attribution, auditable)
   - Message categories
   - Integration with RFCs and federation

2. **[AEGIS_AGP1_MESSAGES.md](./AEGIS_AGP1_MESSAGES.md)** - Complete message schemas and field specifications
   - ACTION_PROPOSE schema with 15+ fields
   - DECISION_RESPONSE schema with decision outcomes
   - EXECUTION_REPORT for outcome tracking
   - ESCALATION_REQUEST for human review
   - AUDIT_QUERY for evidence retrieval
   - HEALTH_CHECK for connectivity testing

3. **[AEGIS_AGP1_WIRE_FORMAT.md](./AEGIS_AGP1_WIRE_FORMAT.md)** - Transport, serialization, and encoding
   - HTTP/1.1 and HTTP/2 endpoints and methods
   - Protocol Buffers alternative format
   - Request/response envelopes
   - Content encoding (JSON, gzip, protobuf)
   - Header specifications

4. **[AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)** - Protocol flows, diagrams, and state machines
   - Happy path (allow decision)
   - Escalation flow (human review)
   - Comprehensive decision tree
   - Complete state machine with all paths
   - Justification for flow design

5. **[AEGIS_AGP1_AUTHENTICATION.md](./AEGIS_AGP1_AUTHENTICATION.md)** - Authentication and authorization
   - Bearer tokens with JWT claims
   - Mutual TLS (mTLS) certificate validation
   - API key authentication (deprecated)
   - Authorization scopes (propose_action, query_audit, etc.)
   - Request attribution

### Decision Logic (Critical for evaluation)

1. **[AEGIS_AGP1_POLICY_EVALUATION.md](./AEGIS_AGP1_POLICY_EVALUATION.md)** - Capability registry and policy evaluation
   - Integration with RFC-0003 Capability Registry
   - Policy language specification with examples
   - Capability inheritance and composition
   - Conflict resolution (precedence rules)
   - Deterministic evaluation algorithm

2. **[AEGIS_AGP1_RISK_SCORING.md](./AEGIS_AGP1_RISK_SCORING.md)** - Risk assessment and decision logic
   - 5-factor risk scoring model with weights
   - Historical attempt rate calculations
   - Actor reputation/trust integration
   - Capability sensitivity factors
   - Behavioral anomaly detection
   - Federation signal incorporation
   - Decision thresholds (allow, monitor, escalate, deny)
   - Confidence scoring

### Operational Specifications

1. **[AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)** - Error handling and recovery
   - Error response envelope format
   - 15 error codes with HTTP mappings
   - Retryable vs. non-retryable errors
   - Exponential backoff strategies
   - Timeout and deadline handling

2. **[AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)** - Deployment, configuration, and operations
   - Deployment topologies (single-instance, HA, authority nodes)
   - Performance requirements and SLOs
   - Kubernetes and Docker examples
   - Monitoring and observability
   - Troubleshooting guide

---

## Quick Reference: Message Types

| Message | Direction | Purpose | Response |
|---------|-----------|---------|----------|
| **ACTION_PROPOSE** | Client → Server | Propose operational action for governance | DECISION_RESPONSE |
| **DECISION_RESPONSE** | Server → Client | Return governance decision (ALLOW/DENY/ESCALATE/REQUIRE_CONFIRMATION) | (none - client decides) |
| **EXECUTION_REPORT** | Client → Server | Report execution outcome (status, duration, resource usage) | ACK |
| **ESCALATION_REQUEST** | Server → Client | Request human review for high-risk/uncertain action | ESCALATION_RESPONSE |
| **AUDIT_QUERY** | Client → Server | Query audit trail for compliance/forensics | AUDIT_RESPONSE |
| **HEALTH_CHECK** | Either → Either | Test protocol health and version negotiation | HEALTH_CHECK_RESPONSE |

---

## Quick Reference: Decision Outcomes

| Decision | Meaning | Client Action |
|----------|---------|---------------|
| **ALLOW** | Action permitted | Execute with standard or enhanced constraints |
| **DENY** | Action forbidden | Stop; do not execute |
| **ESCALATE** | Requires human review | Pause; request human approval |
| **REQUIRE_CONFIRMATION** | Requires explicit user consent | Re-submit with confirmation flag |

---

## Integration with RFC Documents

This protocol specification is tightly integrated with:

- **RFC-0001 (AEGIS Architecture)**: Describes governance runtime architecture that implements AGP-1
- **RFC-0002 (Governance Runtime)**: Runtime API that wraps AGP-1 for local deployment
- **RFC-0003 (Capability Registry)**: Defines capabilities that AGP-1 evaluates policies against
- **RFC-0004 (Governance Event Model)**: Defines federation events that inform risk scoring
- **Federation Docs**: AEGIS_NODE_REFERENCE_ARCHITECTURE, AEGIS_TRUST_MODEL, etc.

---

## Performance Targets

### Latency SLOs (p99)

| Operation | Target | Notes |
|-----------|--------|-------|
| Schema validation | < 5ms | Message structure check |
| Capability resolution | < 10ms | Registry lookup |
| Policy evaluation (simple) | < 50ms | Single-rule match |
| Policy evaluation (complex) | < 500ms | 20+ rules with risk computation |
| Risk score computation | < 100ms | 5-factor calculation + federation lookup |
| Overall decision | < 200ms | Full path with caching |

### Throughput Targets

- **Minimum**: 100 governance decisions/second
- **Recommended**: 1,000+ decisions/second
- **Maximum tested**: 10,000 decisions/second (with HA cluster)

---

## Security Model

**Authentication**: Every message MUST include credentials

- Bearer token (JWT with actor_id, scope, expiry)
- mTLS certificate (CN, OU, organizational info)
- API key (deprecated; sunset plan before AGP-2)

**Authorization**: Actor MUST have appropriate scope for operation

- `governance:propose_action` - submit ACTION_PROPOSE
- `governance:query_audit` - retrieve audit records
- `governance:escalate_decision` - respond to escalations
- `governance:health_check` - protocol health queries

**Audit**: Every decision is tamper-evident and fully attributed

- Decision recorded with actor_id, timestamp, policies evaluated
- Risk factors and federation signals logged
- Execution outcomes tracked for compliance

---

## Conformance

### Server Conformance

A server implementation MUST:

- ✅ Implement all 6 message types
- ✅ Validate all required fields per schema
- ✅ Evaluate policies deterministically
- ✅ Compute risk scores using 5-factor model
- ✅ Support at least one authentication method (Bearer token)
- ✅ Maintain tamper-evident, append-only audit log
- ✅ Return appropriate error codes
- ✅ Support HTTP/1.1 or HTTP/2
- ✅ Enforce rate limiting

### Client Conformance

A client implementation MUST:

- ✅ Provide authentication credentials
- ✅ Include request_id and timestamp
- ✅ Handle DECISION_RESPONSE with all outcomes
- ✅ Respect constraints in ALLOW decisions
- ✅ Support ESCALATION_REQUEST workflow
- ✅ Report execution outcomes via EXECUTION_REPORT
- ✅ Implement retry logic for transient errors
- ✅ Respect rate limits

---

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.0 | 2026-03-05 | Initial normative release | **Current** |

### Future Versions (Planned)

- **AGP-1.1** (planned 2026-Q3): Add data classification controls, enhanced federation support
- **AGP-2.0** (planned 2026-Q4): Breaking changes for distributed consensus, zero-knowledge proofs

---

## Related Documents

### AEGIS Core Specifications

- [RFC-0001: AEGIS Architecture](../../rfc/RFC-0001-AEGIS-Architecture.md)
- [RFC-0002: Governance Runtime](../../rfc/RFC-0002-Governance-Runtime.md)
- [RFC-0003: Capability Registry](../../rfc/RFC-0003-Capability-Registry.md)
- [RFC-0004: Governance Event Model](../../rfc/RFC-0004-Governance-Event-Model.md)

### Federation Specifications

- [AEGIS Node Reference Architecture](../../federation/AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md)
- [AEGIS Trust Model](../../federation/AEGIS_GFN1_TRUST_MODEL.md)
- [Federation README with Reading Order](../../federation/README.md)

### Supporting Documents

- [AEGIS Constitution](https://aegis-constitution.com) - Governance principles
- [AEGIS Threat Model](../../aegis-core/threat-model/AEGIS_ATM1_INDEX.md) - Security analysis

---

## How to Use This Specification

### For Implementers (Building AGP-1 Servers)

1. Start with [AEGIS_AGP1_OVERVIEW.md](./AEGIS_AGP1_OVERVIEW.md) to understand principles
2. Review [AEGIS_AGP1_MESSAGES.md](./AEGIS_AGP1_MESSAGES.md) for exact schemas
3. Implement message parsing and validation per [AEGIS_AGP1_WIRE_FORMAT.md](./AEGIS_AGP1_WIRE_FORMAT.md)
4. Integrate policy evaluation per [AEGIS_AGP1_POLICY_EVALUATION.md](./AEGIS_AGP1_POLICY_EVALUATION.md)
5. Implement risk scoring per [AEGIS_AGP1_RISK_SCORING.md](./AEGIS_AGP1_RISK_SCORING.md)
6. Add error handling per [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)
7. Deploy per [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)

### For Client Developers (Calling AGP-1 Runtimes)

1. Review [AEGIS_AGP1_OVERVIEW.md](./AEGIS_AGP1_OVERVIEW.md) for protocol overview
2. Learn message structure from [AEGIS_AGP1_MESSAGES.md](./AEGIS_AGP1_MESSAGES.md)
3. Implement authentication per [AEGIS_AGP1_AUTHENTICATION.md](./AEGIS_AGP1_AUTHENTICATION.md)
4. Handle all decision outcomes from [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)
5. Implement error handling from [AEGIS_AGP1_INDEX.md](./AEGIS_AGP1_INDEX.md)

### For Policy Authors

1. Review policy evaluation in [AEGIS_AGP1_POLICY_EVALUATION.md](./AEGIS_AGP1_POLICY_EVALUATION.md)
2. Study policy language syntax and examples
3. Understand capability resolution and inheritance
4. Review conflict resolution rules for ordering policies

### For Risk Analysts

1. Review risk scoring in [AEGIS_AGP1_RISK_SCORING.md](./AEGIS_AGP1_RISK_SCORING.md)
2. Understand 5-factor risk model and weights
3. Review risk-based decision thresholds
4. Analyze confidence score calculations

---

## Document Maintenance

**Last Updated**: March 5, 2026\
**Maintained By**: AEGIS Initiative\
**Review Cycle**: Quarterly (every 3 months)\
**Next Review**: June 5, 2026

---

## License & Attribution

All AEGIS governance specifications are published under the AEGIS Governance framework. See [LICENSE](../../LICENSE) for details.

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security (TISSEC)*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../../REFERENCES.md).
