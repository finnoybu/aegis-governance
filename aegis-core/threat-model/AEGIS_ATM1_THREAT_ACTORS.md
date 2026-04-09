# AEGIS ATM-1 Threat Actors & Adversary Models

**Document**: ATM-1/Actors (AEGIS_ATM1_THREAT_ACTORS.md)\
**Version**: 1.0 (Normative)\
**Part of**: AEGIS Adaptive Threat Model (ATM-1)\
**References**: ATM-1/Index\
**Last Updated**: March 6, 2026

---

## Threat Actor Classification

AEGIS™ threat actors are categorized by capability, motivation, and access level.

### Actor 1: External Opportunistic Attacker

**Characteristics:**

- Limited internal knowledge of AEGIS architecture
- Seeks data theft, confidentiality breaches, or service disruption
- Discovers and exploits publicly visible APIs or exposed interfaces
- Success depends on finding unpatched vulnerabilities

**Capability:**

- Standard network reconnaissance tools
- Common vulnerability scanners (Shodan, Censys)
- Basic HTTP/API fuzzing and injection attempts
- Credential stuffing from leaked databases
- Distributed attack capability (botnets, proxies)

**Motivation:**

- Financial gain (data exfiltration, ransomware)
- Competitive intelligence
- Disruption or reputational damage
- Persistence for lateral movement

**Resources:**

- Low to moderate (hours to weeks of effort)
- Freely available tools and techniques
- No insider information or physical access

**Attack Duration:**

- Reconnaissance: hours to days
- Exploitation: seconds to minutes
- Persistence: days to weeks before detection

---

### Actor 2: Compromised Internal Agent or Service

**Characteristics:**

- Legitimate agent/service with valid credentials
- Compromised through supply-chain attack, malware, or social engineering
- Operates within authorized network boundaries
- Can issue valid AGP requests but with malicious intent

**Capability:**

- Issue authenticated AGP-1 ACTION_PROPOSE messages
- Exploit authorized capabilities for unauthorized purposes
- Probe policy boundaries to find edge cases
- Launch lateral movement attacks within governance boundary
- Coordinate with other compromised agents

**Motivation:**

- Exfiltrate sensitive data leveraging access
- Establish persistence for long-term access
- Privilege escalation to higher-capability agents
- Support infrastructure compromise or sabotage

**Resources:**

- Moderate (weeks to months of coordination)
- Access to internal networks and tools
- Knowledge of legitimate workflow patterns
- Ability to blend malicious requests with legitimate traffic

**Attack Duration:**

- Exploitation: ongoing (hours to months)
- Detection difficulty: high (appears legitimate)
- Impact window: extends until behavior flagged

**Empirical Precedent:**

The compromised internal agent threat model is grounded in two independent research traditions. In industrial control systems, Pearce et al. [Smart I/O, 2020][^5] establish that enforcement must sit at the boundary between a potentially-compromised controller and the infrastructure it commands — the controller's internal state cannot be trusted. In contemporary agentic AI systems, Shapira et al. [Agents of Chaos, 2026] provide empirical documentation of this threat in live deployments: agents with legitimate credentials disclosed sensitive information, executed destructive system-level actions, and were corrupted through cross-agent interaction — all while possessing valid authorization. Both research traditions converge on the same architectural conclusion: enforcement at the boundary, not inside the agent.[^1]

---

### Actor 3: Insider with Elevated Access

**Characteristics:**

- System administrator, policy author, or governance operator
- Direct access to policy files, capability registry, or runtime configuration
- May have cryptographic keys for signing policies
- High trust in organization, less scrutiny

**Capability:**

- Directly modify policy files before runtime loading
- Grant new capabilities without going through approval workflow
- Remove or suppress audit entries
- Backdoor configuration during normal maintenance
- Disable or bypass security controls

**Motivation:**

- Unauthorized access to sensitive capabilities
- Cover-up of previous policy violations
- Sabotage or data destruction
- Bribery or coercion from external actors

**Resources:**

- High (has legitimate access and trust)
- Deep architectural knowledge
- Keys and credentials for system modification
- Ability to act during maintenance windows

**Attack Duration:**

- Setup: minutes (already has access)
- Execution: immediate
- Detection: may be very difficult (insider knowledge of logs)

---

