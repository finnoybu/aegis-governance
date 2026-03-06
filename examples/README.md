<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../aegis-core/assets/AEGIS_wordmark.svg" width="90" alt="AEGIS™ Governance Logo">
  </picture>
</p>

# AEGIS™ Examples

This directory contains example integrations demonstrating how AI systems interact with the AEGIS™ governance runtime.

**Examples show:**
- How to initialize and configure the AEGIS runtime
- How AI systems propose actions
- How AEGIS evaluates and controls those actions
- Policy-driven decision flows
- Real-world integration scenarios

> **Getting started?** Start with [Hello AEGIS](runtime/hello_aegis.py) for a minimal example.

---

## Examples by Category

### `runtime/` — Reference Runtime Examples (2 files)

Basic examples using the AEGIS reference implementation.

#### [Hello AEGIS](runtime/hello_aegis.py)
**Minimal example** showing:
- ✅ Initialize AEGIS runtime
- ✅ Create a simple capability
- ✅ Propose and evaluate an action
- ✅ Handle governance decisions

**Start here if:** You're new to AEGIS and want to understand the basic flow.

**Key concepts:** Capabilities, actions, governance decisions, policies.

#### [Basic Runtime Demo](runtime/basic_runtime_demo.py)
**More comprehensive demo** showing:
- ✅ Configuration and setup
- ✅ Multiple capability types
- ✅ Risk scoring in decisions
- ✅ Policy evaluation examples
- ✅ Multi-step workflows

**Read this after:** You understand the basic flow and want to see more realistic scenarios.

**Key concepts:** Policy engine, risk scoring, decision making, capability registry.

---

### `soc-agent-integration/` — Security Operations (Coming Soon)

Real Security Operations Center (SOC) agent investigation workflow examples.

**Expected examples:**
- Security incident investigation workflows
- Automated threat response actions
- Investigation capability governance
- Cross-system coordination with AEGIS

**Status:** 🚧 In development  
**Expected:** Post-announcement community contributions  
**Contribute:** Create an issue with the `roadmap` and `implementation` labels

---

### `cloud-automation-agent/` — Infrastructure Automation (Coming Soon)

Cloud and infrastructure automation examples demonstrating AEGIS governance of infrastructure changes.

**Expected examples:**
- Infrastructure provisioning workflows
- Configuration management actions
- Multi-cloud automation scenarios
- Change approval governance

**Status:** 🚧 In development  
**Expected:** Post-announcement community contributions  
**Contribute:** Create an issue with the `roadmap` and `implementation` labels

---

## Quick Start

### 1. Run Hello AEGIS
```bash
cd runtime
python hello_aegis.py
```
This will demonstrate the basic AEGIS flow in ~50 lines of code.

### 2. Explore the Reference Runtime
See [`../aegis-runtime/`](../aegis-runtime/) for:
- Complete runtime API documentation
- Configuration options
- Advanced features

### 3. Review Specifications
For deeper understanding:
- [AGP-1 Protocol Specification](../aegis-core/protocol/AEGIS_AGP1_INDEX.md)
- [Capability Model](../docs/architecture/CAPABILITY_MODEL.md)
- [Governance Engine Components](../docs/architecture/GOVERNANCE_ENGINE_COMPONENTS.md)

---

## Integration Patterns

### For AI Framework Integration

**Python/LangChain Integration:**
```python
from aegis_runtime import GovernanceGateway

gateway = GovernanceGateway(config)
action = gateway.propose_action(capability, parameters)
decision = gateway.evaluate(action)  # Enforces governance
```

**OpenAI Function Calling:**
Use AEGIS as a tool proxy between the AI and system APIs.

**Custom LLM Integration:**
Wrap tool calls with AEGIS governance decisions.

### For Infrastructure Automation

**Terraform Provider Integration:**
Use AEGIS to gate Terraform apply operations.

**Kubernetes Operator Integration:**
Use AEGIS to gate custom resource deployments.

**Cloud API Proxy:**
Route API calls through AEGIS governance.

---

## Contributing Examples

We welcome community-contributed examples!

**To contribute an example:**
1. Create a new subdirectory in `examples/` (or extend an existing one)
2. Add a `README.md` with:
   - What the example demonstrates
   - Prerequisites and setup
   - How to run it
   - Key concepts it illustrates
3. Include fully commented code
4. Open a pull request with the `implementation` and `examples` labels

**Good examples should:**
- Demonstrate a realistic use case
- Be well-commented and self-contained
- Include error handling and edge cases
- Show both success and rejection scenarios
- Reference relevant specifications

See [`../CONTRIBUTING.md`](../CONTRIBUTING.md) for full guidelines.

---

## Example Matrix

| Example | Demonstrates | Skill Level | Time |
|---------|--------------|-------------|------|
| Hello AEGIS | Basic flow | Beginner | 5 min |
| Basic Runtime Demo | Multiple capabilities | Intermediate | 15 min |
| SOC Agent Integration | Real-world security ops | Advanced | 30 min |
| Cloud Automation Agent | Infrastructure governance | Advanced | 30 min |

---

## Related Resources

**Documentation:**
- [AEGIS Architecture Overview](../docs/architecture/AEGIS_ARCHITECTURE_OVERVIEW.md)
- [End-to-End Request Flow](../docs/architecture/END_TO_END_REQUEST_FLOW.md)
- [Policy Language](../docs/architecture/POLICY_LANGUAGE.md)

**Specifications:**
- [AGP-1 Protocol](../aegis-core/protocol/AEGIS_AGP1_INDEX.md)
- [Capability Schema](../aegis-core/schemas/capability/)
- [Policy Schema](../aegis-core/schemas/policy/)

**Runtime:**
- [Reference Runtime](../aegis-runtime/)
- [Runtime API](../aegis-runtime/README.md)

---

## License & Trademark

- **Copyright**: © 2025 Kenneth Tannenbaum. All rights reserved.
- **License**: See [`../LICENSE`](../LICENSE)
- **Trademark**: AEGIS™ is a trademark of Kenneth Tannenbaum. See [`../TRADEMARKS.md`](../TRADEMARKS.md)

---

**Navigation**: [← Back to Repository Root](../README.md) | [→ Runtime Documentation](../aegis-runtime/README.md) | [→ Specifications](../aegis-core/README.md)
