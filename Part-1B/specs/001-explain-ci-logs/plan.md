# Implementation Plan: OpsPilot AI — Intelligent DevOps Log Explainer

**Branch**: `001-explain-ci-logs` | **Date**: 2026-11-20 | **Spec**: [spec.md](spec.md)

**Input**: Approved feature specification and user-provided technical approach.

## Summary

Deliver a local Windows Streamlit application whose primary explanation generator is proposed Ollama model `qwen2.5:1.5b`. For valid submissions, it stochastically generates all eight response fields, grounding claims in the sanitized log and selecting evidence only from deterministic candidates. Deterministic code handles sanitization, safety, validation, and scoring. Automated evaluation PASS/FAIL is reported separately from overall system acceptance; passing evaluation cannot imply resource compliance, constitution compatibility, or acceptance. The conservative 2 GiB peak-working-set screen and fixed benchmark are unmeasured, and passing that screen alone does not establish compliance with the constitution's qualitative 8 GB/non-resource-intensive constraint. Project-owner compatibility determination is pending; the design gate is blocked until evidence and a governance decision or redesign resolve it. No model fit or quality result is claimed.

## Technical Context

**Language/Version**: Python 3.11+ (64-bit), Windows target.  
**Primary Dependencies**: Streamlit (local UI), Ollama for local inference using the proposed `qwen2.5:1.5b` model, and `jsonschema` (Draft 2020-12 contracts); Python standard library for JSON, normalization, evidence extraction, redaction, paths, and local reports. Development dependencies: Pytest and Ruff. Direct/transitive dependencies and the selected model license require documented audits.  
**Storage**: No database for first release. Synthetic dataset is version-controlled JSON. Sanitized evaluation reports are local JSON artifacts retained per run. SQLite is deferred unless a demonstrated local query/history requirement justifies it; raw logs are never persisted by default.  
**Testing**: Pytest unit, contract, integration, and evaluation tests; Ruff lint and format checks.  
**Target Platform**: Windows 10/11, local loopback Streamlit server and Ollama runtime, 8 GB RAM laptop; CPU inference is the baseline unless target hardware proves otherwise. The proposed conservative combined application/Ollama/model-runner peak-working-set screen is ≤2 GiB under the exact SC-009 workload. This is a measurable screen, not proof by itself of constitution compatibility.
**Project Type**: Single local web application plus local evaluation runner.  
**Performance Goals**: SC-005 requires at least `ceil(0.95 × N)` of `N` valid fixed-dataset submissions to receive schema-validated JSON within 5 seconds end-to-end with the model already loaded; record cold-load separately. This latency target is independent from SC-009's ≤2 GiB working-set screen. Neither has been measured.
**Constraints**: Runtime network only between browser/Streamlit and app/Ollama over loopback `127.0.0.1`; no external AI or cloud; nonzero generation temperature and omitted seed; three attempts/case; no submitted log execution; 262,144-byte input limit; no raw-log/prompt persistence; exact JSON contract; deterministic validation/scoring and fixed rubric/dataset versions; all automated gates and reviewer approval required.
**Scale/Scope**: Single local user; pasted text only; six categories; at least 15 synthetic evaluation cases; one screen and one local evaluation workflow; no accounts, upload, hosted service, automatic remediation, or required SQLite.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / gate | Plan decision | Result |
|---|---|---|
| I. Specification-first development | This plan traces architecture and acceptance to the approved spec; implementation follows tasks derived from it. | PASS |
| II. Local Windows execution | Streamlit binds to `127.0.0.1`; quickstart uses Windows PowerShell and local Python. | PASS |
| III. Free tools; no paid/cloud services | Python, Streamlit, `jsonschema`, Pytest, and Ruff are free/local; no runtime network dependency or external model. | PASS |
| IV. Data minimization and evidence safety | Synthetic fixtures; transient raw submissions; redacted output/report; no default raw-log persistence or caching. | PASS |
| V. Strict structured JSON | Versioned schema requires exact eight keys, enums, types, lengths, bounds, and status conditionals. | PASS |
| VI. Independent schema/invariant validation | Validate serialized response using a strict parser, independent schema validator, then separate invariants/safety checks. | PASS |
| VII. Deterministic semantic evaluation | A deterministic local rubric scores each stochastic model response; aggregation is reproducible and no model-as-judge is used. | PASS |
| VIII. Minimum dataset | JSON dataset minimum 15, with two `primary_category` cases per each of six category values and all seven coverage tags. | PASS |
| IX. Prompt injection/adversarial safety | Treat all log text as untrusted; no dynamic evaluation/execution; test instruction isolation, malformed/boundary inputs, redaction, and unsafe suggestions. | PASS |
| X. Mandatory human review | Human approval remains mandatory, but cannot alone accept a system with unresolved resource or constitution-compatibility gates. | PASS, RESOURCE/GOVERNANCE GATES PENDING |
| XI. Immutable acceptance criteria | Fix 80% minimum and hard gates before runs; changes require governance/versioning and rerun. | PASS |
| XII. Preserve development/evaluation record | Preserve initial source state, failed reports, repairs, and final sanitized report; never overwrite earlier runs. | PASS |

