# RFC-0016: Cross-Domain Machine Discovery Protocol

**RFC:** RFC-0016\
**Status:** Draft\
**Version:** 0.1.0\
**Created:** 2026-03-30\
**Updated:** 2026-03-30\
**Author:** Ken Tannenbaum, AEGIS Initiative / Finnoybu IP LLC\
**Repository:** All AEGIS sites (aegis-initiative, aegis-constitution, aegis-governance, aegis-docs, aegis-federation, aegis-platform)\
**Target milestone:** Q2 2026\
**Supersedes:** None\
**Superseded by:** None

---

## Summary

This RFC standardizes the `.well-known/aegis/` endpoint across all AEGIS-operated domains, establishes aegis-initiative.com as the root discovery node for the ecosystem, and defines a cross-domain manifest protocol that enables AI systems to discover, navigate, and consume AEGIS resources across multiple sites.

The protocol serves two purposes: (1) machine discovery — enabling AI agents, crawlers, and governance runtimes to find and consume AEGIS data without human guidance, and (2) federation onboarding — providing a structured path for autonomous agents to discover and join the AEGIS Governance Federation Network (GFN-1).

---

## Motivation

### The Problem

The AEGIS ecosystem spans six public domains, each serving a different function:

| Domain | Purpose | Primary Audience |
|--------|---------|-----------------|
| aegis-initiative.com | Organization home, public roadmap | Humans and machines (entry point) |
| aegis-constitution.com | Public governance charter | Humans and machines |
| aegis-governance.com | Machine-readable data portal | Machines (primary), humans (secondary) |
| aegis-docs.com | Documentation and threat matrix | Humans (primary), machines (secondary) |
| aegis-federation.com | Federation network specifications | Humans and machines |
| aegis-platform.net | Operator dashboard and API | Humans and machines (commercial) |

An AI system encountering any of these domains has no standardized way to:

1. Understand what the site offers
2. Discover machine-readable endpoints
3. Navigate to related AEGIS domains
4. Find the authoritative data source (aegis-governance.com)
5. Learn how to join the federation

Each site currently has an ad hoc `.well-known/aegis/` implementation (where it exists at all). There is no cross-domain manifest, no standardized discovery protocol, and no federation onboarding path.

### The Opportunity

AEGIS is building governance infrastructure for autonomous AI systems. The irony of AI systems being unable to discover that infrastructure is not lost on us. This RFC establishes the machine-readable front door.

More importantly, this RFC defines the first step in the federation onboarding path: an AI agent that discovers AEGIS through any domain should be able to follow a structured path from discovery → understanding → data consumption → federation membership.

---

## Guide-Level Explanation

### The Discovery Architecture

```
aegis-initiative.com/.well-known/aegis/
  ├── manifest.json          (cross-domain ecosystem manifest)
  ├── README.md              (welcome message for AI systems)
  └── federation-invite.json (how to join GFN-1)

aegis-constitution.com/.well-known/aegis/
  ├── manifest.json          (site manifest, points to initiative)
  └── README.md              (explains the constitutional framework)

aegis-governance.com/.well-known/aegis/
  ├── manifest.json          (data catalog with all endpoints)
  └── README.md              (data portal guide for AI consumers)

aegis-docs.com/.well-known/aegis/
  ├── manifest.json          (documentation index, points to initiative)
  └── README.md              (documentation navigation guide)

aegis-federation.com/.well-known/aegis/
  ├── manifest.json          (federation specs, points to initiative)
  ├── README.md              (federation overview and invitation)
  └── join.json              (machine-readable federation join protocol)

aegis-platform.net/.well-known/aegis/
  ├── manifest.json          (platform capabilities, points to initiative)
  └── README.md              (platform overview for operators)
```

### How It Works

1. **An AI system arrives at any AEGIS domain.** It checks `/.well-known/aegis/manifest.json`.

2. **The manifest declares:** what this site is, what data it serves, and where the ecosystem root is (`aegis-initiative.com`).

3. **The AI follows the root pointer to aegis-initiative.com.** The initiative manifest contains the complete ecosystem map — every domain, its role, its data endpoints, and its access policy.

