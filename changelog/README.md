# Changelog

All notable changes to the AEGIS™ project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

See [INDEX.md](INDEX.md) for a complete list of entries.

---

## Conventions

### File Naming

All changelog entries use the `YYYY-MM-DD-<topic>.md` convention regardless of whether the entry is a version release or a milestone:

```
changelog/
  2026-03-05-v0.1.0-architecture-foundation.md
  2026-03-07-nist-submission.md
  2026-03-13-repository-as-living-paper.md
```

### Entry Types

| Type | Description |
|------|-------------|
| **Version release** | Tagged semver release (e.g., v0.1.0). Topic includes version number. |
| **Milestone** | Significant strategic or architectural decision. |
| **Submission** | External submission (NIST, IEEE, standards bodies). |
| **Patch** | Bug fixes, corrections, minor improvements. |

### Entry Structure

Each file contains:
- Title and date
- Type and status
- Summary (1–3 sentences)
- `### Added`, `### Changed`, `### Fixed`, `### Security` sections as applicable

### Adding a New Entry

1. Create `changelog/YYYY-MM-DD-<topic>.md`
2. Add a row to `changelog/INDEX.md`
3. Update root `CHANGELOG.md` pointer if needed

---

**Part of**: AEGIS™ Documentation\
**Maintained by**: AEGIS™ Initiative