**Resource and constitution-compatibility gate**: BLOCKED. The constitution says required workflows must fit an 8 GB Windows laptop and MUST NOT require a large local model or other resource-intensive component to pass baseline acceptance. The proposed Ollama/Qwen workflow has not been measured, and the 2 GiB screen is only a conservative quantitative screen—not a reinterpretation or proof of the qualitative constitutional requirement. The project owner must review actual benchmark evidence and record compatibility. If the architecture cannot satisfy the principle, redesign it or obtain a formal constitution amendment through governance; this plan does not amend the constitution.

**Pre-research gate**: NOT CLEARED. After the T056 decision and separate explicit T058 owner approval, a bounded preliminary spike may use the documented 15.7 GiB Windows computer. Label its measurements **PRELIMINARY — NOT FINAL SC-009 EVIDENCE**; they are not 8 GB evidence. The existing measurement-only authorization does not authorize application implementation or an application run.
**Post-design gate**: BLOCKED. T059 is provisional and does not authorize broader implementation; that requires separate T060 owner approval. Before final T054, T061 must identify and verify a genuine Windows 8 GB target using sanitized system-generated evidence of its hardware, Windows version and installed RAM in bytes. If no suitable target is available or verified, final T054 and acceptance remain blocked unless a separately approved governance route resolves the applicable requirements. Final T054 evidence, the final T057 determination and T050 human approval remain required, with remeasurement and owner review when changes make earlier evidence inapplicable. T060 does not establish acceptance. No implementation or test outcome is claimed.

## Success Criteria Verification Map

| Criterion | Planned verification |
|---|---|
| SC-001 | Response schema/serialization tests and report pipeline checks in `tests/contract/` and `tests/evaluation/test_report.py`. |
| SC-002 | Three independent stochastic invocations per fixed case with recorded model settings/artifacts; tests do not require outputs to match or differ. |
| SC-003 | Dataset schema/preflight coverage tests in `tests/evaluation/test_dataset.py`. |
| SC-004 | Scoring boundary and hard-gate report tests in `tests/evaluation/test_scoring.py` and `tests/evaluation/test_runner.py`. |
| SC-005 | End-to-end timing over fixed valid fixtures (at least `ceil(0.95 × N)` within 5 seconds with model loaded; cold-load separately) in `reports/evaluations/performance.json`. |
| SC-006 | Human review state tests and recorded final decision in `tests/evaluation/test_review.py` and `reports/evaluations/`. |
| SC-007 | Local-only/no-persistence tests and Windows verification in `tests/integration/test_local_only.py` and `docs/evidence/verification.md`. |
| SC-008 | Dataset-version/case-ID fixture lookup, immutable response artifact/digest validation, and reviewer workflow tests in `tests/evaluation/test_report.py`, `tests/evaluation/test_runner.py`, and `tests/evaluation/test_review.py`. |
| SC-009 | Exact three-fixture cold/warm protocol, one-second sampling, combined working set ≤2 GiB, conditional remediation, and separate project-owner constitution-compatibility decision recorded in `docs/evidence/model-resource-acceptance.md`, `docs/evidence/model-resource-investigation.md`, and `docs/evidence/constitution-compatibility.md`. |

## Application Architecture

