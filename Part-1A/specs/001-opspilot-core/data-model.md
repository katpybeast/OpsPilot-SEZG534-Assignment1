# Data Model: OpsPilot Core

## Overview

The data model centers on a validation run and its findings. Each run represents a single file upload or validation request. Each finding records one deterministic rule result with severity and evidence. The report model captures the aggregated summary and persistence record used in SQLite history.

## Entities

### ValidationRun

Represents one analysis request for one source file.

**Fields**
- id: unique run identifier
- created_at: timestamp for the validation run
- source_file_name: original uploaded file name
- source_type: one of `ci_log`, `dockerfile`, `kubernetes_yaml`, or `security_rule_input`
- status: summary status for the run (`PASS`, `FAIL`, `WARNING`)
- file_size_bytes: size of uploaded content
- user_context: optional label or originating workflow metadata

**Relationships**
- One ValidationRun has many Findings
- One ValidationRun corresponds to one persisted ReportRecord

### Finding

Represents one rule evaluation result.

**Fields**
- id: unique finding identifier
- validation_run_id: foreign key to ValidationRun
- rule_id: unique deterministic rule identifier
- rule_family: one of `ci_cd`, `docker`, `kubernetes`, or `security`
- severity: one of `INFO`, `WARNING`, `FAIL`
- status: normalized result state (`PASS`, `FAIL`, `WARNING`)
- description: human-readable explanation of the problem or pass condition
- evidence: excerpt or snippet from the input that supports the outcome
- location: optional section, resource, or line reference where the issue was detected

**Validation rules**
- rule_id must be unique within the rule set and stable across versions
- rule_family must be explicitly assigned and must reflect the owning rule family (`ci_cd`, `docker`, `kubernetes`, or `security`)
- security findings must belong to the `security` rule family and must be emitted once per canonical issue; Docker and Kubernetes validators may reuse shared security checks without producing duplicated final findings
- severity must be explicitly assigned
- evidence must be present for any FAIL or WARNING finding
- PASS results may include evidence for verification, but are not required to signal a problem

### ReportRecord

Represents the persisted local history entry stored in SQLite.

**Fields**
- id: primary key
- created_at: timestamp of storage
- summary_status: aggregated status of the report
- source_file_name: original artifact name
- validation_run_id: foreign key to ValidationRun
- findings_count: count of findings included in the report
- serialized_report: canonical JSON payload for the report

**Relationships**
- One ReportRecord reference a single ValidationRun
- One ReportRecord contains the structured, stored representation of the run

### SourceFile

Represents the uploaded artifact and its constraints.

**Fields**
- id: unique source file identifier
- original_name: file name
- content_type: mime-like classification or logical type
- content_size_bytes: effective size of the file
- checksum: optional hash to track content identity
- status: accepted, rejected, or unreadable

**Relationships**
- One SourceFile can be associated with one ValidationRun

### RuleSet

Represents the rule library used during validation.

**Fields**
- name: logical rule family (`ci_cd`, `docker`, `kubernetes`, `security`)
- version: deterministic version string for the set
- active_rule_ids: list of rule identifiers in effect
- ownership: the canonical family that owns any shared security check and must prevent duplicate final findings across validators

**Relationships**
- RuleSet governs many Findings across ValidationRuns

## State transitions

- Uploaded file is received
- File accepted or rejected based on size and type validation
- Validation run starts
- Findings are generated
- Report is summarized as PASS, FAIL, or WARNING
- Report is persisted to SQLite history

## Validation constraints

- An uploaded artifact must be supported and under 1 MB
- Malformed YAML or unreadable files must generate explicit failure records rather than crashing
- Each result must include evidence and a rule identifier
- Duplicate security findings must be prevented by canonical rule ownership and final report deduplication
- Mandatory FAIL findings must not be silently downgraded to WARNING
- The dashboard should present the current report and history without changing the source artifact
