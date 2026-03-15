# RFC-0005: Reference Deployment Patterns

**RFC:** RFC-0005
**Status:** Draft  
**Version:** 0.1.0  
**Created:** 2026-03-07  
**Updated:** 2026-03-08  
**Author:** Kenneth Tannenbaum, Finnoybu IP LLC  
**Repository:** aegis-governance  
**Target milestone:** Q2 2026  
**Supersedes:** None  
**Superseded by:** None  

---

## Summary

This RFC establishes the Reference Deployment Patterns (RDP) framework for AEGIS™. It defines how the AEGIS governance architecture may be deployed across heterogeneous infrastructure environments while preserving constitutional integrity and protocol compliance. AEGIS™ is deployment-environment agnostic: the [Constitution](../aegis-core/constitution/) and [AGP-1](../aegis-core/protocol/AEGIS_AGP1_INDEX.md) define what governance must do; this RFC defines how that governance may be instantiated.

---

## Motivation

As AEGIS™ adoption grows, practitioners will ask: how do I actually run this? The answer must not be prescriptive. An architecture that requires Kubernetes to operate is not a governance standard — it is a Kubernetes plugin. At the same time, AEGIS™ cannot remain purely abstract. This RFC establishes a tiered set of Reference Deployment Patterns: concrete enough to be actionable, abstract enough to be universal.

---

## Guide-Level Explanation

AEGIS separates two concerns: what governance does (defined by the Constitution and RFCs) and where governance runs (defined by the deployment environment). A factory's safety inspector performs the same role whether the factory uses conveyor belts or robotic arms. The inspection procedure does not change with the machinery.

RDP-03 (Embedded Lightweight) is the starting point for most practitioners. RDP-01 (Kubernetes) is the enterprise path. RDP-02 and RDP-04 address service mesh and serverless environments respectively.

---

## Reference-Level Explanation

### Core Principle

The Capability Registry, Governance Gateway, Authority Verification, and Decision Integrity components must function correctly regardless of underlying infrastructure.

### RDP-01: Kubernetes Enterprise Pattern

**Status:** Experimental | **Branch:** `experimental/k8s-reference-deployment`

| AEGIS Component | Implementation |
|---|---|
| Capability Registry | OPA policy bundle[^14] |
| Governance Gateway | AgentGateway sidecar |
| Authority Verification | Keycloak token validation |
| Decision Integrity (SP-1) | OpenShift logging stack |

### RDP-02: Sidecar / Service Mesh Pattern

**Status:** Proposed

| AEGIS Component | Implementation |
|---|---|
| Capability Registry | Envoy filter chain |
| Governance Gateway | Envoy external authorization filter |
| Authority Verification | SPIFFE SVID validation |
| Decision Integrity (SP-1) | Envoy access log (append-only) |

### RDP-03: Embedded Lightweight Pattern

**Status:** Proposed | **Reference:** aegis-runtime repository

| AEGIS Component | Implementation |
|---|---|
| Capability Registry | `registry.json` |
| Governance Gateway | `governance_gateway.py` |
| Authority Verification | Caller identity from process context |
| Decision Integrity (SP-1) | Append-only JSONL audit file |

### RDP-04: Serverless Gateway Pattern

**Status:** Proposed

| AEGIS Component | Implementation |
|---|---|
| Capability Registry | API Gateway usage plans |
| Governance Gateway | Lambda authorizer function |
| Authority Verification | IAM role validation |
| Decision Integrity (SP-1) | CloudTrail / Cloud Audit Logs |

### Supply Chain Security Gap

None of the four RDPs currently address supply chain integrity for the AI model itself. Before a model operates in an AEGIS-governed environment, the deployment should verify model artifact hash, registry of model version, and provenance chain. Flagged for a future RFC. Reference: JFrog AI Catalog.

### Branch Strategy

| Concern | Location |
|---|---|
| This RFC | `docs/rdp-deployment-agnosticism/` |
| RDP-01 experimental | `experimental/k8s-reference-deployment/` |
| RDP-03 reference | `aegis-runtime` repository |

---

## Drawbacks

- Four patterns increase documentation and maintenance surface area.
- RDP-01 is marked experimental and may diverge from the specification as the Kubernetes ecosystem evolves.
- No conformance test suite currently exists to validate that a deployment pattern satisfies constitutional requirements. Compliance is currently self-certified.

---

## Alternatives Considered

**Single prescribed deployment pattern:** Simpler to document but excludes the majority of practitioners who do not operate Kubernetes. Conflicts with the deployment-agnostic principle.

**No reference patterns, specification only:** Maintains purity but creates an adoption barrier. Practitioners need working examples, not just specifications.

**Community-contributed patterns only:** Appropriate long-term but requires a stable core set first. The four patterns in this RFC represent the most common real-world deployment environments.

---

## Compatibility

No breaking changes to [RFC-0001](./RFC-0001-AEGIS-Architecture.md) through RFC-0004. Deployment patterns are additive. An existing AEGIS specification deployment is unaffected by this RFC.

---

## Implementation Notes

RDP-03 is the recommended starting point for new implementations. RDP-01 is the recommended path for enterprise Kubernetes environments and is the subject of ongoing experimental work. Derrick Sutherland's article (Shadow-Soft, March 2026) provides independent validation of the Kubernetes control plane approach.

---

## Open Questions

- [ ] Should RDP-01 be promoted from experimental to draft once a working reference exists?
- [ ] Should supply chain security be addressed in this RFC or a dedicated RFC?
- [ ] Should AEGIS define a conformance test suite that validates any deployment pattern against constitutional requirements?

---

## Success Criteria

- A practitioner can deploy a compliant AEGIS runtime using any of the four patterns without modifying the core specification
- RDP-03 can be stood up in a development environment in under 30 minutes
- Each pattern maps all four AEGIS governance components to concrete implementations

---

## References

[^14]: Open Policy Agent, v0.61, Cloud Native Computing Foundation, 2024. [Online]. Available: <https://www.openpolicyagent.org>. See [REFERENCES.md](../REFERENCES.md).

---

*AEGIS™* | *"Capability without constraint is not intelligence"™*  
*AEGIS Initiative — Finnoybu IP LLC*