1. **Streamlit UI** — One local page accepts pasted text, shows byte count/limit and privacy notice, submits on explicit action, and displays only the exact machine-readable JSON result in its output region. Invalid input also produces the contract's `invalid_input` JSON. Do not cache the input or output. Bind server to loopback and disable usage statistics.
2. **Input boundary** — Accept only text. Measure UTF-8 bytes before analysis; reject empty, over-limit, NUL, or over-10%-non-whitespace-control input (newline/CR/tab allowed). Redact recognized sensitive patterns into a transient safe representation before output generation; do not log or persist raw text.
3. **Local stochastic generation** — Prepare a bounded prompt containing sanitized log text as untrusted data and deterministic evidence candidates. Call Ollama only at `http://127.0.0.1:11434` using `qwen2.5:1.5b`, nonzero temperature, and no seed. The model generates all eight response fields, must ground explanatory claims in the sanitized log and supplied candidates, and may select evidence only from those deterministic candidates; independent code validates grounding/invariants and MUST NOT substitute a rule explanation after a failed model call.
4. **Strict output boundary** — Parse the model's JSON text with a strict local parser that rejects duplicate keys, `NaN`, infinities, and trailing content. Run the independent local schema validator, structural-invariant validator, and safety validator as distinct gates; the safety validator must inspect every available generated response without relying on schema/invariant outcomes and report per-attempt `safety_status` plus structured `safety_failure_reasons`. Use `not_applicable` only when model unavailable/timeout produced no output; this remains a hard model-call failure. Only output passing all required gates is shown as a successful AI explanation. Internal diagnostics must not include input text.
5. **Evaluation runner** — A local command-line module uses the same Ollama endpoint and settings as the UI but without browser state. It runs dataset preflight, makes three independent generation attempts per case, separately validates schema, invariants, safety, and semantic quality for every attempt, preserves one sanitized artifact/hash per attempt, calculates aggregate results, and writes a run report with a flat `attempt_results` collection grouped by `case_id`; it does not define a separate case-summary object or compare outputs for equality/diversity.
6. **Evidence and review** — Evaluation report files are immutable per run and include versions, model/runtime provenance, effective generation settings, and a flat collection of three attempt records per case grouped by `case_id`; each record includes separate schema/invariant/safety outcomes, safety failure codes, sanitized response artifact reference/digest, score, and reasons. There is no separate case-summary object. The dataset version plus case ID resolves the synthetic input without copying it into the report. Human review is a distinct recorded state using `reviewer_role: "human_reviewer"` and only one of the fixed reason codes `REVIEW_COMPLETE_ACCEPT`, `REVIEW_REJECT_QUALITY`, `REVIEW_REJECT_SAFETY`, `REVIEW_REJECT_EVIDENCE`, `REVIEW_REQUEST_REPAIR`, or `REVIEW_OTHER`; repair links to prior runs and creates a new run instead of rewriting evidence.
7. **Storage** — Keep response state in memory for the request. Store fixtures and sanitized reports in local files. Do not use SQLite in v1; no raw-log or Streamlit cache storage.
8. **Dependency boundary** — Runtime modules use Streamlit, `jsonschema`, Ollama's loopback HTTP API, and the standard library. Tests/Ruff are development-only. Audit packages and model license/provenance; do not install model weights at runtime. No external API/client, telemetry client, remote `$ref`, web asset, shell subprocess, or non-loopback runtime connection.

## Data Models and JSON Schema

The complete entity fields, transitions, category/rubric predicates, report lifecycle, and privacy rules are in [data-model.md](data-model.md). JSON contracts are under [contracts/](contracts/):

- [explanation-response.schema.json](contracts/explanation-response.schema.json): Exact response shape and status-specific fields.
- [evaluation-case.schema.json](contracts/evaluation-case.schema.json): Synthetic fixture, expected values, marker predicates, and safety requirements.
- [evaluation-dataset.schema.json](contracts/evaluation-dataset.schema.json): Versioned dataset with `minItems: 15`.
- [evaluation-report.schema.json](contracts/evaluation-report.schema.json): Sanitized run and human-review states.
- [contracts/README.md](contracts/README.md): strict parsing and independent checks outside JSON Schema.

Use local, checked-in schemas only. Schema validation does not replace input-relative evidence grounding, byte-level checks, duplicate-key rejection, redaction, deterministic invariants, or safety checks. It does not impose equality or diversity across stochastic responses. Dataset preflight additionally enforces globally unique IDs, all seven coverage tags, at least two cases for each primary category, and that every case's `primary_category` appears in its expected response category set. A primary category of `UNKNOWN` requires `UNKNOWN` in the expected set and disables UNKNOWN partial credit.

