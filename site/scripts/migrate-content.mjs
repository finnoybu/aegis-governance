#!/usr/bin/env node
/**
 * migrate-content.mjs
 * Copies spec markdown files from repo root into site/src/content/docs/
 * with frontmatter injected (title extracted from first # heading).
 */

import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';

const REPO = resolve(import.meta.dirname, '..', '..');
const DEST = resolve(import.meta.dirname, '..', 'src', 'content', 'docs');

// [source (relative to repo root), target (relative to DEST), optional description override]
const FILES = [
  // ── Foundation ──
  ['aegis-core/manifesto/AEGIS_Manifesto.md', 'foundation/index.md', 'The AEGIS governance manifesto — mission, principles, and design philosophy'],
  ['aegis-core/overview/AEGIS_System_Overview.md', 'foundation/overview.md', 'High-level overview of the AEGIS governance system'],
  ['aegis-core/faq/AEGIS_FAQ.md', 'foundation/faq.md', 'Frequently asked questions about AEGIS governance'],
  ['aegis-core/roadmap/AEGIS_Roadmap.md', 'foundation/roadmap.md', 'AEGIS development roadmap and milestones'],

  // ── Architecture ──
  ['docs/architecture/AEGIS_ARCHITECTURE_OVERVIEW.md', 'architecture/index.md', 'AEGIS architecture overview — layers, boundaries, and design principles'],
  ['aegis-core/architecture/AEGIS_Reference_Architecture.md', 'architecture/reference.md', 'AEGIS reference architecture specification'],
  ['aegis-core/architecture/AEGIS_Ecosystem_Map.md', 'architecture/ecosystem-map.md', 'Map of the AEGIS ecosystem — repositories, sites, and services'],
  ['docs/architecture/AEGIS_SYSTEM_STACK.md', 'architecture/system-stack.md', 'AEGIS system stack — layered architecture from schema to runtime'],
  ['docs/architecture/AI_KERNEL_MODEL.md', 'architecture/ai-kernel-model.md', 'AI kernel model — governance as operating system for AI agents'],
  ['docs/architecture/CAPABILITY_MODEL.md', 'architecture/capability-model.md', 'Capability model — bounded, typed, and verifiable agent capabilities'],
  ['docs/architecture/CAPABILITY_SCHEMA.md', 'architecture/capability-schema.md', 'Capability schema — JSON schema definitions for AEGIS capabilities'],
  ['docs/architecture/DECISION_ALGORITHM.md', 'architecture/decision-algorithm.md', 'Governance decision algorithm — deterministic policy evaluation'],
  ['docs/architecture/END_TO_END_REQUEST_FLOW.md', 'architecture/request-flow.md', 'End-to-end request flow through the governance engine'],
  ['docs/architecture/GOVERNANCE_ENGINE_COMPONENTS.md', 'architecture/engine-components.md', 'Governance engine component breakdown'],
  ['docs/architecture/GOVERNANCE_ENGINE_SPEC.md', 'architecture/engine-spec.md', 'Governance engine technical specification'],
  ['docs/architecture/GOVERNED_CAPABILITY_FLOW.md', 'architecture/capability-flow.md', 'Governed capability flow — from proposal to execution'],
  ['docs/architecture/POLICY_LANGUAGE.md', 'architecture/policy-language.md', 'AEGIS policy language — syntax, semantics, and evaluation rules'],
  ['docs/architecture/POLICY_MATCHING_AND_DEBUG.md', 'architecture/policy-matching.md', 'Policy matching and debugging — resolution order and diagnostics'],
  ['docs/architecture/REFERENCE_MONITOR_MODEL.md', 'architecture/reference-monitor.md', 'Reference monitor model — mandatory mediation at execution boundary'],
  ['docs/architecture/RISK_SCORING_ALGORITHM.md', 'architecture/risk-algorithm.md', 'Risk scoring algorithm — deterministic threat quantification'],
  ['docs/architecture/RISK_SCORING_MODEL.md', 'architecture/risk-model.md', 'Risk scoring model — threat classification and severity mapping'],
  ['docs/architecture/SECURITY_ASSUMPTIONS.md', 'architecture/security-assumptions.md', 'Security assumptions — threat model premises and trust boundaries'],
  ['docs/architecture/SYSTEM_PRINCIPLES.md', 'architecture/principles.md', 'System principles — foundational design constraints'],
  ['docs/architecture/TRUST_BOUNDARIES.md', 'architecture/trust-boundaries.md', 'Trust boundaries — isolation zones and crossing rules'],

  // ── Protocol / AGP-1 ──
  ['aegis-core/protocol/AEGIS_AGP1_INDEX.md', 'protocol/index.md', 'AGP-1 specification suite index — the AEGIS governance protocol'],
  ['aegis-core/protocol/AEGIS_AGP1_OVERVIEW.md', 'protocol/overview.md', 'AGP-1 protocol overview — design goals, scope, and terminology'],
  ['aegis-core/protocol/AEGIS_AGP1_AUTHENTICATION.md', 'protocol/authentication.md', 'AGP-1 authentication — identity verification and binding'],
  ['aegis-core/protocol/AEGIS_AGP1_MESSAGES.md', 'protocol/messages.md', 'AGP-1 message types — proposals, decisions, and audit records'],
  ['aegis-core/protocol/AEGIS_AGP1_POLICY_EVALUATION.md', 'protocol/policy-evaluation.md', 'AGP-1 policy evaluation — matching, resolution, and enforcement'],
  ['aegis-core/protocol/AEGIS_AGP1_RISK_SCORING.md', 'protocol/risk-scoring.md', 'AGP-1 risk scoring — threat quantification within the protocol'],
  ['aegis-core/protocol/AEGIS_AGP1_TRUST_MODEL.md', 'protocol/trust-model.md', 'AGP-1 trust model — two-layer agent admissibility'],
  ['aegis-core/protocol/AEGIS_AGP1_WIRE_FORMAT.md', 'protocol/wire-format.md', 'AGP-1 wire format — serialization and transport encoding'],

  // ── Threat Model / ATM-1 + ATX-1 ──
  ['aegis-core/threat-model/AEGIS_ATM1_INDEX.md', 'threat-model/index.md', 'ATM-1 threat model index — security analysis for AEGIS-governed systems'],
  ['aegis-core/threat-model/AEGIS_ATM1_THREAT_ACTORS.md', 'threat-model/threat-actors.md', 'ATM-1 threat actors — adversary profiles and motivations'],
  ['aegis-core/threat-model/AEGIS_ATM1_ATTACK_VECTORS.md', 'threat-model/attack-vectors.md', 'ATM-1 attack vectors — threat surfaces and exploitation paths'],
  ['aegis-core/threat-model/AEGIS_ATM1_SECURITY_PROPERTIES.md', 'threat-model/security-properties.md', 'ATM-1 security properties — invariants the system must maintain'],
  ['aegis-core/threat-model/AEGIS_ATM1_MITIGATIONS.md', 'threat-model/mitigations.md', 'ATM-1 mitigations — architectural countermeasures'],
  ['aegis-core/threat-model/AEGIS_ATM1_RESIDUAL_RISKS.md', 'threat-model/residual-risks.md', 'ATM-1 residual risks — known gaps and deferred mitigations'],
  ['docs/atx/ATX-1_TECHNIQUE_TAXONOMY.md', 'threat-model/taxonomy.md', 'ATX-1 technique taxonomy — 10 tactics, 58 techniques for agentic AI threats'],

  // ── Identity / AIAM-1 ──
  ['aiam/AEGIS_AIAM1_INDEX.md', 'identity/index.md', 'AIAM-1 specification suite — identity and access management for AI agents'],
  ['aiam/AEGIS_AIAM1_IDENTITY.md', 'identity/identity.md', 'AIAM-1 identity model — composite agent identity and principal chains'],
  ['aiam/AEGIS_AIAM1_INTENT.md', 'identity/intent.md', 'AIAM-1 intent claims — structured purpose assertions at moment of action'],
  ['aiam/AEGIS_AIAM1_AUTHORITY.md', 'identity/authority.md', 'AIAM-1 authority model — IBAC authorization framework'],
  ['aiam/AEGIS_AIAM1_CAPABILITIES.md', 'identity/capabilities.md', 'AIAM-1 capability binding — identity-scoped capability grants'],
  ['aiam/AEGIS_AIAM1_DELEGATION.md', 'identity/delegation.md', 'AIAM-1 delegation — authority transfer and chain validation'],
  ['aiam/AEGIS_AIAM1_SESSIONS.md', 'identity/sessions.md', 'AIAM-1 session management — governance-aware session lifecycle'],
  ['aiam/AEGIS_AIAM1_ATTESTATION.md', 'identity/attestation.md', 'AIAM-1 attestation — action-level governance decision proof'],
  ['aiam/AEGIS_AIAM1_REVOCATION.md', 'identity/revocation.md', 'AIAM-1 revocation — credential and authority withdrawal'],
  ['aiam/AEGIS_AIAM1_INTEROPERABILITY.md', 'identity/interoperability.md', 'AIAM-1 interoperability — cross-system identity federation'],
  ['aiam/AEGIS_AIAM1_THREAT_MODEL.md', 'identity/threat-model.md', 'AIAM-1 threat model — identity-specific attack surfaces'],
  ['aiam/AEGIS_AIAM1_CONFORMANCE.md', 'identity/conformance.md', 'AIAM-1 conformance — compliance levels and validation criteria'],

  // ── Federation / GFN-1 ──
  ['federation/AEGIS_GFN1_GOVERNANCE_NETWORK.md', 'federation/index.md', 'GFN-1 governance federation network — decentralized governance intelligence'],
  ['federation/AEGIS_GFN1_TRUST_MODEL.md', 'federation/trust-model.md', 'GFN-1 trust model — federated publisher reputation scoring'],
  ['federation/AEGIS_GFN1_GOVERNANCE_FEEDS.md', 'federation/feeds.md', 'GFN-1 governance feeds — signal format and distribution'],
  ['federation/AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md', 'federation/node-architecture.md', 'GFN-1 node reference architecture — federation participant design'],
  ['federation/AEGIS_GFN1_SCHEMA.md', 'federation/schema.md', 'GFN-1 schema — AT Protocol lexicons for governance federation'],

  // ── RFCs ──
  ['rfc/RFC-0001-AEGIS-Architecture.md', 'rfc/0001.md', 'RFC-0001: AEGIS Governance Architecture'],
  ['rfc/RFC-0002-Governance-Runtime.md', 'rfc/0002.md', 'RFC-0002: Governance Runtime — API, state model, SLOs'],
  ['rfc/RFC-0003-Capability-Registry.md', 'rfc/0003.md', 'RFC-0003: Capability Registry & Policy Language'],
  ['rfc/RFC-0004-Governance-Event-Model.md', 'rfc/0004.md', 'RFC-0004: Governance Event Model — two-layer trust'],
  ['rfc/RFC-0005-Reference-Deployment-Patterns.md', 'rfc/0005.md', 'RFC-0005: Reference Deployment Patterns'],
  ['rfc/RFC-0006-Claude-Code-Plugin.md', 'rfc/0006.md', 'RFC-0006: Claude Code Plugin — embedded governance'],
  ['rfc/RFC-0009-Prior-Art-and-External-Validation-Record.md', 'rfc/0009.md', 'RFC-0009: Prior Art and External Validation Record'],
  ['rfc/RFC-0010-State-Dump-Protocol-Formalization.md', 'rfc/0010.md', 'RFC-0010: State Dump Protocol Formalization'],
  ['rfc/RFC-0011-Authority-Binding-Sub-Spec-Revision.md', 'rfc/0011.md', 'RFC-0011: Authority Binding Sub-Spec Revision'],
  ['rfc/RFC-0012-ATX1-v2-Taxonomy-Normalization.md', 'rfc/0012.md', 'RFC-0012: ATX-1 v2 Taxonomy Normalization'],
  ['rfc/RFC-0013-ACF1-Control-Framework.md', 'rfc/0013.md', 'RFC-0013: ACF-1 Control Framework'],
  ['rfc/RFC-0014-ATX1-Dual-Licensing.md', 'rfc/0014.md', 'RFC-0014: ATX-1 Dual Licensing'],
  ['rfc/RFC-0015-Runtime-Consolidation.md', 'rfc/0015.md', 'RFC-0015: Runtime Consolidation'],
  ['rfc/RFC-0016-Cross-Domain-Machine-Discovery.md', 'rfc/0016.md', 'RFC-0016: Cross-Domain Machine Discovery Protocol'],
  ['rfc/RFC-0017-Commit-Boundary-and-Binding-Validation.md', 'rfc/0017.md', 'RFC-0017: Commit Boundary and Binding Validation'],
  ['rfc/RFC-0018-Automated-Governance-Attestation-Protocol.md', 'rfc/0018.md', 'RFC-0018: Automated Governance Attestation Protocol'],
  ['rfc/RFC-0019-AIAM-1-Identity-Access-Management-AI-Agents.md', 'rfc/0019.md', 'RFC-0019: AIAM-1 Identity & Access Management for AI Agents'],
];

