# OpsPilot Core Constitution

## Core Principles

### I. Local-First and Zero-Cost Operation
- The application MUST run locally on Windows.
- No paid cloud infrastructure, subscriptions, or external AI APIs may be required.
- Core deterministic validation MUST work offline after dependencies are installed.
- Local execution and storage MUST be the default.

### II. Deterministic and Explainable Validation
- Identical inputs and identical rule versions MUST produce identical validation results.
- Every validation finding MUST include a unique rule ID, severity, description, and supporting evidence.
- Validation outcomes MUST use explicitly defined statuses: PASS, FAIL, or WARNING.
- Mandatory failures MUST NOT be silently downgraded to warnings.

### III. Test-First Engineering
- Every functional requirement MUST have corresponding test coverage.
- Unit and contract tests MUST be derived from approved acceptance criteria.
- Pytest MUST be used for automated testing.
- Tests MUST NOT be deleted, weakened, or bypassed merely to achieve a passing result.
- Changes to expected behaviour MUST be justified by an approved specification change.

### IV. Independent Quality and Security Gates
- Ruff MUST be used for linting.
- Bandit MUST be used for Python static security analysis.
- Pytest MUST execute mandatory unit and contract tests.
- The harness MUST report each gate independently.
- A failed mandatory gate MUST result in an overall FAIL.

### V. Secure Input Processing
- Uploaded files and log content MUST be treated as untrusted input.
- The application MUST NOT execute uploaded scripts, shell commands, Dockerfiles, or Kubernetes configurations.
- File types and input sizes MUST be restricted to explicitly supported limits.
- Secrets, credentials, and API keys MUST NOT be stored in source code or committed to Git.

### VI. Modular and Maintainable Architecture
- User interface, business logic, validation rules, and persistence MUST remain separate.
- Validation rules MUST be independently testable.
- SQLite MUST be used for local persistence where persistence is required.
- Error handling and report formats MUST be consistent and documented.

### VII. Traceability and Evidence Preservation
- Every implemented feature MUST trace back to an approved specification requirement.
- Tasks MUST trace back to the implementation plan.
- Harness failures MUST preserve relevant input, expected behaviour, observed behaviour, and diagnostic output.
- Initial and repaired implementations MUST be preserved as evidence.
- Harness results MUST NOT be manually altered to manufacture a PASS.

### VIII. Human Accountability
- Automated PASS MUST NOT be treated as automatic approval for production use.
- Final acceptance or rejection MUST be a human decision.
- Known limitations and residual risks MUST be documented.
- The application MUST NOT perform automatic infrastructure deployment or remediation.

## Technical Constraints

- Programming language: Python 3.11 or later.
- User interface: Streamlit.
- Local database: SQLite.
- Testing framework: Pytest.
- Linting: Ruff.
- Static security analysis: Bandit.
- Supported configuration formats: Dockerfile and YAML.
- Supported log inputs: Plain-text build and application logs.
- The application MUST operate without a running cloud service.
- All dependencies MUST be documented and installable through a local Python environment.

## Development Workflow

1. Establish the problem statement and measurable acceptance criteria before implementation.
2. Follow the approved Spec Kit workflow: constitution, specification, clarification, plan, tasks, analysis where applicable, and implementation.
3. Review generated code against approved requirements.
4. Run the independent deterministic harness after implementation.
5. Capture genuine failures and provide actionable feedback to the coding agent.
6. Repair the implementation without weakening specifications or validation gates.
7. Rerun the same harness.
8. Record the final human acceptance or rejection decision.

## Governance

- This constitution governs the development of OpsPilot Core.
- Specifications, plans, tasks, tests, and implementation MUST remain consistent with these principles.
- Any change to a constitutional principle MUST be documented and justified.
- Changes to requirements MUST be reflected in the relevant upstream Spec Kit artifacts.
- No implementation change may bypass mandatory security, lint, or test checks.
- The project owner is responsible for reviewing automated results and making the final acceptance decision.

**Version:** 1.0.0  
**Ratified:** 2026-11-15  
**Last Amended:** 2026-11-15