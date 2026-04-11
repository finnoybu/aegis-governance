<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="../../aegis-core/assets/AEGIS_wordmark_dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="../../aegis-core/assets/AEGIS_wordmark_light.svg">
    <img src="../../aegis-core/assets/AEGIS_wordmark.svg" width="90" alt="AEGIS Governance Logo">
  </picture>
</p>

# AEGIS Schema Pack

> **Note:** The canonical editable schemas live in
> [`aegis/schemas/`](https://github.com/aegis-initiative/aegis/tree/main/schemas).
> This directory is a **public mirror** with additional examples for documentation
> purposes. Do not edit schema files here directly — changes should be made in
> `aegis/schemas/` and synced to this directory. The `aiam/` schemas and
> `examples/` directory are governance-specific additions that have not yet been
> promoted upstream.

This directory contains machine-validated schema definitions for AEGIS protocol and governance artifacts.

## Mirror Sync

Shared schema domains in this directory are synchronized from the canonical editable source in `../aegis/schemas/`
using:

```bash
python scripts/sync-canonical-schemas.py
```

To check whether the mirror is out of sync without modifying files:

```bash
python scripts/sync-canonical-schemas.py --check
```

The mirror script updates only:

- `agp/`
- `capability/`
- `common/`
- `governance/`

It intentionally does not modify:

- `aiam/`
- `examples/`

## Structure

- `common/` reusable schema primitives
- `agp/` AGP protocol message schemas
- `capability/` capability registry schemas
- `governance/` governance envelope and event schemas
- `examples/` sample payloads validated in CI

## Examples

All schemas include validated example files demonstrating proper document structure:

### AGP Examples (`examples/agp/`)

- `action_propose.example.json` - Simple ACTION_PROPOSE message
- `action_propose.complex.example.json` - Complex ACTION_PROPOSE with nested parameters, filters, and enrichment
- `decision_response.example.json` - Governance decision response
- `escalation_request.example.json` - Request for human review
- `execution_result.example.json` - Action execution outcome

### Governance Event Examples (`examples/governance/`)

- `policy_update.example.json` - Policy update event
- `circumvention_report.example.json` - Security circumvention technique report
- `governance_envelope_signed.example.json` - Full signed governance event demonstrating envelope structure with cryptographic signature

## Validation

CI validates schemas with `ajv-cli` and checks that examples conform to their corresponding schemas.

### Example Validation

All example files MUST:

- ✅ Conform to their corresponding schema
- ✅ Include all required fields
- ✅ Use realistic data values
- ✅ Demonstrate actual use cases

Run validation:

```bash
ajv -s agp/action_propose.schema.json -d examples/agp/action_propose.*.example.json
ajv -s governance/governance_event_envelope.schema.json -d examples/governance/*.example.json
```
