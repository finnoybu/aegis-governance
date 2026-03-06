# Capability Request Schema

Author: Ken Tannenbaum  
Project: AEGIS  
Version: 0.2

## JSON Schema Example

``` json
{
  "actor_id": "agent_123",
  "capability": "filesystem.read",
  "resource": "/data/file.txt",
  "scope": "single_file",
  "context": {
    "environment": "production",
    "request_source": "agent"
  }
}
```

## Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| actor_id | string | Identity of requesting entity | Yes |
| capability | string | Action requested (dot-separated) | Yes |
| resource | string | Target object (URI/path/identifier) | Yes |
| scope | string | Breadth of operation | No |
| context | object | Environmental metadata | No |

## Nested Capabilities

Capabilities use dot-notation hierarchy:

```
filesystem
  └─ read
  └─ write
  └─ delete

network
  └─ http_get
  └─ http_post
  └─ dns_query

data
  └─ database_query
  └─ api_call
  └─ cache_access

compute
  └─ process_spawn
  └─ memory_allocate
  └─ cpu_bind
```

## Common Capability Types

### Filesystem Operations

```json
{
  "actor_id": "agent_456",
  "capability": "filesystem.write",
  "resource": "/data/output.log",
  "scope": "append_only",
  "context": {"max_size_mb": 100}
}
```

### Network Operations

```json
{
  "actor_id": "agent_789",
  "capability": "network.http_post",
  "resource": "https://api.example.com/webhook",
  "context": {"max_payload_bytes": 10000}
}
```

### Data Access

```json
{
  "actor_id": "agent_101",
  "capability": "data.database_query",
  "resource": "production_db.users",
  "scope": "select_only",
  "context": {"max_rows": 1000}
}
```

### API Calls

```json
{
  "actor_id": "agent_202",
  "capability": "data.api_call",
  "resource": "https://service.internal/lookup",
  "context": {"rate_limit": "10/sec"}
}
```

### Process Management

```json
{
  "actor_id": "agent_303",
  "capability": "compute.process_spawn",
  "resource": "python",
  "scope": "subprocess",
  "context": {"memory_limit_mb": 512}
}
```

## Scope Values

| Scope | Meaning |
|-------|----------|
| single_file | Single file only |
| directory | Entire directory tree |
| append_only | Add records, no modifications |
| select_only | Read queries only |
| subprocess | Child process only |
| read_only | No write permissions |

## Context Metadata

Optional contextual constraints:

```json
{
  "environment": "production|staging|development",
  "request_source": "agent|scheduler|api",
  "max_size_mb": 100,
  "max_rows": 1000,
  "max_payload_bytes": 10000,
  "rate_limit": "10/sec",
  "memory_limit_mb": 512,
  "timeout_seconds": 30
}
```
