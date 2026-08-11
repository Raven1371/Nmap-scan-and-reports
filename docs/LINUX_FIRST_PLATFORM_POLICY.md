# Linux-First Platform Policy

## Platform status

Primary validated Ubuntu baseline:

- Ubuntu 26.04 LTS x86-64

Not part of the current validated Ubuntu release baseline:

- Ubuntu 24.04

Separate platform milestones:

- Rocky Linux / RHEL-compatible x86-64 completion
- Windows 11 x64

Windows validation, packaging, and application integration are deferred
to a later dedicated development phase.

The Linux-first development strategy must not be represented as validated
Windows support or as a fully cross-platform production release.

Rocky and Windows work does not block Ubuntu completion. Existing platform
compatibility code, documentation, tests, and workflows should be preserved
where practical and must not be deleted solely because completion is separate.

Shared components remain platform-neutral: schemas, evidence formats,
identifiers, timestamps, normalized event structures, compatibility metadata,
APIs, path representations, package manifests, and provenance records.
Operating-system-specific behavior belongs behind platform adapters. Shared
logic must avoid unnecessary hard-coded Linux paths.

Platform claims require validation on the named platform. Linux-first status
does not imply that the ecosystem integration or a cross-platform production
release is complete.
