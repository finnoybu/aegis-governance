# AEGIS™ GFN-1 Trust Model & Federated Reputation

**Document**: GFN-1/Trust (AEGIS_GFN1_TRUST_MODEL.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Governance Federation Network\
**Last Updated**: March 6, 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Trust Primitives](#2-trust-primitives)
3. [Normative Trust Score Calculation](#3-normative-trust-score-calculation)
4. [Event Weighting](#4-event-weighting)
5. [Trust Bootstrap Mechanisms](#5-trust-bootstrap-mechanisms)
6. [Sybil Attack Resistance](#6-sybil-attack-resistance)
7. [Game-Theoretic Incentive Model](#7-game-theoretic-incentive-model)
8. [Trust Revocation Procedures](#8-trust-revocation-procedures)
9. [Reputation Graph Extensions](#9-reputation-graph-extensions)
10. [Signal Ingestion and Quarantine](#10-signal-ingestion-and-quarantine)
11. [Audit and Compliance](#11-audit-and-compliance)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the normative trust evaluation model for AEGIS Federation Network (GFN) nodes.

The model enables autonomous governance nodes to:

- **Evaluate signal credibility** from diverse publishers without central authority
- **Resist coordinated attacks** (malicious injection, spam, Sybil nodes, misinformation)
- **Preserve operational autonomy** (nodes retain final decision authority)
- **Enable transparent auditing** (all trust decisions are auditable)[^1]

### 1.2 Trust Evaluation Objectives

The model balances:

| Objective | Mechanism |
|-----------|-----------|
| Decentralization | No global trust oracle; nodes compute locally |
| Security | Cryptographic verification, replay resistance, identity binding |
| Reliability | Multi-factor weighting, corroboration requirements, reputation decay |
| Transparency | Auditable trust factors, documented thresholds, reviewable logs |
| Autonomy | Local policy override; federation signals are advisory only |

### 1.3 Threat Model

The trust model defends against:

- **Malicious Publishers**: inject false signals to manipulate governance
- **Sybil Attackers**: create multiple pseudo-identities to amplify false signals
- **Spam Publishers**: flood federation with low-quality, high-confidence claims
- **Coordinated Misinformation**: synchronized false reports to exploit corroboration metrics
- **Key Compromise**: stolen publisher keys used to forge authentic-looking signals
- **Replay Attacks**: old signals re-injected to trigger outdated mitigations

---

## 2. Trust Primitives

### 2.1 Identity Verification (Mandatory)[^17]

All federation signals MUST carry cryptographic identity binding.

Nodes MUST verify before accepting any signal:

1. **DID Format Validity**
   - Format: `did:aegis:<network>:<node-identifier>`
   - Network: `mainnet`, `testnet`, `consortium-<id>`
   - Node-identifier: must match regex `^[a-z0-9][a-z0-9.-]*$`

2. **Signature Validity**
   - Algorithm: `ed25519` (preferred), `rsa-sha256` (legacy)
   - Signature MUST verify against publisher's DID document public key
   - Key ID in signature MUST be active (not revoked, within validity period)

3. **Timestamp Freshness**
   - Event timestamp MUST be within ±5 minutes of receiver's clock
   - Protects against stale event injection
   - Configurable per governance domain (min: ±2 min, max: ±10 min)

4. **Replay Protection**
   - `event_id` (UUID) MUST be unique per publisher
   - Receiver maintains replay-prevention cache (TTL: 24 hours minimum)
   - Signals with duplicate `event_id` are rejected immediately

5. **Schema Validation**
   - All required fields MUST be present
   - Field types MUST match schema definition
   - Unknown fields are ignored (for forward compatibility)

Any signal failing verification is **immediately rejected** and logged.

### 2.2 Authority Classification Scheme (Normative)

Each publisher MUST be assigned to exactly one authority class based on verifiable credentials:

| Class | Criteria | Initial Trust Score | Examples |
|-------|----------|-------------------|----------|
| `L0_SYSTEM` | AEGIS org-published; hardcoded DID | 0.95 | AEGIS Security Research |
| `L1_AUTHORITY` | Consortium-verified auditor; third-party attestation | 0.85 | NIST AIVRF, Big4 auditor |
| `L2_ENTERPRISE` | Registered organization; proof of operational AEGIS runtime; audit history > 90 days | 0.70 | Fortune 500 SOC, regulated bank |
| `L3_CONTRIBUTOR` | Community-submitted; signed contributor agreement; minimal audit history | 0.50 | Open-source security team |
| `UNCLASSIFIED` | No verifiable credentials; unknown publisher | 0.25 | First-time publisher |
| `QUARANTINE` | Trust revoked; previous violation detected | 0.05 | Malicious publisher (see section 8) |

Classification MUST be:

- **Deterministic**: same input → same classification across all nodes
- **Auditable**: classification reason logged with timestamp
- **Appealable**: nodes MAY adjust class via local policy override with audit trail

---

## 3. Normative Trust Score Calculation

### 3.1 Trust Score Inputs

Each publisher is evaluated on five independent factors. Trust score is computed as a **weighted average** of factor scores.

All factor scores are in range **[0.0, 1.0]**.

### 3.2 Baseline Trust Factor (B)

$$
B = 0.95 I_{L0} + 0.85 I_{L1} + 0.70 I_{L2} + 0.50 I_{L3} + 0.25 I_{U} + 0.05 I_{Q}
$$

**Authority Class Baselines** (from section 2.2):

- L0_SYSTEM: 0.95
- L1_AUTHORITY: 0.85
- L2_ENTERPRISE: 0.70
- L3_CONTRIBUTOR: 0.50
- UNCLASSIFIED: 0.25
- QUARANTINE: 0.05

### 3.3 Historical Accuracy Factor (H)

Measures fraction of publisher signals that are **not subsequently contradicted** by strong evidence.

$$
H = \frac{S_{nc}}{S_{total}}
$$

Where:

- **Window**: last 90 days or 100 events, whichever is larger
- **Contradicted**: signal claims X, but corroborating evidence shows ¬X
- **Bootstrap value** (no history): H = 0.8 (assume good faith)

Examples:

- Publisher claims "Prompt Injection Technique XYZ affects GPT-4": later verified by independent researchers → **not contradicted** (H +1)
- Publisher claims "User accounts compromised", but audit shows no breach → **contradicted** (H -3)

### 3.4 Consistency and Quality Factor (Q)

Measures publisher's consistency in:

- schema compliance (no validation errors)
- metadata completeness (all recommended fields present)
- evidence quality (strong justification provided)

$$
Q = 1.0 - \frac{E_{quality}}{E_{total}}
$$

Where quality issues include:

- schema validation failures (weight: -0.5 per event)
- missing recommended metadata (weight: -0.1 per event)
- low-confidence claims presented as high (weight: -0.2 per event)

**Bootstrap value**: Q = 0.9 (assume reasonable quality initially)

### 3.5 Audit Posture Factor (A)

Measures publisher's operational governance maturity.

$$
A = \frac{1}{2} A_{audit} + \frac{1}{2} A_{trans}
$$

**Audit Score** (requires evidence):

- No audit available: 0.3
- Self-attested audit: 0.5
- Third-party audit < 1 year old: 0.8
- Third-party audit < 6 months old: 0.9

**Transparency Score** (requires evidence):

- No published security posture: 0.3
- Published incident disclosure policy: 0.6
- Published key rotation schedule: 0.8
- Published AEGIS governance audit record: 0.95

**Bootstrap value**: A = 0.5 (no evidence available)

### 3.6 Federation Reputation Factor (F)

Measures how other federation nodes rate this publisher.

$$
F = \frac{P_{endorse}}{P_{total}}
$$

Where:

- **Endorsement**: another node with trust_score ≥ 0.6 reports consuming this publisher's events successfully
- **Opinion**: another node either endorses or reports problems with this publisher

**Weighting**:

- Endorsement from L0/L1 node: weight +1.0
- Endorsement from L2 node: weight +0.5
- Negative report from L0/L1 node: weight -1.0

**Bootstrap value**: F = 0.5 (no peer feedback available)

### 3.7 Normative Trust Score Formula

$$
T = 0.30B + 0.25H + 0.20Q + 0.15A + 0.10F
$$

**Constraint**: `trust_score` is clamped to **[0.0, 1.0]**

### 3.8 Trust Score Decay

Publisher trust scores decay over time if not updated within evaluation window.

$$
T_{decayed} = T \cdot e^{-\lambda t}
$$

Where:

- $\lambda = 0.01$ (half-life ≈ 69 days)
- $t$ = days since last update of evidence factors

**Rationale**: publishers inactive for 6+ months have uncertain current posture

**Success criteria**: The trust score calculation is reproducible given the same input signals and evaluation timestamp $t$. Implementations MUST treat $t$ as an explicit, logged input parameter — identical values of $T_0$, $\lambda$, and $t$ MUST always yield the identical decayed score on any node. Score variation across nodes or time reflects differing values of $t$, not non-determinism in the computation.

### 3.9 Trust Score Thresholds (Normative)

| Threshold | Interpretation | Action |
|-----------|-----------------|--------|
| ≥ 0.80 | High Trust | Auto-ingest signal; apply constraints if reasonable |
| [0.50, 0.80) | Medium Trust | Ingest signal; require corroboration for risk changes |
| [0.25, 0.50) | Low Trust | Quarantine signal; manual review required |
| < 0.25 | Untrusted | Reject signal; log for audit |

---

## 4. Event Weighting

Once a publisher's trust score is computed, individual events are weighted based on:

1. **Publisher Trust Score** (main factor)
2. **Event Confidence** (if provided by publisher)
3. **Event Freshness** (decay over time)
4. **Corroboration** (multi-publisher consistency)

### 4.1 Event Weight Calculation (Normative)

$$W_{\text{event}} = TS \times C \times F \times B$$

Where:

- **TS**: Publisher trust_score (section 3.7)
- **C**: Event confidence claim [0.0, 1.0] (from event payload; default 1.0 if omitted)
- **F**: Freshness factor (decay)
- **B**: Boost or penalty based on corroboration

### 4.2 Freshness Factor (Normative)

$$F(t) = e^{-\alpha t}$$

Where:

- $t$ = days since event timestamp
- $\alpha$ = 0.02 (default); half-life ≈ 35 days
- Receivers MAY adjust $\alpha$ per event type (min: 0.005, max: 0.1)

Example:

- Event 7 days old: $F(7) = e^{-0.02 \times 7} \approx 0.87$
- Event 35 days old: $F(35) = e^{-0.02 \times 35} = 0.5$

### 4.3 Corroboration Boost (Normative)

$$B = 1.0 + k \times N_{\text{corroborators}}$$

Where:

- $N_{\text{corroborators}}$ = number of independent publishers reporting same core claim
- $k = 0.15$ (default); configurable [0.05, 0.3]
- Capped at B ≤ 2.0 (avoid over-amplification)

**Corroboration Rules**:

- Only count events within 30-day window
- Only count from publishers with trust_score ≥ 0.3
- Claims MUST be semantically equivalent (checked via content hash similarity)

Example:

- Single report of technique X: W = TS × C × F × 1.0
- Same report from 2 additional publishers: W = TS × C × F × 1.3

---

## 5. Trust Bootstrap Mechanisms

### 5.1 Problem Statement

New federation nodes have no historical trust evidence. Nodes need **deterministic, secure** ways to establish initial trust relationships without requiring centralized authority.

### 5.2 Bootstrap Method 1: Allowlist (Highest Assurance)

**Requirement**: Node operator maintains a manually curated **allowlist of trusted publisher DIDs**.

**Process**:

1. Allowlisted DID automatically assigned to L1_AUTHORITY class
2. Allowlisted DIDs bypass historical evidence verification (H = 0.95)
3. Nodes MUST publish allowlist as verifiable configuration
4. Allowlist changes MUST be audited and timestamped

**Use Case**: Bootstrapping from known consortiums, NIST authorities

**Authority**: Node operator has full control; federation signals cannot override

### 5.3 Bootstrap Method 2: Consortium Membership (Medium Assurance)

**Requirement**: Publisher has cryptographic proof of membership in known consortium.

**Process**:

1. Consortium publishes list of member DIDs + proof tokens
2. Node verifies proof token signature by consortium's DID
3. Publisher automatically assigned L2_ENTERPRISE class
4. Publisher's H factor set to 0.85 initially

**Proof Token Format**:

```json
{
  "consortium_id": "did:aegis:consortium-financial",
  "member_did": "did:aegis:mainnet:bank-001",
  "valid_from": "2026-01-01T00:00:00Z",
  "valid_until": "2027-01-01T00:00:00Z",
  "signature": {
    "alg": "ed25519",
    "signed_by": "did:aegis:consortium-financial#key-1",
    "signature_bytes": "base64url(...)",
    "timestamp": "2026-03-05T12:00:00Z"
  }
}
```

**Consortium Requirements**:

- Consortium DID must be allowlisted or verified through L1 authority
- Consortium MUST publish revocation list annually
- Consortium MUST have vetted membership criteria

### 5.4 Bootstrap Method 3: Transitive Trust Endorsement (Low-Medium Assurance)

**Requirement**: Publisher has endorsement from existing trusted peer.

**Process**:

1. Trusted peer (trust_score ≥ 0.75) publishes endorsement of new publisher
2. New publisher's A factor set to 0.70 initially (peer trust vouches for operational maturity)
3. New publisher's F factor initialized from endorser's opinion

**Endorsement Format**:

```json
{
  "message_type": "TRUST_ENDORSEMENT",
  "endorser_did": "did:aegis:mainnet:org-a",
  "endorsed_did": "did:aegis:mainnet:org-b-new",
  "capability_areas": ["circumvention_reports"],
  "confidence": 0.85,
  "evidence": "org-b-new has shared 3 credible reports with us; no contradictions",
  "valid_until": "2026-12-31T23:59:59Z",
  "signature": {...}
}
```

**Validation**:

- Endorser's current trust_score MUST be ≥ 0.75
- Endorsement MUST NOT be older than 180 days
- New publisher MUST validate endorser's identity independently

### 5.5 Bootstrap Method 4: Accelerated Onboarding (for L3_CONTRIBUTOR)

**Requirement**: New publisher accepts lower initial trust with accelerated update path.

**Process**:

1. New publisher starts at UNCLASSIFIED (0.25)
2. Publisher's first 10 events are processed and evaluated carefully
3. If no contradictions detected and quality is good: H jumps to 0.90, Q to 0.85
4. Publisher can reach L3_CONTRIBUTOR (0.50) in as little as 30 days

**Safeguards**:

- All L3_CONTRIBUTOR signals require corroboration or manual approval
- Rate limiting: max 10 events/day from new publishers
- Automatic re-evaluation every 30 days

---

## 6. Sybil Attack Resistance

### 6.1 Sybil Attack Threat

A **Sybil attacker** creates multiple pseudo-identities to:

- Amplify false signals through corroboration
- Bypass rate limits through distributed injection
- Accumulate trust independently for each identity

### 6.2 Sybil Resistance Mechanisms

#### 6.2.1 Identity Binding to Real-World Artifacts

All publishers MUST bind their DID to verifiable real-world credentials:

| Evidence Type | Sybil Resistance | Required For |
|---------------|-----------------|---------------|
| Domain-controlled key (DNSSEC) | High | L1_AUTHORITY, L2_ENTERPRISE |
| Third-party audit certificate | High | L2_ENTERPRISE and above |
| Consortium membership proof | Medium | L2_ENTERPRISE |
| Self-signed only | Low | L3_CONTRIBUTOR (rate-limited) |

**Requirement**: nodes MUST verify one of the above before accepting event ≥ L3_CONTRIBUTOR trust level

#### 6.2.2 Corroboration Requires Independent Evidence

Corroboration boost (section 4.3) ONLY applies if:

1. Publishers have **distinct DIDs** (not variant spellings)
2. Publishers have **different infrastructure origins** (verified by IP WHOIS, ASN)
3. Publishers have **different trust bootstrap sources** (not all consortium members from same org)
4. Time delay between events ≥ 1 hour (prevent synchronized injection)

**Check Logic**:

```
for each corroborating publisher P:
  if P.DID_similarity(main_publisher) > 0.95:
    reject corroboration (likely alias)
  if P.infrastructure_owner == main_publisher.infrastructure_owner:
    reduce corroboration boost by 50%
  if P.bootstrap_source == main_publisher.bootstrap_source:
    reduce corroboration boost by 30%
```

#### 6.2.3 Rate Limiting and Burst Detection

Per-publisher rate limits prevent Sybil amplification:

| Trust Level | Max Events/Day | Burst Size | Evaluation Window |
|-------------|---|---|---|
| L0_SYSTEM | Unlimited | Unlimited | N/A |
| L1_AUTHORITY | 1000 | 100 | 1 hour |
| L2_ENTERPRISE | 500 | 50 | 1 hour |
| L3_CONTRIBUTOR | 100 | 10 | 1 hour |
| UNCLASSIFIED | 20 | 5 | 6 hours |

**Burst** = events exceeding rate within evaluation window

Burst response:

- Warning: burst count recorded; publisher trust decays by 10%
- Second burst: automatic downgrade to lower class
- Third burst within 30 days: automatic QUARANTINE

#### 6.2.4 Entropy Requirement for New Publishers

New publishers (UNCLASSIFIED) must exhibit **signal diversity** to resist profile-based Sybil detection:

- First 20 events MUST cover ≥ 3 distinct event types
- events MUST have ≥ 2 distinct target systems mentioned
- Temporal distribution MUST be non-uniform (not bot-like)

Events violating entropy requirements are quarantined pending manual review.

---

## 7. Game-Theoretic Incentive Model

### 7.1 Motivation: Why Publishers Participate?

Rational federation participants face a **prisoner's dilemma** between:

- **Defection**: publish low-quality/malicious signals for short-term advantage
- **Cooperation**: publish honest signals to build reputation

This section specifies incentive structures that make **cooperation individually rational**.

### 7.2 Payoff Model

Define publisher utility as function of:

- $R_t$: reputation score (trust_score) at time $t$
- $S_t$: number of consuming nodes at time $t$
- $C(q)$: cost to produce signal of quality $q$
- $U^i$: intrinsic utility from honest participation

**Utility Function**:
$$U = R_t \times S_t + U^i - C(q)$$

Where:

- Honest signals (high $q$) maintain high $R_t$ and $S_t$
- Dishonest signals (low $q$) initially high utility, but rapid $R_t$ decay ends consuming

### 7.3 Reputation Stability (Nash Equilibrium)

**Claim**: Honest publication is a Nash equilibrium if:

$$\Delta U_{\text{honest}} > \Delta U_{\text{dishonest}}$$

Over long horizon:

$$\text{Long-term utility (honest)} = T \times R_{\text{honest}} \times S_{\text{honest}} - \sum C(q) > \\
\text{Long-term utility (defection)} = T_{\text{short}} \times R_{\text{spike}} \times S_{\text{spike}} - C(q_{\text{low}})$$

Where:
- $T_{\text{short}}$ = short window before reputation collapse (typically 7-14 days)
- $R_{\text{spike}}$ = initial reputation from lying (0.6-0.8)
- $R_{\text{honest}}$ = steady-state reputation (0.7-0.95 for honest publishers)

**Proof Sketch**:
1. Dishonest signals are eventually contradicted (H factor → 0)
2. Reputation decay (section 3.8) multiplies remaining utility by $e^{-0.01t}$
3. Over 1 year, dishonest trajectory yields 10-20% of honest trajectory

### 7.4 Incentives Provided by Federation

#### 7.4.1 Reputation Increases Signal Reach

Nodes with trust_score ≥ 0.80 get preferential treatment:
- Automatic ingestion without corroboration
- Featured in federation digests
- Faster policy propagation (lower adoption latency)

**Effect**: honest publishers reach 3-4x more nodes than low-trust publishers

#### 7.4.2 Corroboration Rewards Collaboration

Publishers benefit from corroboration (section 4.3):
- 15% boost per additional independent publisher
- Creates incentive to coordinate honest reporting
- Discourages manipulation (only works with honest peers)

**Effect**: honest publishers amplify each other's reach

#### 7.4.3 Reputation Decay Punishes Abstinence

Inactive publishers lose reach:
- trust_score decays ~1% per day after 30 days of inactivity
- After 6 months: trust_score reduced 50%

**Effect**: incentivizes continuous honest participation

#### 7.4.4 Anti-Sybil Quotas Limit Attack Scaling

Sybil resistances (section 6) prevent attacker from scaling:
- Cannot amplify through corroboration (infrastructure check)
- Cannot scale through rate limits (burst detection)
- Bootstrap cost increases per identity (auditor attestation)

**Effect**: attacker cost grows exponentially; defense is proportional

### 7.5 Defection Failure Modes

**Why dishonest participation fails**:

1. **Immediate: Detection**
   - False claims are proven wrong within 1-7 days (H factor update)
   - Quality issues caught by Q factor (schema, metadata)

2. **Medium Term: Reputation Collapse**
   - After first contradiction: 10-20% drop in trust_score
   - After 3rd contradiction: automatic QUARANTINE
   - Defector loses all network reach

3. **Long Term: Bootstrap Cost**
   - Recovering to medium trust requires 90+ days
   - Cannot use old DID (blacklisted)
   - Must bootstrap new identity (auditor cost ~$5-10k for L2)

**Attacker ROI**: defection costs → payoff break-even point unachievable within realistic timeframe

---

## 8. Trust Revocation Procedures

### 8.1 Revocation Events

A publisher's trust can be revoked (moved to QUARANTINE) when evidence of malice or systematic unreliability emerges.

**Revocation is a serious action** and requires:
- Clear evidence
- Documented justification
- Opportunity for publisher to respond

### 8.2 Automatic Revocation (Machine Triggers)

Revocation occurs **automatically** (without human review) when:

| Trigger | Evidence Required | Recovery Time |
|---------|-------------------|---|
| 3 contradictions in 30 days | H factor drops below 0.4 | 90 days minimum |
| 5 schema failures in 1 week | Q factor shows systematic issues | 30 days  |
| Burst detection 3x in 30 days | Rate limit violations | 14 days |
| Key compromise detection | Signature verification fails on known key | Permanent (key blacklist) |
| Successful Sybil attack proof | Multiple DIDs traced to same operator | Permanent (all variants blacklisted) |

**Automatic Revocation Action**:
1. Publisher moved to QUARANTINE class (trust_score = 0.05)
2. All signals quarantined (not applied automatically)
3. Audit log records trigger + evidence
4. Publisher notified (via DID document contact method, if available)

### 8.3 Manual Revocation (Human Authority)

Node operators MAY manually revoke trust if evidence warrants:

**Examples**:
- Publisher organization dissolves / goes offline indefinitely
- Publisher admits to publishing false information
- External auditor reports systematic integrity issues
- Law enforcement indicates compromise or criminal intent

**Process**:
1. Operator submits revocation request with documented evidence
2. Request logged in audit trail (hash, timestamp, reason)
3. Publisher moved to QUARANTINE
4. Notification sent via DID contact (if possible)
5. Decision visible in node's transparency report

**Appeal Process**:
- Publisher MAY request revocation review within 30 days
- Node operator MUST respond to substantive appeals
- Appeal outcome becomes part of audit trail
- Successful appeal restores original trust_score

### 8.4 Revocation Recovery

Revocations are **not permanent by default**. Publishers may recover trust.

#### 8.4.1 Automatic Recovery Conditions

After revocation, trust recovers if:

**Condition 1**: Revocation cause eliminated
- E.g., compromised key is rotated; new key shows no failures for 30 days
- Time-based: H factor recovers 5% per week of clean events
- Max recovery: back to pre-revocation trust_score after 90 days

**Condition 2**: Third-party re-attestation
- Another L1_AUTHORITY publisher re-endorses publisher
- H factor jumps to 0.80 upon re-attestation
- Skip to L2_ENTERPRISE class immediately

**Condition 3**: Manual operator override
- Operator can restore trust based on new evidence
- Override requires audit trail documentation

#### 8.4.2 Permanent Revocation

Some revocations are permanent:

| Revocation Reason | Permanent? | Reason |
|-------------------|-----------|--------|
| 3 contradictions | No | Can recover in 90+ days |
| Key compromise | Yes | Key is blacklisted; attacker could still have it |
| Sybil attack proven | Yes | Trust in all identities compromised |
| Criminal activity | Maybe | Depends on seriousness; operator decides |

### 8.5 Revocation Transparency

Nodes MUST publish:

1. **Revocation Register**: list of currently revoked DIDs (updated weekly)
2. **Revocation Log**: historic revocations with evidence summaries (append-only)
3. **Recovery Metrics**: statistics on revocation → recovery pipeline

**Format** (minimum):
```json
{
  "revoked_publishers": [
    {
      "did": "did:aegis:mainnet:bad-actor-1",
      "revoked_at": "2026-02-15T12:00:00Z",
      "reason": "3_contradictions_in_30_days",
      "evidence_hash": "sha256:abc...def",
      "eligible_for_recovery_at": "2026-05-15T12:00:00Z",
      "recovery_status": "eligible | blocked | recovered"
    }
  ]
}
```

---

## 9. Reputation Graph Extensions

### 9.1 Optional: Typed Trust Relationships

Nodes MAY maintain fine-grained trust relationships per **event type**:

Instead of single trust_score, compute:

- `trust_score[circumvention_reports]` = 0.85
- `trust_score[policy_updates]` = 0.60
- `trust_score[risk_signals]` = 0.75
- `trust_score[incident_notices]` = 0.40

**Use Case**: Publisher is excellent at threat detection but poor at policy analysis

**Implementation**: duplicate trust score calculation per event type with specialized H factor

### 9.2 Optional: Audit Chain Weighting

Track **transitive endorsements**:

- Node A trusts Node B (trust_score: 0.80)
- Node B trusts Publisher C (trust_score: 0.70)
- Node A infers trust in C ≈ 0.72 (weighted by A-B trust)

**Formula**:

$$
T_{A \to C} = T_{A \to B} \times T_{B \to C}
$$

**Use Case**: larger federations with multi-hop endorsements

**Caveat**: risk of trust propagation loops; require acyclic endorsement graphs

---

## 10. Signal Ingestion and Quarantine

### 10.1 Ingestion Policy by Trust Level[^2]

| Trust Level | Automatic Ingestion? | Corroboration Required? | Human Review? |
|---|---|---|---|
| L0_SYSTEM | Yes | No | No |
| L1_AUTHORITY | Yes | No (recommended) | No |
| L2_ENTERPRISE | Yes | Low-risk events only | No |
| L3_CONTRIBUTOR | Partial | Yes, min 1 peer | Recommended |
| UNCLASSIFIED | No | Yes, min 2 peers | Required |
| QUARANTINE | No | N/A (always rejected) | N/A |

### 10.2 Quarantine Queue

Low-trust signals are placed in **quarantine** (not applied automatically).

**Quarantine Actions**:
1. Signal stored in isolated ledger
2. Operator notified of pending signal
3. Operator can:
   - **APPROVE**: apply signal + increase publisher H factor
   - **REJECT**: discard signal + decrease publisher H factor
   - **IGNORE**: hold for later review

**Metrics** (for operator analytics):
- Approval rate by publisher
- Time from quarantine to resolution
- False positive rate over time

---

## 11. Audit and Compliance

### 11.1 Mandatory Audit Logs

Every trust decision MUST be logged with:

```json
{
  "timestamp": "2026-03-05T14:30:00Z",
  "event_id": "evt-001",
  "publisher_did": "did:aegis:mainnet:org-b",
  "decision": "ACCEPT | REJECT | QUARANTINE",
  "decision_reason": "trust_score=0.75; corroboration_required=false",
  "trust_factors": {
    "baseline_B": 0.70,
    "accuracy_H": 0.90,
    "quality_Q": 0.85,
    "audit_A": 0.65,
    "federation_F": 0.60,
    "computed_trust_score": 0.755
  },
  "event_weight": 0.68,
  "applied_thresholds": {
    "trust_threshold": 0.50,
    "weight_threshold": 0.10
  }
}
```

### 11.2 Compliance Reports

Nodes SHOULD generate quarterly trust audit reports showing:

- Top 20 trusted publishers (by ingestion volume)
- Revocations + recovery statistics
- False positive rate (signals later contradicted)
- Agreement rate with federation (% time decisions align with peer nodes)

---

## 12. Failure Modes and Safe Defaults

### 12.1 Conservative Safe Defaults

Nodes MUST implement safe defaults:

- **Never auto-apply policy updates from UNCLASSIFIED publishers**
- **Never ingest unsigned events** (even from allowlist)
- **Never accept events failing signature verification** (even if from L0_SYSTEM)
- **Never accept duplicate event_id** (even if different signature)
- **Never override operator's local policy decisions** (federation is advisory)
- **Always log trust decisions** (even if later proven wrong)

### 12.2 Subsystem Failures

| Failure | Recovery |
|---------|----------|
| DID resolution service offline | Cached DIDs remain valid; new verifications blocked |
| Signature verification service down | Defer event processing; retry hourly up to 24h |
| Audit storage full | Reject new events; alert operator |
| Clock skew > ±6 hours | Reject all events; check system time |

---

## 13. Relationship to Other Specifications

- **RFC-0001**: AEGIS Architecture and trust boundaries
- **RFC-0004**: Governance Event Model and federation events
- **AEGIS_GFN1_GOVERNANCE_NETWORK.md**: network topology and protocol
- **AEGIS_GFN1_NODE_REFERENCE_ARCHITECTURE.md**: node deployment and trust anchors

---

**Document Status**: Normative\
**Version**: 1.0\
**Next Review**: September 5, 2026

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../REFERENCES.md).

[^2]: F. B. Schneider, "Enforceable Security Policies," *ACM Transactions on Information and System Security*, vol. 3, no. 1, pp. 30–50, Feb. 2000, doi: 10.1145/353323.353382. See [REFERENCES.md](../REFERENCES.md).

[^17]: National Institute of Standards and Technology, *Zero Trust Architecture*, NIST SP 800-207, Aug. 2020. [Online]. Available: https://doi.org/10.6028/NIST.SP.800-207. See [REFERENCES.md](../REFERENCES.md).