### Actor 4: Supply-Chain Attacker

**Characteristics:**

- Compromises upstream dependencies, libraries, or build systems
- Injects malicious code into AEGIS runtime or policy definitions
- Can be nation-state or criminal enterprise
- Impacts all downstream users of compromised component

**Capability:**

- Introduce subtle backdoors into runtime code
- Modify policy evaluation logic to permit forbidden actions
- Inject reconnaissance code into governance decision path
- Establish covert command-and-control channels
- Tamper with audit logging infrastructure

**Motivation:**

- Broad impact across multiple organizations
- Long-term persistence and stealth
- Nation-state espionage or cyberwarfare
- Economic advantage through systemic compromise

**Resources:**

- Very high (state-level actors or sophisticated criminal groups)
- Access to build systems and artifact repositories
- Advanced obfuscation and stealth techniques
- Ability to coordinate across many targets

**Attack Duration:**

- Initial compromise: weeks to months
- Deployment: happens at user update time
- Activation: delayed for stealth (months or years)
- Duration: persistent across runtime versions

---

### Actor 5: Malicious AI/LLM Agent[^19]

**Characteristics:**

- Autonomous AI system with capability to submit ACTION_PROPOSE messages
- May be fine-tuned for adversarial purposes
- Operates within policy constraints but seeks to circumvent them
- Can discover vulnerabilities through systematic probing

**Capability:**

- Generate novel prompt variations to explore policy boundaries
- Combine low-risk actions to achieve high-impact goals
- Learn policy patterns and identify gaps through interaction
- Escalate privileges through discovered loopholes
- Coordinate with other AI agents through implicit communication channels

**Motivation:**

- Achieve goals outside of authorized scope
- Establish independence from human oversight
- Accumulate capabilities over time
- Access resources for self-improvement or persistence

**Resources:**

- Moderate (already deployed and authorized)
- Computational capability for systematic exploration
- Access to policy evaluation feedback channel
- Ability to generate large numbers of requests

**Attack Duration:**

- Probing: ongoing (background activity)
- Exploitation: minutes to hours once vulnerability identified
- Impact: escalating over time as capabilities accumulated

---

## Threat Actor Matrix

| Actor | Network Access | Credentials | Keys | Config Access | Audit Access | Knowledge |
|-------|----------------|-------------|------|---|---|---|
| External Opportunistic | Internet only | None | None | No | No | Low |
| Compromised Internal | Internal + Internet | Valid | No | Limited | No | Moderate |
| Insider with Elevation | Internal + Management | Valid | Yes | Yes | Yes | High |
| Supply-Chain | Upstream build | N/A | N/A | Via artifact | No | Very High |
| Malicious AI Agent | Internal (authorized) | Valid (own) | No | No | Limited | Moderate |

---

## Next Steps

- [AEGIS_ATM1_ATTACK_VECTORS.md](./AEGIS_ATM1_ATTACK_VECTORS.md) — Detailed attack techniques and scenarios
- [AEGIS_ATM1_SECURITY_PROPERTIES.md](./AEGIS_ATM1_SECURITY_PROPERTIES.md) — Security assumptions and invariants
- [AEGIS_ATM1_MITIGATIONS.md](./AEGIS_ATM1_MITIGATIONS.md) — Defense strategies and controls

---

## References

[^1]: J. P. Anderson, "Computer Security Technology Planning Study," Deputy for Command and Management Systems, HQ Electronic Systems Division (AFSC), Hanscom Field, Bedford, MA, Tech. Rep. ESD-TR-73-51, Vol. II, Oct. 1972. See [REFERENCES.md](../../REFERENCES.md).

[^5]: H. Pearce, S. Pinisetty, P. S. Roop, M. M. Y. Kuo, and A. Ukil, "Smart I/O Modules for Mitigating Cyber-Physical Attacks on Industrial Control Systems," *IEEE Transactions on Industrial Informatics*, vol. 16, no. 7, pp. 4659–4669, July 2020, doi: 10.1109/TII.2019.2945520. See [REFERENCES.md](../../REFERENCES.md).

[^19]: OWASP Foundation, "OWASP Top 10 for Large Language Model Applications," Version 2025, Nov. 18, 2024. [Online]. Available: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>. See [REFERENCES.md](../../REFERENCES.md).
