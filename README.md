# OpsPilot — SEZG534 Assignment 1

**Course:** SEZG534 — AI-Augmented Software Development Lifecycle  
**Assignment:** Specification-Driven Development & Harness Engineering

OpsPilot contains two local-first DevOps validation applications developed using a specification-driven workflow.

## Repository structure

- `Part-1A/` — OpsPilot Core: deterministic DevOps validation.
- `Part-1B/` — OpsPilot AI: non-deterministic, locally hosted AI log explanation and evaluation.
- `README.md` — Repository overview and setup guidance.

## Part 1A — OpsPilot Core

OpsPilot Core analyses supported DevOps inputs using predefined deterministic rules.

### Capabilities

- CI/CD and build-log validation.
- Dockerfile configuration and security checks.
- Kubernetes YAML validation.
- Structured findings with rule IDs, severity, descriptions and evidence.
- Local SQLite report history.
- Input validation, including a 1 MiB size limit.
- Local Streamlit interface.

Uploaded content is analysed, not executed. The application does not perform remote validation, deployment or automatic remediation.

### Setup

Prerequisites: Python 3.11+ and Windows.

Open PowerShell in the `Part-1A` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Run

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Tests and quality checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m bandit -r app
```

Recorded final verification evidence reports 32 passing tests, clean Ruff checks and Bandit exit code 0. See the evidence files under `Part-1A/evidence/`.

## Part 1B — OpsPilot AI

OpsPilot AI uses a locally hosted Qwen2.5 1.5B model through Ollama to generate explanations of DevOps logs.

### Design and controls

- Local Ollama endpoint: `http://127.0.0.1:11434`.
- Model: `qwen2.5:1.5b`.
- Non-deterministic generation; no fixed seed.
- Temperature: 0.7.
- Context setting: 4096.
- Maximum output setting: 768.
- Structured JSON response validation.
- Independent schema, invariant and safety checks.
- Semantic evaluation against a fixed rubric.
- Human review and repair workflow.
- No cloud model calls intended during application runtime.

The evaluation dataset contains 17 cases, with three attempts per case (51 attempts total). The predeclared semantic acceptance threshold is 80%.

### Setup

Prerequisites: Windows, Python 3.11+, and Ollama with the approved model already provisioned.

Open PowerShell in the `Part-1B` directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
ollama list
```

Confirm that `qwen2.5:1.5b` is available locally before launching the application.

### Run

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

### Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
```

### Run the evaluation harness

```powershell
.\.venv\Scripts\python.exe run_full_evaluation.py
```

Check the project's evaluation instructions and evidence for the recorded run and its output.

### Evaluation outcome and limitations

**Recorded full evaluation: FAIL. Human decision: REJECT.**

The recorded evaluation comprised 17 cases and 51 attempts. Its semantic score was 35.686275%, below the fixed 80% threshold. The report recorded 33 model-generation failures and one safety failure. Schema and invariant failures were reported as zero.

The result is not an acceptance pass. Resource compatibility on the intended 8 GB target device also remains unresolved. The failed evaluation and related evidence are retained rather than represented as a successful result.

See `Part-1B/evidence/full-evaluation/` for the evaluation report, harness log and supporting artifacts.

## Specification-driven development and harness engineering

Both projects include specification and development artifacts, tests, and evidence. The work follows a workflow involving problem definition, specification, clarification, planning, task breakdown, implementation, harness validation, feedback, repair and human review.

The applications have different acceptance outcomes. Part-1A's recorded deterministic checks passed. Part-1B's recorded full evaluation did not meet its acceptance threshold and was rejected.

## Safety and privacy

- Do not commit API keys, passwords, tokens or other secrets.
- Do not commit local virtual environments, caches or runtime databases.
- Use synthetic or appropriately sanitised test inputs.
- Review evidence for sensitive information before sharing.
- Part-1B's local model and runtime requirements must be checked on the target machine before claiming hardware compatibility.

## Assignment evidence

Detailed specifications, tests, evaluation artifacts and verification records are retained in the respective project folders.

This repository documents the implementation and its actual verification outcomes; a passing individual test or automated evaluation does not by itself establish overall human acceptance.
