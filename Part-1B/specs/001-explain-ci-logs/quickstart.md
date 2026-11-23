# Quickstart: OpsPilot AI — Intelligent DevOps Log Explainer

**Status**: Planned validation/run guide. Commands describe the implementation after it is created; this document does not claim that setup, tests, or evaluation have been run.

## Prerequisites

- Windows 10/11 laptop, 8 GB RAM, and 64-bit Python 3.11+ available on `PATH`.
- Ollama for Windows and the approved `qwen2.5:1.5b` model artifact provisioned before offline runtime; record the exact Ollama version, model tag, digest, and license source.
- PowerShell in the repository root.
- For first-time online dependency provisioning only: access to the configured Python package index. Runtime, application analysis, tests, and evaluation must not require internet access.
- For an offline setup, obtain a wheelhouse prepared for the target Windows architecture and Python version, then use the offline command below.

## Create a local environment

From the repository root, create a local virtual environment and install the project-declared development dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

If PowerShell activation scripts are permitted, activation is optional; commands below call the environment interpreter directly. For a machine without network access, install only from an already-provisioned wheelhouse:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links .\wheelhouse -r requirements-dev.txt
```

The environment is machine-local and must be recreated rather than copied. Dependency downloads are an installation step only, not a runtime service dependency.

## Provision and verify the local model

Install Ollama and provision the approved model artifact during an authorized setup phase while network access or an approved offline artifact source is available. Verify it is present with `ollama list`; do not rely on app startup or evaluation to download or update a model. Record the exact model digest/license and Ollama version in setup evidence. The proposed initial generation settings are temperature `0.7`, no seed, context `4096`, and output limit `768`; confirm effective settings through the implementation's provenance record.

Before full evaluation, confirm the Ollama API is reachable only at `http://127.0.0.1:11434`. Follow the exact three-fixture cold/warm protocol in the spec: three cold-start sessions, each invoking `resource-build-001`, `resource-dependency-001`, and `resource-test-001` once; then one warm session with one unmeasured warm-up per fixture and three measured repetitions per fixture. Use temperature 0.7, no seed, context 4096, and output limit 768. Sample once per second the combined working sets of unique PIDs in the Streamlit/Python app and Ollama/model-runner trees throughout startup and inference. The conservative screen is ≤2 GiB; record exact workload, conditions, OS/hardware, model/runtime/digest, configuration, PID selection/sampling, trial maxima, and overall maximum in `docs/evidence/model-resource-acceptance.md`. If exceeded, acceptance is blocked pending a smaller-model/quantization investigation or justified specification revision and the identical remeasurement. Even a screen pass does not prove compliance with the constitution's qualitative “not resource-intensive” requirement. Project-owner compatibility determination is required; until it is documented, the design and overall acceptance gates remain blocked. Separately measure SC-005 with the model loaded: at least `ceil(0.95 × N)` valid fixtures return schema-validated JSON within 5 seconds end-to-end; record cold-load in `reports/evaluations/performance.json`. No model fit, latency, or quality is assumed. Offline runtime must not require internet or pull a model.

## Launch the local application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open the local address printed by Streamlit. The server must bind only to loopback. Paste a synthetic CI/CD failure log, submit it, and inspect the single JSON response. No raw log should be retained after the request, and the application must not contact an external service. If Ollama is unavailable or generation/validation fails, expect a safe `analysis_error` response; the app must not fall back to a deterministic rule explanation.

