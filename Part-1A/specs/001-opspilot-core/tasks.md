---

description: "Task list for OpsPilot Core implementation"
---

# Tasks: OpsPilot Core

**Input**: Design documents from `/specs/001-opspilot-core/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Pytest is required for all story-level validation and quality gates as defined in the constitution and quickstart workflow.

**Organization**: Tasks are grouped by user story so each story can be implemented, tested, and delivered independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Python app**: `app/`, `tests/`, and `specs/001-opspilot-core/`
- Local rule logic, data models, validators, SQLite persistence, and Streamlit UI remain separated per the implementation plan

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling for local validation work

- [X] T001 Create the project structure for app modules, tests, and feature docs under app/, tests/, and specs/001-opspilot-core/
- [X] T002 Initialize the Python 3.11+ environment and dependency list for Streamlit, SQLite, PyYAML, Pytest, Ruff, and Bandit in requirements.txt or pyproject.toml
- [X] T003 [P] Configure linting, test discovery, and security scanning in pyproject.toml, pytest.ini, or equivalent project configuration files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared models, validation infrastructure, and local persistence must be in place before user story work begins

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create the domain entities for validation runs, findings, reports, and source metadata in app/models/finding.py, app/models/report.py, and app/models/validation_run.py
- [X] T005 [P] Establish the rule registry and shared result model in app/rules/rule_registry.py and app/rules/__init__.py
- [X] T006 [P] Implement input validation and size/type checks in app/validators/input_validator.py for supported plain-text logs, Dockerfiles, and Kubernetes YAML under 1 MB
- [X] T007 Create the SQLite schema and persistence layer in app/storage/sqlite_repo.py for local history and stored report records
- [X] T008 Implement the canonical report contract helpers and schema validation in app/schema/report_contract.py
- [X] T009 Create the shared validation service bootstrap and rule execution flow in app/services/validation_service.py and app/services/report_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validate CI/CD logs for common pipeline failures (Priority: P1) 🎯 MVP

**Goal**: Detect known build, dependency, and test failure patterns in plain-text pipeline logs with deterministic rule output and evidence.

**Independent Test**: A user uploads a CI/CD log file, runs validation, and receives PASS/FAIL/WARNING findings that include a rule ID, severity, description, and supporting log evidence.

### Tests for User Story 1

- [X] T010 [P] [US1] Add unit tests for CI/CD log detection rules in tests/unit/test_log_rules.py
- [X] T011 [P] [US1] Add contract coverage for the validation report schema in tests/contract/test_validation_contracts.py

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement deterministic CI/CD rule definitions for dependency, build, and test failures in app/rules/ci_cd_rules.py
- [X] T013 [P] [US1] Implement the log validation parser and matching logic in app/validators/log_validator.py
- [X] T014 [US1] Implement log validation orchestration and aggregate status calculation in app/services/validation_service.py
- [X] T015 [US1] Implement report assembly for CI/CD findings and evidence preservation in app/services/report_service.py
- [X] T016 [US1] Add unsupported-input and unreadable-log handling to app/validators/input_validator.py for clear user-facing errors and no execution of uploaded content

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable

---

## Phase 4: User Story 2 - Review Docker and Kubernetes configuration risks before deployment (Priority: P1)

**Goal**: Flag risky Dockerfile settings and Kubernetes YAML issues without executing the files, including malformed YAML, missing resource limits, and privileged containers.

**Independent Test**: A user uploads a Dockerfile or a Kubernetes manifest and receives structured findings with explicit rule IDs, severities, descriptions, and evidence.

### Tests for User Story 2

- [X] T017 [P] [US2] Add unit tests for Dockerfile risk rules in tests/unit/test_docker_rules.py
- [X] T018 [P] [US2] Add unit tests for Kubernetes manifest policy checks in tests/unit/test_kubernetes_rules.py
- [X] T038 [P] [US2] Add unit tests for security validation rules in tests/unit/test_security_rules.py covering positive detections, safe configurations, malformed or incomplete inputs, and evidence reporting; depends on T037

### Implementation for User Story 2

- [X] T019 [P] [US2] Implement Dockerfile security and configuration rule checks in app/rules/docker_rules.py
- [X] T020 [P] [US2] Implement Kubernetes validation rules for malformed YAML, resource-limit gaps, and privileged containers in app/rules/kubernetes_rules.py
- [X] T037 [P] [US2] Implement independent security validation rules in app/rules/security_rules.py for approved security checks only, including privileged container detection and missing resource limits where applicable, without duplicating Docker or Kubernetes findings; depends on T005 and T006
- [X] T021 [P] [US2] Implement Dockerfile validation parsing and risk detection in app/validators/dockerfile_validator.py
- [X] T022 [P] [US2] Implement Kubernetes YAML parsing and error handling in app/validators/kubernetes_validator.py
- [X] T023 [US2] Integrate Docker, Kubernetes, and security validation into the main validation workflow in app/services/validation_service.py; depends on T019, T020, and T037
- [X] T024 [US2] Add manifest-level evidence assembly and detection of malformed multi-document YAML in app/services/report_service.py and app/validators/kubernetes_validator.py; depends on T020 and T037

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Review historical results and current validation outcomes in a local dashboard (Priority: P2)

**Goal**: Display current validation results and prior stored runs in a local Streamlit dashboard backed by SQLite history.

**Independent Test**: A user opens the dashboard, reviews recent local history, selects a prior validation, and sees the summary and findings without any cloud dependency.

### Tests for User Story 3

- [X] T025 [P] [US3] Add an integration test for the dashboard history flow in tests/integration/test_dashboard_flow.py
- [X] T026 [P] [US3] Add a local e2e validation test covering upload, report generation, and SQLite persistence in tests/e2e/test_local_validation.py

### Implementation for User Story 3

- [X] T027 [P] [US3] Implement local history storage and report retrieval in app/storage/sqlite_repo.py
- [X] T028 [P] [US3] Implement dashboard state management and history query helpers in app/ui/state.py
- [X] T029 [US3] Build the Streamlit dashboard for upload, validation execution, summary cards, and finding display in app/ui/dashboard.py
- [X] T030 [US3] Add history service orchestration and local report lookup in app/services/history_service.py
- [X] T031 [US3] Connect dashboard actions to validation and report services and provide clear error messaging for oversized or rejected inputs in app/app.py and app/ui/dashboard.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates, validation coverage, and documentation closure for the final feature

- [X] T032 [P] Validate the quickstart workflow against the implemented app flow in specs/001-opspilot-core/quickstart.md and app/
- [X] T033 [P] Run Ruff across app/ and tests/ to confirm lint compliance
- [X] T034 [P] Run Bandit against the Python implementation to confirm static security checks pass
- [X] T035 [P] Run the full Pytest suite for unit, contract, integration, and e2e tests across tests/
- [X] T036 Finalize user-facing documentation and traceability notes in specs/001-opspilot-core/ and app/ to ensure each feature maps back to the approved requirement set

### Evidence and governance verification

- [X] T039 [P] Verify local validation completes within 5 seconds for representative 1 MB CI/CD log and configuration samples in the standard Windows developer environment; record the measured runtime as evidence in tests/perf/test_validation_performance.py and the local verification artifact
- [X] T040 [P] Verify rule coverage is at least 90% across the active rule IDs in the approved `ci_cd`, `docker`, `kubernetes`, and `security` rule families; record the coverage denominator and measured percentage as evidence in tests/unit/test_security_rules.py or the project verification report
- [X] T041 [US2] Verify deterministic offline validation after dependencies are installed by running the local validation suite with no internet connectivity and recording matching results for the same input and rule set; traceable to NFR-001, NFR-003, and NFR-009
- [X] T042 [P] Verify architecture separation between UI, business logic, validation rules, and persistence by reviewing import boundaries and module ownership; traceable to NFR-007 and NFR-010; evidence to be captured in architecture boundary checks or the project verification artifact
- [X] T043 [US2] Add duplicate-finding prevention tests to ensure the approved security rule family emits one canonical security finding per issue across Docker, Kubernetes, and security validation paths; traceable to FR-004, FR-005, and the security ownership design in the data model and report contract

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; is the MVP story and should be validated before further scope expansion
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can proceed in parallel with US1 once the shared validators and rule registry are ready
- **User Story 3 (Phase 5)**: Depends on Foundational completion and on the main result/report flow from US1/US2 being stable enough to persist history
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories; this is the MVP and primary local validation use case
- **User Story 2 (P2)**: No dependency on US1, but it should integrate the same report contract and validation service outputs
- **User Story 3 (P3)**: Depends on the report model and history persistence created in the foundational layer; it consumes the outputs of US1 and US2

### Within Each User Story

- Tests must be defined before implementation for the story
- Models and shared validation primitives precede service work
- Services precede UI integration and persistence wiring
- Story completion occurs before moving to the next priority

### Parallel Opportunities

- Setup tasks T001-T003 can all run in parallel when the project shell is ready
- Foundational tasks T005-T008 can be implemented in parallel, with T009 as the integration step
- User Story 1 tests T010 and T011 can run in parallel
- User Story 1 implementation tasks T012 and T013 can run in parallel before T014-T016 integrate them into the validation service
- User Story 2 tests T017 and T018 can run in parallel; T038 follows T037 after the security rule module is in place
- User Story 2 implementation tasks T019-T022 and T037 can run in parallel before T023-T024 complete integration
- User Story 3 tests T025 and T026 can run in parallel
- User Story 3 implementation tasks T027 and T028 can run in parallel before T029-T031 connect the dashboard to the validation flow
- Polish tasks T032-T035 can be run in parallel as independent quality gates once implementation is complete
- Evidence and governance tasks T039-T043 run after the main quality gates and rule-family validation tasks; T041 depends on T035, T042 depends on T003 and T009, and T043 depends on T023, T024, T037, and T038

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together
Task: "Add unit tests for CI/CD log detection rules in tests/unit/test_log_rules.py"
Task: "Add contract coverage for the validation report schema in tests/contract/test_validation_contracts.py"

# Launch rule and validator work in parallel
Task: "Implement deterministic CI/CD rule definitions for dependency, build, and test failures in app/rules/ci_cd_rules.py"
Task: "Implement the log validation parser and matching logic in app/validators/log_validator.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Confirm a log upload produces a structured PASS/FAIL/WARNING report with evidence and clear rule IDs
5. Expand to User Story 2 only after the first validation flow is stable and testable
6. Complete User Story 3 last as it depends on persisted results and dashboard presentation

### Incremental Delivery

- Stage 1: deterministic log detection and schema output
- Stage 2: Dockerfile and Kubernetes security validation using the same report contract
- Stage 3: local history persistence and dashboard presentation
- Stage 4: polish, linting, static analysis, and final traceability checks

The workflow keeps each user story independently testable while preserving an MVP that can be validated without implementing the full dashboard or history layer first.
