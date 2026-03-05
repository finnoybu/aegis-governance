---
name: Capability Registry Schema
about: Define the standardized schema for capability definitions
title: 'Capability Registry Schema Specification'
labels: ['rfc', 'specification', 'capability-registry']
assignees: ''
---

## Overview

Define the standardized schema for capability definitions in the AEGIS Capability Registry.

## Scope

This issue tracks the design of:

- [ ] Capability definition schema (YAML/JSON format)
- [ ] Required and optional fields
- [ ] Capability taxonomy and naming conventions
- [ ] Constraint types and validation rules
- [ ] Risk classification methodology
- [ ] Registry storage and versioning

## Related Specifications

- RFC-003: Capability Registry & Policy Language

## Schema Requirements

A capability definition should include:
- Unique identifier (e.g., `telemetry.query`)
- Human-readable description
- Allowed roles/actors
- Environment scope (production, staging, etc.)
- Risk level classification
- Optional constraints (rate limits, parameter validation, etc.)
- Approval requirements

## Discussion Points

1. Should capability schemas support inheritance or composition?
2. How should we handle capability versioning and deprecation?
3. Should capabilities be statically defined or support dynamic registration?
4. What constraint types should be supported? (time-based, rate-limit, parameter validation, etc.)

## Deliverables

- [ ] JSON Schema or YAML schema definition
- [ ] Example capability definitions
- [ ] Validation tooling specification
- [ ] Registry management API design
- [ ] Migration and versioning strategy

## Additional Context

The capability registry is the authoritative source for what AI systems may do within a governed environment. The schema must balance expressiveness with simplicity.