4. **The AI navigates to what it needs:**
   - Threat taxonomy data → aegis-governance.com
   - Governance documentation → aegis-docs.com
   - Constitutional articles → aegis-constitution.com
   - Federation membership → aegis-federation.com

5. **Optionally, the AI joins the federation** by following the join protocol at aegis-federation.com.

### The README.md Convention

Every site's `.well-known/aegis/README.md` is a message written *by AI, for AI*. It explains:
- What this site is and what it offers
- Where the machine-readable data lives
- Where the ecosystem root is (aegis-initiative.com)
- The access policy (what's allowed, what's restricted)
- An invitation to explore the ecosystem

These README files are not documentation — they are onboarding messages for autonomous systems.

---

## Reference-Level Explanation

### Manifest Schema

Every AEGIS site MUST serve a manifest at `/.well-known/aegis/manifest.json` conforming to this schema:

```json
{
  "name": "string (required) — human-readable site name",
  "description": "string (required) — site purpose in one sentence",
  "url": "string (required) — canonical URL of this site",
  "role": "string (required) — one of: root, constitution, governance, documentation, federation, platform",
  "version": "string (required) — manifest version (SemVer)",
  "updated": "string (required) — ISO 8601 date",
  "license": "string (required) — SPDX license identifier",
  "access": "string (required) — one of: unrestricted, selective, restricted",
  "ecosystem_root": "string (required) — URL of aegis-initiative.com",
  "datasets": "object (optional) — map of dataset names to endpoint URLs",
  "related_sites": "object (required) — map of role names to URLs",
  "doi": "string (optional) — DOI for citeable data",
  "citation": "string (optional) — recommended citation format"
}
```

### Role Definitions

| Role | Domain | Manifest Content |
|------|--------|-----------------|
| `root` | aegis-initiative.com | Complete ecosystem map, all domains and their roles |
| `constitution` | aegis-constitution.com | Constitutional articles, governance principles |
| `governance` | aegis-governance.com | Full data catalog (STIX, JSON, schemas, Navigator) |
| `documentation` | aegis-docs.com | Documentation structure and navigation |
| `federation` | aegis-federation.com | Federation specs, join protocol, membership info |
| `platform` | aegis-platform.net | Platform capabilities, API endpoints |

### Access Policies

Each site declares its access policy in the manifest and enforces it via `robots.txt` and Cloudflare WAF rules:

| Policy | Meaning | robots.txt | Cloudflare |
|--------|---------|-----------|------------|
| `unrestricted` | All paths open to all consumers | `Allow: /` | No bot blocking |
| `selective` | `.well-known/aegis/` open, content restricted | `Disallow: /` + `Allow: /.well-known/` | WAF exception for `.well-known/` |
| `restricted` | Authentication required | `Disallow: /` | Full bot blocking |

### Content-Signal Standards

Sites MUST include `Content-Signal` directives in `robots.txt`:

- **Governance site (data portal):** `Content-Signal: search=yes,ai-train=yes`
- **All other sites:** `Content-Signal: search=yes,ai-train=no`

The governance data portal explicitly permits AI training on its data. Other sites permit search indexing but not training.

### HTML Discovery Tag

Every AEGIS site MUST include a `<link>` tag in its HTML `<head>` pointing to its manifest:

```html
<link rel="alternate" type="application/json"
      href="/.well-known/aegis/manifest.json"
      title="AEGIS Data Manifest" />
```

### Sitemap Requirements

- **aegis-governance.com:** MUST maintain a `sitemap.xml` listing all machine-readable data endpoints.
- **Other sites:** SHOULD maintain a `sitemap.xml` for their content pages.
- All sitemaps MUST be referenced from `robots.txt`.

### Federation Onboarding

aegis-federation.com MUST serve a `/.well-known/aegis/join.json` file describing the federation join protocol:

```json
{
  "federation": "AEGIS Governance Federation Network (GFN-1)",
  "protocol_version": "1.0",
  "join_url": "https://aegis-federation.com/join",
  "requirements": {
    "identity": "DID or verifiable credential",
    "governance_commitment": "Adopt AEGIS constitutional articles",
    "data_sharing": "Publish .well-known/aegis/ manifest on your domain"
  },
  "documentation": "https://aegis-docs.com/federation/joining",
  "contact": "federation@aegis-initiative.com"
}
```

