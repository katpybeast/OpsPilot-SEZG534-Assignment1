# Implementation Plan: OpsPilot Core

**Branch**: `001-opspilot-core` | **Date**: 2026-11-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-opspilot-core/spec.md`

## Summary

OpsPilot Core is a local-first Windows validation platform for developers and DevOps engineers. It provides deterministic analysis for CI/CD logs, Dockerfiles, and Kubernetes YAML, classifies findings as PASS/FAIL/WARNING with evidence, stores report history in SQLite, and presents results via a local Streamlit dashboard. The solution will enforce safe local-only processing, reject unsupported or oversized inputs, and maintain modular separation between UI, validation rules, and persistence.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Streamlit, SQLite, Pytest, Ruff, Bandit, PyYAML, and local Python package structure for rule evaluation.

**Storage**: SQLite database for local validation history and report persistence.

**Testing**: Pytest for unit and contract tests; Ruff for linting; Bandit for static security analysis.

**Target Platform**: Local Windows desktop deployment with no cloud runtime requirement.

**Project Type**: Local web application with background validation logic and persistent SQLite history.

**Performance Goals**: Process typical 1 MB input files quickly enough for interactive local review, with deterministic rule evaluation and readable findings.

**Verification Evidence**: The implementation MUST record measured validation runtime for representative 1 MB local inputs and MUST record the measured percentage of active rules covered by automated tests, using the approved active rule IDs from the rule registry as the denominator. The 90% coverage threshold and the 5-second processing target remain mandatory unless a formal specification change is approved.

**Constraints**: Offline operation, local-only execution, 1 MB maximum upload size, no execution of uploaded content, no automatic infrastructure remediation.

**Scale/Scope**: Initial implementation targets developer and DevOps validation workflows for log, Dockerfile, and YAML checks using a deterministic rule library.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Local-first requirement is satisfied by Windows-only local execution and offline processing.
- PASS: Deterministic validation and evidence-based findings align with the traceability and explainability principles.
- PASS: Security and input handling rules are explicit: no execution of uploaded content, supported file types only, enforced 1 MB limit.
- PASS: Test-first engineering is satisfied by the requirement to create tests for validation rules, reports, and input handling.
- PASS: Independent quality gates are required: Ruff, Bandit, and Pytest must all execute and be reported independently.
- PASS: SQLite is the designated local persistence mechanism.
- PASS: Human accountability is preserved because validation does not perform automatic deployment or remediation.
- PASS: No constitutional violation requires a complexity exception or override.

## Project Structure

### Documentation (this feature)

```text
specs/001-opspilot-core/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
├── spec.md              # Approved specification
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
app/
├── ui/
│   ├── dashboard.py
│   └── state.py
├── services/
│   ├── validation_service.py
│   ├── report_service.py
│   └── history_service.py
├── rules/
│   ├── ci_cd_rules.py
│   ├── docker_rules.py
│   ├── kubernetes_rules.py
│   ├── security_rules.py
│   └── rule_registry.py
├── models/
│   ├── finding.py
│   ├── report.py
│   └── validation_run.py
├── storage/
│   └── sqlite_repo.py
├── validators/
│   ├── log_validator.py
│   ├── dockerfile_validator.py
│   ├── kubernetes_validator.py
│   └── input_validator.py
├── schema/
│   └── report_contract.py
├── app.py
└── main.py

tests/
├── unit/
│   ├── test_log_rules.py
│   ├── test_docker_rules.py
│   ├── test_kubernetes_rules.py
│   ├── test_security_rules.py
│   └── test_report_schema.py
├── contract/
│   └── test_validation_contracts.py
├── integration/
│   └── test_dashboard_flow.py
└── e2e/
    └── test_local_validation.py
```

**Structure Decision**: Use a single local Python application with a modular internal layout. UI, validation logic, rules, models, and storage remain separate modules so rule logic can be tested independently and the dashboard can remain a thin presentation layer.

**Security Rule Ownership**: The approved `security` rule family owns all security findings. Docker and Kubernetes validators may reuse shared security-check helpers or invoke the security rule registry, but they must not emit duplicate security findings for the same issue. The canonical report must keep one security finding per issue using the stable `rule_id` and evidence from the matching source artifact.

## Complexity Tracking

No constitution violations or exceptional complexity exceptions are required for this feature.