let count = 0;
let errors = [];

for (const [src, dest, descOverride] of FILES) {
  const srcPath = resolve(REPO, src);
  const destPath = resolve(DEST, dest);

  let content;
  try {
    content = readFileSync(srcPath, 'utf-8');
  } catch (e) {
    errors.push(`MISSING: ${src}`);
    continue;
  }

  // Extract title from first # heading
  const titleMatch = content.match(/^#\s+(.+)$/m);
  const title = titleMatch ? titleMatch[1].trim() : dest.replace(/\.md$/, '');

  // Generate description: use override or extract from metadata
  const description = descOverride || title;

  // Escape quotes in title/description for YAML
  const safeTitle = title.replace(/"/g, '\\"');
  const safeDesc = description.replace(/"/g, '\\"');

  // Build new content with frontmatter prepended
  const frontmatter = `---\ntitle: "${safeTitle}"\ndescription: "${safeDesc}"\n---\n\n`;
  const newContent = frontmatter + content;

  mkdirSync(dirname(destPath), { recursive: true });
  writeFileSync(destPath, newContent, 'utf-8');
  count++;
}

// Create RFC index page (no source file)
const rfcIndex = `---
title: "Request for Comments (RFCs)"
description: "AEGIS RFC series — technical specifications and design documents"
---

# AEGIS RFCs

The RFC series documents the technical design decisions behind the AEGIS governance architecture. Each RFC addresses a specific aspect of the system — from core architecture to deployment patterns to identity management.

---

## Active RFCs

| RFC | Title | Version | Status |
|-----|-------|---------|--------|
| [RFC-0001](/rfc/0001/) | AEGIS Governance Architecture | 0.2 | Final |
| [RFC-0002](/rfc/0002/) | Governance Runtime | 0.2 | Draft |
| [RFC-0003](/rfc/0003/) | Capability Registry & Policy | 0.2 | Draft |
| [RFC-0004](/rfc/0004/) | Governance Event Model | 0.4 | Draft |
| [RFC-0005](/rfc/0005/) | Reference Deployment Patterns | 0.1 | Draft |
| [RFC-0006](/rfc/0006/) | Claude Code Plugin | 0.2 | Draft |

## Normative RFCs

| RFC | Title | Version | Status |
|-----|-------|---------|--------|
| [RFC-0009](/rfc/0009/) | Prior Art and External Validation | 0.0.1 | Placeholder |
| [RFC-0010](/rfc/0010/) | State Dump Protocol Formalization | 0.0.1 | Placeholder |
| [RFC-0011](/rfc/0011/) | Authority Binding Sub-Spec Revision | 0.0.1 | Placeholder |
| [RFC-0012](/rfc/0012/) | ATX-1 v2 Taxonomy Normalization | 1.0 | Final |
| [RFC-0013](/rfc/0013/) | ACF-1 Control Framework | 1.0 | Final |
| [RFC-0014](/rfc/0014/) | ATX-1 Dual Licensing | 1.0 | Final |
| [RFC-0015](/rfc/0015/) | Runtime Consolidation | 1.0 | Final |
| [RFC-0016](/rfc/0016/) | Cross-Domain Machine Discovery | 1.0 | Final |
| [RFC-0017](/rfc/0017/) | Commit Boundary and Binding Validation | 0.1 | Draft |
| [RFC-0018](/rfc/0018/) | Automated Governance Attestation Protocol | 0.1 | Draft |
| [RFC-0019](/rfc/0019/) | AIAM-1 Identity & Access Management | 0.1 | Draft |

---

RFC-0007 (Operational Considerations) and RFC-0008 (Federation Network Protocol) are reserved placeholders — content pending.
`;

writeFileSync(resolve(DEST, 'rfc/index.md'), rfcIndex, 'utf-8');
count++;

console.log(`Migrated ${count} files`);
if (errors.length) {
  console.log(`Errors:\n  ${errors.join('\n  ')}`);
}
