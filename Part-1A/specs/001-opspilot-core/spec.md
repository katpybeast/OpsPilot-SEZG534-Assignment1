# Feature Specification: OpsPilot Core

**Feature Branch**: `[001-opspilot-core]`

**Created**: 2026-11-15

**Status**: Draft

**Input**: User description: "Create OpsPilot Core, a local-first DevOps validation platform for Windows. The application is intended for software developers and DevOps engineers. It must provide the following features: 1. CI/CD Log Analyzer: Accept plain-text pipeline logs and detect known build, dependency, and test failures. 2. Dockerfile Validator: Check Dockerfiles for predefined configuration and security risks. 3. Kubernetes Validator: Parse Kubernetes YAML files and identify malformed YAML, missing resource limits, and privileged containers. 4. Security Checks: Detect predefined risky configurations using deterministic rules. 5. Validation Reports: Generate structured PASS, FAIL, and WARNING results with rule IDs, severity, descriptions, and evidence. 6. Local History: Store validation reports in SQLite. 7. Web Interface: Provide a local Streamlit dashboard to upload files and view results. Technical constraints: - Python 3.11+ - Streamlit - SQLite - Pytest - Ruff - Bandit - Maximum input file size: 1 MB - No cloud infrastructure, paid APIs, or external services. - Never execute uploaded files or automatically modify infrastructure. Define functional requirements, non-functional requirements, measurable acceptance criteria, input validation, and error handling. Use the existing OpsPilot Core constitution. Create the feature specification only. Do not implement code."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate CI/CD logs for common pipeline failures (Priority: P1)

A developer or DevOps engineer uploads a plain-text build or deployment log from a Windows-based pipeline and wants to quickly understand whether the result is a pass, failure, or warning. The system should highlight the likely cause, show the evidence from the relevant lines, and let the user assess the issue without running any of the pipeline content.

**Why this priority**: This is the primary operational use case for the product. Fast identification of build, dependency, and test failures reduces wasted investigation time and supports local troubleshooting without internet or cloud services.

**Independent Test**: A user can upload one log file, run validation, and receive findings tied to known failure patterns with descriptive evidence.

**Acceptance Scenarios**:

1. **Given** a plain-text log file containing a known dependency resolution failure, **When** the user uploads it to the dashboard and starts validation, **Then** the system identifies the issue as FAIL and shows the relevant rule ID, severity, description, and supporting log evidence.
2. **Given** a log file with no matching rule violations, **When** the user validates it, **Then** the system returns a PASS result for the applicable checks and does not invent a failure.
3. **Given** a log file containing one known risky pattern and one non-critical warning, **When** the user validates it, **Then** the system emits a FAIL or WARNING outcome consistent with the configured rule severity and includes evidence from the log.

---

### User Story 2 - Review Docker and Kubernetes configuration risks before deployment (Priority: P1)

An engineer wants to validate configuration files before they are used in a build or deployment process. The system should inspect Dockerfiles and Kubernetes YAML, flag risky or malformed content, and help the user understand each finding without executing the files.

**Why this priority**: Misconfigured containers and cluster manifests are common causes of deployment failure and security exposure. Early deterministic checks provide high user value and reduce risk before operational changes.

**Independent Test**: A user can upload a Dockerfile or Kubernetes manifest and receive structured results for malformed content, missing safeguards, or risky configuration.

**Acceptance Scenarios**:

1. **Given** a Dockerfile that uses root execution or exposes a privileged port, **When** the user validates it, **Then** the system records a FAIL or WARNING result with the associated rule ID, severity, description, and evidence.
2. **Given** a Kubernetes YAML file that is malformed or omits required resource limits, **When** the user validates it, **Then** the system reports the relevant YAML or policy issue and identifies the affected resource.
3. **Given** a Kubernetes manifest that defines a privileged container, **When** the user validates it, **Then** the system flags the condition as a security violation and explains the evidence in the report.

