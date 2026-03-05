# AEGIS Threat Model

## Threat Categories

1. Prompt Injection
2. Privilege Escalation
3. Data Exfiltration
4. Autonomous System Damage
5. Governance Bypass

## Core Mitigation Strategy

AEGIS separates reasoning from execution.

AI → Governance Layer → Tool Proxy → Infrastructure

Even if an AI model produces unsafe instructions, the governance layer blocks execution unless policies permit the action.