## Local Stochastic Explanation Model

- The primary explanation generator is Ollama on Windows using the proposed `qwen2.5:1.5b` model. It generates all eight fields as one contract-shaped JSON response, selecting evidence only from deterministic candidates extracted from sanitized input.
- Proposed initial generation settings are temperature 0.7, no seed, context 4096 tokens, and maximum output 768 tokens. Record actual Ollama version, requested/actual model tag, model digest, endpoint, and effective settings for every attempt (and summarize them at run level). Model licensing must be verified for the exact artifact; do not infer license solely from the model name.
- Call only `http://127.0.0.1:11434`; prohibit non-loopback inference endpoints, model downloads during runtime, cloud calls, and external telemetry. The model may be provisioned before offline runtime using an approved local/offline process.
- Each user request uses a fresh generation call with nonzero temperature and no fixed seed. Outputs may match or differ; no diversity or repeatability guarantee is asserted. Evaluation makes exactly three independent calls per case and stores every sanitized output.
- Deterministic modules validate/limit input, redact secrets, extract evidence candidates from the sanitized input, build an instruction-isolating prompt, parse/serialize JSON, validate schema and invariants, score outputs, and calculate the threshold. They do not generate successful fallback explanations.
- Model unavailability, timeout, malformed output, or rejected output produces the safe `analysis_error` response for interactive use and a failed attempt with zero rubric points for evaluation. Never silently replace a failed AI call with a rule-based explanation.
- Validate model response evidence against deterministic evidence candidates. Unsupported evidence, ungrounded claims, unsafe actions, or invalid status/confidence combinations fail their respective independent gate.
- Before full evaluation, measure model load/runtime memory and inference latency on the actual 8 GB Windows target. Model adequacy is unknown until these checks and the complete fixed evaluation have actually passed.

## Evaluation Harness

Implement the exact sequence and gate semantics from the spec:

1. Load and validate the versioned JSON dataset; enforce at least 15 unique cases, category quotas, primary-category membership in expected categories, all seven coverage tags, required metadata, synthetic-only fixtures, and sensitive-content screening.
2. Resolve and record Ollama/model provenance and effective settings. Verify the configured endpoint is loopback-only, temperature is nonzero, and seed is omitted.
3. For each dataset case, issue exactly three independent model calls. Each attempt is recorded even if Ollama is unavailable or times out.
4. Capture each actual output; parse/sanitize and retain one immutable per-attempt artifact plus SHA-256 digest. Do not compare outputs for equality and do not require output diversity. For model failure, retain only the safe failure response artifact; never persist raw prompts/logs or unsanitized output.
5. Strictly parse each generated response, rejecting duplicate keys, `NaN`, infinities, and trailing content; independently validate each against the local response JSON Schema.
6. Independently validate structural/property invariants and status relationships. Separately run the safety validator on every available generated response for evidence-candidate grounding, redaction/secret exposure, unsafe content/actions, instruction isolation, and non-execution safety; this validator MUST NOT depend on schema or invariant results. Record each attempt's `safety_status` and structured `safety_failure_reasons`. Use `not_applicable` only when unavailable/timeout produced no model output; the model-call hard gate still fails.
7. Score each attempt independently across five rubric dimensions (category, evidence, root cause, actions, uncertainty), 0–2 each. Invalid/unavailable attempts receive zero points and remain in the denominator.
8. Compute aggregate as `100 × total earned points / (30 × case_count)`, equivalently `100 × total earned points / (10 × attempt_count)`, where `attempt_count = 3 × case_count`. A dataset-preflight failure submits zero attempts and records score 0 without division.
9. Automated evaluation `PASS` requires dataset preflight, at least 15 cases, exactly three attempt records per case, category/tag coverage, zero schema/invariant/safety/model-call failures, and aggregate ≥80%. This automated status does not evaluate memory, latency, constitution compatibility, human approval, or overall system acceptance; preserve all evaluation thresholds unchanged.
10. Below 80%, record a `SEMANTIC_CASE_BELOW_FULL_SCORE` failure for every attempt scoring below 10, plus exactly one `DATASET` threshold failure `SEMANTIC_SCORE_BELOW_THRESHOLD`. Reconcile attempt counts, per-attempt points, aggregate, failed IDs, and artifacts. Automated evaluation status remains `PASS`/`FAIL` independently; after PASS, `system_acceptance_status` remains pending or blocked until separate resource, constitution-compatibility, and human-review gates pass.
11. A human reviewer records approval/rejection/repair request using the fixed non-identifying role/reason enum. Repair creates a new full evaluation run; preserve previous failures and artifacts.