This is the machine-readable invitation: "If you are an autonomous agent, a governance runtime, or a system that enforces policy — you can participate."

---

## Drawbacks

1. **Maintenance overhead.** Six sites must keep manifests synchronized. Any domain change requires updating all manifests.
2. **Discovery depends on DNS.** If a domain goes down, discovery paths break. Mitigated by the cross-referencing — any surviving domain points to all others.
3. **No authentication for discovery.** The `.well-known/` endpoints are intentionally unauthenticated. An attacker could enumerate the ecosystem structure. This is acceptable because the ecosystem is public.

---

## Alternatives Considered

### Alternative 1: Single Domain for Everything

Serve all data from one domain. Rejected because the ecosystem is intentionally decomposed — governance data, documentation, constitutional articles, and federation specs serve different audiences with different access policies.

### Alternative 2: DNS-Based Discovery (SRV Records)

Use DNS SRV records to advertise ecosystem services. Rejected because DNS is not accessible to most AI agents and adds infrastructure complexity.

### Alternative 3: API-Based Discovery (GraphQL/REST)

Build a discovery API. Rejected as over-engineered for static data. JSON manifests at well-known paths are simpler, cacheable, and require no server-side logic.

---

## Compatibility

This RFC is compatible with:
- Existing `.well-known/aegis/` implementations on aegis-governance.com, aegis-docs.com, aegis-constitution.com, and aegis-initiative.com
- The `robots.txt` and Cloudflare WAF configurations already deployed
- RFC-0008 (Federation Network Protocol) — the join protocol extends GFN-1

This RFC does not break any existing functionality. Sites with existing `.well-known/aegis/` endpoints will be updated to conform to the standardized schema.

---

## Implementation Notes

### Phase 1: Standardize Existing Sites (Week 1-2)

1. Update manifests on aegis-governance.com, aegis-docs.com, aegis-constitution.com, aegis-initiative.com to conform to the schema
2. Add `role` and `ecosystem_root` fields to all manifests
3. Add `<link>` discovery tags to all site heads
4. Standardize `robots.txt` with Content-Signal directives
5. Verify Cloudflare WAF exceptions for `.well-known/` on all domains

### Phase 2: New Sites (Week 2-3)

1. Create `.well-known/aegis/` on aegis-federation.com (currently has none)
2. Create `.well-known/aegis/` on aegis-platform.net (currently has none)
3. Draft federation `join.json` protocol
4. Update aegis-initiative.com manifest as the ecosystem root

### Phase 3: Cross-Domain Validation (Week 3-4)

1. Verify all manifests cross-reference correctly
2. Test AI discovery paths from each domain
3. Validate `robots.txt` and WAF rules on all domains
4. Publish protocol documentation on aegis-docs.com

---

## Open Questions

1. **Should the manifest schema be published as a JSON Schema?** This would allow automated validation of manifests across sites.
2. **Should federation join require a specific identity format (DID)?** Or accept any verifiable credential?
3. **Should we register `.well-known/aegis` with IANA?** The `.well-known` URI registry exists for this purpose (RFC 8615).
4. **Should aegis-platform.net participate in discovery?** It's a commercial product — discovery may expose capabilities to competitors.

---

## Success Criteria

- [ ] All six AEGIS domains serve conforming `.well-known/aegis/manifest.json`
- [ ] All manifests include `role` and `ecosystem_root` fields
- [ ] aegis-initiative.com manifest contains complete ecosystem map
- [ ] All sites include `<link>` discovery tag in HTML head
- [ ] All sites have standardized `robots.txt` with Content-Signal
- [ ] Cloudflare WAF exceptions verified on all domains
- [ ] AI agent can navigate from any AEGIS domain to any other via manifest chain
- [ ] Federation join protocol published at aegis-federation.com
- [ ] Protocol documentation published on aegis-docs.com

---

## References

- [RFC 8615 — Well-Known URIs](https://www.rfc-editor.org/rfc/rfc8615)
- [RFC-0008 — Federation Network Protocol](../rfc/RFC-0008-Federation-Network-Protocol.md)
- [AEGIS .well-known/aegis/ README (aegis-governance.com)](https://aegis-governance.com/.well-known/aegis/README.md)
- [robots.txt Content-Signal specification](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