---

### User Story 3 - Review historical results and current validation outcomes in a local dashboard (Priority: P2)

A developer wants to look back at prior validation runs and compare them with the current file analysis. The dashboard should show current outcomes and historical entries in a local environment without cloud dependency or external API calls.

**Why this priority**: Local history supports recurring review, auditing, and debugging. It helps users understand whether a problem is new, recurring, or already known.

**Independent Test**: A user can open the local dashboard, review prior results, and navigate to recent validations stored in SQLite.

**Acceptance Scenarios**:

1. **Given** at least one valid validation run has been stored locally, **When** the user opens the dashboard, **Then** the system displays the recent validation history and the latest summary for each run.
2. **Given** a report contains multiple findings, **When** the user selects a run, **Then** the system shows the structured findings in a readable list.
3. **Given** an upload is rejected because it is too large or unsupported, **When** the user attempts the validation, **Then** the system provides a clear error message without leaving the user uncertain about the next step.

---

### Edge Cases

- What happens when an uploaded file exceeds 1 MB?
- What happens when the input is empty, unreadable, or not in a supported format?
- What happens when a Kubernetes YAML file contains multiple documents and one is malformed?
- What happens when a validation rule has no supporting evidence in the file content?
- What happens when SQLite history is unavailable or the report cannot be recorded?
- What happens when a rule would otherwise be a mandatory failure but the user is not permitted to remediate it automatically?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept plain-text CI/CD log files for analysis and identify known build, dependency, and test failures using deterministic rules.
- **FR-002**: The system MUST validate Dockerfiles for predefined configuration and security risks, including unsafe defaults and known risky patterns.
- **FR-003**: The system MUST parse Kubernetes YAML files and identify malformed YAML, missing resource limits, privileged containers, and other predefined risky configurations.
- **FR-004**: The system MUST apply security checks that detect deterministic risky configurations with explicit rule identifiers, severity levels, and descriptions.
- **FR-005**: The system MUST produce structured validation reports with PASS, FAIL, and WARNING statuses and include a rule ID, severity, description, and evidence for each finding.
- **FR-006**: The system MUST persist validation reports in SQLite for local history and retrieval by the user.
- **FR-007**: The system MUST provide a local Streamlit dashboard for file upload, validation execution, and display of result summaries and detailed findings.
- **FR-008**: The system MUST reject unsupported file types and files larger than 1 MB using clear validation errors.
- **FR-008 clarification**: The original 1 MB maximum input-size requirement, including FR-008, NFR-006, the input-validation requirement, and SC-001, means 1 MiB (1,048,576 bytes).
- **FR-009**: The system MUST validate input content before processing to detect empty files, unreadable content, malformed YAML, and invalid report data.
- **FR-010**: The system MUST never execute uploaded content, shell commands, Dockerfiles, Kubernetes manifests, or scripts as part of validation.
- **FR-011**: The system MUST not automatically modify infrastructure, change deployment state, or perform remediation actions as a result of validation findings.
- **FR-012**: The system MUST preserve deterministic rule behavior so that identical inputs and rule versions yield equivalent results.
- **FR-013**: The system MUST store enough metadata to trace each result to the source file, timestamp, validation status, and findings.
- **FR-014**: The system MUST clearly communicate validation errors to the user without exposing internal system details that are not necessary for the user to act.

### Non-Functional Requirements