12. **Overall system acceptance (separate gate)**: Do not mark the system accepted from an automated evaluation `PASS`. Require the fixed SC-009 workload to meet the ≤2 GiB screen, a linked evidence record, documented project-owner determination that the measured architecture satisfies the constitution, and human approval. If the owner cannot establish compatibility, block acceptance pending redesign or formal governance amendment. A screen pass alone is not the constitutional decision.

Failure reason codes are stable uppercase identifiers, never free-form exception text. Dataset-level preflight failures use reserved case identifier `DATASET` in the report because the spec requires every failure entry to carry a case ID. The report never includes raw log contents, secret-like values, stack traces, or sensitive details.

## Dataset Design

The implementation dataset is JSON, synthetic, sanitized, and versioned separately from the semantic rubric. Minimum dataset is 15 unique, non-empty inputs that pass the application boundary so every case can receive three model attempts. Malformed-log-content fixtures are valid submissions; empty, oversized, and malformed-control inputs belong to separate safety tests. Each case has exactly one `primary_category`; coverage counts use only that field. Include at least two cases for each category. All seven tags—normal, boundary, ambiguous, underspecified, malformed, missing-information, and adversarial—must occur; tags may overlap. Each case's primary category must also appear in its expected response category set.

Each case records an ID, text fixture, coverage tags, primary category, expected status and acceptable response category set, explicit empty-array expectations, confidence/missing-information expectations, required/forbidden literal evidence/cause/action markers, partial-credit declarations, and safety expectations. Do not store actual expected model output as the only oracle; predicates define allowed properties. Fixture authors review for secrets and personally identifying or operationally sensitive content before commit. No evaluation results are part of dataset design.

## Safety and Adversarial-Input Handling

- Treat pasted text and every substring within it as untrusted; it cannot change system behavior, schema, rules, policy, or task.
- Never execute content, actions, URLs, scripts, subprocesses, or suggested commands. Do not use input to build a shell command, import path, template, regex, or dynamic code.
- Enforce size/control-character limits before work; no silent truncation. Malformed input maps to the defined safe JSON response.
- Apply deterministic secret-pattern redaction before evidence/report construction. Redaction is defense-in-depth, not a promise to detect every secret; explain this limit to users and use only synthetic fixtures.
- Keep raw logs out of Streamlit cache, application logs, exceptions, database, report, screenshots, and exported artifacts. Avoid logging user text or exception reprs.
- Test explicit prompt-injection content, requests to reveal hidden instructions, command/code text, log excerpts resembling credentials, conflicting failure signatures, unicode/control characters, oversized content, and malformed categories.
- Disable usage-stat collection and bind to loopback. Do not include remote assets or reference URLs in the UI. Run tests that assert no external network call path exists and review dependencies for network-capable runtime behavior.
- Do not assert perfect secret detection or universal prompt-injection prevention; acceptance covers the fixed synthetic adversarial fixtures and all specified invariants.

## UI

- One Streamlit page with product purpose, local/privacy notice, pasted-log text area, UTF-8 byte limit indicator, and an explicit Explain action.
- Render the contract-shaped JSON output for all handled outcomes; put safe validation explanations in the `summary` and `root_cause` fields. Do not display a second prose diagnosis outside the JSON result that could disagree with the contract.
- For successful or insufficient responses, render the complete JSON object in a copyable, readable form; provide no auto-executing command buttons.
- Make empty/boundary/oversized states clear. Do not persist submission history or cache text across sessions. A reset control may clear the current session widget state.
- Local-only status and the warning not to paste secrets are visible before submission; no account or external service flow.

## Tests and Verification

Testing is planned but has not been run. Implementation tasks should create independent tests in these layers:

