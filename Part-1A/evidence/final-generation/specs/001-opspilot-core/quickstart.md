# Quickstart: OpsPilot Core Validation Workflow

## Prerequisites

- Python 3.11+
- Local Windows environment
- Project dependencies installed in a local virtual environment
- Access to the validation input files to be reviewed

## Setup

1. Create a virtual environment for the Python project.
2. Install the project dependencies for local validation, testing, linting, and security scanning.
3. Confirm that SQLite is available in the local environment.
4. Confirm the Streamlit app is available to run locally.

## Validation scenarios

### Scenario 1: Validate a CI/CD log

1. Launch the local dashboard.
2. Upload a plain-text pipeline or build log.
3. Start validation.
4. Review the summary and finding list.
5. Confirm each issue includes rule ID, severity, description, and evidence.

Expected outcome: The report indicates PASS, FAIL, or WARNING and shows the relevant evidence from the log.

### Scenario 2: Validate a Dockerfile

1. Upload a Dockerfile.
2. Start validation.
3. Review findings for configuration or security risks.

Expected outcome: Risky settings are captured as structured findings with evidence from the Dockerfile.

### Scenario 3: Validate a Kubernetes manifest

1. Upload a YAML manifest.
2. Start validation.
3. Review malformed YAML and policy findings.

Expected outcome: Invalid YAML and manifest issues are reported with actionable details and no execution of the content.

### Scenario 4: Confirm input rejection behavior

1. Attempt to upload a file larger than 1 MB.
2. Attempt to upload an unsupported file type.
3. Attempt to upload an empty file.

Expected outcome: The system rejects each input with a clear user-facing error message and no file execution.

### Scenario 5: Confirm persistence

1. Run a validation on a supported file.
2. Review the local history list.
3. Open the latest record.

Expected outcome: The report is persisted in SQLite and visible in local history.

## Quality gates

The implementation must pass:
- Pytest for unit and contract validation
- Ruff for linting
- Bandit for static security analysis

The application must not perform remote validation or automatic remediation and must not execute uploaded content.