- **NFR-001**: The system MUST run locally on Windows and operate without cloud infrastructure, paid APIs, or external services.
- **NFR-002**: The application MUST support Python 3.11 or later and use Streamlit, SQLite, Pytest, Ruff, and Bandit as documented in the constitution.
- **NFR-003**: Validation MUST be deterministic and explainable, producing consistent status decisions for the same rule set and input.
- **NFR-004**: Validation results MUST be precise enough for human review and must preserve the evidence required to explain each outcome.
- **NFR-005**: The dashboard and local persistence MUST remain accessible without requiring user authentication or remote services.
- **NFR-006**: Input limits MUST be enforced before processing so that oversized or unsupported content is rejected consistently.
- **NFR-007**: The application MUST maintain separation between the user interface, validation logic, security rules, and persistence layers.
- **NFR-008**: The system MUST support local development, testing, and validation in a standard Python environment without network dependency for core checks.
- **NFR-009**: The system MUST be verified in a local offline environment after dependencies are installed and MUST produce deterministic validation outcomes without internet connectivity for the same input and rule set.
- **NFR-010**: The system MUST demonstrate that UI, business logic, validation rules, and persistence remain separate modules through architecture verification and import-boundary checks during implementation and testing.

### Input Validation and Error Handling

- The system MUST reject empty uploads and unsupported file extensions with a clear user-facing error.
- The system MUST enforce the 1 MB maximum input size before performing analysis.
- The system MUST detect malformed Kubernetes YAML and report a structured validation failure instead of crashing or misclassifying the file.
- The system MUST handle file read errors and invalid report storage conditions gracefully and present a clear user message.
- The system MUST treat uploaded content as untrusted input at every stage and avoid execution or remediation behavior.
- The system MUST record warnings for conditions that are risky but do not necessarily block the review, while using FAIL when a rule indicates a mandatory issue.
- The system MUST allow human review of all validation findings and must not silently downgrade mandatory failures into warnings.

### Key Entities *(include if feature involves data)*

- **Validation Run**: Represents one file upload or validation request, including the timestamp, input type, status summary, and source file metadata.
- **Finding**: Represents one rule outcome and includes a unique rule ID, severity, description, status, and evidence from the uploaded content.
- **Source File**: Represents the uploaded artifact that is being analyzed, such as a pipeline log, Dockerfile, or Kubernetes manifest, with its metadata and constraints.
- **Report Record**: Represents a persisted validation result stored in the local SQLite history, including the report summary and individual findings.
- **Rule Set**: Represents the deterministic rule library used to evaluate known Docker, Kubernetes, security, and CI/CD patterns.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a supported file under the 1 MB size limit and receive a structured validation result within 5 seconds for typical local developer workloads. Measurement condition: the validation run MUST be executed on a local Windows developer workstation using an installed local dependency set, a representative 1 MB input file, and the project-defined rule engine; the measured runtime MUST be recorded as evidence in the project test output or verification artifact.
- **SC-002**: At least 90% of predefined known failure patterns in the supported rule set are correctly classified as PASS, FAIL, or WARNING in the project test suite. Coverage denominator: the approved active rule IDs across the `ci_cd`, `docker`, `kubernetes`, and `security` rule families defined in the project rule registry; the measured coverage result MUST be recorded as evidence and the 90% threshold MUST NOT be changed silently.
- **SC-003**: All invalid uploads, oversized files, malformed YAML, and unsupported file types are rejected with clear, actionable user messages and no execution of the uploaded content.
- **SC-004**: The dashboard shows recent local validation history and allows users to review findings without requiring any external service or cloud access.
- **SC-005**: Each validation result includes enough evidence to explain the outcome to a developer or DevOps engineer without requiring source code changes or additional tooling.
- **SC-006**: The system records each validation report in SQLite and preserves the result history for later review while refusing to perform automatic infrastructure changes.
- **SC-007**: Human operators can review the validation outcomes and decide whether to accept or reject the file based on the evidence, rather than trusting an automated PASS as final approval.

## Assumptions

- The initial version focuses on supported file types and predefined rule checks rather than arbitrary custom rule definition by end users.
- Project users are developers and DevOps engineers working on Windows-based local environments who need offline validation.
- Validation results are intended for human review and not for automatic deployment or remediation.
- The rule library is deterministic and versioned so that repeat validation under the same conditions yields consistent outcomes.
- The design assumes no cloud dependency for core operations; offline local execution is the default operating model.