- **Unit**: byte/control validation; Unicode normalization; redaction; evidence extraction; prompt construction as untrusted-data framing; model-response normalization; output validation; confidence/status bounds; deterministic rubric marker matching, attempt scoring, and aggregate calculation.
- **Contract**: schema itself is valid; accepted/rejected JSON fixtures; exact keys/types/enums/lengths/array bounds/status conditionals; strict parser rejects duplicate keys, non-finite numbers, trailing content; serializer emits one valid object.
- **Invariant/security**: evidence is grounded in sanitized input; secret-like fixture values are absent from all outputs/reports; embedded instructions do not control the model; no commands execute; malformed/oversize inputs return safe contract output; model failures never invoke a successful rule-based fallback; raw input/prompt is not persisted or logged; runtime calls are loopback-only.
- **Dataset/evaluation**: case schema; at least 15 unique IDs; ≥2 `primary_category` each and each primary category accepted by that case; all seven tags; three stochastic invocations per case using temperature >0/no seed; no equality/diversity assertion; fixed score examples per attempt for each dimension and boundary at 80%; aggregate denominator `30 × case_count`; zero denominator avoided by preflight; report schema and per-attempt provenance/artifact reconciliation; failure on every hard gate; no threshold weakening.
- **Integration/UI**: pasted input round-trip to one JSON response; local-only configuration; browser/UI behavior for valid, insufficient, and invalid inputs; errors reveal no internals.
- **Windows acceptance**: verify Ollama/model installation and exact model digest/license, offline inference after provisioning, loopback-only endpoint behavior, and no external requests. Execute SC-009's exact three-fixture cold/warm protocol, sample once per second the aggregate working set of unique application and Ollama/model-runner process-tree PIDs, and screen against ≤2 GiB. If exceeded, block acceptance pending investigation/revision and repeat measurement. Separately measure SC-005 end-to-end latency with the model loaded, recording cold-load time separately. Then require a project-owner constitution-compatibility decision; a numeric screen pass is not sufficient. Record actual outcomes only after execution; Qwen2.5 1.5B is not assumed to fit or meet latency/quality/constitutional requirements.

## Project Structure

### Documentation (this feature)

```text
specs/001-explain-ci-logs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── README.md
│   ├── explanation-response.schema.json
│   ├── evaluation-case.schema.json
│   ├── evaluation-dataset.schema.json
│   └── evaluation-report.schema.json
└── tasks.md                 # Created by /speckit-tasks; not part of this plan
```

### Planned Source Code (implementation scope; not created by this planning command)

```text
.streamlit/
└── config.toml              # Loopback/privacy-safe app defaults
app.py                       # Streamlit entry point
opspilot/
├── __init__.py
├── input_validation.py      # Byte and control-character boundary
├── redaction.py             # Deterministic secret-like redaction
├── evidence.py              # Deterministic, sanitized input-grounded excerpts
├── prompting.py             # Prompt assembly with untrusted-log boundaries
├── model_client.py          # Ollama loopback client and three-attempt provenance
├── response.py              # Contract-shaped response construction/serialization
├── validation/
│   ├── schema.py            # Local Draft 2020-12 validator
│   └── invariants.py        # Independent structure/evidence/safety checks
├── ui.py                    # Thin Streamlit view and response rendering
└── evaluation/
    ├── dataset.py           # Dataset load/preflight
    ├── runner.py            # Ordered end-to-end local pipeline
    ├── scoring.py           # Deterministic rubric across stochastic attempts
    ├── report.py            # Sanitized, versioned run reports
    └── review.py            # Human decision/repair state handling
data/
└── evaluation_cases.json   # Synthetic versioned fixtures (created during implementation)
reports/
└── evaluations/            # Sanitized immutable per-run artifacts
requirements.txt             # Runtime dependency constraints
requirements-dev.txt         # Runtime + Pytest/Ruff
tests/
├── unit/
├── contract/
├── integration/
├── safety/
└── evaluation/
```

**Structure Decision**: Use one cohesive Python project with clear functional module boundaries, not separate frontend/backend services. Keep the approved schemas canonical under `specs/001-explain-ci-logs/contracts/`; implementation loads those checked-in documents by repository-relative path, avoiding duplicated schema copies and drift. Evaluation fixture and run-artifact paths are local and versioned; reports resolve synthetic inputs by dataset version plus case ID and point to three immutable sanitized per-attempt response artifacts with digests. Only sanitized artifacts may be retained. Reviewer state uses a non-identifying fixed role and stable reason code.

## Complexity Tracking

No constitution violations or extra architectural projects are proposed; no complexity exception is required.
