# Security Policy

## Reporting Security Vulnerabilities

The AEGIS™ project takes security seriously. We appreciate your efforts to responsibly disclose security concerns.

### Scope

This security policy covers all repositories in the [aegis-initiative](https://github.com/aegis-initiative) organization, including:

- **Specifications and RFCs** — Design flaws or security issues in the architecture
- **Reference implementations** — Vulnerabilities in runtime code or examples
- **Governance protocols** — Issues with AGP message handling or validation
- **Schema definitions** — Validation bypasses or injection vulnerabilities
- **Infrastructure** — CI/CD, deployment, and operational security concerns

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, use one of the following methods:

1. **GitHub Private Vulnerability Reporting:** Use the "Report a security vulnerability" link in the relevant repository's Issues tab
2. **Email:** Contact the project maintainer through GitHub with "SECURITY" in the subject line

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested remediation (if available)
- Your contact information for follow-up

### Response Timeline

We aim to respond to security reports within:

- **Initial acknowledgment:** 48 hours
- **Impact assessment:** 5 business days
- **Remediation plan:** 10 business days for critical issues

### Disclosure Policy

We follow a coordinated disclosure model:

1. Security issue is reported privately
2. Maintainers investigate and develop a fix
3. Fix is released and tested
4. Public disclosure occurs after fix is available

We request that you:

- Allow reasonable time for remediation before public disclosure
- Act in good faith to avoid privacy violations or service disruption
- Do not exploit the vulnerability beyond what is necessary for demonstration

---

## Security Best Practices

### For Specification Contributors

When proposing changes to AEGIS™ specifications:

- Consider adversarial scenarios and bypass attempts
- Document security implications in RFC proposals
- Evaluate impact on deterministic enforcement guarantees
- Review threat model alignment

### For Implementation Developers

When building AEGIS™-compliant systems:

- Validate all protocol messages according to schemas
- Implement proper authentication and authorization
- Use secure defaults (default-deny policies)
- Follow principle of least privilege for capabilities
- Enable comprehensive audit logging
- Test failure modes and error handling
- Review third-party dependencies regularly

---

## Known Security Considerations

### Governance Boundary Enforcement

AEGIS™ enforces governance at the **action proposal layer**. It does not:

- Control what AI models generate as text or reasoning
- Prevent social engineering or phishing attempts
- Secure the underlying infrastructure or runtime environment
- Guarantee safety of approved actions (only that they passed policy evaluation)

### Audit Log Integrity

The audit system provides append-only logging but relies on:

- Secure storage of the audit database
- Access control to prevent unauthorized reads
- Backup and retention policies defined by operators

### Federation Trust Model

The Governance Federation Network relies on:

- DID-based identity verification
- Cryptographic signature validation
- Trust decisions by node operators

Review the [Federation Trust Model](federation/AEGIS_GFN1_TRUST_MODEL.md) for details.

---

## Security Updates

Security updates will be published through:

- GitHub Security Advisories
- Release notes with `[SECURITY]` prefix
- Updates to relevant RFC specifications

---

**Thank you for helping keep AEGIS™ secure.**

---

*AEGIS™ and "Capability without constraint is not intelligence™" are trademarks of Finnoybu IP LLC.*