## Run automated tests and static checks

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\ruff.exe format --check .
```

Expected acceptance behavior: commands return success only when the automated suite, lint rules, and formatting checks pass. Actual outcomes must be recorded when run; none are asserted here.

## Run the evaluation harness

```powershell
.\.venv\Scripts\python.exe -m opspilot.evaluation.runner --dataset data\evaluation_cases.json --output reports\evaluations
```

The harness must preflight the dataset, make exactly three independent local model calls per fixture, and separately report model invocation, strict JSON/schema, structural-invariant, safety, deterministic per-attempt semantic score, and threshold outcomes. Its flat `attempt_results` collection is grouped by `case_id`; it contains exactly three individually inspectable attempts per case and no separate case-summary object. It must reject fewer than 15 cases or fewer than two `primary_category` cases for any category. The semantic threshold is fixed at 80% or higher and is not changed to obtain a pass.

For every fixture, the harness records three independent attempts using nonzero temperature and no seed. Each attempt is validated, scored, and preserved with its sanitized artifact/hash and model provenance. Outputs may coincide or differ; no equality or diversity guarantee is asserted. Preflight also requires each case's `primary_category` to be present in its `expected_categories`; an `UNKNOWN` primary case must expect `UNKNOWN` and cannot claim partial credit for returning it.

Expected acceptance behavior: the report records automated `evaluation_status` PASS/FAIL separately from `system_acceptance_status`, resource status, and constitution compatibility. Automated PASS does not imply overall acceptance. Every failed safety status uses only the four versioned `SAFETY-1` codes defined in the spec; unknown codes are rejected. Failed safety outcomes include attempt-linked reason codes and top-level failures. Each attempt record contains an immutable sanitized response or safe-failure artifact reference and digest plus separate schema/invariant/safety outcomes. Aggregate score is `100 × total earned points / (30 × case_count)`, equivalently `100 × total earned points / (10 × attempt_count)` with `attempt_count = 3 × case_count`; failed calls receive zero points but remain in the denominator.

When a preflight-passing aggregate is below 80%, expect one `SEMANTIC_CASE_BELOW_FULL_SCORE` semantic failure record for each attempt scoring below 10/10, including its attempt number, and one `DATASET` threshold record with `SEMANTIC_SCORE_BELOW_THRESHOLD`. The report's `failed_case_ids` lists the unique non-sentinel case IDs from all failure records. Partial scores alone do not create semantic failures when the aggregate is at least 80%.

## Human review and repair

1. Inspect the sanitized report, per-attempt outcomes/artifacts, model provenance/configuration, and dataset/rubric/application versions; locate each synthetic fixture by dataset version and case ID.
2. Record a human approval, rejection, or request for repair using only the fixed `human_reviewer` role and the corresponding schema reason code: `REVIEW_COMPLETE_ACCEPT`, `REVIEW_REJECT_QUALITY`, `REVIEW_REJECT_SAFETY`, `REVIEW_REJECT_EVIDENCE`, `REVIEW_REQUEST_REPAIR`, or `REVIEW_OTHER`. Do not enter a name, email, username, personal handle, or free-form personal details. Automated pass alone is not acceptance.
3. For a failure, retain the original report, record the repair reference, and rerun the complete affected evaluation without changing acceptance criteria.
4. Review the new report and explicitly approve only if all automated gates pass and the result is acceptable.

Human decisions are requirements of the workflow; this guide contains no fabricated decisions or evaluation outcomes.

## Windows acceptance evidence to capture during implementation

- Python version, Windows version, processor architecture, and installed RAM for the reference machine.
- Direct/transitive dependency versions, free/open-source license identifiers, and local-installability review.
- pytest, Ruff lint, and Ruff formatting check results.
- Full evaluation provenance and all sanitized attempt-level outcomes; keep failed runs as well as passes.
- A measured peak-working-set report for the exact cold/warm fixtures and one-second process-tree sampling, assessing the ≤2 GiB screen; include the later project-owner compatibility determination separately.
- A separate measured timing report for the fixed fixture set to assess the 95%-within-5-seconds latency criterion; record cold model-load time separately.
- A reviewer decision and repair/reevaluation links where applicable.

Remove secrets and sensitive details before saving or sharing any evidence. See [the evaluation report contract](contracts/evaluation-report.schema.json), [the response contract](contracts/explanation-response.schema.json), and [the data model](data-model.md).
